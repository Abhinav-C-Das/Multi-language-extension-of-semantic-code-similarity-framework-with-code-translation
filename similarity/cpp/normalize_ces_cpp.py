#!/usr/bin/env python3
"""
L2 normalize CES vectors for C++ programs
"""
import sys
import math
from pathlib import Path

def load_vector(path: Path):
    text = path.read_text(errors="ignore").strip()
    if not text:
        return []

    vec = []
    for tok in text.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            vec.append(float(tok))
        except ValueError:
            vec.append(0.0)
    return vec

def l2_normalize(vec):
    if not vec:
        return []

    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return [0.0 for _ in vec]
    return [x / norm for x in vec]

def save_vector(vec, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(",".join(f"{x:.6f}" for x in vec) + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python normalize_ces_cpp.py <input.vec> <output.norm.vec>")
        sys.exit(1)

    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])

    vec = load_vector(inp)
    norm_vec = l2_normalize(vec)
    save_vector(norm_vec, out)
    
    print(f"[CES CPP] Normalized: {out}")
