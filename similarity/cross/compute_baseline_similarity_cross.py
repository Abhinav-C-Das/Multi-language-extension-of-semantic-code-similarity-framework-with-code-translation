#!/usr/bin/env python3
"""
Cross-Language Baseline Similarity
Scans outputs/cross/p{N}/ for combined_features.json, flattens nested dicts,
applies ratio normalization to make features language-agnostic,
and computes cosine similarity.
"""

import json
import os
import sys
import math
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

# Single output directory (problem-first layout)
OUTPUT_DIR = "outputs/cross"
BASELINE_FILENAME = "combined_features.json"  # Same across all languages
OUTPUT_FILE = "evaluation/cross/baseline_similarity_matrix_cross.json"


# ============================================================
# Core Functions
# ============================================================

def detect_language(prog_name):
    """Detect language from program directory name suffix (_java, _cpp, _c)."""
    if prog_name.endswith("_java"):
        return "java"
    elif prog_name.endswith("_cpp"):
        return "cpp"
    elif prog_name.endswith("_c"):
        return "c"
    return None


def load_baseline_features(output_dir):
    """Load combined_features.json from a program's output directory."""
    filepath = os.path.join(output_dir, BASELINE_FILENAME)

    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def flatten_features(baseline):
    """Flatten nested feature dicts into a flat dict."""
    flat = {}
    for key, value in baseline.items():
        if isinstance(value, dict):
            for subkey, subval in value.items():
                flat[f"{key}.{subkey}"] = subval
        elif isinstance(value, (int, float)):
            flat[key] = value
        elif isinstance(value, bool):
            flat[key] = 1.0 if value else 0.0
    return flat


def ratio_normalize(flat_features):
    """
    Convert raw counts to ratios to make features language-agnostic.
    - Count features → divide by max(total, 1) to get proportions
    - Binary features → pass through as-is
    - Histogram features → normalize to sum=1
    """
    normalized = {}
    total = sum(abs(v) for v in flat_features.values()) if flat_features else 1.0
    total = max(total, 1.0)  # Division-by-zero safeguard

    for key, value in flat_features.items():
        if isinstance(value, bool) or value in (0, 1, 0.0, 1.0):
            # Binary flags pass through
            normalized[key] = float(value)
        else:
            # Ratio normalization
            normalized[key] = float(value) / total

    return normalized


def build_local_vocab(features_list):
    """Build a local vocabulary from a list of feature dicts."""
    vocab = {}
    idx = 0
    for features in features_list:
        for label in features.keys():
            if label not in vocab:
                vocab[label] = idx
                idx += 1
    return vocab


def vectorize(features, vocab):
    """Convert feature dict to vector using vocabulary mapping."""
    vec = [0.0] * len(vocab)
    for label, count in features.items():
        if label in vocab:
            vec[vocab[label]] = count
    return vec


def l2_normalize(vec):
    """L2-normalize a vector."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two L2-normalized vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(0.0, min(1.0, dot))


def scan_all_programs():
    """
    Scan outputs/cross/ for all programs across all languages.
    
    Layout:
      outputs/cross/{problem}/{role}/{prog}/          (Java)
      outputs/cross/c/{problem}/{role}/{prog}/         (C)
      outputs/cross/cpp/{problem}/{role}/{prog}/       (C++)
    """
    programs = {}

    if not os.path.exists(OUTPUT_DIR):
        print(f"  [ERROR] {OUTPUT_DIR} not found")
        return programs

    scan_roots = [
        OUTPUT_DIR,
        os.path.join(OUTPUT_DIR, "c"),
        os.path.join(OUTPUT_DIR, "cpp"),
    ]

    for root in scan_roots:
        if not os.path.exists(root):
            continue

        for problem in sorted(os.listdir(root)):
            if problem in ("c", "cpp", "java"):
                continue
            prob_path = os.path.join(root, problem)
            if not os.path.isdir(prob_path):
                continue

            for role in ["ref", "s"]:
                role_path = os.path.join(prob_path, role)
                if not os.path.isdir(role_path):
                    continue

                for prog in sorted(os.listdir(role_path)):
                    prog_path = os.path.join(role_path, prog)
                    if not os.path.isdir(prog_path):
                        continue

                    lang = detect_language(prog)
                    if not lang:
                        print(f"  [WARN] Cannot detect language for {prog}")
                        continue

                    raw = load_baseline_features(prog_path)
                    flat = flatten_features(raw)
                    normalized = ratio_normalize(flat)

                    prog_key = f"{problem}/{role}/{prog}"
                    programs[prog_key] = normalized

                    if normalized:
                        print(f"  [LOAD] {prog_key}: {len(normalized)} features ({lang})")
                    else:
                        print(f"  [WARN] {prog_key}: no baseline features ({lang})")

    return programs


def compute_similarity_matrix(programs):
    """Compute pairwise cosine similarity with inline local vocab."""
    prog_keys = sorted(programs.keys())
    matrix = {}

    for key_a in prog_keys:
        matrix[key_a] = {}
        for key_b in prog_keys:
            if key_a == key_b:
                matrix[key_a][key_b] = 1.0
                continue

            if key_b in matrix and key_a in matrix.get(key_b, {}):
                matrix[key_a][key_b] = matrix[key_b][key_a]
                continue

            features_a = programs[key_a]
            features_b = programs[key_b]

            if not features_a and not features_b:
                matrix[key_a][key_b] = 0.0
                continue

            local_vocab = build_local_vocab([features_a, features_b])
            vec_a = l2_normalize(vectorize(features_a, local_vocab))
            vec_b = l2_normalize(vectorize(features_b, local_vocab))

            score = cosine_similarity(vec_a, vec_b)
            matrix[key_a][key_b] = round(score, 6)

    return matrix


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 55)
    print("[BASELINE CROSS] Computing cross-language baseline similarity")
    print("=" * 55)

    programs = scan_all_programs()

    if not programs:
        print("[ERROR] No programs found.")
        sys.exit(1)

    print(f"\n[INFO] Total programs loaded: {len(programs)}")

    matrix = compute_similarity_matrix(programs)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(matrix, f, indent=2)

    print(f"\n[✓] Baseline cross-language similarity matrix written to {OUTPUT_FILE}")
    print(f"    Matrix size: {len(matrix)}x{len(matrix)}")


if __name__ == "__main__":
    main()
