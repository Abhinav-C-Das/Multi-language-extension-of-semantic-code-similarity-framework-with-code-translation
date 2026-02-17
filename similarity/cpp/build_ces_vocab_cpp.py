#!/usr/bin/env python3
"""
Build CES vocabulary for C++ programs
Creates a global vocabulary of all CES pattern keys
"""
import json
from pathlib import Path
from collections import Counter

OUT_DIR = Path("vocabulary/cpp")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VOCAB_PATH = OUT_DIR / "ces_vocab.json"

vocab = Counter()

for ces_file in Path("outputs/cpp").rglob("semantic.json"):
    # Skip empty files (valid - means no CES features)
    if ces_file.stat().st_size == 0:
        continue
    
    # Read and filter [INFO] logs
    text = ces_file.read_text(errors="ignore").strip()
    lines = [l for l in text.splitlines() if not l.startswith('[INFO')]
    text = '\n'.join(lines).strip()
    
    if not text:
        continue
    
    try:
        records = json.loads(text)
    except json.JSONDecodeError:
        print(f"[WARN] Invalid JSON in {ces_file}, skipping")
        continue
        
    if not records:  # Skip empty lists []
        continue
    for r in records:
        key = f"{r['context']}::{r['evolution']}::{r['operator']}"
        vocab[key] += 1

# Stable index
vocab_index = {k: i for i, k in enumerate(sorted(vocab))}

with open(VOCAB_PATH, "w") as f:
    json.dump(vocab_index, f, indent=2)

print(f"[CES CPP] vocab size = {len(vocab_index)}")
print(f"[CES CPP] Vocabulary saved to {VOCAB_PATH}")
