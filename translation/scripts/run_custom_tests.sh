#!/bin/bash

# run_custom_tests.sh
# Orchestrates translation and verification across all files in cpg_t1/input

# Do NOT use set -e: we want ALL tests to run even if some fail

INPUT_DIR="data/cpg_t1"
OUTPUT_DIR="cpg_t1/outputs"
LANGUAGES=("java" "cpp")

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
        bash cpg_t1/scripts/run_translation.sh "$src_file" "$TARGET_LANG" "$OUTPUT_DIR" > /dev/null 2>&1
        
        gen_file="$OUTPUT_DIR/${basename_no_ext}_generated.${TARGET_LANG}"
        
        if [ ! -f "$gen_file" ]; then
             echo "    [❌] Pipeline failed: No generated file found at $gen_file"
             continue
        fi

        # 2. Run the Verification Script
        echo "  [Verifying Semantic Equivalence]"
        python3 cpg_t1/scripts/verify_translation.py --source "$src_file" --generated "$gen_file" --target-lang "$TARGET_LANG"
        
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
