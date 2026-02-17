#!/usr/bin/env bash
set -e

echo "[WL Pipeline Java] Starting WL pipeline"

# Step 1: Extract WL features
echo ""
echo "[WL Pipeline Java] Step 1: Extract WL features"
./experiments/pipeline/java/run_wl_extract_java.sh

# Step 2: Build vocabulary
echo ""
echo "[WL Pipeline Java] Step 2: Build WL vocabulary"
python3 similarity/java/build_wl_vocab_java.py

# Step 3: Vectorize
echo ""
echo "[WL Pipeline Java] Step 3: Vectorize WL features"
python3 similarity/java/vectorize_wl_java.py

# Step 4: Normalize
echo ""
echo "[WL Pipeline Java] Step 4: Normalize WL vectors"
python3 similarity/java/normalize_wl_java.py

# Step 5: Compute similarity matrix
echo ""
echo "[WL Pipeline Java] Step 5: Compute WL similarity"
python3 similarity/java/compute_wl_similarity_java.py

echo ""
echo "[WL Pipeline Java] ✓ WL pipeline complete"
