#!/usr/bin/env python3
"""
Vectorize WL features using global vocabulary
Converts WL feature histograms to fixed-dimension vectors
"""
import json
from pathlib import Path

OUT_DIR = Path("outputs/java")
VOCAB_FILE = Path("vocabulary/java/wl_vocab.json")
VEC_DIR = Path("vectors/java/wl")

print("[WL Vectorize] Loading vocabulary...")

# Load vocabulary
with open(VOCAB_FILE) as f:
    vocab = json.load(f)

print(f"[WL Vectorize] Vocabulary size: {len(vocab)} dimensions")

# Create output directory
VEC_DIR.mkdir(parents=True, exist_ok=True)

# Vectorize each program
vec_count = 0

for wl_file in OUT_DIR.rglob("wl.json"):
    try:
        with open(wl_file) as f:
            features = json.load(f)
        
        if not isinstance(features, dict):
            continue
        
        # Create vector (initialize with zeros)
        vec = [0] * len(vocab)
        
        # Fill vector with feature counts
        for key, value in features.items():
            if key in vocab:
                idx = vocab[key]
                vec[idx] = value if isinstance(value, (int, float)) else 1
        
        # Determine output path
        rel_path = wl_file.relative_to(OUT_DIR)
        parts = rel_path.parts  # (problem, role, prog, 'wl.json')
        
        if len(parts) < 3:
            continue
        
        vec_id = f"{parts[0]}_{parts[1]}_{parts[2]}"
        vec_file = VEC_DIR / f"{vec_id}.vec"
        
        # Save vector as JSON
        with open(vec_file, "w") as f:
            json.dump(vec, f)
        
        vec_count += 1
            
    except Exception as e:
        print(f"[WARN] Failed to vectorize {wl_file}: {e}")
        continue

print(f"[WL Vectorize] ✓ Vectorized {vec_count} programs")
print(f"[WL Vectorize] Saved to {VEC_DIR}")
