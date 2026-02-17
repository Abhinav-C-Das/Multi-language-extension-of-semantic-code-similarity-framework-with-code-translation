#!/usr/bin/env bash
set -e

echo "[WL Extract Java] Extracting WL features from CPGs..."

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
      
      echo "  [WL] $PNAME/$ROLE/$PROG"
      
      # Find the Java source file to get its name
      SRC_FILE=$(find "data/java/$PNAME/$ROLE" -name "*.java" | head -1 | xargs basename 2>/dev/null || echo "unknown.java")
      
      # Run WL extraction script
      TARGET_FILE="$SRC_FILE" \
      joern --exit --cpg "$CPG" \
        --script "$SCRIPTS_DIR/wl/wl_ast_java.sc" \
        > wl.out 2>/dev/null || true
      
      # Extract JSON output
      sed -n '/^{/,$p' wl.out > "$PROG_DIR/wl.json" 2>/dev/null || echo "{}" > "$PROG_DIR/wl.json"
      
      # Check if extraction succeeded
      if [ -s "$PROG_DIR/wl.json" ]; then
        extract_count=$((extract_count + 1))
      fi
    done
  done
done

echo "[WL Extract Java] ✓ Extracted WL features for $extract_count programs"
