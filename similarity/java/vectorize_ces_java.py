#!/usr/bin/env python3
"""
Vectorize CES features using global vocabulary
Converts CES pattern records to fixed-dimension vectors with importance weights
"""
import json
from pathlib import Path

OUT_DIR = Path("outputs/java")
VOCAB_FILE = Path("vocabulary/java/ces_vocab.json")
VEC_DIR = Path("vectors/java/ces")

print("[CES Vectorize] Loading vocabulary...")

# Load vocabulary
with open(VOCAB_FILE) as f:
    vocab = json.load(f)

print(f"[CES Vectorize] Vocabulary size: {len(vocab)} dimensions")

# Create output directory
VEC_DIR.mkdir(parents=True, exist_ok=True)

# Vectorize each program
vec_count = 0

for ces_file in OUT_DIR.rglob("ces_v2.json"):
    try:
        with open(ces_file) as f:
            records = json.load(f)
        
        if not isinstance(records, list):
            continue
        
        # Create vector (initialize with zeros)
        vec = [0.0] * len(vocab)
        
        # Fill vector with importance-weighted pattern counts
        for record in records:
            if not isinstance(record, dict):
                continue
            
            context = record.get("context", "")
            evolution = record.get("evolution", "")
            operator = record.get("operator", "")
            importance = record.get("importance", 1.0)
            
            key = f"{context}::{evolution}::{operator}"
            
            if key in vocab:
                idx = vocab[key]
                vec[idx] += importance  # Accumulate importance weights
        
        # Determine output path
        rel_path = ces_file.relative_to(OUT_DIR)
        parts = rel_path.parts  # (problem, role, prog, 'ces_v2.json')
        
        if len(parts) < 3:
            continue
        
        vec_id = f"{parts[0]}_{parts[1]}_{parts[2]}"
        vec_file = VEC_DIR / f"{vec_id}.vec"
        
        # Save vector as JSON
        with open(vec_file, "w") as f:
            json.dump(vec, f)
        
        vec_count += 1
            
    except Exception as e:
        print(f"[WARN] Failed to vectorize {ces_file}: {e}")
        continue

print(f"[CES Vectorize] ✓ Vectorized {vec_count} programs")
print(f"[CES Vectorize] Saved to {VEC_DIR}")
