#!/usr/bin/env bash
set -e

# Default to C++ for this script
LANGUAGE="cpp"
DATA_DIR="${DATA_DIR:-data/cpp}"
OUT_DIR="${OUT_DIR:-outputs}"
SCRIPTS_DIR="cpg/scripts/cpp"
CPG_BASE="${CPG_BASE:-cpgs}"
# LANG_SUBDIR: subdirectory under OUT_DIR for this language.
# Default: "cpp" (standalone mode). Set to "" for cross-language (flat) mode.
LANG_SUBDIR="${LANG_SUBDIR:-cpp}"

echo "========================================"
echo "[JOERN] Starting CPG generation for: $LANGUAGE"
echo "========================================"

mkdir -p "$OUT_DIR"

# Determine extensions based on language
if [ "$LANGUAGE" == "cpp" ]; then
    EXTS=("cpp" "cc" "C" "cxx")
    # joern-parse/c2cpg auto-detects C++ mode by extension usually.
    # --c++ flag is evidently NOT supported by the CLI wrapper.
    JOERN_FLAGS=""
elif [ "$LANGUAGE" == "java" ]; then
    EXTS=("java")
    JOERN_FLAGS=""
else
    EXTS=("c")
    JOERN_FLAGS=""
fi

for PROBLEM in "$DATA_DIR"/*; do
  [ -d "$PROBLEM" ] || continue
  PNAME=$(basename "$PROBLEM")
  
  # SKIP if not a valid problem directory (must have 'ref' or 's')
  if [ ! -d "$PROBLEM/ref" ] && [ ! -d "$PROBLEM/s" ]; then
      # Echo only if verbose, or just skip silently to avoid confirming invalid problems
      # But since we echo [PROBLEM], we should only echo if valid
      continue
  fi

  echo "[+] Problem: $PNAME"

  for ROLE in ref s; do
    SRC_DIR="$PROBLEM/$ROLE"
    [ -d "$SRC_DIR" ] || continue

    # Check for files with any valid extension
    FOUND_FILES=false
    for EXT in "${EXTS[@]}"; do
        if ls "$SRC_DIR"/*.$EXT 1> /dev/null 2>&1; then
            FOUND_FILES=true
            break
        fi
    done

    if [ "$FOUND_FILES" = false ]; then
        continue
    fi

    for EXT in "${EXTS[@]}"; do
        for SRC in "$SRC_DIR"/*.$EXT; do
          [ -f "$SRC" ] || continue

          PROG=$(basename "$SRC" .$EXT)
          SRC_FILE=$(basename "$SRC")
          if [ -n "$LANG_SUBDIR" ]; then
            OUT_PROG="$OUT_DIR/$LANG_SUBDIR/$PNAME/$ROLE/$PROG"
            CPG_DIR="$CPG_BASE/$LANG_SUBDIR/$PNAME/$ROLE/$PROG"
          else
            OUT_PROG="$OUT_DIR/$PNAME/$ROLE/$PROG"
            CPG_DIR="$CPG_BASE/$PNAME/$ROLE/$PROG"
          fi
          CPG="$CPG_DIR/cpg.bin"

          mkdir -p "$OUT_PROG"
          mkdir -p "$CPG_DIR"

          echo "  └─ $ROLE/$PROG ($SRC_FILE)"

          # -----------------------------------------------
          # 1. Build or reuse CPG (PERSISTENT)
          # -----------------------------------------------
          if [ ! -f "$CPG" ]; then
            echo "     [CPG] building..."
            joern-parse "$SRC" --output "$CPG" $JOERN_FLAGS > /dev/null 2>&1
          else
            echo "     [CPG] reused"
          fi

          # -----------------------------------------------
          # 2. Canonicalization
          # -----------------------------------------------
          # TODO: Check if canonicalization script supports C++/Java syntax
          
          TARGET_FILE="$SRC_FILE" \
          joern --exit --cpg "$CPG" \
            --script "$SCRIPTS_DIR/preprocess/canonicalize.sc" \
            > canon.out 2>/dev/null

          # Filter out [INFO] logs, keep only JSON
          grep -v "^\[INFO\]" canon.out | sed -n '/^{/,$p' > "$OUT_PROG/canonical.json"
          echo "     [✓] Canonicalization"

          # -----------------------------------------------
          # 3. Structural features
          # -----------------------------------------------
          TARGET_FILE="$SRC_FILE" \
          joern --exit --cpg "$CPG" \
            --script "$SCRIPTS_DIR/structural/basic_structural.sc" \
            > structural.out 2>/dev/null

          grep -v "^\[INFO\]" structural.out | sed -n '/^{/,$p' > "$OUT_PROG/structural.json"
          echo "     [✓] Structural features"

          # -----------------------------------------------
          # 4. Semantic features (CES V3 Enhanced)
          # -----------------------------------------------
          TARGET_FILE="$SRC_FILE" \
          joern --exit --cpg "$CPG" \
            --script "$SCRIPTS_DIR/semantic/ces_v3_enhanced.sc" \
            > semantic.out 2>/dev/null

          # Filter [INFO] logs, then extract JSON array
          grep -v "^\[INFO\]" semantic.out | sed -n '/^[[{]/,$p' > "$OUT_PROG/semantic.json"
          echo "     [✓] CES v3 Enhanced features"

          # -----------------------------------------------
          # 5. WL (Weisfeiler-Leman) features  
          # -----------------------------------------------
          if [ -f "$SCRIPTS_DIR/wl/wl_ast.sc" ]; then
            TARGET_FILE="$SRC_FILE" \
            joern --exit --cpg "$CPG" \
              --script "$SCRIPTS_DIR/wl/wl_ast.sc" \
              > wl.out 2>/dev/null

            grep -v "^\[INFO\]" wl.out | sed -n '/^{/,$p' > "$OUT_PROG/wl_ast.json"
            echo "     [✓] WL features"
          fi

          # -----------------------------------------------
          # 6. Behavioral features
          # -----------------------------------------------
          TARGET_FILE="$SRC_FILE" \
          joern --exit --cpg "$CPG" \
            --script "$SCRIPTS_DIR/behavioral/basic_behavioral.sc" \
            > behavioral.out 2>/dev/null

          grep -v "^\[INFO\]" behavioral.out | sed -n '/^{/,$p' > "$OUT_PROG/behavioral.json"
          echo "     [✓] Behavioral features"
     
          # -----------------------------------------------
          # 7. Variable role features (CANONICALIZED)
          # -----------------------------------------------
          CANONICAL_JSON="$OUT_PROG/canonical.json" \
          TARGET_FILE="$SRC_FILE" \
          joern --exit --cpg "$CPG" \
            --script "$SCRIPTS_DIR/semantic/variable_roles.sc" \
            > variable_roles.out 2>/dev/null

          grep -v "^\[INFO\]" variable_roles.out | sed -n '/^{/,$p' > "$OUT_PROG/variable_roles.json"
          echo "     [✓] Variable roles"

          # -----------------------------------------------
          # 8. Aggregate baseline features
          # -----------------------------------------------
          if [ -f "similarity/aggregate_baseline.py" ]; then
            python3 similarity/aggregate_baseline.py "$OUT_PROG" > /dev/null 2>&1
            echo "     [✓] Baseline aggregated"
          fi

        done
    done
  done
done

echo "[✓] Joern feature extraction complete (CPG reused)"
