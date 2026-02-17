#!/usr/bin/env python3
"""
CES Similarity with Local Vocabulary and Importance Weights (Java Version)
Builds vocabulary per student-reference comparison with importance weighting
"""

import json
import math
from pathlib import Path

OUT_DIR = Path("outputs/java")
RESULT_FILE = Path("evaluation/java/ces_similarity_matrix_java.json")

def load_ces_features(path):
    """Load CES patterns from ces_v2.json with importance weights"""
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        with open(path) as f:
            records = json.load(f)
            if not records:
                return {}
            
            # Build pattern dict with importance weights
            patterns = {}
            for r in records:
                if not isinstance(r, dict):
                    continue
                key = f"{r.get('context', '')}::{r.get('evolution', '')}::{r.get('operator', '')}"
                importance = r.get('importance', 1.0)
                # Accumulate importance if same pattern appears multiple times
                patterns[key] = patterns.get(key, 0.0) + importance
            
            return patterns
    except:
        return {}

def build_local_vocab(pattern_dicts):
    """Build vocabulary from multiple pattern dicts"""
    vocab = {}
    idx = 0
    for patterns in pattern_dicts:
        for pattern in patterns.keys():
            if pattern not in vocab:
                vocab[pattern] = idx
                idx += 1
    return vocab

def vectorize(patterns_dict, vocab):
    """Convert pattern dict with importance to vector"""
    vec = [0.0] * len(vocab)
    for pattern, importance in patterns_dict.items():
        if pattern in vocab:
            vec[vocab[pattern]] = importance
    return vec

def l2_normalize(vec):
    """L2 normalization"""
    if not vec:
        return vec
    norm = math.sqrt(sum(x*x for x in vec))
    if norm == 0:
        return [0.0] * len(vec)
    return [x/norm for x in vec]

def cosine(v1, v2):
    """Cosine similarity"""
    if not v1 or not v2:
        return 0.0
    return sum(a*b for a,b in zip(v1, v2))

# Group files
print("[CES Java] Scanning for CES features...")
problems = {}
for ces_file in OUT_DIR.rglob("ces_v2.json"):
    parts = ces_file.relative_to(OUT_DIR).parts
    if len(parts) < 3:
        continue
    problem, role, prog = parts[0], parts[1], parts[2]
    problems.setdefault(problem, {"s": {}, "ref": {}})
    problems[problem][role][prog] = ces_file

print(f"[CES Java] Found {len(problems)} problems")

# Compute with local vocabulary and importance weights
results = {}
for problem, files in sorted(problems.items()):
    print(f"[CES Java] Processing {problem}...")
    problem_results = {}
    
    # Load all reference patterns
    ref_patterns = {}
    for ref_name, ref_path in files.get("ref", {}).items():
        ref_patterns[ref_name] = load_ces_features(ref_path)
    
    # For each student
    for student_name, student_path in sorted(files.get("s", {}).items()):
        student_pats = load_ces_features(student_path)
        
        # Build local vocabulary for this student vs all refs
        all_dicts = [student_pats] + list(ref_patterns.values())
        vocab = build_local_vocab(all_dicts)
        
        # Handle empty vocab case
        if not vocab:
            scores = {ref_name: 0.0 for ref_name in ref_patterns.keys()}
            problem_results[student_name] = scores
            continue
        
        # Vectorize with importance weights and normalize
        s_vec = vectorize(student_pats, vocab)
        s_vec = l2_normalize(s_vec)
        
        # Compare with each ref
        scores = {}
        for ref_name, ref_pats in sorted(ref_patterns.items()):
            r_vec = vectorize(ref_pats, vocab)
            r_vec = l2_normalize(r_vec)
            scores[ref_name] = cosine(s_vec, r_vec)
        
        problem_results[student_name] = scores
    
    results[problem] = problem_results

# Save
RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(RESULT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"[CES Java] ✓ Saved to {RESULT_FILE}")
print(f"[CES Java] Total comparisons: {sum(len(p) for p in results.values())}")
