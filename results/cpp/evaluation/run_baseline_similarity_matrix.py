#!/usr/bin/env python3
import json
import math
from pathlib import Path

# Config
VECTORS_DIR = Path("vectors/baseline")
OUTPUT_FILE = Path("evaluation/matrices/similarity_matrix.json")

# Feature Ranges (Matches similarity.py)
STRUCTURAL = range(0, 7)
SEMANTIC   = range(7, 13)
BEHAVIORAL = range(13, 16)

def load_vector(path):
    with open(path) as f:
        return [float(x) for x in f.read().strip().split(",")]

def cosine(v1, v2, idxs):
    a = [v1[i] for i in idxs]
    b = [v2[i] for i in idxs]
    dot = sum(x*y for x, y in zip(a, b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0: return 0.0
    return dot / (na * nb)

def compute_similarity(v1, v2):
    s = cosine(v1, v2, STRUCTURAL)
    sem = cosine(v1, v2, SEMANTIC)
    beh = cosine(v1, v2, BEHAVIORAL)
    return (s + sem + beh) / 3.0

def main():
    print(f"[Matrix] Scanning {VECTORS_DIR}...")
    
    # Load all vectors: {problem: {role: {id: vector}}}
    data = {}
    
    if not VECTORS_DIR.exists():
        print(f"[ERROR] {VECTORS_DIR} not found!")
        return

    for f in VECTORS_DIR.glob("*.norm.vec"):
        # Filename format: PROBLEM_ROLE_ID.norm.vec
        # Example: p1_vector_sum_ref_ref1.norm.vec
        # Warning: "p1_vector_sum" contains underscores. 
        # Strategy: Valid IDs are sX or refX.
        # So split from right.
        
        parts = f.name.replace(".norm.vec", "").split("_")
        if len(parts) < 3:
            continue
            
        prog_id = parts[-1]   # ref1, s1
        role = parts[-2]      # ref, s
        problem = "_".join(parts[:-2]) # p1_vector_sum
        
        if problem not in data: data[problem] = {'s': {}, 'ref': {}}
        if role not in data[problem]: data[problem][role] = {} # Should be covered but safe
        
        data[problem][role][prog_id] = load_vector(f)

    # Compute Matrix
    matrix = {}
    
    for prob, roles in data.items():
        matrix[prob] = {}
        students = roles.get('s', {})
        references = roles.get('ref', {})
        
        for s_id, s_vec in students.items():
            matrix[prob][s_id] = {}
            for r_id, r_vec in references.items():
                sim = compute_similarity(s_vec, r_vec)
                matrix[prob][s_id][r_id] = sim

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(matrix, f, indent=2)
    
    print(f"[Matrix] Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
