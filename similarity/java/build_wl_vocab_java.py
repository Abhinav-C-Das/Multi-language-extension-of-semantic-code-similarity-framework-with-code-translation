#!/usr/bin/env python3
"""
Build WL vocabulary from all Java programs
Creates a global vocabulary of all WL feature keys
"""
import json
from pathlib import Path

OUT_DIR = Path("outputs/java")
VOCAB_FILE = Path("vocabulary/java/wl_vocab.json")

print("[WL Vocab] Scanning for WL features...")

# Collect all WL keys across all programs
all_keys = set()
file_count = 0

for wl_file in OUT_DIR.rglob("wl.json"):
    try:
        with open(wl_file) as f:
            data = json.load(f)
            if isinstance(data, dict):
                all_keys.update(data.keys())
                file_count += 1
    except Exception as e:
        print(f"[WARN] Failed to read {wl_file}: {e}")
        continue

print(f"[WL Vocab] Found {file_count} WL feature files")
print(f"[WL Vocab] Extracted {len(all_keys)} unique features")

# Create vocabulary mapping (sorted for determinism)
vocab = {key: idx for idx, key in enumerate(sorted(all_keys))}

# Save vocabulary
VOCAB_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(VOCAB_FILE, "w") as f:
    json.dump(vocab, f, indent=2)

print(f"[WL Vocab] ✓ Saved vocabulary to {VOCAB_FILE}")
print(f"[WL Vocab] Vocabulary size: {len(vocab)} dimensions")
