#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DATA_DIR="${DATA_DIR:-"data/cpp"}"
OUT_DIR="outputs/cpp"
WL_SCRIPT="cpg/scripts/cpp/wl/wl_ast.sc"

for PROBLEM in "$DATA_DIR"/*; do
  [ -d "$PROBLEM" ] || continue
  PNAME=$(basename "$PROBLEM")
  echo "[WL CPP] Problem: $PNAME"

  for ROLE in ref s; do
    CPG_BASE="cpgs/cpp/$PNAME/$ROLE"
    [ -d "$CPG_BASE" ] || continue

    for PROG_DIR in "$CPG_BASE"/*; do
      [ -d "$PROG_DIR" ] || continue
      PROG=$(basename "$PROG_DIR")
      CPG="$PROG_DIR/cpg.bin"

      # Find source file in data directory
      SRC_FILE=$(ls "$DATA_DIR/$PNAME/$ROLE/$PROG".* 2>/dev/null | head -n 1 | xargs basename)
      if [ -z "$SRC_FILE" ]; then 
         # Fallback if source not found but CPG exists
         SRC_FILE="$PROG" 
      fi

      OUT_PROG="$OUT_DIR/$PNAME/$ROLE/$PROG"
      
      # Skip if no CPG
      if [ ! -f "$CPG" ]; then
        continue 
      fi

      echo "  └─ WL $ROLE/$PROG"

      mkdir -p "$OUT_PROG"

      TARGET_FILE="$SRC_FILE" \
      joern --exit --cpg "$CPG" \
        --script "$WL_SCRIPT" \
        > wl.out 2>/dev/null

      sed -n '/^{/,$p' wl.out > "$OUT_PROG/wl_ast.json"

    done
  done
done

echo "[✓] WL AST extraction complete for C++ (CPG reused)"
