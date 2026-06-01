"""
GraphCodeBERT Zero-Shot Cross-Language Retrieval Evaluation
=============================================================
Evaluates microsoft/graphcodebert-base on the same 400-program cross-language
dataset under identical hard-filtering protocol as the paper and UniXcoder eval.

GraphCodeBERT (Guo et al., ICLR 2021) incorporates Data Flow Graphs (DFG)
into pretraining, making it the most structurally comparable neural model
to our CPG-based approach. It is the canonical code retrieval neural baseline.

Protocol: CLS-token cosine similarity, no fine-tuning, identical GT and
hard-filtering constraint as all other baselines.
"""

import json
import os
import sys
import math
from pathlib import Path
from collections import defaultdict

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

MODEL_NAME   = "microsoft/graphcodebert-base"
DATA_DIR     = Path("data/cross")
GT_FILE      = DATA_DIR / "ground_truth.json"
RESULTS_FILE = Path("graphcodebert_results.json")
MAX_LENGTH   = 512

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {device}")
print(f"[INFO] Loading model: {MODEL_NAME}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()
print("[OK] Model loaded\n")

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_lang(filename):
    if filename.endswith('.java'): return 'java'
    if filename.endswith('.cpp'):  return 'cpp'
    if filename.endswith('.c'):    return 'c'
    return 'unknown'

def read_file_safe(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ""

def encode_code(code_str):
    """CLS-token embedding via GraphCodeBERT."""
    tokens = tokenizer(
        code_str,
        return_tensors="pt",
        max_length=MAX_LENGTH,
        truncation=True,
        padding="max_length"
    ).to(device)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state[:, 0, :].squeeze().cpu().numpy()

def cosine_sim(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0

def wilson_ci(correct, total, z=1.96):
    if total == 0:
        return (0.0, 0.0)
    p = correct / total
    center = p + z**2 / (2*total)
    spread = z * math.sqrt(p*(1-p)/total + z**2/(4*total**2))
    denom  = 1 + z**2 / total
    return ((center - spread)/denom * 100, (center + spread)/denom * 100)

# ── Load ground truth ──────────────────────────────────────────────────────────
with open(GT_FILE, 'r') as f:
    gt = json.load(f)

problems = sorted(gt.keys())
print(f"[INFO] Problems: {len(problems)}")

# ── Encode all files ───────────────────────────────────────────────────────────
print("[INFO] Encoding all submissions and references...")
embeddings = {}
file_meta  = {}

for prob in problems:
    prob_dir = DATA_DIR / prob
    for subdir_name, ftype in [("s", "sub"), ("ref", "ref")]:
        subdir = prob_dir / subdir_name
        if not subdir.exists():
            continue
        for fp in sorted(subdir.iterdir()):
            if fp.suffix not in ('.c', '.cpp', '.java'):
                continue
            code = read_file_safe(fp)
            if not code.strip():
                continue
            stem = fp.stem
            key  = f"{prob}/{subdir_name}/{stem}"
            embeddings[key] = encode_code(code)
            file_meta[key]  = {
                'lang': get_lang(fp.name),
                'prob': prob,
                'type': ftype,
                'stem': stem
            }

print(f"[OK] Encoded {len(embeddings)} files\n")

# ── Build ref lookup ───────────────────────────────────────────────────────────
def get_ref_base(stem):
    for suf in ('_java', '_cpp', '_c'):
        if stem.endswith(suf):
            return stem[:-len(suf)]
    return stem

ref_by_prob_lang = defaultdict(lambda: defaultdict(list))
for key, meta in file_meta.items():
    if meta['type'] == 'ref':
        ref_by_prob_lang[meta['prob']][meta['lang']].append(key)

# ── Evaluate ───────────────────────────────────────────────────────────────────
results = []
direction_correct = defaultdict(int)
direction_total   = defaultdict(int)

for key, meta in file_meta.items():
    if meta['type'] != 'sub':
        continue

    prob     = meta['prob']
    sub_lang = meta['lang']
    sub_stem = meta['stem']

    gt_ref_base = gt.get(prob, {}).get(sub_stem)
    if gt_ref_base is None:
        continue

    cross_lang_refs = []
    for ref_lang, ref_keys in ref_by_prob_lang[prob].items():
        if ref_lang == sub_lang:
            continue
        for rk in ref_keys:
            ref_meta = file_meta[rk]
            ref_base = get_ref_base(ref_meta['stem'])
            sim = cosine_sim(embeddings[key], embeddings[rk])
            cross_lang_refs.append({
                'ref_key':    rk,
                'ref_lang':   ref_lang,
                'ref_base':   ref_base,
                'sim':        sim,
                'is_correct': (ref_base == gt_ref_base)
            })

    if not cross_lang_refs:
        continue

    cross_lang_refs.sort(key=lambda x: -x['sim'])
    top1 = cross_lang_refs[0]

    direction = f"{sub_lang}->{'java' if top1['ref_lang'] == 'java' else 'c_cpp'}"
    direction_total[direction] += 1
    if top1['is_correct']:
        direction_correct[direction] += 1

    results.append({
        'sub_key':   key,
        'sub_lang':  sub_lang,
        'prob':      prob,
        'gt_ref':    gt_ref_base,
        'top1_ref':  top1['ref_base'],
        'top1_lang': top1['ref_lang'],
        'top1_score':top1['sim'],
        'correct':   top1['is_correct'],
        'direction': direction
    })

# ── Report ─────────────────────────────────────────────────────────────────────
total   = len(results)
correct = sum(1 for r in results if r['correct'])
acc     = correct / total * 100 if total > 0 else 0
ci_lo, ci_hi = wilson_ci(correct, total)

print("=" * 70)
print("GRAPHCODEBERT ZERO-SHOT CROSS-LANGUAGE RETRIEVAL RESULTS")
print("=" * 70)
print(f"\nTotal evaluations:  {total}")
print(f"Correct (Top-1):    {correct}")
print(f"Aggregate Accuracy: {acc:.2f}%")
print(f"95% Wilson CI:      [{ci_lo:.2f}%, {ci_hi:.2f}%]")

print("\n-- Directional Breakdown --")
for k in sorted(direction_total.keys()):
    n    = direction_total[k]
    corr = direction_correct.get(k, 0)
    a    = corr / n * 100 if n > 0 else 0
    print(f"  {k:<25}: {corr}/{n} = {a:.2f}%")

print("\n" + "=" * 70)
print("Full comparison table (all neural baselines):")
print(f"  JPlag (token):              51.50%")
print(f"  MOSS (token):               54.20%")
print(f"  CodeBERT (zero-shot):       59.50%")
print(f"  UniXcoder (zero-shot):      68.92%  [64.22%, 73.26%]")
print(f"  GraphCodeBERT (zero-shot):  {acc:.2f}%  [{ci_lo:.2f}%, {ci_hi:.2f}%]  <-- NEW")
print(f"  TF-IDF baseline:            79.50%")
print(f"  Proposed Framework:         87.25%  [83.60%, 90.20%]")
print("=" * 70)

with open(RESULTS_FILE, 'w') as f:
    json.dump({
        'model':        MODEL_NAME,
        'total':        total,
        'correct':      correct,
        'accuracy_pct': round(acc, 2),
        'wilson_ci':    [round(ci_lo, 2), round(ci_hi, 2)],
        'by_direction': {
            k: {
                'n':       direction_total[k],
                'correct': direction_correct.get(k, 0),
                'acc':     round(direction_correct.get(k,0)/direction_total[k]*100, 2)
            }
            for k in direction_total
        }
    }, f, indent=2)
print(f"\n[OK] Results saved to {RESULTS_FILE}")
