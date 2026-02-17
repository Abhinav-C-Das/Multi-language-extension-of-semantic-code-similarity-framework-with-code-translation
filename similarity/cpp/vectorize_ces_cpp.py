#!/usr/bin/env python3
"""
Vectorize CES features for C++ programs using global vocabulary
Converts CES pattern records to fixed-dimension vectors
"""
import json
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------
VEC_DIR = Path("vectors/cpp/ces")
VEC_DIR.mkdir(parents=True, exist_ok=True)

VOCAB = json.load(open("vocabulary/cpp/ces_vocab.json"))
RAW_DIR = Path("outputs/cpp")

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def load_ces(path: Path):
    """Load CES JSON with [INFO] log filtering"""
    text = path.read_text(errors="ignore").strip()
    # Filter out [INFO] lines
    lines = [l for l in text.splitlines() if not l.startswith('[INFO')]
    text = '\n'.join(lines).strip()
    
    if not text:
        return []
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return []

# --------------------------------------------------
# Vectorization
# --------------------------------------------------
for ces_file in RAW_DIR.rglob("semantic.json"):
    rel = ces_file.relative_to(RAW_DIR)
    parts = rel.parts
    # Structure: outputs/cpp/p1/s/s1/semantic.json
    # parts = ('p1', 's', 's1', 'semantic.json')

    if len(parts) < 4:
        continue

    problem = parts[0]  # p1
    role = parts[1]     # s or ref
    prog = parts[2]     # s1 or ref1
    out_path = VEC_DIR / f"{problem}_{role}_{prog}.vec"

    vec = [0] * len(VOCAB)

    records = load_ces(ces_file)
    for r in records:
        key = f"{r['context']}::{r['evolution']}::{r['operator']}"
        if key in VOCAB:
            vec[VOCAB[key]] += 1

    with open(out_path, "w") as f:
        f.write(",".join(map(str, vec)) + "\n")

print("[CES CPP] vectorization complete")
