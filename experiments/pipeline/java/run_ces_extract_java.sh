#!/usr/bin/env bash
set -e

echo "[CES Extract Java] Extracting CES v3 features from CPGs..."

SCRIPTS_DIR="cpg/scripts/java"
OUT_DIR="outputs/java"
CPG_BASE="cpgs/java"

extract_count=0

for PROBLEM_DIR in "$OUT_DIR"/*; do
  [ -d "$PROBLEM_DIR" ] || continue
  PNAME=$(basename "$PROBLEM_DIR")
  
  for ROLE in ref s; do
    ROLE_DIR="$PROBLEM_DIR/$ROLE"
    [ -d "$ROLE_DIR" ] || continue
    
    for PROG_DIR in "$ROLE_DIR"/*; do
      [ -d "$PROG_DIR" ] || continue
      PROG=$(basename "$PROG_DIR")
      
      CPG="$CPG_BASE/$PNAME/$ROLE/$PROG/cpg.bin"
      [ -f "$CPG" ] || continue
      
      echo "  [CES v3] $PNAME/$ROLE/$PROG"
      
      # Find the Java source file
      SRC_FILE=$(find "data/java/$PNAME/$ROLE" -name "*.java" | head -1 | xargs basename 2>/dev/null || echo "unknown.java")
      
      # Set canonical.json path for the script
      CANONICAL_JSON="$PROG_DIR/canonical.json"
      
      # Run CES v3 extraction script
      CANONICAL_JSON="$CANONICAL_JSON" \
      TARGET_FILE="$SRC_FILE" \
      joern --exit --cpg "$CPG" \
        --script "$SCRIPTS_DIR/semantic/ces_v3_java.sc" \
        > ces.out 2>/dev/null || true
      
      # Extract JSON output (CES outputs array starting with [)
      # Filter out Joern INFO messages first
      grep -v "\[INFO \]" ces.out | sed -n '/^\[/,$p' > "$PROG_DIR/ces_v2.json" 2>/dev/null || echo "[]" > "$PROG_DIR/ces_v2.json"
      
      # Check if extraction succeeded
      if [ -s "$PROG_DIR/ces_v2.json" ]; then
        extract_count=$((extract_count + 1))
      fi
    done
  done
done

echo "[CES Extract Java] ✓ Extracted CES v3 features for $extract_count programs"
