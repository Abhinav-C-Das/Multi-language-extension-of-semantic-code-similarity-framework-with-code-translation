#!/usr/bin/env python3
"""
CES V3 Similarity for C++ Programs - TVERSKY ENHANCED

IMPROVEMENTS:
1. Primary Metric: Tversky Similarity (better for subset matching)
2. Asymmetric Matching: Penalizes missing reference patterns (beta) more than extra student patterns (alpha)
3. Pattern Importance Weighting Integrated into Tversky

Outputs to: evaluation/cpp/ces_similarity_matrix_cpp.json
"""

import json
import math
from pathlib import Path

OUT_DIR = Path("outputs/cpp")
RESULT_FILE = Path("evaluation/cpp/ces_similarity_matrix_cpp.json")

# Configuration
# Tversky index: S(A, B) = |A n B| / (|A n B| + alpha*|A - B| + beta*|B - A|)
# where A = Student, B = Reference
# beta > alpha -> we care more about finding all reference patterns than avoiding extra student patterns
TVERSKY_ALPHA = 0.1  # Low penalty for extra student patterns (FP)
TVERSKY_BETA = 0.9   # High penalty for missing reference patterns (FN)
USE_WEIGHTS = True   # Weighted Tversky

def load_ces_features(path):
    """Load CES v3 patterns from semantic.json with [INFO] log filtering"""
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with open(path) as f:
            # Filter out [INFO] logs before parsing
            text = f.read()
            lines = [line for line in text.splitlines() if not line.strip().startswith('[INFO')]
            text = '\n'.join(lines)
            
            # Parse JSON
            records = json.loads(text) if text.strip() else []
            return records if records else []
    except Exception as e:
        print(f"[WARNING] Could not load {path}: {e}")
        return []

def extract_patterns_with_weights(records):
    """
    Convert CES v3 records to pattern keys with importance weights
    Sum importance weights for duplicate patterns
    """
    patterns = []
    weights = {}
    
    for r in records:
        key = f"{r['context']}::{r['evolution']}::{r['operator']}"
        patterns.append(key)
        
        # Extract importance weight (default 1.0 if not present)
        importance = float(r.get('importance', 1.0))
        
        # Sum weights for duplicate patterns (don't overwrite!)
        if key in weights:
            weights[key] += importance
        else:
            weights[key] = importance
    
    return patterns, weights

def weighted_tversky(patterns1, weights1, patterns2, weights2, alpha=TVERSKY_ALPHA, beta=TVERSKY_BETA):
    """
    Weighted Tversky Similarity
    A = patterns1 (Student)
    B = patterns2 (Reference)
    
    Intersection = Sum of min(wA, wB) for shared patterns
    Difference (A-B) = Sum of wA for patterns only in A (or surplus weight)
    Difference (B-A) = Sum of wB for patterns only in B (or surplus weight)
    """
    set1 = set(patterns1)
    set2 = set(patterns2)
    
    if not set1 and not set2:
        return 0.0
    
    all_patterns = set1 | set2
    
    intersection = 0.0
    diff_a_b = 0.0 # Weight specific to A (Student only)
    diff_b_a = 0.0 # Weight specific to B (Ref only)
    
    for p in all_patterns:
        w1 = weights1.get(p, 0.0)
        w2 = weights2.get(p, 0.0)
        
        # Intersection: shared weight
        shared = min(w1, w2)
        intersection += shared
        
        # A - B: extra weight in A not in B
        if w1 > w2:
            diff_a_b += (w1 - w2)
            
        # B - A: extra weight in B not in A
        if w2 > w1:
            diff_b_a += (w2 - w1)
            
    denominator = intersection + (alpha * diff_a_b) + (beta * diff_b_a)
    
    return intersection / denominator if denominator > 0 else 0.0

# Group files
print("[CES CPP] Scanning for semantic.json files...")
problems = {}
for ces_file in OUT_DIR.rglob("semantic.json"):
    parts = ces_file.relative_to(OUT_DIR).parts
    if len(parts) < 4:
        continue
    problem, role, prog = parts[0], parts[1], parts[2]
    problems.setdefault(problem, {"s": {}, "ref": {}})
    problems[problem][role][prog] = ces_file

print(f"[CES CPP] Found {len(problems)} problems")
print(f"[CES CPP] Metric: Weighted Tversky (alpha={TVERSKY_ALPHA}, beta={TVERSKY_BETA})")

# Compute
results = {}
for problem, files in sorted(problems.items()):
    print(f"[CES CPP] Processing {problem}...")
    problem_results = {}
    
    # Load all reference patterns with weights
    ref_data = {}
    for ref_name, ref_path in files["ref"].items():
        records = load_ces_features(ref_path)
        patterns, weights = extract_patterns_with_weights(records)
        ref_data[ref_name] = (patterns, weights)
    
    # For each student
    for student_name, student_path in sorted(files["s"].items()):
        records = load_ces_features(student_path)
        student_pats, student_weights = extract_patterns_with_weights(records)
        
        # Compare with refs
        scores = {}
        for ref_name, (ref_pats, ref_weights) in sorted(ref_data.items()):
            score = weighted_tversky(student_pats, student_weights, ref_pats, ref_weights)
            scores[ref_name] = score
        
        problem_results[student_name] = scores
    
    results[problem] = problem_results

# Save
RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(RESULT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n[CES CPP] ✅ Similarity matrix saved to {RESULT_FILE}")
