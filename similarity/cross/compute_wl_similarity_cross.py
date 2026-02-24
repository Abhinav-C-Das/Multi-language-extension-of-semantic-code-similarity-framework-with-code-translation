#!/usr/bin/env python3
"""
Cross-Language WL (Weisfeiler-Leman) Similarity
Scans outputs/cross/p{N}/ for all programs (mixed languages), filters to wl_i0_* features only,
builds local vocabulary per comparison, and computes cosine similarity.
"""

import json
import os
import sys
import math
import re
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

# Single output directory (problem-first layout)
OUTPUT_DIR = "outputs/cross"

# Language-specific WL filenames
WL_FILENAMES = {
    "java": "wl.json",
    "cpp":  "wl_ast.json",
    "c":    "wl_ast.json",
}

# Only use iteration-0 features (language-agnostic AST label counts)
WL_PREFIX = "wl_i0_"

OUTPUT_FILE = "evaluation/cross/wl_similarity_matrix_cross.json"


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


def load_wl_features(output_dir, lang):
    """Load WL features from a program's output directory, filtering to i0 only."""
    filename = WL_FILENAMES.get(lang, "wl_ast.json")
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, 'r') as f:
            raw = f.read().strip()
            if not raw:
                return {}
            # Strip Joern log lines before JSON parsing
            lines = raw.split('\n')
            json_lines = [l for l in lines if not re.match(r'^\[\w+\s*\]', l.strip())]
            raw = '\n'.join(json_lines).strip()
            if not raw:
                return {}
            data = json.loads(raw)
    except (json.JSONDecodeError, IOError):
        return {}

    if not isinstance(data, dict):
        return {}

    # Filter to i0 features only
    filtered = {}
    for key, value in data.items():
        if key.startswith(WL_PREFIX):
            try:
                filtered[key] = float(value)
            except (TypeError, ValueError):
                continue

    return filtered


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
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(0.0, min(1.0, dot))  # Clamp [0, 1] for normalized vectors


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

                    features = load_wl_features(prog_path, lang)
                    prog_key = f"{problem}/{role}/{prog}"
                    programs[prog_key] = features

                    if features:
                        print(f"  [LOAD] {prog_key}: {len(features)} i0 features ({lang})")
                    else:
                        print(f"  [WARN] {prog_key}: no WL i0 features ({lang})")

    return programs


def compute_similarity_matrix(programs):
    """
    Compute pairwise cosine similarity using inline local vocab approach.
    For each pair, builds a local vocab from only those two programs,
    vectorizes, normalizes, and computes cosine.
    """
    prog_keys = sorted(programs.keys())
    matrix = {}

    for key_a in prog_keys:
        matrix[key_a] = {}
        for key_b in prog_keys:
            if key_a == key_b:
                matrix[key_a][key_b] = 1.0
                continue

            # Skip if already computed (symmetric)
            if key_b in matrix and key_a in matrix.get(key_b, {}):
                matrix[key_a][key_b] = matrix[key_b][key_a]
                continue

            features_a = programs[key_a]
            features_b = programs[key_b]

            if not features_a and not features_b:
                matrix[key_a][key_b] = 0.0
                continue

            # Build local vocab for just this pair
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
    print("=" * 50)
    print("[WL CROSS] Computing cross-language WL similarity")
    print("=" * 50)

    programs = scan_all_programs()

    if not programs:
        print("[ERROR] No programs found.")
        sys.exit(1)

    print(f"\n[INFO] Total programs loaded: {len(programs)}")

    matrix = compute_similarity_matrix(programs)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(matrix, f, indent=2)

    print(f"\n[✓] WL cross-language similarity matrix written to {OUTPUT_FILE}")
    print(f"    Matrix size: {len(matrix)}x{len(matrix)}")


if __name__ == "__main__":
    main()
