#!/usr/bin/env python3
"""
Build CES vocabulary from all Java programs
Creates a global vocabulary of all CES pattern keys
"""
import json
from pathlib import Path

OUT_DIR = Path("outputs/java")
VOCAB_FILE = Path("vocabulary/java/ces_vocab.json")

print("[CES Vocab] Scanning for CES features...")

# Collect all CES pattern keys across all programs
all_keys = set()
file_count = 0

for ces_file in OUT_DIR.rglob("ces_v2.json"):
    try:
        with open(ces_file) as f:
            data = json.load(f)
            if isinstance(data, list):
                # Extract pattern keys from CES v2 records
                for record in data:
                    if isinstance(record, dict):
                        context = record.get("context", "")
                        evolution = record.get("evolution", "")
                        operator = record.get("operator", "")
                        key = f"{context}::{evolution}::{operator}"
                        all_keys.add(key)
                file_count += 1
    except Exception as e:
        print(f"[WARN] Failed to read {ces_file}: {e}")
        continue

print(f"[CES Vocab] Found {file_count} CES feature files")
print(f"[CES Vocab] Extracted {len(all_keys)} unique patterns")

# Create vocabulary mapping (sorted for determinism)
vocab = {key: idx for idx, key in enumerate(sorted(all_keys))}

# Save vocabulary
VOCAB_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(VOCAB_FILE, "w") as f:
    json.dump(vocab, f, indent=2)

print(f"[CES Vocab] ✓ Saved vocabulary to {VOCAB_FILE}")
print(f"[CES Vocab] Vocabulary size: {len(vocab)} dimensions")
