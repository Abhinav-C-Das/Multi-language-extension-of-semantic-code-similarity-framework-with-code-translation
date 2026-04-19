
import json
import sys
from pathlib import Path

# Paths
MATRICES_DIR = Path("evaluation/matrices")
GROUND_TRUTH_FILE = Path("data/cpp_test/ground_truth.json")

# Matrix Files
FILES = {
    "baseline": MATRICES_DIR / "similarity_matrix.json",
    "wl": MATRICES_DIR / "wl_similarity_matrix_local.json",
    "ces_v3": MATRICES_DIR / "ces_v3_similarity_matrix_local.json",
    "scdps": MATRICES_DIR / "scdps_similarity_matrix_local.json"
}

# Configs to test
CONFIGS = {
    "Baseline Only": {"baseline": 1.0, "wl": 0.0, "ces_v3": 0.0, "scdps": 0.0},
    "WL Only":       {"baseline": 0.0, "wl": 1.0, "ces_v3": 0.0, "scdps": 0.0},
    "CES v3 Only":   {"baseline": 0.0, "wl": 0.0, "ces_v3": 1.0, "scdps": 0.0},
    "SCDPS Only":    {"baseline": 0.0, "wl": 0.0, "ces_v3": 0.0, "scdps": 1.0},
    "Standard (No SCDPS)": {"baseline": 0.35, "wl": 0.40, "ces_v3": 0.25, "scdps": 0.0},
    "With SCDPS":          {"baseline": 0.25, "wl": 0.35, "ces_v3": 0.20, "scdps": 0.20}
}

def load_json(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)

def get_rank_1(scores):
    """Return list of references with the highest score"""
    if not scores:
        return []
    max_score = max(scores.values())
    return [ref for ref, score in scores.items() if score == max_score]

def evaluate(name, weights, matrices, ground_truth):
    correct = 0
    total = 0
    errors = []

    # Iterate over ground truth
    for prob, students in ground_truth.items():
        for student, expected_refs in students.items():
            total += 1
            
            # Aggregate scores
            final_scores = {}
            # Get union of refs
            all_refs = set()
            for key, mat in matrices.items():
                if mat and prob in mat and student in mat[prob]:
                    all_refs.update(mat[prob][student].keys())
            
            for ref in all_refs:
                score = 0.0
                for key, w in weights.items():
                    if w > 0:
                        mat = matrices[key]
                        if mat and prob in mat and student in mat[prob]:
                            score += w * mat[prob][student].get(ref, 0.0)
                final_scores[ref] = score
            
            # Check Rank 1
            top_refs = get_rank_1(final_scores)
            
            # Success if ANY of the top refs is in expected_refs
            is_correct = any(tr in expected_refs for tr in top_refs)
            
            if is_correct:
                correct += 1
            else:
                errors.append({
                    "problem": prob,
                    "student": student,
                    "expected": expected_refs,
                    "predicted": top_refs,
                    "scores": {k: v for k, v in final_scores.items() if v > 0}
                })
    
    accuracy = correct / total if total > 0 else 0.0
    return accuracy, errors

def main():
    print("Loading data...")
    ground_truth = load_json(GROUND_TRUTH_FILE)
    matrices = {k: load_json(v) for k, v in FILES.items()}
    
    with open("evaluation/ablation_results.txt", "w") as f:
        f.write("Ablation Results\n================\n\n")
        f.write(f"{'CONFIGURATION':<25} | {'ACCURACY':<10} | {'ERRORS':<10}\n")
        f.write(f"{'-'*60}\n")
        
        results = {}
        for name, weights in CONFIGS.items():
            acc, errs = evaluate(name, weights, matrices, ground_truth)
            results[name] = (acc, errs)
            f.write(f"{name:<25} | {acc:.2%}    | {len(errs)}\n")

        f.write(f"{'='*60}\n\n")
        
        f.write("ERROR ANALYSIS:\n")
        for name, (acc, errs) in results.items():
            if errs:
                f.write(f"\n--- {name} ({len(errs)} errors) ---\n")
                for e in errs:
                    f.write(f"  {e['problem']}/{e['student']}: Exp {e['expected']}, Got {e['predicted']}\n")

    print("Results saved to evaluation/ablation_results.txt")

if __name__ == "__main__":
    main()
