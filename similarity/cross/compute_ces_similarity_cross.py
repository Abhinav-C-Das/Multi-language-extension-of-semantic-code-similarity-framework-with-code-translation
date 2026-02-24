#!/usr/bin/env python3
"""
Cross-Language CES (Computation Evolution Signatures) Similarity
Scans outputs/cross/p{N}/ for all programs (mixed languages), applies context filtering,
and computes weighted Tversky similarity across all programs regardless of language.
"""

import json
import os
import sys
import re
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

# Single output directory (problem-first layout)
OUTPUT_DIR = "outputs/cross"

# Language-specific CES filenames
CES_FILENAMES = {
    "java": "ces_v2.json",
    "cpp":  "semantic.json",
    "c":    "semantic.json",
}

# Contexts to exclude (language-specific, not CS-1 universal)
EXCLUDED_CONTEXTS = {
    "java_api", "java_stream", "java_collection",
    "stl_algo", "stl_container", "raii",
    "template_meta", "operator_overload",
}

# Tversky asymmetry parameters
TVERSKY_ALPHA = 0.1  # Weight for patterns only in student
TVERSKY_BETA  = 0.9  # Weight for patterns only in reference

# Output
OUTPUT_FILE = "evaluation/cross/ces_similarity_matrix_cross.json"


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


def load_ces_features(output_dir, lang):
    """Load CES features from a program's output directory, filtering excluded contexts."""
    filename = CES_FILENAMES.get(lang, "semantic.json")
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        return [], {}

    try:
        with open(filepath, 'r') as f:
            raw = f.read().strip()
            if not raw:
                return [], {}
            # Strip Joern log lines before JSON parsing
            lines = raw.split('\n')
            json_lines = [l for l in lines if not re.match(r'^\[\w+\s*\]', l.strip())]
            raw = '\n'.join(json_lines).strip()
            if not raw:
                return [], {}
            data = json.loads(raw)
    except (json.JSONDecodeError, IOError):
        return [], {}

    # Handle both list-of-records and dict formats
    records = []
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        if "patterns" in data:
            records = data["patterns"]
        elif "records" in data:
            records = data["records"]
        else:
            records = [data]

    # Extract patterns and weights, filtering excluded contexts
    patterns = []
    weights = {}
    for r in records:
        if not isinstance(r, dict):
            continue

        # Filter [INFO] log artifacts
        if any(str(v).startswith("[INFO]") for v in r.values() if isinstance(v, str)):
            continue

        context = r.get("context", "")
        if context in EXCLUDED_CONTEXTS:
            continue

        evolution = r.get("evolution", "")
        operator = r.get("operator", "")
        key = f"{context}::{evolution}::{operator}"

        patterns.append(key)
        importance = float(r.get("importance", 1.0))

        if key in weights:
            weights[key] += importance
        else:
            weights[key] = importance

    return patterns, weights


def weighted_tversky(patterns1, weights1, patterns2, weights2,
                     alpha=TVERSKY_ALPHA, beta=TVERSKY_BETA):
    """
    Compute weighted Tversky similarity between two pattern sets.
    Asymmetric: alpha penalizes patterns only in A (student),
    beta penalizes patterns only in B (reference).
    """
    set1 = set(patterns1)
    set2 = set(patterns2)

    if not set1 and not set2:
        return 0.0

    all_patterns = set1 | set2

    intersection = 0.0
    diff_a_b = 0.0
    diff_b_a = 0.0

    for p in all_patterns:
        w1 = weights1.get(p, 0.0)
        w2 = weights2.get(p, 0.0)

        shared = min(w1, w2)
        intersection += shared

        if w1 > w2:
            diff_a_b += (w1 - w2)

        if w2 > w1:
            diff_b_a += (w2 - w1)

    denominator = intersection + (alpha * diff_a_b) + (beta * diff_b_a)
    return intersection / denominator if denominator > 0 else 0.0


def scan_all_programs():
    """
    Scan outputs/cross/ for all programs across all languages.
    
    Layout:
      outputs/cross/{problem}/{role}/{prog}/          (Java — directly under problem)
      outputs/cross/c/{problem}/{role}/{prog}/         (C — under c/ subdirectory)
      outputs/cross/cpp/{problem}/{role}/{prog}/       (C++ — under cpp/ subdirectory)
    
    Returns dict: {prog_key: (patterns, weights)}
    """
    programs = {}

    if not os.path.exists(OUTPUT_DIR):
        print(f"  [ERROR] {OUTPUT_DIR} not found")
        return programs

    # Scan roots: top-level (Java) + c/ + cpp/
    scan_roots = [
        OUTPUT_DIR,                            # Java: outputs/cross/p1/ref/ref1_java
        os.path.join(OUTPUT_DIR, "c"),          # C:    outputs/cross/c/p1/ref/ref1_c
        os.path.join(OUTPUT_DIR, "cpp"),        # C++:  outputs/cross/cpp/p1/ref/ref1_cpp
    ]

    for root in scan_roots:
        if not os.path.exists(root):
            continue

        for problem in sorted(os.listdir(root)):
            # Skip language subdirectories themselves when scanning top-level
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

                    patterns, weights = load_ces_features(prog_path, lang)

                    # Key format: "p1/ref/ref1_java" (matches ground truth)
                    prog_key = f"{problem}/{role}/{prog}"
                    programs[prog_key] = (patterns, weights)

                    if patterns:
                        print(f"  [LOAD] {prog_key}: {len(patterns)} patterns ({lang})")
                    else:
                        print(f"  [WARN] {prog_key}: no CES features ({lang})")

    return programs


def compute_similarity_matrix(programs):
    """Compute pairwise Tversky similarity for all programs."""
    prog_keys = sorted(programs.keys())
    matrix = {}

    for key_a in prog_keys:
        matrix[key_a] = {}
        patterns_a, weights_a = programs[key_a]

        for key_b in prog_keys:
            if key_a == key_b:
                matrix[key_a][key_b] = 1.0
                continue

            patterns_b, weights_b = programs[key_b]
            score = weighted_tversky(patterns_a, weights_a, patterns_b, weights_b)
            matrix[key_a][key_b] = round(score, 6)

    return matrix


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 50)
    print("[CES CROSS] Computing cross-language CES similarity")
    print("=" * 50)

    # Scan all programs across all languages
    programs = scan_all_programs()

    if not programs:
        print("[ERROR] No programs found. Check output directories.")
        sys.exit(1)

    print(f"\n[INFO] Total programs loaded: {len(programs)}")

    # Compute similarity matrix
    matrix = compute_similarity_matrix(programs)

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(matrix, f, indent=2)

    print(f"\n[✓] CES cross-language similarity matrix written to {OUTPUT_FILE}")
    print(f"    Matrix size: {len(matrix)}x{len(matrix)}")


if __name__ == "__main__":
    main()
