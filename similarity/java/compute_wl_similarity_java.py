#!/usr/bin/env python3
"""
Compute WL similarity matrix using pre-built normalized vectors
Uses cosine similarity (vectors already normalized, so just dot product)
"""
import json
from pathlib import Path

VEC_DIR = Path("vectors/java/wl_norm")
OUT_FILE = Path("evaluation/java/wl_similarity_matrix_java.json")

print("[WL Similarity] Loading normalized vectors...")

def cosine(v1, v2):
    """Cosine similarity - assumes vectors are already L2 normalized"""
    return sum(a*b for a,b in zip(v1, v2))

# Load all vectors
vectors = {}
for vec_file in VEC_DIR.glob("*.norm.vec"):
    vec_id = vec_file.stem.replace(".norm", "")
    try:
        with open(vec_file) as f:
            vectors[vec_id] = json.load(f)
    except:
        continue

print(f"[WL Similarity] Loaded {len(vectors)} vectors")

# Group by problem
problems = {}
for vec_id in vectors.keys():
    parts = vec_id.split("_")
    if len(parts) < 3:
        continue
    problem, role, prog = parts[0], parts[1], parts[2]
    problems.setdefault(problem, {"s": {}, "ref": {}})
    problems[problem][role][prog] = vec_id

print(f"[WL Similarity] Found {len(problems)} problems")

# Compute similarities
results = {}
for problem, roles in sorted(problems.items()):
    results[problem] = {}
    
    for student, student_id in sorted(roles.get("s", {}).items()):
        results[problem][student] = {}
        
        for ref, ref_id in sorted(roles.get("ref", {}).items()):
            sim = cosine(vectors[student_id], vectors[ref_id])
            results[problem][student][ref] = sim

# Save
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"[WL Similarity] ✓ Saved similarity matrix to {OUT_FILE}")
print(f"[WL Similarity] Total comparisons: {sum(len(students) for students in results.values())}")
