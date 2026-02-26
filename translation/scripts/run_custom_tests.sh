#!/bin/bash

# run_custom_tests.sh
# Orchestrates translation and verification across all files in translation/input

# Do NOT use set -e: we want ALL tests to run even if some fail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_DIR="translation/input"
OUTPUT_DIR="translation/output/custom"
LANGUAGES=("java" "cpp" "c")

mkdir -p "$OUTPUT_DIR"

echo "=================================================="
echo "    🧪 Custom CS-1 Concept Translation Suite"
echo "=================================================="

# Loop through every source file in the input directory
for src_file in "$INPUT_DIR"/*; do
    if [ ! -f "$src_file" ]; then
        continue
    fi
    filename=$(basename "$src_file")
    basename_no_ext="${filename%.*}"

    # Detect source language and targets
    case "$filename" in
      *.c)    TARGETS="cpp java" ;;
      *.cpp)  TARGETS="c java" ;;
      *.java) TARGETS="c cpp" ;;
      *)      continue ;;
    esac

    echo ""
    echo "▶ Testing File: $filename"
    echo "--------------------------------------------------"
    echo "--- ORIGINAL SOURCE CODE ($src_file) ---"
    cat "$src_file"
    echo "--------------------------------------------------"

    for TARGET_LANG in $TARGETS; do
        echo "  Target -> $TARGET_LANG"
        
        # 1. Run the translation pipeline
        bash "$SCRIPT_DIR/run_translation.sh" "$src_file" "$TARGET_LANG" "$OUTPUT_DIR" > /dev/null 2>&1
        
        # Determine correct file extension for generated file
        case "$TARGET_LANG" in
          c)    GEN_EXT="c" ;;
          cpp)  GEN_EXT="cpp" ;;
          java) GEN_EXT="java" ;;
        esac
        gen_file="$OUTPUT_DIR/${basename_no_ext}_generated.${GEN_EXT}"
        
        if [ ! -f "$gen_file" ]; then
             echo "    [❌] Pipeline failed: No generated file found at $gen_file"
             continue
        fi

        # 2. Run the Verification Script
        echo "  [Verifying Semantic Equivalence]"
        python3 "$SCRIPT_DIR/verify_translation.py" --source "$src_file" --generated "$gen_file" --target-lang "$TARGET_LANG"
        
        echo ""
        echo "--- GENERATED CODE ($gen_file) ---"
        cat "$gen_file"
        echo "----------------------------------------"
        echo ""
    done
done

echo ""
echo "=================================================="
echo "    🏁 Custom Suite Execution Complete"
echo "=================================================="
