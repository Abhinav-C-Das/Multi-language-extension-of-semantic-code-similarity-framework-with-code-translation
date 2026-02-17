import json
import sys
from pathlib import Path
import re

if len(sys.argv) != 2:
    print("Usage: python aggregate_baseline_java.py <features_dir>")
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

    match = JSON_BLOCK.search(text)
    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

# ---------------------------------------
# Baseline feature components (ENHANCED)
# ---------------------------------------
BASELINE_FILES = [
    "structural.json",
    "semantic.json",
    "behavioral.json",
    "variable_roles.json",
    "loop_patterns.json",  # NEW: Java-specific loop patterns
]

combined = {}

for fname in BASELINE_FILES:
    features = load_json_safe(prog_dir / fname)
    for k, v in features.items():
        combined[k] = v

# Add derived features for better discrimination
if "var_update_ACCUMULATIVE" in combined and "var_update_RECOMPUTED" in combined:
    total_updates = combined["var_update_ACCUMULATIVE"] + combined["var_update_RECOMPUTED"]
    if total_updates > 0:
        combined["accumulation_ratio"] = combined["var_update_ACCUMULATIVE"] / total_updates
    else:
        combined["accumulation_ratio"] = 0.0

# ---------------------------------------
# Write combined features (REQUIRED)
# ------------------------------------
with open(out_path, "w") as f:
    json.dump(combined, f, indent=2)

# Optional: also print for logs/debug
print(json.dumps(combined, indent=2))
