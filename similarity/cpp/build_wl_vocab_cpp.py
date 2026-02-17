#!/usr/bin/env python3
"""
Build WL vocabulary for C++ programs
Creates a global vocabulary of all WL feature keys
"""
import json
from pathlib import Path

OUT_DIR = Path("outputs/cpp")
VOCAB_OUT = Path("vocabulary/cpp/wl_vocab.json")

VOCAB_OUT.parent.mkdir(parents=True, exist_ok=True)

vocab = {}
next_id = 0

# --------------------------------------------------
# Scan all wl_ast.json files under outputs/cpp/
# --------------------------------------------------
for wl_file in OUT_DIR.rglob("wl_ast.json"):
    with open(wl_file) as f:
        data = json.load(f)

    for label in data.keys():
        if label not in vocab:
            vocab[label] = next_id
            next_id += 1

print(f"[WL CPP] vocab size = {len(vocab)}")

with open(VOCAB_OUT, "w") as f:
    json.dump(vocab, f, indent=2)

print(f"[WL CPP] Vocabulary saved to {VOCAB_OUT}")
