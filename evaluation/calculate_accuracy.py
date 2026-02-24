import json
import argparse
import re
from pathlib import Path

def reshape_cross_matrix(flat_matrix):
    """
    Reshape flat NxN cross-language matrix into {problem: {student: {ref_strategy: score}}}.
    
    Input keys:  "p1/ref/ref1_java", "p1/s/s1_java"
    Output:      {"p1": {"s1_java": {"ref1": 0.92, "ref2": 0.41}}}
    
    For each ref, extracts strategy prefix (ref1 from ref1_java) and takes the
    MAX score across all languages for that strategy.
    """
    # Classify all keys into refs and students, grouped by problem
    problems = {}
    for key in flat_matrix:
        parts = key.split('/')
        if len(parts) != 3:
            continue
        problem, role, name = parts
        if problem not in problems:
            problems[problem] = {"refs": [], "students": []}
        if role == "ref":
            problems[problem]["refs"].append(key)
        elif role == "s":
            problems[problem]["students"].append(key)
    
    # Build nested structure
    nested = {}
    for problem, roles in problems.items():
        nested[problem] = {}
        for student_key in roles["students"]:
            student_name = student_key.split('/')[-1]  # "s1_java"
            ref_scores = {}
            
            for ref_key in roles["refs"]:
                ref_name = ref_key.split('/')[-1]  # "ref1_java"
                # Extract strategy prefix: "ref1_java" → "ref1", "ref2_cpp" → "ref2"
                strategy = re.match(r'(ref\d+)', ref_name)
                if not strategy:
                    continue
                strategy = strategy.group(1)
                
                # Get score from flat matrix
                score = flat_matrix.get(student_key, {}).get(ref_key, 0.0)
                
                # Take MAX across all languages for same strategy
                if strategy not in ref_scores or score > ref_scores[strategy]:
                    ref_scores[strategy] = score
            
            nested[problem][student_name] = ref_scores
    
    return nested


def calculate_accuracy(matrix_file, ground_truth_file, weights):
    # Load similarity matrix
    with open(matrix_file) as f:
        matrix = json.load(f)
    
    # Auto-detect language from matrix path if ground truth not specified
    if ground_truth_file is None:
        # Check if matrix path contains language indicator
        matrix_path = Path(matrix_file)
        if 'cross' in str(matrix_path).lower():
            ground_truth_file = "data/cross/ground_truth.json"
        elif 'java' in str(matrix_path).lower():
            ground_truth_file = "data/java/ground_truth.json"
        elif 'cpp' in str(matrix_path).lower() or 'c++' in str(matrix_path).lower():
            ground_truth_file = "data/cpp/ground_truth.json"
        elif '/c/' in str(matrix_path) or '\\c\\' in str(matrix_path):
            ground_truth_file = "data/c/ground_truth.json"
        else:
            # Default to C
            ground_truth_file = "data/c/ground_truth.json"
    
    # Load ground truth
    gt_path = Path(ground_truth_file)
    ground_truth = {}
    if gt_path.exists():
        with open(gt_path) as f:
            ground_truth = json.load(f)
    else:
        print(f"[ERROR] Ground truth not found at {gt_path}")
        return
    
    # Reshape cross-language flat matrix if needed
    # Cross-language format: {"p1/ref/ref1_java": {"p1/s/s1_java": 0.85, ...}}
    # Expected format:       {"p1": {"s1_java": {"ref1": 0.85, ...}}}
    sample_key = next(iter(matrix), "")
    raw_flat_matrix = None
    if '/' in sample_key:
        raw_flat_matrix = matrix  # keep raw for cross-language breakdown
        matrix = reshape_cross_matrix(matrix)
    
    # Calculate predictions
    correct = 0
    total = 0
    results = []
    
    for problem, students in matrix.items():
        for student, refs in students.items():
            if not refs:
                continue
            
            # Scores are already weighted during aggregation
            # Prediction: highest scoring reference
            predicted_ref = max(refs, key=lambda x: refs[x])
            
            # Get expected from ground truth
            expected_ref = None
            if problem in ground_truth and student in ground_truth[problem]:
                expected_ref = ground_truth[problem][student]
            
            if expected_ref:
                total += 1
                match = (predicted_ref == expected_ref)
                if match:
                    correct += 1
                
                results.append({
                    "problem": problem,
                    "student": student,
                    "expected": expected_ref,
                    "predicted": predicted_ref,
                    "match": match,
                    "scores": refs
                })
    
    if total == 0:
        print("[ERROR] No ground truth matches found")
        return
    
    # Display beautiful output
    print("\n" + "="*60)
    print(" "*15 + "ACCURACY EVALUATION REPORT")
    print("="*60)
    
    # Ground Truth Table
    print("\n📋 Ground Truth:")
    print("  " + "-"*56)
    print(f"  {'Problem':<12} {'Student':<15} → {'Expected Ref':<15}")
    print("  " + "-"*56)
    for problem, students in ground_truth.items():
        for student, expected in students.items():
            print(f"  {problem:<12} {student:<15} → {expected:<15}")
    print("  " + "-"*56)

    # ── Cross-Language Breakdown: student vs each ref per language ──
    if raw_flat_matrix is not None:
        print("\n🌐 Cross-Language Similarity Breakdown:")
        print("  (Similarity of each student against every ref in every language)")
        
        # Group by problem
        problems_map = {}
        for key in raw_flat_matrix:
            parts = key.split('/')
            if len(parts) != 3:
                continue
            problem, role, name = parts
            if problem not in problems_map:
                problems_map[problem] = {"refs": [], "students": []}
            if role == "ref":
                if key not in problems_map[problem]["refs"]:
                    problems_map[problem]["refs"].append(key)
            elif role == "s":
                if key not in problems_map[problem]["students"]:
                    problems_map[problem]["students"].append(key)
        
        for problem in sorted(problems_map.keys()):
            info = problems_map[problem]
            ref_keys = sorted(info["refs"])
            student_keys = sorted(info["students"])
            ref_names = [k.split('/')[-1] for k in ref_keys]
            
            print(f"\n  ── {problem} " + "─"*60)
            
            # Header
            header = f"  {'Student':<15}"
            for rn in ref_names:
                header += f" {rn:<12}"
            print(header)
            print("  " + "-"*(15 + 13*len(ref_names)))
            
            for sk in student_keys:
                sname = sk.split('/')[-1]
                row = f"  {sname:<15}"
                for rk in ref_keys:
                    score = raw_flat_matrix.get(sk, {}).get(rk, 0.0)
                    row += f" {score:<12.4f}"
                print(row)
        
        print()
    
    # Predictions Table — with per-ref similarity scores
    print("\n🎯 Predictions (with per-ref similarity scores):")
    print("  " + "-"*80)
    
    # Collect all ref strategy names across all results
    all_refs = sorted(set(ref for r in results for ref in r["scores"]))
    
    # Header
    ref_header = "  ".join(f"{r:<8}" for r in all_refs)
    print(f"  {'Problem':<8} {'Student':<15} {ref_header}  {'Pred':<8} {'Exp':<8} {''}") 
    print("  " + "-"*80)
    
    for r in results:
        status = "✓" if r["match"] else "✗"
        score_strs = []
        for ref in all_refs:
            score = r["scores"].get(ref, 0.0)
            # Highlight the predicted ref with brackets
            if ref == r["predicted"]:
                score_strs.append(f"[{score:.4f}]")
            else:
                score_strs.append(f" {score:.4f} ")
        scores_line = "".join(f"{s:<10}" for s in score_strs)
        print(f"  {r['problem']:<8} {r['student']:<15} {scores_line}{r['predicted']:<8} {r['expected']:<8} {status}")
    
    print("  " + "-"*80)
    
    # Mismatches detail (if any)
    errors = [r for r in results if not r["match"]]
    if errors:
        print(f"\n❌ {len(errors)} Mismatch(es):")
        for e in errors:
            print(f"  {e['problem']}/{e['student']}: predicted {e['predicted']} but expected {e['expected']}")
            for ref, score in sorted(e['scores'].items()):
                mark = "→" if ref == e['predicted'] else " "
                print(f"    {mark} {ref}: {score:.4f}")
    
    
    # Final Statistics
    accuracy = correct / total
    print("\n" + "="*60)
    print(" "*20 + "FINAL RESULTS")
    print("="*60)
    print(f"  Weights: Baseline={weights['baseline']:.0%}, WL={weights['wl']:.0%}, CES={weights['ces']:.0%}")
    print(f"  Correct Predictions: {correct}/{total}")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True, help="Path to final similarity matrix json")
    parser.add_argument("--gt", default=None, help="Path to ground truth json (auto-detected if not provided)")
    args = parser.parse_args()
    
    # Weights are applied during aggregation, not here
    # This parameter is kept for compatibility but not used
    WEIGHTS = {"baseline": 0.35, "wl": 0.40, "ces": 0.25}
    
    calculate_accuracy(args.matrix, args.gt, WEIGHTS)

