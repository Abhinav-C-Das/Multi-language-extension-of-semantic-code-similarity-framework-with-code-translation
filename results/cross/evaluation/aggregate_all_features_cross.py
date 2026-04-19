#!/usr/bin/env python3
"""
Cross-Language Feature Aggregation
Combines CES, WL, and Baseline similarity matrices using configurable weights.
Default: CES 25%, Baseline 35%, WL 40%
"""

import json
import os
import sys

# ============================================================
# Configuration
# ============================================================

INPUT_DIR = "evaluation/cross"

MATRICES = {
    "ces":      os.path.join(INPUT_DIR, "ces_similarity_matrix_cross.json"),
    "baseline": os.path.join(INPUT_DIR, "baseline_similarity_matrix_cross.json"),
    "wl":       os.path.join(INPUT_DIR, "wl_similarity_matrix_cross.json"),
}

DEFAULT_WEIGHTS = {
    "ces":      0.25,
    "baseline": 0.35,
    "wl":       0.40,
}

OUTPUT_FILE = os.path.join(INPUT_DIR, "final_similarity_matrix_cross.json")


# ============================================================
# Core Functions
# ============================================================

def load_matrix(filepath):
    """Load a similarity matrix from JSON file."""
    if not os.path.exists(filepath):
        print(f"  [WARN] Matrix not found: {filepath}")
        return None

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  [ERROR] Failed to load {filepath}: {e}")
        return None


def aggregate_matrices(matrices_data, weights):
    """
    Aggregate multiple similarity matrices using weighted combination.
    Only programs present in ALL matrices are included.
    """
    # Find common programs across all available matrices
    available = {name: data for name, data in matrices_data.items() if data is not None}

    if not available:
        print("[ERROR] No similarity matrices available.")
        sys.exit(1)

    # Normalize weights for available views only
    total_weight = sum(weights[name] for name in available)
    norm_weights = {name: weights[name] / total_weight for name in available}

    print(f"\n[INFO] Available views: {list(available.keys())}")
    print(f"[INFO] Normalized weights: {', '.join(f'{k}={v:.3f}' for k, v in norm_weights.items())}")

    # Find common program keys
    key_sets = [set(data.keys()) for data in available.values()]
    common_keys = sorted(set.intersection(*key_sets))

    if not common_keys:
        print("[ERROR] No common programs across matrices.")
        sys.exit(1)

    print(f"[INFO] Common programs: {len(common_keys)}")

    # Compute weighted aggregation
    aggregated = {}
    for key_a in common_keys:
        aggregated[key_a] = {}
        for key_b in common_keys:
            if key_a == key_b:
                aggregated[key_a][key_b] = 1.0
                continue

            weighted_sum = 0.0
            for name, data in available.items():
                score = data.get(key_a, {}).get(key_b, 0.0)
                weighted_sum += norm_weights[name] * score

            aggregated[key_a][key_b] = round(weighted_sum, 6)

    return aggregated


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 55)
    print("[AGGREGATE] Cross-Language Feature Aggregation")
    print("=" * 55)

    # Parse weights from CLI if provided
    weights = DEFAULT_WEIGHTS.copy()
    if len(sys.argv) >= 4:
        try:
            weights["ces"] = float(sys.argv[1])
            weights["baseline"] = float(sys.argv[2])
            weights["wl"] = float(sys.argv[3])
            print(f"[INFO] Using CLI weights: CES={weights['ces']}, Baseline={weights['baseline']}, WL={weights['wl']}")
        except ValueError:
            print("[WARN] Invalid weight arguments, using defaults")
    else:
        print(f"[INFO] Using default weights: CES={weights['ces']}, Baseline={weights['baseline']}, WL={weights['wl']}")

    # Load all matrices
    matrices_data = {}
    for name, filepath in MATRICES.items():
        print(f"\n[LOAD] Loading {name} matrix: {filepath}")
        matrices_data[name] = load_matrix(filepath)

    # Aggregate
    aggregated = aggregate_matrices(matrices_data, weights)

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(aggregated, f, indent=2)

    print(f"\n[✓] Aggregated matrix written to {OUTPUT_FILE}")
    print(f"    Matrix size: {len(aggregated)}x{len(aggregated)}")


if __name__ == "__main__":
    main()
