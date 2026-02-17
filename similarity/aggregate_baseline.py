#!/usr/bin/env python3
"""
Language-agnostic baseline aggregation and vectorization
Works for both C++ and Java by detecting language from path
"""
import json
import sys
from pathlib import Path
import re

if len(sys.argv) != 2:
    print("Usage: python aggregate_baseline.py <features_dir>")
    sys.exit(1)

prog_dir = Path(sys.argv[1])
out_path = prog_dir / "combined_features.json"

JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)

def load_json_safe(path: Path):
    if not path.exists():
        return {}

    text = path.read_text(errors="ignore").strip()
    if not text:
        return {}
    
    # Filter out [INFO] lines
    lines = [l for l in text.splitlines() if not l.startswith('[INFO')]
    text = '\n'.join(lines).strip()
    
    if not text:
        return {}

    match = JSON_BLOCK.search(text)
    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

# ---------------------------------------
# Baseline feature components (MODULAR)
# ---------------------------------------
BASELINE_FILES = [
    "structural.json",
    # "semantic.json",       # CES features (handled separately in CES view)
    "behavioral.json",
    "variable_roles.json",   # ← canonicalized features
]

combined = {}

for fname in BASELINE_FILES:
    features = load_json_safe(prog_dir / fname)
    for k, v in features.items():
        combined[k] = v

# ---------------------------------------
# Write combined features (REQUIRED)
# ---------------------------------------
with open(out_path, "w") as f:
    json.dump(combined, f, indent=2)

# Optional: also print for logs/debug
print(json.dumps(combined, indent=2))
