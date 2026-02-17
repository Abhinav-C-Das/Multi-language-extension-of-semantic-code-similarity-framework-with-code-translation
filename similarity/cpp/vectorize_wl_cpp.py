#!/usr/bin/env python3
"""
Vectorize WL features for C++ programs using global vocabulary
Converts WL feature histograms to fixed-dimension vectors
"""
import json
from pathlib import Path

OUT_DIR = Path("vectors/cpp/wl")
VOCAB_FILE = Path("vocabulary/cpp/wl_vocab.json")
WL_ROOT = Path("outputs/cpp")

OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Load vocabulary
# --------------------------------------------------
with open(VOCAB_FILE) as f:
    vocab = json.load(f)

dim = len(vocab)

# --------------------------------------------------
# Vectorize
# --------------------------------------------------
count = 0

for wl_file in WL_ROOT.rglob("wl_ast.json"):
    # wl_file = outputs/cpp/p1/ref/ref1/wl_ast.json
    parts = wl_file.parts

    problem = parts[2]   # p1 (index 2 because of outputs/cpp/)
    role = parts[3]      # ref | s
    prog = parts[4]      # ref1 | s1

    out_name = f"{problem}_{role}_{prog}.vec"
    out_path = OUT_DIR / out_name

    vec = [0.0] * dim

    with open(wl_file) as f:
        feats = json.load(f)

    for label, value in feats.items():
        if label in vocab:
            vec[vocab[label]] = float(value)

    with open(out_path, "w") as f:
        f.write(",".join(map(str, vec)) + "\n")

    print(f"[WL CPP] vectorized {out_name}")
    count += 1

print(f"[WL CPP] wrote {count} WL vectors")
