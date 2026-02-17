#!/usr/bin/env bash
set -e

echo "[Baseline Pipeline Java] Starting baseline pipeline"

# Baseline features are already extracted and aggregated by run_joern_java.sh
# We just need to compute similarity

echo ""
echo "[Baseline Pipeline Java] Computing baseline similarity"
python3 similarity/java/compute_baseline_similarity_java.py

echo ""
echo "[Baseline Pipeline Java] ✓ Baseline pipeline complete"
