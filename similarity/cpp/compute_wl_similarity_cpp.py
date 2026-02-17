#!/usr/bin/env python3
"""
WL Similarity with Local Vocabulary for C++ Programs

Builds vocabulary per student-reference comparison instead of global vocabulary.
This ensures all patterns from both student and references are captured.
"""

import json
import math
from pathlib import Path

OUT_DIR = Path("outputs/cpp")
RESULT_FILE = Path("evaluation/cpp/wl_similarity_matrix_cpp.json")

def load_wl_features(path):
    """Load WL AST labels from wl_ast.json"""
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)  # {label: count}
    except:
        return {}

def build_local_vocab(features_list):
    """Build vocabulary from a list of feature dicts"""
    vocab = {}
    idx = 0
    for features in features_list:
        for label in features.keys():
            if label not in vocab:
                vocab[label] = idx
                idx += 1
    return vocab

def vectorize(features, vocab):
    """Convert features to vector using vocab"""
    vec = [0] * len(vocab)
    for label, count in features.items():
        if label in vocab:
            vec[vocab[label]] = count
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

# Group files by problem
print("[WL CPP] Scanning output directory...")
problems = {}
for wl_file in OUT_DIR.rglob("wl_ast.json"):
    parts = wl_file.relative_to(OUT_DIR).parts
    
    if len(parts) < 4:
        print(f"Skipping {wl_file}: {parts} length < 4")
        continue
    
    problem = parts[0]
    role = parts[1]
    prog = parts[2]
    
    if role not in ["s", "ref"]:
        print(f"Skipping {wl_file}: Role '{role}' not 's' or 'ref'")
        continue
        
    problems.setdefault(problem, {"s": {}, "ref": {}})
    problems[problem][role][prog] = wl_file

print(f"[WL CPP] Found {len(problems)} problems")

# Compute similarities per problem
results = {}

for problem, files in sorted(problems.items()):
    print(f"[WL CPP] Processing {problem}...")
    problem_results = {}
    
    # Load all reference features once
    ref_features = {}
    for ref_name, ref_path in files["ref"].items():
        ref_features[ref_name] = load_wl_features(ref_path)
    
    # For each student
    for student_name, student_path in sorted(files["s"].items()):
        student_feat = load_wl_features(student_path)
        
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
RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(RESULT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"[WL CPP] Similarity matrix saved to {RESULT_FILE}")
print(f"[WL CPP] Total comparisons: {sum(len(p) for p in results.values())}")
