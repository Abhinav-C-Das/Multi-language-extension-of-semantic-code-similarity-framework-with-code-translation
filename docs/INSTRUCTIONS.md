# Multi-View Code Similarity Framework - Instructions

This repository contains a multi-view code similarity framework supporting C and Java.
It uses Joern for CPG generation and extracts Structural, Semantic (CES), and Behavioral (WL) features.

## Directory Structure

- `data/`
  - `c/` : Contains C sample data and ground truth (`ground_truth.json`).
  - `java/` : Contains Java sample data and ground truth (`ground_truth.json`).
- `cpg/` : Joern CPG generation scripts.
- `experiments/` : Main experiment runners.
- `similarity/` : Feature vectorization and similarity computation scripts.
- `evaluation/` : Similarity matrix comparison and accuracy calculation.

## Prerequisites

- **Joern**: Must be installed and available in your PATH as `joern`.
- **Python 3.8+**: Standard library.

## Running the C Pipeline

The C pipeline processes code in `data/c/`.

1. **Run the full pipeline:**
   ```bash
   ./run_c_pipeline.sh
   ```

   This script will:
   - Clean previous outputs in `outputs/c` and `vectors/c`.
   - Generate CPGs using Joern.
   - Run Baseline, WL, and CES pipelines.
   - Aggregate features.
   - Calculate accuracy against `data/ground_truth.json`.

2. **Check Results:**
   - Accuracy Report: Displayed in the terminal.
   - Similarity Matrices: `evaluation/c/*.json`.
     - `final_similarity_matrix.json`: The aggregated weighted matrix.

## Running the Java Pipeline

The Java pipeline processes code in `data/java/`.

1. **Run the full pipeline:**
   ```bash
   ./run_java_pipeline.sh
   ```

   This script will:
   - Clean previous outputs in `outputs/java` and `vectors/java`.
   - Generate CPGs using Joern.
   - Run Baseline, WL, and CES pipelines.
   - Aggregate features.
   - Calculate accuracy against `data/ground_truth.json`.

2. **Check Results:**
   - Accuracy Report: Displayed in the terminal.
   - Similarity Matrices: `evaluation/java/*.json`.
     - `final_similarity_matrix_java.json`: The aggregated weighted matrix.

## Adding New Data

1. Create a problem directory in `data/c/` or `data/java/` (e.g., `data/c/p2`).
2. Add reference solutions to `data/c/p2/ref/` (e.g., `ref1.c`).
3. Add student submissions to `data/c/p2/s/` (e.g., `s1.c`).
4. Update the language-specific ground truth file:
   - For C: `data/c/ground_truth.json`
   - For Java: `data/java/ground_truth.json`
   
   Example for C (`data/c/ground_truth.json`):
   ```json
   {
     "p2": {
       "s1": "ref1",
       "s2": "ref2"
     }
   }
   ```
5. Run the respective pipeline script.
