import json
import argparse
from pathlib import Path

def calculate_accuracy(matrix_file, ground_truth_file, weights):
    # Load similarity matrix
    with open(matrix_file) as f:
        matrix = json.load(f)
    
    # Auto-detect language from matrix path if ground truth not specified
    if ground_truth_file is None:
        # Check if matrix path contains language indicator
        matrix_path = Path(matrix_file)
        if 'java' in str(matrix_path).lower():
            ground_truth_file = "data/java/ground_truth.json"
        elif 'cpp' in str(matrix_path).lower() or '/cpp/' in str(matrix_path) or '\\cpp\\' in str(matrix_path):
            ground_truth_file = "data/cpp/ground_truth.json"
        else:
            # Default to C++ (since most recent datasets use cpp)
            ground_truth_file = "data/cpp/ground_truth.json"
    
    # Load ground truth
    gt_path = Path(ground_truth_file)
    ground_truth = {}
    if gt_path.exists():
        with open(gt_path) as f:
            raw_gt = json.load(f)
        
        # Convert array format to dict format if needed
        # Array format: {"p1": [["s1", "ref1"], ["s2", "ref2"]]}
        # Dict format:  {"p1": {"s1": "ref1", "s2": "ref2"}}
        for problem, value in raw_gt.items():
            if isinstance(value, list):
                # Array format - convert to dict
                ground_truth[problem] = {student: ref for student, ref in value}
            else:
                # Already dict format
                ground_truth[problem] = value
    else:
        print(f"[ERROR] Ground truth not found at {gt_path}")
        return
    
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
    
    # Predictions Table
    print("\n🎯 Predictions:")
    print("  " + "-"*56)
    print(f"  {'Student':<15} {'Predicted':<15} {'Expected':<15} {'Status':<8}")
    print("  " + "-"*56)
    
    for r in results:
        status = "✓" if r["match"] else "✗"
        color = "" if r["match"] else ""
        print(f"  {r['student']:<15} {r['predicted']:<15} {r['expected']:<15} {status:<8}")
    
    print("  " + "-"*56)
    
    # Detailed Scores (only for mismatches)
    errors = [r for r in results if not r["match"]]
    if errors:
        print("\n❌ Mismatches (Detailed Scores):")
        for e in errors:
            print(f"\n  {e['problem']}/{e['student']}:")
            print(f"    Expected: {e['expected']}, Predicted: {e['predicted']}")
            for ref, score in e['scores'].items():
                mark = "→" if ref == e['predicted'] else " "
                print(f"    {mark} {ref}: weighted={score:.4f}")
    
    
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

