#!/usr/bin/env bash
set -e

echo "========================================"
echo "[FULL PIPELINE JAVA] Starting full pipeline (Java Language)"
echo "========================================"

# --------------------------------------------------
# 0. Cleaning previous Java outputs
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 0: Cleaning previous Java outputs"
rm -rf outputs/java vectors/java evaluation/java/*.json

# --------------------------------------------------
# 0.5 Joern / CPG feature extraction
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 0.5: Running Joern / CPG feature extraction"
./experiments/java/run_joern_java.sh

# --------------------------------------------------
# 1. WL pipeline
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 1: Running WL pipeline"
echo "[WL] Extracting features..."
./experiments/pipeline/java/run_wl_extract_java.sh > /dev/null 2>&1

echo "[WL] Building vocabulary..."
python3 similarity/java/build_wl_vocab_java.py > /dev/null 2>&1

echo "[WL] Vectorizing..."
python3 similarity/java/vectorize_wl_java.py > /dev/null 2>&1

echo "[WL] Normalizing..."
python3 similarity/java/normalize_wl_java.py > /dev/null 2>&1

echo "[WL] Computing similarity matrix..."
python3 similarity/java/compute_wl_similarity_java.py > /dev/null 2>&1
echo "[✓] WL pipeline complete"

# --------------------------------------------------
# 2. CES pipeline
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 2: Running CES pipeline"
# CES features already extracted in Step 0.5 (run_joern_java.sh)

echo "[CES] Building vocabulary..."
python3 similarity/java/build_ces_vocab_java.py > /dev/null 2>&1

echo "[CES] Vectorizing..."
python3 similarity/java/vectorize_ces_java.py > /dev/null 2>&1

echo "[CES] Normalizing..."
python3 similarity/java/normalize_ces_java.py > /dev/null 2>&1

echo "[CES] Computing similarity matrix..."
python3 similarity/java/compute_ces_similarity_java.py > /dev/null 2>&1
echo "[✓] CES pipeline complete"

# --------------------------------------------------
# 3. Baseline similarity
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 3: Computing baseline similarity"
python3 similarity/java/compute_baseline_similarity_java.py > /dev/null 2>&1
echo "[✓] Baseline similarity complete"

# --------------------------------------------------
# 4. Aggregate all features
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 4: Aggregating all features"
python3 evaluation/java/aggregate_all_features_java.py 0.35 0.40 0.25 > /dev/null 2>&1
echo "[✓] Aggregation complete"

# --------------------------------------------------
# 5. Evaluate Accuracy
# --------------------------------------------------
echo
echo "[FULL PIPELINE] Step 5: Calculating Accuracy"
python3 evaluation/calculate_accuracy.py --matrix evaluation/java/final_similarity_matrix_java.json

echo
echo "[FULL PIPELINE] ✅ Full Java pipeline completed"
