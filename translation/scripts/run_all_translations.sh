#!/usr/bin/env bash
# =============================================================
# run_all_translations.sh — Batch translation for all problems
#
# Translates all source files across all 10 problems and all
# 6 translation directions (C↔Java, C↔C++, Java↔C++).
#
# Usage:
#   bash cpg_t1/run_all_translations.sh [data_dir]
# =============================================================
# Do NOT use set -e — each translation is independent; record all results even on partial failure

DATA_DIR=${1:-data/cross}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_BASE="translation/output"
RESULTS_FILE="$OUTPUT_BASE/translation_results.json"

mkdir -p "$OUTPUT_BASE"

TOTAL=0
PASS=0
FAIL=0
RESULTS="["

echo "============================================"
echo " Batch CPG Translation"
echo " Data: $DATA_DIR"
echo " Output: $OUTPUT_BASE"
echo "============================================"
echo ""

for PROBLEM in "$DATA_DIR"/p*; do
  [ -d "$PROBLEM" ] || continue
  PNAME=$(basename "$PROBLEM")
  echo "━━━ $PNAME ━━━"

  for ROLE in ref s; do
    SRC_DIR="$PROBLEM/$ROLE"
    [ -d "$SRC_DIR" ] || continue

    for SRC in "$SRC_DIR"/*; do
      [ -f "$SRC" ] || continue
      FNAME=$(basename "$SRC")

      # Detect source language
      case "$FNAME" in
        *.c)    SLANG="c";    TARGETS="cpp java" ;;
        *.cpp)  SLANG="cpp";  TARGETS="c java" ;;
        *.java) SLANG="java"; TARGETS="c cpp" ;;
        *)      continue ;;
      esac

      SRC_BASE=$(basename "$FNAME" | sed 's/\.[^.]*$//')

      for TLANG in $TARGETS; do
        OUT_DIR="$OUTPUT_BASE/$PNAME/$ROLE/${SRC_BASE}_to_${TLANG}"
        TOTAL=$((TOTAL + 1))

        # Run translation — create OUT_DIR first so pipeline.log can be written
        RESULT="FAIL"
        mkdir -p "$OUT_DIR"
        if bash "$SCRIPT_DIR/run_translation.sh" "$SRC" "$TLANG" "$OUT_DIR" > "$OUT_DIR/pipeline.log" 2>&1; then
          # Check if compilation passed
          if grep -q "Compilation successful" "$OUT_DIR/pipeline.log" 2>/dev/null; then
            RESULT="PASS"
            PASS=$((PASS + 1))
          else
            FAIL=$((FAIL + 1))
          fi
        else
          FAIL=$((FAIL + 1))
          mkdir -p "$OUT_DIR"
        fi

        STATUS_ICON=$([ "$RESULT" = "PASS" ] && echo "✓" || echo "✗")
        echo "  [$STATUS_ICON] $ROLE/$SRC_BASE → $TLANG ($RESULT)"

        # Add to results JSON
        [ $TOTAL -gt 1 ] && RESULTS="$RESULTS,"
        RESULTS="$RESULTS
  {\"problem\": \"$PNAME\", \"role\": \"$ROLE\", \"source\": \"$FNAME\", \"target\": \"$TLANG\", \"result\": \"$RESULT\"}"
      done
    done
  done
  echo ""
done

RESULTS="$RESULTS
]"

# Write results
echo "$RESULTS" > "$RESULTS_FILE"

# Summary
echo "============================================"
echo " TRANSLATION SUMMARY"
echo "   Total:  $TOTAL"
echo "   Pass:   $PASS"
echo "   Fail:   $FAIL"
echo "   Rate:   $(( PASS * 100 / (TOTAL > 0 ? TOTAL : 1) ))%"
echo "   Results: $RESULTS_FILE"
echo "============================================"
