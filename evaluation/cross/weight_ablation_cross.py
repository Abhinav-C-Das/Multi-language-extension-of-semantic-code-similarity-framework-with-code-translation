#!/usr/bin/env python3
"""
Cross-Language Weight Ablation Study
Performs a grid search over CES/Baseline/WL weights to find optimal combinations.
"""

import json
import os
import sys

# ============================================================
# Configuration
# ============================================================

INPUT_DIR = "evaluation/cross"
GT_FILE = "data/cross/ground_truth.json"

MATRICES = {
    "ces":      os.path.join(INPUT_DIR, "ces_similarity_matrix_cross.json"),
    "baseline": os.path.join(INPUT_DIR, "baseline_similarity_matrix_cross.json"),
    "wl":       os.path.join(INPUT_DIR, "wl_similarity_matrix_cross.json"),
}

GRID_STEP = 0.05  # Step size for weight grid search

# ============================================================
# Core Logic
# ============================================================

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {filepath}: {e}")
        return None

def get_predictions(final_matrix, ground_truth):
    """
    Given a similarity matrix and ground truth, predict strategies and compute accuracy.
    Returns: (num_correct, total, per_student_results)
    """
    total = 0
    correct = 0
    results = {}

    for problem, students in ground_truth.items():
        for student, expected_ref_strategy in students.items():
            student_key = f"{problem}/s/{student}"
            if student_key not in final_matrix:
                continue

            # Get matches for this student
            matches = final_matrix[student_key]

            # Find best match per strategy
            strategy_scores = {}
            for ref_key, score in matches.items():
                if "/ref/" not in ref_key:
                    continue
                # Extract strategy name (e.g. "p1/ref/ref1_java" -> "ref1")
                ref_name = ref_key.split("/")[-1].split("_")[0] 
                strategy_scores[ref_name] = max(strategy_scores.get(ref_name, 0.0), score)

            if not strategy_scores:
                continue

            # Predict strategy with highest score
            predicted_strategy = max(strategy_scores, key=strategy_scores.get)
            
            is_correct = (predicted_strategy == expected_ref_strategy)
            if is_correct:
                correct += 1
            total += 1
            
            results[student_key] = {
                "predicted": predicted_strategy,
                "expected": expected_ref_strategy,
                "correct": is_correct,
                "scores": strategy_scores
            }

    return correct, total, results

def compute_cross_lang_gap(temp_matrix, gt, common_keys):
    """
    For each student, measure how much the score drops when comparing
    to the CORRECT ref in a DIFFERENT language vs the SAME language.
    
    Returns: average gap (lower = more language-agnostic)
    """
    gaps = []
    
    for problem, students in gt.items():
        for student, expected_strategy in students.items():
            s_key = f"{problem}/s/{student}"
            if s_key not in temp_matrix:
                continue
            
            # Detect student language
            s_lang = None
            if student.endswith("_java"): s_lang = "java"
            elif student.endswith("_cpp"): s_lang = "cpp"
            elif student.endswith("_c"): s_lang = "c"
            if not s_lang:
                continue
            
            # Collect scores for the correct strategy refs, grouped by language
            same_lang_scores = []
            cross_lang_scores = []
            
            for ref_key, score in temp_matrix[s_key].items():
                if "/ref/" not in ref_key:
                    continue
                ref_name = ref_key.split("/")[-1]  # e.g., "ref1_java"
                # Check if this ref matches the expected strategy
                strategy = ref_name.split("_")[0]  # "ref1"
                if strategy != expected_strategy:
                    continue
                
                # Detect ref language
                r_lang = None
                if ref_name.endswith("_java"): r_lang = "java"
                elif ref_name.endswith("_cpp"): r_lang = "cpp"
                elif ref_name.endswith("_c"): r_lang = "c"
                if not r_lang:
                    continue
                
                if r_lang == s_lang:
                    same_lang_scores.append(score)
                else:
                    cross_lang_scores.append(score)
            
            if same_lang_scores and cross_lang_scores:
                same_max = max(same_lang_scores)
                cross_avg = sum(cross_lang_scores) / len(cross_lang_scores)
                gap = same_max - cross_avg  # positive = cross-lang is lower
                gaps.append(gap)
    
    if not gaps:
        return 1.0  # worst case
    return sum(gaps) / len(gaps)


def run_ablation():
    print("=" * 70)
    print(" CROSS-LANGUAGE WEIGHT ABLATION STUDY")
    print(" Optimizing for: Accuracy + Cross-Language Agnosticism")
    print("=" * 70)

    # Load data
    matrices = {}
    for name, path in MATRICES.items():
        data = load_json(path)
        if data is None:
            return
        matrices[name] = data
    
    gt = load_json(GT_FILE)
    if gt is None:
        return

    # Prepare common keys
    key_sets = [set(m.keys()) for m in matrices.values()]
    common_keys = set.intersection(*key_sets)
    print(f"[INFO] Common programs: {len(common_keys)}")
    
    # Generate weight combinations (grid search)
    combinations = []
    steps = int(1.0 / GRID_STEP) + 1
    for i in range(steps):
        w_ces = i * GRID_STEP
        remaining = 1.0 - w_ces
        sub_steps = int(remaining / GRID_STEP) + 1
        for j in range(sub_steps):
            w_base = j * GRID_STEP
            w_wl = 1.0 - w_ces - w_base
            if abs(w_wl) < 1e-9: w_wl = 0.0
            if w_wl >= -1e-9:
                combinations.append((w_ces, w_base, w_wl))

    print(f"[INFO] Testing {len(combinations)} weight combinations...")
    
    best_acc = -1.0
    best_weights = None
    best_gap = 1.0
    best_gap_weights = None
    results_log = []

    # Run grid search
    for (wc, wb, ww) in combinations:
        temp_matrix = {}
        
        # Build full matrix for all common keys (needed for gap computation)
        for s_key in common_keys:
            temp_matrix[s_key] = {}
            for r_key in common_keys:
                ces_score = matrices["ces"].get(s_key, {}).get(r_key, 0.0)
                bl_score = matrices["baseline"].get(s_key, {}).get(r_key, 0.0)
                wl_score = matrices["wl"].get(s_key, {}).get(r_key, 0.0)
                temp_matrix[s_key][r_key] = wc * ces_score + wb * bl_score + ww * wl_score

        # Evaluate accuracy
        correct, total, _ = get_predictions(temp_matrix, gt)
        acc = correct / total if total > 0 else 0.0
        
        # Compute cross-language gap
        gap = compute_cross_lang_gap(temp_matrix, gt, common_keys)
        
        results_log.append({
            "weights": (wc, wb, ww),
            "accuracy": acc,
            "correct": correct,
            "total": total,
            "gap": gap,
        })
        
        if acc > best_acc:
            best_acc = acc
            best_weights = (wc, wb, ww)
        
        # Best gap among 100% accuracy combos
        if acc >= best_acc and gap < best_gap:
            best_gap = gap
            best_gap_weights = (wc, wb, ww)

    # ── REPORT: Sorted by accuracy first, then by gap ──
    results_log.sort(key=lambda x: (-x["accuracy"], x["gap"]))

    print("\n" + "=" * 70)
    print(" TOP 15 COMBINATIONS (sorted by accuracy, then cross-language gap)")
    print("=" * 70)
    print(f"  {'CES':<6} {'Base':<6} {'WL':<6} | {'Acc':<7} {'Correct':<9} | {'Gap':<8} {'Assessment'}")
    print("  " + "-" * 65)
    for res in results_log[:15]:
        wc, wb, ww = res["weights"]
        gap_str = f"{res['gap']:.4f}"
        assessment = "[BEST]" if res == results_log[0] else \
                     "good" if res["gap"] < 0.10 else \
                     "biased" if res["gap"] < 0.20 else "poor"
        print(f"  {wc:.2f}   {wb:.2f}   {ww:.2f}   | {res['accuracy']:.0%}    {res['correct']}/{res['total']}      | {gap_str:<8} {assessment}")

    # ── Best by accuracy ──
    print(f"\n  [BEST ACCURACY]    CES={best_weights[0]:.2f}, Base={best_weights[1]:.2f}, WL={best_weights[2]:.2f}  ->  {best_acc:.0%}")
    if best_gap_weights:
        print(f"  [MOST AGNOSTIC]    CES={best_gap_weights[0]:.2f}, Base={best_gap_weights[1]:.2f}, WL={best_gap_weights[2]:.2f}  ->  gap={best_gap:.4f}")

    # ── Single View Analysis ──
    print(f"\n{'='*70}")
    print(" SINGLE VIEW ANALYSIS")
    print("=" * 70)
    for n, w in [("CES Only",  (1.0, 0.0, 0.0)), 
                 ("Base Only", (0.0, 1.0, 0.0)), 
                 ("WL Only",   (0.0, 0.0, 1.0))]:
        match = next((r for r in results_log if 
                      abs(r["weights"][0]-w[0])<1e-5 and 
                      abs(r["weights"][1]-w[1])<1e-5 and 
                      abs(r["weights"][2]-w[2])<1e-5), None)
        if match:
             print(f"  {n:<12}: Acc={match['accuracy']:.2%} ({match['correct']}/{match['total']})  Gap={match['gap']:.4f}")
        else:
             print(f"  {n:<12}: (Not found in grid)")

    # ── Current weights analysis ──
    current = next((r for r in results_log if 
                    abs(r["weights"][0]-0.25)<1e-5 and 
                    abs(r["weights"][1]-0.35)<1e-5 and 
                    abs(r["weights"][2]-0.40)<1e-5), None)
    if current:
        print(f"\n  [CURRENT]  CES=0.25, Base=0.35, WL=0.40  ->  Acc={current['accuracy']:.2%} ({current['correct']}/{current['total']})  Gap={current['gap']:.4f}")

    print("=" * 70)

if __name__ == "__main__":
    run_ablation()
