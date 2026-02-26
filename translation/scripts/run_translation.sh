#!/usr/bin/env bash
# =============================================================
# run_translation.sh — Single-file CPG translation pipeline
#
# Translates a source file to a target language via CPG → APM.
#
# Usage:
#   bash cpg_t1/scripts/run_translation.sh <source_file> <target_lang> [output_dir]
#
# Example:
#   bash cpg_t1/scripts/run_translation.sh data/cross/p1/ref/ref1_c.c java cpg_t1/output
# =============================================================
# Do NOT use set -e — compilation failure at step 4 should not abort the whole script

SOURCE_FILE=$1
TARGET_LANG=$2
OUTPUT_DIR=${3:-translation/output}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Validate inputs
if [ -z "$SOURCE_FILE" ] || [ -z "$TARGET_LANG" ]; then
  echo "Usage: $0 <source_file> <target_lang> [output_dir]"
  echo "  target_lang: c | cpp | java"
  exit 1
fi

if [ ! -f "$SOURCE_FILE" ]; then
  echo "[ERROR] Source file not found: $SOURCE_FILE"
  exit 1
fi

# Determine file extension for target
case "$TARGET_LANG" in
  c)    EXT="c" ;;
  cpp)  EXT="cpp" ;;
  java) EXT="java" ;;
  *)
    echo "[ERROR] Unsupported target language: $TARGET_LANG (use: c, cpp, java)"
    exit 1
    ;;
esac

# Derive output filename
SRC_BASENAME=$(basename "$SOURCE_FILE" | sed 's/\.[^.]*$//')
mkdir -p "$OUTPUT_DIR"

echo "============================================"
echo " CPG Translation Pipeline"
echo " Source: $SOURCE_FILE"
echo " Target: $TARGET_LANG"
echo " Output: $OUTPUT_DIR"
echo "============================================"

echo ""
echo "--- ORIGINAL SOURCE CODE ($SOURCE_FILE) ---"
cat "$SOURCE_FILE"
echo "-------------------------------------------"
echo ""

# -----------------------------------------------
# Step 1: Generate CPG
# -----------------------------------------------
CPG_FILE="$OUTPUT_DIR/${SRC_BASENAME}_cpg.bin"
echo "[1/4] Generating CPG..."
if [ ! -f "$CPG_FILE" ]; then
  joern-parse "$SOURCE_FILE" --output "$CPG_FILE" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "  [ERROR] CPG generation failed"
    exit 1
  fi
  echo "  [✓] CPG generated"
else
  echo "  [✓] CPG reused (cached)"
fi

# -----------------------------------------------
# Step 2: Extract APM
# -----------------------------------------------
APM_FILE="$OUTPUT_DIR/${SRC_BASENAME}_apm.json"
echo "[2/4] Extracting APM..."
CPG_FILE="$CPG_FILE" TARGET_FILE="$(basename "$SOURCE_FILE")" \
  joern \
    --script "$SCRIPT_DIR/extract_apm.sc" \
    > "$OUTPUT_DIR/apm_raw.out" 2> "$OUTPUT_DIR/apm_err.log"

# Extract JSON from output (skip Joern header lines)
sed -n '/^{/,$p' "$OUTPUT_DIR/apm_raw.out" > "$APM_FILE"

# Validate JSON
if ! python3 -c "import json; json.load(open('$APM_FILE'))" 2>/dev/null; then
  echo "  [ERROR] APM extraction produced invalid JSON"
  echo "  Raw output saved to: $OUTPUT_DIR/apm_raw.out"
  exit 1
fi
echo "  [✓] APM extracted"

# -----------------------------------------------
# Step 3: Generate target code
# -----------------------------------------------
GENERATED_FILE="$OUTPUT_DIR/${SRC_BASENAME}_generated.${EXT}"
echo "[3/4] Generating $TARGET_LANG code..."
python3 "$SCRIPT_DIR/generate_${TARGET_LANG}.py" \
  "$APM_FILE" \
  --output "$GENERATED_FILE"

if [ ! -f "$GENERATED_FILE" ]; then
  echo "  [ERROR] Code generation failed"
  exit 1
fi
echo "  [✓] Generated: $GENERATED_FILE"

# -----------------------------------------------
# Step 4: Verify (compile)
# -----------------------------------------------
echo "[4/4] Verifying (compilation)..."
COMPILE_OK=0
case "$TARGET_LANG" in
  c)
    gcc "$GENERATED_FILE" -o "$OUTPUT_DIR/${SRC_BASENAME}_gen" 2>/dev/null && COMPILE_OK=1
    ;;
  cpp)
    g++ "$GENERATED_FILE" -o "$OUTPUT_DIR/${SRC_BASENAME}_gen" 2>/dev/null && COMPILE_OK=1
    ;;
  java)
    javac "$GENERATED_FILE" -d "$OUTPUT_DIR" 2>/dev/null && COMPILE_OK=1
    ;;
esac

if [ "$COMPILE_OK" -eq 1 ]; then
  echo "  [✓] Compilation successful"
else
  echo "  [⚠] Compilation failed — review generated code"
fi

# -----------------------------------------------
# Summary
# -----------------------------------------------
echo ""
echo "============================================"
echo " Results:"
echo "   APM:       $APM_FILE"
echo "   Generated: $GENERATED_FILE"
echo "   Compiled:  $([ $COMPILE_OK -eq 1 ] && echo 'YES' || echo 'NO')"
echo "============================================"

echo ""
echo "--- GENERATED CODE ($GENERATED_FILE) ---"
cat "$GENERATED_FILE"
echo "----------------------------------------"
echo ""
