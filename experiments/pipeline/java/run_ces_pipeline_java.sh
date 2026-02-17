#!/usr/bin/env bash
set -e

echo "[CES Pipeline Java] Starting CES v3 pipeline"

# Step 1: Extract CES v3 features
echo ""
echo "[CES Pipeline Java] Step 1: Extract CES v3 features"
./experiments/pipeline/java/run_ces_extract_java.sh

# Step 2: Compute similarity with LOCAL vocabulary and importance weights
echo ""
echo "[CES Pipeline Java] Step 2: Compute CES similarity (local vocab + importance)"
python3 similarity/java/compute_ces_similarity_java.py

echo ""
echo "[CES Pipeline Java] ✓ CES pipeline complete"
