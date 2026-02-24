#!/usr/bin/env bash
set -e

echo "========================================"
echo "[FULL PIPELINE C] Starting full pipeline (C Language)"
echo "========================================"

export DATA_DIR=${DATA_DIR:-"data/c"}

# --------------------------------------------------
# 0. Cleaning previous C outputs
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 0: Cleaning previous C outputs"
rm -rf outputs/c vectors/c evaluation/c/*.json

# --------------------------------------------------
# 0.5 Joern / CPG feature extraction
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 0.5: Running Joern / CPG feature extraction"
./experiments/c/run_joern_c.sh

# --------------------------------------------------
# 1. Baseline similarity
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 1: Computing baseline similarity"
python3 similarity/cpp/compute_baseline_similarity_cpp.py > /dev/null 2>&1
echo "[✓] Baseline similarity complete"

# --------------------------------------------------
# 2. WL pipeline
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 2: Running WL pipeline"
echo "[WL] Computing similarity matrix..."
python3 similarity/cpp/compute_wl_similarity_cpp.py > /dev/null 2>&1
echo "[✓] WL pipeline complete"

# --------------------------------------------------
# 3. CES pipeline
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 3: Running CES pipeline"
echo "[CES] Computing similarity matrix..."
python3 similarity/cpp/compute_ces_similarity_cpp.py > /dev/null 2>&1
echo "[✓] CES pipeline complete"

# --------------------------------------------------
# 4. Aggregate all features
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 4: Aggregating all features"
python3 evaluation/cpp/aggregate_all_features_cpp.py 0.35 0.40 0.25 > /dev/null 2>&1
echo "[✓] Aggregation complete"

# --------------------------------------------------
# 5. Evaluate Accuracy
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 5: Calculating Accuracy"
python3 evaluation/calculate_accuracy.py --matrix evaluation/cpp/final_similarity_matrix_cpp.json

echo
echo "[FULL PIPELINE] ✅ Full C pipeline completed"
