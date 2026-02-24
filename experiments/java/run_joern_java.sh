#!/usr/bin/env bash
set -e

echo "=========================================="
echo "Java CPG Generation & Feature Extraction"
echo "=========================================="

DATA_DIR="${DATA_DIR:-data/java}"
OUT_DIR="${OUT_DIR:-outputs/java}"
SCRIPTS_DIR="cpg/scripts/java"
CPG_BASE="${CPG_BASE:-cpgs/java}"

mkdir -p "$OUT_DIR"
mkdir -p "$CPG_BASE"

# Check if Joern is installed
if ! command -v joern-parse &> /dev/null; then
    echo "ERROR: Joern not found. Please install Joern first."
    exit 1
fi

echo "[INFO] Processing Java programs..."

for PROBLEM in "$DATA_DIR"/*; do
  [ -d "$PROBLEM" ] || continue
  PNAME=$(basename "$PROBLEM")
  echo ""
  echo "[+] Problem: $PNAME"

  for ROLE in ref s; do
    SRC_DIR="$PROBLEM/$ROLE"
    [ -d "$SRC_DIR" ] || continue

    for SRC in "$SRC_DIR"/*.java; do
      [ -f "$SRC" ] || continue

      PROG=$(basename "$SRC" .java)
      SRC_FILE=$(basename "$SRC")
      OUT_PROG="$OUT_DIR/$PNAME/$ROLE/$PROG"
      CPG_DIR="$CPG_BASE/$PNAME/$ROLE/$PROG"
      CPG="$CPG_DIR/cpg.bin"

      mkdir -p "$OUT_PROG"
      mkdir -p "$CPG_DIR"

      echo "  └─ $ROLE/$PROG"

      # -----------------------------------------------
      # 1. Build or reuse CPG (PERSISTENT)
      # -----------------------------------------------
      if [ ! -f "$CPG" ]; then
        echo "     [CPG] building..."
        joern-parse "$SRC" --output "$CPG" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
          echo "     [ERROR] Failed to generate CPG for $SRC"
          continue
        fi
      else
        echo "     [CPG] reused"
      fi

      # -----------------------------------------------
      # 2. Canonicalization (Java-specific)
      # -----------------------------------------------
      if [ -f "$SCRIPTS_DIR/preprocess/canonicalize_java.sc" ]; then
        TARGET_FILE="$SRC_FILE" \
        joern --exit --cpg "$CPG" \
          --script "$SCRIPTS_DIR/preprocess/canonicalize_java.sc" \
          > canon.out 2>/dev/null

        sed -n '/^{/,$p' canon.out > "$OUT_PROG/canonical.json"
        echo "     [✓] Canonicalization"
      fi

      # -----------------------------------------------
      # 3. Structural features
      # -----------------------------------------------
      if [ -f "$SCRIPTS_DIR/structural/basic_structural_java.sc" ]; then
        TARGET_FILE="$SRC_FILE" \
        joern --exit --cpg "$CPG" \
          --script "$SCRIPTS_DIR/structural/basic_structural_java.sc" \
          > structural.out 2>/dev/null

        sed -n '/^{/,$p' structural.out > "$OUT_PROG/structural.json"
        echo "     [✓] Structural features"
      fi

      # -----------------------------------------------
      # 4. Semantic features (CES V3 Enhanced)
      # -----------------------------------------------
      if [ -f "$SCRIPTS_DIR/semantic/ces_v3_java.sc" ]; then
        TARGET_FILE="$SRC_FILE" \
        joern --exit --cpg "$CPG" \
          --script "$SCRIPTS_DIR/semantic/ces_v3_java.sc" \
          > semantic.out 2>/dev/null

        # CES v3 outputs JSON array, so match [ or {
        sed -n '/^[[{]/,$p' semantic.out > "$OUT_PROG/ces_v2.json"
        echo "     [✓] CES v3 Enhanced features"
      fi

      # -----------------------------------------------
      # 5. WL (Weisfeiler-Leman) features
      # -----------------------------------------------
      if [ -f "$SCRIPTS_DIR/wl/wl_ast_java.sc" ]; then
        TARGET_FILE="$SRC_FILE" \
        joern --exit --cpg "$CPG" \
          --script "$SCRIPTS_DIR/wl/wl_ast_java.sc" \
          > wl.out 2>/dev/null

        sed -n '/^{/,$p' wl.out > "$OUT_PROG/wl.json"
        echo "     [✓] WL features"
      fi

      # -----------------------------------------------
      # 6. Behavioral features
      # -----------------------------------------------
      if [ -f "$SCRIPTS_DIR/behavioral/basic_behavioral_java.sc" ]; then
        TARGET_FILE="$SRC_FILE" \
        joern --exit --cpg "$CPG" \
          --script "$SCRIPTS_DIR/behavioral/basic_behavioral_java.sc" \
          > behavioral.out 2>/dev/null

        sed -n '/^{/,$p' behavioral.out > "$OUT_PROG/behavioral.json"
        echo "     [✓] Behavioral features"
      fi

      # -----------------------------------------------
      # 6. Variable roles (canonicalized)
      # -----------------------------------------------
      if [ -f "$SCRIPTS_DIR/semantic/variable_roles_java.sc" ]; then
        CANONICAL_JSON="$OUT_PROG/canonical.json" \
        TARGET_FILE="$SRC_FILE" \
        joern --exit --cpg "$CPG" \
          --script "$SCRIPTS_DIR/semantic/variable_roles_java.sc" \
          > variable_roles.out 2>/dev/null

        sed -n '/^{/,$p' variable_roles.out > "$OUT_PROG/variable_roles.json"
        echo "     [✓] Variable roles"
      fi

      # -----------------------------------------------
      # 7. Aggregate baseline features
      # -----------------------------------------------
      if [ -f "similarity/java/aggregate_baseline_java.py" ]; then
        python3 similarity/java/aggregate_baseline_java.py "$OUT_PROG" > /dev/null 2>&1
        echo "     [✓] Baseline aggregated"
      fi

    done
  done
done

echo ""
echo "[✓] Java feature extraction complete"
echo "    Output: $OUT_DIR"
echo "    CPGs: $CPG_BASE"
