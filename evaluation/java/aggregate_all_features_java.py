#!/usr/bin/env python3
"""
Aggregate All Features for Java Programs

Combines Baseline + WL + CES similarity matrices
with configurable weights to produce final similarity matrix.

Usage:
    python3 aggregate_all_features_java.py [baseline_weight] [wl_weight] [ces_weight]

Example:
    python3 aggregate_all_features_java.py 0.35 0.40 0.25
    # Standard weights: Baseline=35%, WL=40%, CES=25%
"""

import sys
import json
from pathlib import Path

# Default weights (standard configuration)
DEFAULT_WEIGHTS = {
    'baseline': 0.35,
    'wl': 0.40,
    'ces': 0.25
}

# Input similarity matrices
BASELINE_FILE = Path("evaluation/java/similarity_matrix_java.json")
WL_FILE = Path("evaluation/java/wl_similarity_matrix_java.json")
CES_FILE = Path("evaluation/java/ces_similarity_matrix_java.json")

# Output
OUTPUT_FILE = Path("evaluation/java/final_similarity_matrix_java.json")

def load_matrix(path):
    """Load similarity matrix from JSON file"""
    if not path.exists():
        print(f"[WARN] File not found: {path}")
        return None
    
    with open(path) as f:
        return json.load(f)

def aggregate_matrices(baseline, wl, ces, weights):
    """
    Aggregate similarity matrices with weighted combination
    
    Returns: final_matrix with same structure as inputs
    """
    result = {}
    
    # Get all problems
    all_problems = set()
    for matrix in [baseline, wl, ces]:
        if matrix:
            all_problems.update(matrix.keys())
    
    for problem in sorted(all_problems):
        result[problem] = {}
        
        # Get students for this problem (from any available matrix)
        students = set()
        for matrix in [baseline, wl, ces]:
            if matrix and problem in matrix:
                students.update(matrix[problem].keys())
        
        for student in sorted(students):
            result[problem][student] = {}
            
            # Get references (from any available matrix)
            refs = set()
            for matrix in [baseline, wl, ces]:
                if matrix and problem in matrix and student in matrix[problem]:
                    refs.update(matrix[problem][student].keys())
            
            for ref in sorted(refs):
                # Get scores from each view
                baseline_score = 0.0
                wl_score = 0.0
                ces_score = 0.0
                
                if baseline and problem in baseline and student in baseline[problem]:
                    baseline_score = baseline[problem][student].get(ref, 0.0)
                
                if wl and problem in wl and student in wl[problem]:
                    wl_score = wl[problem][student].get(ref, 0.0)
                
                if ces and problem in ces and student in ces[problem]:
                    ces_score = ces[problem][student].get(ref, 0.0)
                
                # Weighted combination
                final_score = (
                    weights['baseline'] * baseline_score +
                    weights['wl'] * wl_score +
                    weights['ces'] * ces_score
                )
                
                result[problem][student][ref] = final_score
    
    return result

# Parse command line weights
if len(sys.argv) == 4:
    try:
        weights = {
            'baseline': float(sys.argv[1]),
            'wl': float(sys.argv[2]),
            'ces': float(sys.argv[3])
        }
        
        # Validate weights sum to 1.0 (allow small tolerance)
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            print(f"[WARN] Weights sum to {total:.3f}, not 1.0. Normalizing...")
            for key in weights:
                weights[key] /= total
    except ValueError:
        print("[ERROR] Invalid weight values. Using defaults.")
        weights = DEFAULT_WEIGHTS
else:
    weights = DEFAULT_WEIGHTS

print("=" * 80)
print("AGGREGATE ALL FEATURES - JAVA PIPELINE")
print("=" * 80)
print(f"\nWeights:")
print(f"  Baseline: {weights['baseline']:.2f}")
print(f"  WL:       {weights['wl']:.2f}")
print(f"  CES:      {weights['ces']:.2f}")
print(f"  Total:    {sum(weights.values()):.2f}\n")

# Load matrices
print("[Step 1/3] Loading similarity matrices...")
baseline_matrix = load_matrix(BASELINE_FILE)
wl_matrix = load_matrix(WL_FILE)
ces_matrix = load_matrix(CES_FILE)

# Check required matrices
missing = []
if not baseline_matrix:
    missing.append("baseline")
if not wl_matrix:
    missing.append("WL")
if not ces_matrix:
    missing.append("CES")

if missing:
    print(f"[ERROR] Missing required matrices: {', '.join(missing)}")
    print("\nPlease run:")
    if not baseline_matrix:
        print("  - python3 similarity/java/compute_baseline_similarity_java.py")
    if not wl_matrix:
        print("  - python3 similarity/java/compute_wl_similarity_java.py")
    if not ces_matrix:
        print("  - python3 similarity/java/compute_ces_similarity_java.py")
    sys.exit(1)

# Aggregate
print("[Step 2/3] Aggregating matrices...")
final_matrix = aggregate_matrices(baseline_matrix, wl_matrix, ces_matrix, weights)

# Save
print(f"[Step 3/3] Saving to {OUTPUT_FILE}...")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(final_matrix, f, indent=2)

# Stats
total_comparisons = sum(
    len(students) * len(list(students.values())[0]) if students else 0
    for students in final_matrix.values()
)

print("\n" + "=" * 80)
print("✅ AGGREGATION COMPLETE")
print("=" * 80)
print(f"\nOutput: {OUTPUT_FILE}")
print(f"Problems: {len(final_matrix)}")
print(f"Total comparisons: {total_comparisons}")
print(f"\nJava Pipeline uses standard weights (configurable via command-line)")
