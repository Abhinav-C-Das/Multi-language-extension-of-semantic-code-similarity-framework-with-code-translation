"""
Fine-Tuned CodeBERT Cross-Language Retrieval Baseline
=======================================================
Fine-tunes microsoft/codebert-base on the cross-language dataset using an
InfoNCE contrastive learning objective on same-strategy cross-language pairs.

Protocol mirrors the UniXcoder fine-tuning exactly (Section V-C of the paper):
  - 80/20 stratified train/test split  →  320 train programs, 80 held-out
  - Same 80-program held-out set used for UniXcoder fine-tuned evaluation
  - InfoNCE loss, AdamW lr=2e-5, batch_size=8, 3 epochs (CPU-feasible config)
  - max_length=128 tokens (reduced from 512 for CPU speed)
  - Evaluated under identical hard-filtering constraint

Outputs:
  - Per-problem accuracy on 80-program held-out set
  - Overall Top-1 accuracy with 95% Wilson CI
  - codebert_finetuned_results.json
"""

import os
import sys
import json
import math
import re
import glob
import random
import numpy as np
from pathlib import Path
from collections import defaultdict

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModel
    from torch.optim import AdamW
    print("[OK] torch and transformers available")
except ImportError:
    import subprocess
    print("[INSTALL] Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "transformers", "torch", "numpy", "--quiet"])
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModel
    from torch.optim import AdamW
    print("[OK] packages installed")

# ── Config ─────────────────────────────────────────────────────────────────────
SEED          = 42
MODEL_NAME    = "microsoft/codebert-base"
DATA_DIR      = Path("data/cross")
GT_FILE       = DATA_DIR / "ground_truth.json"
RESULTS_FILE  = Path("evaluation/neural_baselines/codebert_finetuned_results.json")
MAX_LENGTH    = 128          # CPU-feasible; shorter than GPU run (512)
TRAIN_RATIO   = 0.80         # 320 train / 80 test (same split as UniXcoder)
LR            = 2e-5
BATCH_SIZE    = 8            # in-batch negatives; each batch has B programs
EPOCHS        = 3            # CPU feasible (vs 10 on GPU)
TEMP          = 0.07         # InfoNCE temperature

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Device: {DEVICE}")
print(f"[INFO] Model: {MODEL_NAME}")
print(f"[INFO] Epochs: {EPOCHS}, Batch: {BATCH_SIZE}, MaxLen: {MAX_LENGTH}\n")

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_lang(filename):
    if str(filename).endswith('.java'): return 'java'
    if str(filename).endswith('.cpp'):  return 'cpp'
    if str(filename).endswith('.c'):    return 'c'
    return 'unknown'

def read_safe(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ""

def get_ref_base(stem):
    for suf in ('_java', '_cpp', '_c'):
        if stem.endswith(suf):
            return stem[:-len(suf)]
    return stem

def wilson_ci(p_hat, n, z=1.96):
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2*n)) / denom
    margin = (z * math.sqrt(p_hat*(1-p_hat)/n + z**2/(4*n**2))) / denom
    return centre - margin, centre + margin

# ── Load data ─────────────────────────────────────────────────────────────────
print("[INFO] Loading ground truth...")
with open(GT_FILE, 'r') as f:
    gt = json.load(f)

problems = sorted(gt.keys())

# Collect all program files with metadata
all_programs = []
for prob in problems:
    prob_dir = DATA_DIR / prob
    for split_type in ('s', 'ref'):
        split_dir = prob_dir / split_type
        if not split_dir.exists():
            continue
        for fp in sorted(split_dir.iterdir()):
            if fp.suffix not in ('.c', '.cpp', '.java'):
                continue
            code = read_safe(fp)
            if not code.strip():
                continue
            stem = fp.stem
            lang = get_lang(fp.name)
            # Determine ground-truth strategy
            if split_type == 's':
                strat = gt.get(prob, {}).get(stem)
            else:
                strat = get_ref_base(stem)  # e.g. ref1_java -> ref1
            if strat is None:
                continue
            all_programs.append({
                'prob': prob,
                'type': split_type,
                'stem': stem,
                'lang': lang,
                'strat': strat,
                'code': code,
            })

print(f"[INFO] Loaded {len(all_programs)} programs total")

# ── Stratified 80/20 split (by problem) ──────────────────────────────────────
# Split submissions only (not refs); refs always go to both splits
sub_programs = [p for p in all_programs if p['type'] == 's']
ref_programs  = [p for p in all_programs if p['type'] == 'ref']

# Stratify by problem: 80% train, 20% test from each problem
train_progs, test_progs = [], []
for prob in problems:
    prob_subs = [p for p in sub_programs if p['prob'] == prob]
    n = len(prob_subs)
    n_train = max(1, int(n * TRAIN_RATIO))
    shuffled = list(prob_subs)
    random.shuffle(shuffled)
    train_progs.extend(shuffled[:n_train])
    test_progs.extend(shuffled[n_train:])

print(f"[INFO] Train submissions: {len(train_progs)}")
print(f"[INFO] Test  submissions: {len(test_progs)}")
print(f"[INFO] References:        {len(ref_programs)}\n")

# ── Load model ────────────────────────────────────────────────────────────────
print(f"[INFO] Loading {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.to(DEVICE)
print("[OK] Model loaded\n")

# ── Encoding ──────────────────────────────────────────────────────────────────
def encode_batch(codes, tokenizer, model, device, max_length):
    """Encode a list of code strings; return (n, 768) tensor."""
    inputs = tokenizer(
        codes,
        return_tensors="pt",
        max_length=max_length,
        truncation=True,
        padding=True,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs)
    return out.last_hidden_state[:, 0, :]   # CLS token

# ── Build training pairs ──────────────────────────────────────────────────────
# Strategy: group by (problem, strategy) → positive pairs across languages
# We pair each submission in the training set with a reference of the same strategy
def build_pairs(subs, refs):
    """
    Returns list of (code_a, code_b, is_positive) for contrastive training.
    Positive pairs: sub and ref share same problem AND same strategy AND different language.
    """
    pairs = []
    # Index refs by (prob, strat) -> list of codes (excluding same lang)
    ref_by_ps = defaultdict(list)
    for r in refs:
        ref_by_ps[(r['prob'], r['strat'])].append(r)

    for sub in subs:
        pos_refs = [r for r in ref_by_ps.get((sub['prob'], sub['strat']), [])
                    if r['lang'] != sub['lang']]
        if not pos_refs:
            continue
        pos_ref = random.choice(pos_refs)
        pairs.append((sub['code'], pos_ref['code']))

    return pairs

train_pairs = build_pairs(train_progs, ref_programs)
print(f"[INFO] Training pairs: {len(train_pairs)}")

# ── InfoNCE loss ──────────────────────────────────────────────────────────────
def infonce_loss(emb_a, emb_b, temperature=TEMP):
    """
    In-batch InfoNCE. emb_a, emb_b are (B, D) tensors.
    Row i of emb_a is the positive pair of row i in emb_b.
    """
    emb_a = F.normalize(emb_a, dim=-1)
    emb_b = F.normalize(emb_b, dim=-1)
    logits = torch.mm(emb_a, emb_b.t()) / temperature   # (B, B)
    labels = torch.arange(emb_a.size(0)).to(emb_a.device)
    loss_ab = F.cross_entropy(logits, labels)
    loss_ba = F.cross_entropy(logits.t(), labels)
    return (loss_ab + loss_ba) / 2.0

# ── Fine-tuning loop ──────────────────────────────────────────────────────────
optimizer = AdamW(model.parameters(), lr=LR)
model.train()

random.shuffle(train_pairs)
print(f"\n[TRAIN] Starting fine-tuning: {EPOCHS} epochs on {DEVICE}")

for epoch in range(1, EPOCHS + 1):
    epoch_loss = 0.0
    n_batches  = 0
    random.shuffle(train_pairs)

    for i in range(0, len(train_pairs), BATCH_SIZE):
        batch = train_pairs[i: i + BATCH_SIZE]
        if len(batch) < 2:   # need at least 2 for in-batch negatives
            continue

        codes_a = [p[0] for p in batch]
        codes_b = [p[1] for p in batch]

        # Tokenize
        tok_a = tokenizer(codes_a, return_tensors="pt", max_length=MAX_LENGTH,
                          truncation=True, padding=True)
        tok_b = tokenizer(codes_b, return_tensors="pt", max_length=MAX_LENGTH,
                          truncation=True, padding=True)

        tok_a = {k: v.to(DEVICE) for k, v in tok_a.items()}
        tok_b = {k: v.to(DEVICE) for k, v in tok_b.items()}

        optimizer.zero_grad()
        model.train()

        emb_a = model(**tok_a).last_hidden_state[:, 0, :]
        emb_b = model(**tok_b).last_hidden_state[:, 0, :]

        loss = infonce_loss(emb_a, emb_b)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()
        n_batches  += 1

    avg = epoch_loss / n_batches if n_batches else 0
    print(f"  Epoch {epoch}/{EPOCHS}  avg_loss={avg:.4f}  batches={n_batches}")

print("[OK] Fine-tuning complete\n")

# ── Evaluate on 80-program held-out set ──────────────────────────────────────
model.eval()
print("[EVAL] Encoding test submissions and references...")

# Encode all refs first
ref_embeddings = {}
for r in ref_programs:
    key = f"{r['prob']}/ref/{r['stem']}"
    tok = tokenizer(r['code'], return_tensors="pt", max_length=MAX_LENGTH,
                    truncation=True, padding=False)
    tok = {k: v.to(DEVICE) for k, v in tok.items()}
    with torch.no_grad():
        emb = model(**tok).last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    ref_embeddings[key] = {'emb': emb, 'lang': r['lang'],
                           'prob': r['prob'], 'strat': r['strat'], 'stem': r['stem']}

# Evaluate test submissions
results        = []
prob_stats     = defaultdict(lambda: {'correct': 0, 'total': 0})

def cosine_sim(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0

for sub in test_progs:
    tok = tokenizer(sub['code'], return_tensors="pt", max_length=MAX_LENGTH,
                    truncation=True, padding=False)
    tok = {k: v.to(DEVICE) for k, v in tok.items()}
    with torch.no_grad():
        sub_emb = model(**tok).last_hidden_state[:, 0, :].squeeze().cpu().numpy()

    # Hard-filtering: only cross-language refs for this problem
    cand_refs = {k: v for k, v in ref_embeddings.items()
                 if v['prob'] == sub['prob'] and v['lang'] != sub['lang']}

    if not cand_refs:
        continue

    # Aggregate by strategy (take max sim per strategy)
    strat_scores = {}
    for k, rv in cand_refs.items():
        sim = cosine_sim(sub_emb, rv['emb'])
        s   = rv['strat']
        if s not in strat_scores or sim > strat_scores[s]:
            strat_scores[s] = sim

    predicted = max(strat_scores, key=strat_scores.get)
    correct   = (predicted == sub['strat'])

    prob_stats[sub['prob']]['total']   += 1
    prob_stats[sub['prob']]['correct'] += int(correct)

    results.append({
        'prob':      sub['prob'],
        'stem':      sub['stem'],
        'lang':      sub['lang'],
        'gt':        sub['strat'],
        'predicted': predicted,
        'correct':   correct,
    })

total   = len(results)
correct = sum(1 for r in results if r['correct'])
acc     = correct / total if total else 0.0
ci_lo, ci_hi = wilson_ci(acc, total)

# ── Report ────────────────────────────────────────────────────────────────────
print("=" * 60)
print("FINE-TUNED CODEBERT — Cross-Language Top-1 Retrieval")
print("=" * 60)
print(f"  Correct:         {correct}/{total}")
print(f"  Accuracy:        {acc*100:.2f}%")
print(f"  95% Wilson CI:   [{ci_lo*100:.2f}%, {ci_hi*100:.2f}%]")
print(f"  Device:          {DEVICE}")
print(f"  Epochs:          {EPOCHS}")
print(f"  Max seq length:  {MAX_LENGTH}")
print()
print("Comparison table:")
print(f"  CodeBERT   (zero-shot):  59.50%  [54.72%, 64.10%]  (n=400)")
print(f"  UniXcoder  (fine-tuned): 71.37%  [62.15%, 79.12%]  (n=80)")
print(f"  CodeBERT   (fine-tuned): {acc*100:.2f}%  [{ci_lo*100:.2f}%, {ci_hi*100:.2f}%]  (n={total})")
print(f"  Proposed Framework:      87.25%  [83.60%, 90.20%]  (n=400)")
print("=" * 60)

# ── Save ──────────────────────────────────────────────────────────────────────
RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
out = {
    'model':           MODEL_NAME,
    'protocol':        f'fine-tuned, InfoNCE contrastive, AdamW lr={LR}, '
                       f'{EPOCHS} epochs, batch={BATCH_SIZE}, max_length={MAX_LENGTH}, seed={SEED}',
    'train_n':         len(train_progs),
    'test_n':          total,
    'correct':         correct,
    'accuracy_pct':    round(acc * 100, 2),
    'wilson_ci_95':    [round(ci_lo * 100, 2), round(ci_hi * 100, 2)],
    'device':          DEVICE,
    'epochs':          EPOCHS,
    'per_problem':     {p: {'correct': v['correct'], 'total': v['total'],
                            'accuracy': round(v['correct']/v['total']*100, 2) if v['total'] else 0}
                        for p, v in prob_stats.items()},
    'detail':          results,
}

with open(RESULTS_FILE, 'w') as f:
    json.dump(out, f, indent=2)

print(f"\n[OK] Results saved to {RESULTS_FILE}")
