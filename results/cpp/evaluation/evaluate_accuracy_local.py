#!/usr/bin/env python3
"""
Evaluate Accuracy - Local (CES V3 Enhanced)

Compares generated similarity matrix against ground truth.
Handles the specific format of ground_truth.json (dict of lists).
"""

import json
from pathlib import Path
import sys

# Paths
GROUND_TRUTH_FILE = Path("data/ground_truth.json")
SIMILARITY_MATRIX_FILE = Path("evaluation/matrices/final_similarity_matrix_ces_v3_local.json")

def load_json(path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def get_rank_1(scores):
    """Return list of references with the highest score"""
    if not scores:
        return []
    # Values might be floats, use small epsilon if comparing directly, 
    # but max() is usually safe for finding the peak
    max_score = max(scores.values())
    if max_score == 0 and len(scores) > 0:
         # Depending on logic, 0 might be valid or might mean no match. 
         # Usually valid if all are 0.
         pass
    return [ref for ref, score in scores.items() if score == max_score]

def main():
    print("=" * 80)
    print("EVALUATION - ACCURACY (LOCAL)")
    print("=" * 80)

    # Load Data
    print(f"Loading Ground Truth: {GROUND_TRUTH_FILE}")
    ground_truth = load_json(GROUND_TRUTH_FILE)
    if not ground_truth:
        print(f"[ERROR] Ground truth file not found: {GROUND_TRUTH_FILE}")
        sys.exit(1)

    print(f"Loading Similarity Matrix: {SIMILARITY_MATRIX_FILE}")
    matrix = load_json(SIMILARITY_MATRIX_FILE)
    if not matrix:
        print(f"[ERROR] Similarity matrix not found: {SIMILARITY_MATRIX_FILE}")
        print("Please run aggregation script first!")
        sys.exit(1)

    correct = 0
    total = 0
    errors = []
    
    # Iterate over Ground Truth
    # GT Format: {"p1": [["s1", "ref1"], ["s2", "ref1"], ...], ...}
    for prob, submissions in ground_truth.items():
        if prob not in matrix:
            print(f"[WARN] Problem {prob} not found in similarity matrix")
            continue
            
        problem_matrix = matrix[prob]
        
        for item in submissions:
            # item is ["s1", "ref1"]
            if len(item) < 2:
                continue
                
            student = item[0]
            expected_ref = item[1]
            
            total += 1
            
            if student not in problem_matrix:
                print(f"[WARN] Student {student} not found in {prob} matrix")
                errors.append({
                    "problem": prob,
                    "student": student,
                    "expected": expected_ref,
                    "predicted": "MISSING",
                    "reason": "Student not in matrix"
                })
                continue
            
            # Get scores for this student
            scores = problem_matrix[student]
            
            # Determine Rank 1
            predicted_refs = get_rank_1(scores)
            
            # Check if expected is in top predictions (handling ties)
            if expected_ref in predicted_refs:
                correct += 1
            else:
                errors.append({
                    "problem": prob,
                    "student": student,
                    "expected": expected_ref,
                    "predicted": predicted_refs,
                    "scores": scores
                })

    # Report
    if total == 0:
        print("[ERROR] No valid comparisons found!")
        sys.exit(1)
        
    accuracy = correct / total
    
    print("\n" + "-" * 40)
    print(f"RESULTS")
    print("-" * 40)
    print(f"Total Samples: {total}")
    print(f"Correct:       {correct}")
    print(f"Errors:        {len(errors)}")
    print(f"Accuracy:      {accuracy:.2%}")
    print("-" * 40)
    
    if errors:
        print("\nERROR DETAILS:")
        for e in errors:
            print(f"  {e['problem']}/{e['student']}: Expected {e['expected']}, Got {e['predicted']}")

if __name__ == "__main__":
    main()
