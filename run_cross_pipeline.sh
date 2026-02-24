#!/usr/bin/env bash
set -e

echo "================================================================"
echo " CROSS-LANGUAGE CODE SIMILARITY PIPELINE"
echo " 3-Way Matching: C ↔ Java ↔ C++"
echo "================================================================"

# Override DATA_DIR so all Joern scripts process the cross-language dataset
export DATA_DIR="data/cross"

# ==================================================================
# Phase 0: Feature Extraction (per-language Joern runs)
#   Outputs routed to outputs/cross/{java,cpp,c}/ and cpgs/cross/{java,cpp,c}/
# ==================================================================
echo ""
echo "[Phase 0] Feature Extraction (Joern CPG + scripts)"
echo "---------------------------------------------------"

echo "[Phase 0.1] Java extraction..."
OUT_DIR="outputs/cross" CPG_BASE="cpgs/cross" \
  ./experiments/java/run_joern_java.sh

echo "[Phase 0.2] C++ extraction..."
LANG_SUBDIR="" OUT_DIR="outputs/cross" CPG_BASE="cpgs/cross" \
  ./experiments/cpp/run_joern_cpp.sh

echo "[Phase 0.3] C extraction..."
LANG_SUBDIR="" OUT_DIR="outputs/cross" CPG_BASE="cpgs/cross" \
  ./experiments/c/run_joern_c.sh

echo ""
echo "[✓] Phase 0 complete: All features extracted"

# ==================================================================
# Phase 1: Cross-Language Similarity Computation
# ==================================================================
echo ""
echo "[Phase 1] Computing cross-language similarity"
echo "----------------------------------------------"

echo "[Phase 1.1] CES similarity (Tversky α=0.1, β=0.9)..."
python3 similarity/cross/compute_ces_similarity_cross.py

echo "[Phase 1.2] WL similarity (i0-only, Cosine)..."
python3 similarity/cross/compute_wl_similarity_cross.py

echo "[Phase 1.3] Baseline similarity (ratio-normalized, Cosine)..."
python3 similarity/cross/compute_baseline_similarity_cross.py

echo ""
echo "[✓] Phase 1 complete: All similarity matrices computed"

# ==================================================================
# Phase 2: Weighted Aggregation
# ==================================================================
echo ""
echo "[Phase 2] Aggregating similarity views"
echo "--------------------------------------"

# Weights: CES=25%, Baseline=35%, WL=40%
python3 evaluation/cross/aggregate_all_features_cross.py 0.25 0.35 0.40

echo ""
echo "[✓] Phase 2 complete: Final aggregated matrix ready"

# ==================================================================
# Phase 3: Accuracy Evaluation
# ==================================================================
echo ""
echo "[Phase 3] Evaluating accuracy"
echo "-----------------------------"

python3 evaluation/calculate_accuracy.py \
  --matrix evaluation/cross/final_similarity_matrix_cross.json \
  --gt data/cross/ground_truth.json

echo ""
echo "================================================================"
echo " CROSS-LANGUAGE PIPELINE COMPLETE"
echo "================================================================"
