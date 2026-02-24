# Cross-Language Code Similarity

## Overview

This extension enables **3-way cross-language code similarity matching** (C ↔ Java ↔ C++) for CS-1 level algorithms. It builds on the existing intra-language pipelines (Java, C++) by adding:

- **C language support** via Joern's unified `c2cpg` frontend
- **Language-agnostic similarity scripts** that compare programs regardless of source language
- **A master orchestration pipeline** that extracts features, computes similarity, and evaluates accuracy across all three languages

## Quick Start

```bash
# Run the full cross-language pipeline
./run_cross_pipeline.sh
```

## Architecture

### Views & Weights

| View     | Weight | Metric   | Description                                    |
|----------|--------|----------|------------------------------------------------|
| CES      | 25%    | Tversky  | Computation Evolution Signatures (α=0.1, β=0.9) |
| Baseline | 35%    | Cosine   | Structural + behavioral features (ratio-normalized) |
| WL       | 40%    | Cosine   | Weisfeiler-Leman iteration-0 AST labels         |

**SCDPS is excluded** — it provides 0% weight even in intra-language evaluation.

### Language-Specific Filenames

| Language | CES Output       | WL Output     | Baseline Output          |
|----------|-----------------|---------------|--------------------------|
| Java     | `ces_v2.json`    | `wl.json`     | `combined_features.json` |
| C++      | `semantic.json`  | `wl_ast.json` | `combined_features.json` |
| C        | `semantic.json`  | `wl_ast.json` | `combined_features.json` |

### Cross-Language Adaptations

1. **CES**: Filters excluded contexts (`java_api`, `stl_algo`, etc.) to keep only CS-1 universal patterns
2. **WL**: Uses only `wl_i0_*` features (iteration-0 AST labels are language-agnostic; i1/i2 contain language-specific hashes)
3. **Baseline**: Applies ratio normalization (counts → proportions) to eliminate language-specific scale differences

## Dataset Structure

```
data/cross/
├── ground_truth.json        # Maps students to algorithm strategies (e.g., "ref1")
└── p1/                      # Problem: Array Sum
    ├── ref/                  # 2 strategies × 3 languages = 6 files
    │   ├── ref1_java.java    # Strategy 1: Indexed for-loop with +=
    │   ├── ref1_c.c
    │   ├── ref1_cpp.cpp
    │   ├── ref2_java.java    # Strategy 2: While-loop with explicit addition
    │   ├── ref2_c.c
    │   └── ref2_cpp.cpp
    └── s/                    # 9 students (3 per language)
        ├── s1_java.java      # → ref1
        ├── s2_cpp.cpp        # → ref1
        └── ...
```

### Ground Truth Format

Maps student directory names to **algorithm strategy identifiers** (not language-specific references):
```json
{"p1": {"s1_java": "ref1", "s2_cpp": "ref1", "s3_c": "ref2"}}
```

This means `s1_java` should match **any** `ref1_*` program (Java, C++, or C) — the system is truly language-agnostic.

## Pipeline Flow

```
run_cross_pipeline.sh
│
├── Phase 0: Joern extraction (Java, C++, C)
│   └── export DATA_DIR="data/cross" → language scripts use fallback pattern
│
├── Phase 1: Cross-language similarity
│   ├── CES  → evaluation/cross/ces_similarity_matrix_cross.json
│   ├── WL   → evaluation/cross/wl_similarity_matrix_cross.json
│   └── Base → evaluation/cross/baseline_similarity_matrix_cross.json
│
├── Phase 2: Weighted aggregation (0.25 / 0.35 / 0.40)
│   └── → evaluation/cross/final_similarity_matrix_cross.json
│
└── Phase 3: Accuracy evaluation
    └── → accuracy report
```

## Files Created

| File | Purpose |
|------|---------|
| `cpg/scripts/c/` (6 scripts) | C Joern feature extraction scripts |
| `experiments/c/run_joern_c.sh` | C CPG + feature extraction |
| `similarity/cross/compute_ces_similarity_cross.py` | Cross-language CES similarity |
| `similarity/cross/compute_wl_similarity_cross.py` | Cross-language WL similarity |
| `similarity/cross/compute_baseline_similarity_cross.py` | Cross-language baseline similarity |
| `evaluation/cross/aggregate_all_features_cross.py` | Weighted matrix aggregation |
| `run_cross_pipeline.sh` | Master pipeline orchestrator |
| `run_c_pipeline.sh` | Standalone C pipeline |
