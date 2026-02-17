#!/usr/bin/env bash
set -euo pipefail

echo "[CES] Extraction"
./experiments/pipeline/run_ces_all_extract.sh

echo "[CES] Build vocab"
python3 similarity/build_ces_vocab.py

echo "[CES] Vectorize"
python3 similarity/vectorize_ces.py

echo "[CES] Normalize"
mkdir -p vectors/ces_norm
for f in vectors/ces/*.vec; do
  [ -f "$f" ] || continue  # Skip if glob doesn't match any files
  python3 similarity/normalize_ces.py "$f" \
    "vectors/ces_norm/$(basename "$f" .vec).norm.vec"
done

echo "[CES] Similarity"
python3 similarity/compute_ces_similarity.py

echo "[CES] DONE"
