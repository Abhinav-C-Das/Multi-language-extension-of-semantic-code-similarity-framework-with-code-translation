#!/usr/bin/env python3
"""
Cross-Language Auto-Optimizer
Brute forces all combination weights of CES, Baseline, and WL
to find the absolutely supreme hyper-parameters mathematically.
"""

import json
import re
from pathlib import Path
import itertools

def load_matrix(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load {filepath}: {e}")
        return {}

def main():
    ces_file = "evaluation/cross/ces_similarity_matrix_cross.json"
    wl_file = "evaluation/cross/wl_similarity_matrix_cross.json"
    base_file = "evaluation/cross/baseline_similarity_matrix_cross.json"
    gt_file = "data/cross/ground_truth.json"

    print("=======================================================")
    print("      CROSS-LANGUAGE OPTIMIZATION GRID SEARCH")
    print("=======================================================")

    m_ces = load_matrix(ces_file)
    m_wl = load_matrix(wl_file)
    m_base = load_matrix(base_file)

    try:
        with open(gt_file, 'r') as f:
            ground_truth = json.load(f)
    except:
        print(f"[ERROR] Could not load {gt_file}")
        return

    # Extract all testable student keys from ground truth
    core_students = []
    for problem, st_dict in ground_truth.items():
        for st_name in st_dict.keys():
            core_students.append((problem, st_name, st_dict[st_name]))
    
    # We have to build the references mapping from the raw matrices
    # Format raw matrices: {"p1/ref/ref1_java": {"p1/s/s1_java": 0.85}}
    # We will invert to lookup: student_key -> ref_strategy -> dict(ces=_, wl=_, base=_)
    
    # We first collect all reference keys and map them to their strategy
    # e.g., "p1/ref/ref1_java" -> {"problem": "p1", "strategy": "ref1"}
    
    student_maps = {}
    
    for problem, student, expected_ref in core_students:
        s_key = f"{problem}/s/{student}"
        student_maps[s_key] = {"problem": problem, "expected": expected_ref, "refs": {}}
        
        # Look through ces matrix for references belonging to this problem
        for ref_key in m_ces.get(s_key, {}):
            if not ref_key.startswith(f"{problem}/ref/"):
                continue
            
            ref_name = ref_key.split('/')[-1]
            strategy_match = re.match(r'(ref\d+)', ref_name)
            if not strategy_match:
                continue
            strategy = strategy_match.group(1)
            
            v_ces = m_ces.get(s_key, {}).get(ref_key, 0.0)
            v_wl = m_wl.get(s_key, {}).get(ref_key, 0.0)
            v_base = m_base.get(s_key, {}).get(ref_key, 0.0)
            
            if strategy not in student_maps[s_key]["refs"]:
                student_maps[s_key]["refs"][strategy] = []
            
            student_maps[s_key]["refs"][strategy].append({
                "ces": v_ces, "wl": v_wl, "base": v_base
            })

    # Now let's test all possible weights!
    steps = [x / 100.0 for x in range(0, 105, 5)]
    results = []

    for w_ces in steps:
        for w_wl in steps:
             for w_base in steps:
                if round(w_ces + w_wl + w_base, 5) != 1.0:
                    continue
                
                correct = 0
                total = 0
                
                for s_key, st_info in student_maps.items():
                    if not st_info["refs"]:
                        continue
                    
                    strategy_scores = {}
                    for strategy, versions in st_info["refs"].items():
                        # We take the MAXIMUM score across all implementations of that strategy
                        max_score = 0.0
                        for v in versions:
                            score = (v["ces"] * w_ces) + (v["wl"] * w_wl) + (v["base"] * w_base)
                            if score > max_score:
                                max_score = score
                        strategy_scores[strategy] = max_score
                    
                    if not strategy_scores:
                        continue
                        
                    predicted = max(strategy_scores, key=lambda k: strategy_scores[k])
                    expected = st_info["expected"]
                    
                    total += 1
                    if predicted == expected:
                        correct += 1
                
                if total > 0:
                    acc = correct / total
                    results.append({
                        "acc": acc,
                        "ces": w_ces,
                        "wl": w_wl,
                        "base": w_base,
                        "correct": correct,
                        "total": total
                    })

    # Sort results
    results.sort(key=lambda x: (x["acc"], x["ces"]), reverse=True)
    
    print("\n[✓] OPTIMIZATION COMPLETE!")
    print(f"Tested {len(results)} weight combinations.\n")
    
    print("="*60)
    print("🏆 TOP 10 HIGHEST ACCURACY COMBINATIONS:")
    print("="*60)
    
    for i, r in enumerate(results[:10]):
        print(f" #{i+1:<2} | Accuracy: {r['acc']*100:6.2f}% ({r['correct']}/{r['total']})  =>  CES: {r['ces']:.2f} | WL: {r['wl']:.2f} | Base: {r['base']:.2f}")

if __name__ == "__main__":
    main()
