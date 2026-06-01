"""
Zero-Shot CodeBERT Baseline for Cross-Language Code Retrieval
=============================================================
Computes Top-1 retrieval accuracy on the exact same 400-program cross-language
dataset used in the CKG Multi-View paper, using zero-shot CodeBERT embeddings
(microsoft/codebert-base) with NO fine-tuning.

Applies the identical Strict Hard-Filtering Constraint: same-language references
are blocked during retrieval, matching the paper's evaluation protocol exactly.

Outputs:
  - Per-problem accuracy breakdown
  - Overall Top-1 accuracy with 95% Wilson CI
  - Comparison table vs. CKG Multi-View framework
  - Results saved to: evaluation/cross/codebert_baseline_results.json
"""

import os
import json
import math
import re
import glob
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# ── Config ────────────────────────────────────────────────────────────────────
CROSS_DATA_DIR   = os.path.join(os.path.dirname(__file__), "data", "cross")
RESULTS_OUT      = os.path.join(os.path.dirname(__file__), "evaluation", "cross",
                                "codebert_baseline_results.json")
GROUND_TRUTH_PATH = os.path.join(CROSS_DATA_DIR, "ground_truth.json")
MODEL_NAME       = "microsoft/codebert-base"
MAX_TOKEN_LENGTH = 512          # CodeBERT max; code is truncated to this
DEVICE           = "cuda" if torch.cuda.is_available() else "cpu"
PROBLEMS         = [f"p{i}" for i in range(1, 21)]   # p1 … p20
LANG_SUFFIXES    = {"java": ".java", "cpp": ".cpp", "c": ".c"}

print(f"[INFO] Device: {DEVICE}")
print(f"[INFO] Loading {MODEL_NAME} …")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModel.from_pretrained(MODEL_NAME)
model.eval()
model.to(DEVICE)
print("[INFO] Model loaded.\n")

# ── Helpers ───────────────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    """Read a source code file; return empty string if missing."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def embed(code: str) -> np.ndarray:
    """
    Encode a code string with CodeBERT.
    Returns the [CLS] token embedding as a 1D numpy array (768-dim).
    No fine-tuning, no task head — pure zero-shot embedding.
    """
    inputs = tokenizer(
        code,
        return_tensors="pt",
        max_length=MAX_TOKEN_LENGTH,
        truncation=True,
        padding=False,
    )
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    # Use [CLS] token (index 0) from last hidden state — standard practice
    cls_vec = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
    return cls_vec


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def get_lang_from_filename(fname: str) -> str:
    """
    Extract language tag from filename.
    Handles: s1_java.java, s2_cpp.cpp, s3_c.c, s1.java (p1 edge case)
    Returns: 'java', 'cpp', or 'c'
    """
    base = os.path.splitext(os.path.basename(fname))[0]  # e.g. s2_cpp
    if "_java" in base or fname.endswith(".java"):
        return "java"
    if "_cpp" in base or fname.endswith(".cpp"):
        return "cpp"
    if "_c" in base or fname.endswith(".c"):
        return "c"
    return "unknown"


def get_submission_key(fname: str) -> str:
    """
    Map filename to ground_truth key.
    e.g. s1.java -> s1_java, s2_cpp.cpp -> s2_cpp, s3_c.c -> s3_c
    """
    base = os.path.splitext(os.path.basename(fname))[0]
    # handle the p1 edge case: s1.java → s1_java
    if re.match(r'^s\d+$', base):
        # no language suffix in stem — infer from extension
        ext = os.path.splitext(fname)[1]
        lang_map = {".java": "java", ".cpp": "cpp", ".c": "c"}
        lang = lang_map.get(ext, "unknown")
        return f"{base}_{lang}"
    return base


def get_ref_lang(ref_filename: str) -> str:
    """Extract language from ref filename, e.g. ref1_java.java → java."""
    base = os.path.splitext(os.path.basename(ref_filename))[0]
    if base.endswith("_java"):
        return "java"
    if base.endswith("_cpp"):
        return "cpp"
    if base.endswith("_c"):
        return "c"
    return "unknown"


def get_ref_strategy(ref_filename: str) -> str:
    """Extract strategy from ref filename, e.g. ref1_java.java → ref1."""
    base = os.path.splitext(os.path.basename(ref_filename))[0]
    # ref1_java → ref1
    match = re.match(r'^(ref\d+)_', base)
    if match:
        return match.group(1)
    return base


def wilson_ci(p_hat: float, n: int, z: float = 1.96):
    """95% Wilson Score Confidence Interval."""
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2*n)) / denom
    margin = (z * math.sqrt(p_hat*(1-p_hat)/n + z**2/(4*n**2))) / denom
    return centre - margin, centre + margin

# ── Main Evaluation Loop ──────────────────────────────────────────────────────

with open(GROUND_TRUTH_PATH, "r") as f:
    ground_truth = json.load(f)

total_correct  = 0
total_count    = 0
per_problem    = {}
detailed_log   = []

for problem in PROBLEMS:
    prob_dir = os.path.join(CROSS_DATA_DIR, problem)
    sub_dir  = os.path.join(prob_dir, "s")
    ref_dir  = os.path.join(prob_dir, "ref")

    if not os.path.isdir(sub_dir) or not os.path.isdir(ref_dir):
        print(f"[WARN] Missing directories for {problem}, skipping.")
        continue

    gt_map = ground_truth.get(problem, {})

    # ── Embed all references for this problem ─────────────────────────
    ref_files = glob.glob(os.path.join(ref_dir, "*"))
    refs = []   # list of (strategy, lang, embedding)
    for rf in ref_files:
        code = read_file(rf)
        if not code.strip():
            continue
        emb      = embed(code)
        strategy = get_ref_strategy(rf)
        lang     = get_ref_lang(rf)
        refs.append((strategy, lang, emb))

    if not refs:
        print(f"[WARN] No references found for {problem}, skipping.")
        continue

    # ── Embed all submissions and retrieve ────────────────────────────
    sub_files = sorted(glob.glob(os.path.join(sub_dir, "*")))
    prob_correct = 0
    prob_count   = 0

    for sf in sub_files:
        sub_key  = get_submission_key(sf)
        sub_lang = get_lang_from_filename(sf)
        gt_label = gt_map.get(sub_key)

        if gt_label is None:
            # Try alternate key format
            alt_key = os.path.splitext(os.path.basename(sf))[0]
            gt_label = gt_map.get(alt_key)

        if gt_label is None:
            print(f"  [SKIP] No ground truth for {problem}/{sub_key}")
            continue

        sub_code = read_file(sf)
        if not sub_code.strip():
            print(f"  [SKIP] Empty submission: {problem}/{sub_key}")
            continue

        sub_emb = embed(sub_code)

        # ── Strict Hard-Filtering: block same-language references ─────
        candidate_refs = [(s, l, e) for s, l, e in refs if l != sub_lang]

        if not candidate_refs:
            # Shouldn't happen with the full ref bank, but be safe
            print(f"  [SKIP] No cross-language refs for {problem}/{sub_key}")
            continue

        # ── Compute cosine similarity to all candidates ───────────────
        sims = [(s, cosine_sim(sub_emb, e)) for s, l, e in candidate_refs]

        # ── Top-1 retrieval: pick strategy with max mean similarity
        #    (each strategy appears in multiple languages; aggregate)
        strategy_scores = {}
        strategy_counts = {}
        for strat, sim in sims:
            strategy_scores[strat] = strategy_scores.get(strat, 0.0) + sim
            strategy_counts[strat] = strategy_counts.get(strat, 0) + 1
        mean_scores = {s: strategy_scores[s] / strategy_counts[s]
                       for s in strategy_scores}

        predicted = max(mean_scores, key=mean_scores.get)
        correct   = (predicted == gt_label)

        prob_correct += int(correct)
        prob_count   += 1

        detailed_log.append({
            "problem": problem,
            "submission": sub_key,
            "lang": sub_lang,
            "gt": gt_label,
            "predicted": predicted,
            "correct": correct,
            "scores": {s: round(v, 4) for s, v in mean_scores.items()},
        })

    per_problem[problem] = {
        "correct": prob_correct,
        "total":   prob_count,
        "accuracy": round(prob_correct / prob_count, 4) if prob_count else 0.0,
    }
    total_correct += prob_correct
    total_count   += prob_count

    print(f"  {problem}: {prob_correct}/{prob_count} "
          f"({100*prob_correct/prob_count:.1f}%)" if prob_count else
          f"  {problem}: no data")

# ── Final Statistics ──────────────────────────────────────────────────────────

overall_acc = total_correct / total_count if total_count else 0.0
ci_lo, ci_hi = wilson_ci(overall_acc, total_count)

print("\n" + "="*60)
print(f"Zero-Shot CodeBERT Baseline — Cross-Language Top-1 Retrieval")
print("="*60)
print(f"  Correct:          {total_correct}/{total_count}")
print(f"  Accuracy:         {100*overall_acc:.2f}%")
print(f"  95% Wilson CI:    [{100*ci_lo:.1f}%, {100*ci_hi:.1f}%]")
print(f"  Device used:      {DEVICE}")
print()
print(f"  CKG Multi-View Framework: 87.25% [84.0%, 90.5%]")
print(f"  Zero-Shot CodeBERT:       {100*overall_acc:.2f}% [{100*ci_lo:.1f}%, {100*ci_hi:.1f}%]")
print("="*60)

# ── Save Results ──────────────────────────────────────────────────────────────

results = {
    "model": MODEL_NAME,
    "protocol": "zero-shot, no fine-tuning, CLS token, hard-filtering applied",
    "total_correct": total_correct,
    "total_count":   total_count,
    "overall_accuracy": round(overall_acc, 4),
    "wilson_ci_95": [round(ci_lo, 4), round(ci_hi, 4)],
    "per_problem": per_problem,
    "detail": detailed_log,
}

os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
with open(RESULTS_OUT, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n[INFO] Full results saved to: {RESULTS_OUT}")
