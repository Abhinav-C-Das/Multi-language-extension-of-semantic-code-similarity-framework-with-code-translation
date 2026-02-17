#!/usr/bin/env python3
"""
Compute baseline similarity matrix using pre-aggregated baseline features
Inline vectorization approach (no separate vectorize step needed)
"""
import json
import math
from pathlib import Path

OUT_DIR = Path("outputs/cpp")
OUT_FILE = Path("evaluation/cpp/similarity_matrix_cpp.json")

print("[Baseline CPP] Loading baseline features...")

def flatten_features(baseline):
    """Flatten nested baseline dict to single-level feature dict"""
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

def build_vocab(feature_dicts):
    """Build vocabulary from list of feature dicts"""
    vocab = {}
    idx = 0
    for features in feature_dicts:
        for key in features.keys():
            if key not in vocab:
                vocab[key] = idx
                idx += 1
    return vocab

def vectorize(features, vocab):
    """Convert features to vector using vocab"""
    vec = [0.0] * len(vocab)
    for key, value in features.items():
        if key in vocab:
            vec[vocab[key]] = float(value) if isinstance(value, (int, float)) else 0.0
    return vec

def l2_normalize(vec):
    """L2 normalization"""
    norm = math.sqrt(sum(x*x for x in vec))
    if norm == 0:
        return vec
    return [x/norm for x in vec]

def cosine(v1, v2):
    """Cosine similarity"""
    return sum(a*b for a,b in zip(v1, v2))

# Scan for baseline features (look for combined_features.json)
problems = {}
for baseline_file in OUT_DIR.rglob("combined_features.json"):
    parts = baseline_file.relative_to(OUT_DIR).parts
    if len(parts) < 3:
        continue
    
    problem, role, prog = parts[0], parts[1], parts[2]
    
    try:
        with open(baseline_file) as f:
            features = json.load(f)
        problems.setdefault(problem, {"s": {}, "ref": {}})
        problems[problem][role][prog] = flatten_features(features)
    except:
        continue

print(f"[Baseline CPP] Found {len(problems)} problems")

# Compute similarities per problem
results = {}

for problem, roles in sorted(problems.items()):
    results[problem] = {}
    
    for student, student_feat in sorted(roles.get("s", {}).items()):
        results[problem][student] = {}
        
        for ref, ref_feat in sorted(roles.get("ref", {}).items()):
            # Build local vocab for this comparison
            all_features = [student_feat, ref_feat]
            vocab = build_vocab(all_features)
            
            # Vectorize and normalize
            s_vec = vectorize(student_feat, vocab)
            s_vec = l2_normalize(s_vec)
            
            r_vec = vectorize(ref_feat, vocab)
            r_vec = l2_normalize(r_vec)
            
            # Compute similarity
            sim = cosine(s_vec, r_vec)
            results[problem][student][ref] = sim

# Save
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"[Baseline CPP] ✓ Saved similarity matrix to {OUT_FILE}")
print(f"[Baseline CPP] Total comparisons: {sum(len(students) for students in results.values())}")
