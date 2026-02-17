#!/usr/bin/env python3
"""
Java Similarity Computation (Unified for Baseline, WL, SCDPS)

Computes cosine similarity for different feature views using local vocabularies.
Based on the C version's compute_wl_similarity_local.py pattern.
"""

import json
import math
import sys
from pathlib import Path

# Configuration
OUT_DIR = Path("outputs/java")
EVAL_DIR = Path("evaluation/java")
EVAL_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path):
    """Load JSON file safely"""
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

def build_local_vocab(features_list):
    """Build vocabulary from list of feature dicts"""
    vocab = {}
    idx = 0
    for features in features_list:
        if isinstance(features, dict):
            for key in features.keys():
                if key not in vocab:
                    vocab[key] = idx
                    idx += 1
    return vocab

def vectorize(features, vocab):
    """Convert features to vector using vocab"""
    vec = [0] * len(vocab)
    for key, value in features.items():
        if key in vocab:
            vec[vocab[key]] = value if isinstance(value, (int, float)) else 1
    return vec

def l2_normalize(vec):
    """L2 normalization"""
    norm = math.sqrt(sum(x*x for x in vec))
    if norm == 0:
        return vec
    return [x/norm for x in vec]

def cosine(v1, v2):
    """Cosine similarity (assumes normalized vectors)"""
    if not v1 or not v2:
        return 0.0
    return sum(a*b for a,b in zip(v1, v2))

def flatten_baseline(baseline):
    """Flatten baseline dict to single-level feature dict"""
    if not isinstance(baseline, dict):
        return {}
    
    flat = {}
    for key, value in baseline.items():
        if isinstance(value, dict):
            # Nested dict - flatten with prefix
            for subkey, subval in value.items():
                flat[f"{key}.{subkey}"] = subval
        else:
            flat[key] = value
    return flat

def compute_similarity(view_name, file_pattern, output_file):
    """
    Compute similarity for a specific view
    
    Args:
        view_name: Name of the view (baseline, wl, scdps)
        file_pattern: File name to look for (e.g., 'baseline.json', 'wl.json')
        output_file: Output similarity matrix file
    """
    print(f"\n[{view_name.upper()}] Computing similarity...")
    print(f"[{view_name.upper()}] Looking for {file_pattern} files...")
    
    # Scan for files
    problems = {}
    for feature_file in OUT_DIR.rglob(file_pattern):
        parts = feature_file.relative_to(OUT_DIR).parts
        if len(parts) < 3:
            continue
        
        problem = parts[0]  # p1
        role = parts[1]     # s or ref
        prog = parts[2]     # s1 or ref1
        
        problems.setdefault(problem, {"s": {}, "ref": {}})
        problems[problem][role][prog] = feature_file
    
    print(f"[{view_name.upper()}] Found {len(problems)} problems")
    
    if not problems:
        print(f"[{view_name.upper()}] WARNING: No problems found!")
        return
    
    # Compute similarities per problem
    results = {}
    
    for problem, files in sorted(problems.items()):
        print(f"[{view_name.upper()}] Processing {problem}...")
        problem_results = {}
        
        # Load all reference features
        ref_features = {}
        for ref_name, ref_path in files["ref"].items():
            feat = load_json(ref_path)
            if view_name == "baseline":
                feat = flatten_baseline(feat)
            ref_features[ref_name] = feat
        
        # For each student
        for student_name, student_path in sorted(files["s"].items()):
            student_feat = load_json(student_path)
            if view_name == "baseline":
                student_feat = flatten_baseline(student_feat)
            
            # Build LOCAL vocab from student + all refs
            all_features = [student_feat] + list(ref_features.values())
            vocab = build_local_vocab(all_features)
            
            # Vectorize student
            s_vec = vectorize(student_feat, vocab)
            s_vec = l2_normalize(s_vec)
            
            # Compare with each ref
            scores = {}
            for ref_name, ref_feat in sorted(ref_features.items()):
                r_vec = vectorize(ref_feat, vocab)
                r_vec = l2_normalize(r_vec)
                scores[ref_name] = cosine(s_vec, r_vec)
            
            problem_results[student_name] = scores
        
        results[problem] = problem_results
    
    # Save
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"[{view_name.upper()}] ✅ Saved to {output_file}")
    print(f"[{view_name.upper()}] Total comparisons: {sum(len(p) for p in results.values())}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compute_similarity_java.py <view>")
        print("  view: baseline | wl | scdps")
        sys.exit(1)
    
    view = sys.argv[1].lower()
    
    if view == "baseline":
        compute_similarity("baseline", "baseline.json", EVAL_DIR / "similarity_matrix_java.json")
    elif view == "wl":
        compute_similarity("wl", "wl.json", EVAL_DIR / "wl_similarity_matrix_java.json")
    elif view == "scdps":
        compute_similarity("scdps", "scdps.json", EVAL_DIR / "scdps_similarity_matrix_java.json")
    else:
        print(f"ERROR: Unknown view '{view}'")
        print("  Valid views: baseline, wl, scdps")
        sys.exit(1)

if __name__ == "__main__":
    main()
