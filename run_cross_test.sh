#!/usr/bin/env bash
set -e

echo "================================================================"
echo " CROSS-LANGUAGE TEST: Quick Similarity Check"
echo " p1: Java ref ↔ C student (Array Sum)"
echo " p2: C ref ↔ C++ student (Factorial)"
echo " p3: C++ ref ↔ Java student (Find Max)"
echo "================================================================"

export DATA_DIR="data/cross_test"
TEST_OUT="outputs/cross_test"
TEST_CPG="cpgs/cross_test"
TEST_EVAL="evaluation/cross_test"

# ==================================================================
# Phase 0: Feature Extraction
# ==================================================================
echo ""
echo "[Phase 0] Feature Extraction"
echo "----------------------------"

# Clean previous outputs
rm -rf "$TEST_OUT" "$TEST_CPG" "$TEST_EVAL"
mkdir -p "$TEST_EVAL"

# Run Java extraction (picks up .java files)
echo "[Phase 0.1] Java features..."
OUT_DIR="$TEST_OUT" CPG_BASE="$TEST_CPG" \
  ./experiments/java/run_joern_java.sh 2>/dev/null

# Run C++ extraction (picks up .cpp files)
echo "[Phase 0.2] C++ features..."
LANG_SUBDIR="" OUT_DIR="$TEST_OUT" CPG_BASE="$TEST_CPG" \
  ./experiments/cpp/run_joern_cpp.sh 2>/dev/null

# Run C extraction (picks up .c files)
echo "[Phase 0.3] C features..."
LANG_SUBDIR="" OUT_DIR="$TEST_OUT" CPG_BASE="$TEST_CPG" \
  ./experiments/c/run_joern_c.sh 2>/dev/null

echo ""
echo "[✓] Phase 0 complete"

# ==================================================================
# Phase 1: Compute Similarity (reuse cross scripts with overrides)
# ==================================================================
echo ""
echo "[Phase 1] Computing cross-language similarity"
echo "----------------------------------------------"

# Create a small Python script to compute similarity for our test data
python3 - <<'PYEOF'
import json, os, sys, re
from pathlib import Path

TEST_OUT = "outputs/cross_test"

# ============ HELPERS ============

def detect_language(prog_name):
    if prog_name.endswith("_java"): return "java"
    elif prog_name.endswith("_cpp"): return "cpp"
    elif prog_name.endswith("_c"): return "c"
    return None

def scan_programs(out_dir):
    """Scan all programs from outputs directory, handling both flat and nested layouts."""
    programs = {}
    if not os.path.exists(out_dir):
        return programs
    
    scan_roots = [out_dir, os.path.join(out_dir, "c"), os.path.join(out_dir, "cpp")]
    
    for root in scan_roots:
        if not os.path.exists(root):
            continue
        for problem in sorted(os.listdir(root)):
            if problem in ("c", "cpp", "java"):
                continue
            prob_path = os.path.join(root, problem)
            if not os.path.isdir(prob_path):
                continue
            for role in ["ref", "s"]:
                role_path = os.path.join(prob_path, role)
                if not os.path.isdir(role_path):
                    continue
                for prog in sorted(os.listdir(role_path)):
                    prog_path = os.path.join(role_path, prog)
                    if not os.path.isdir(prog_path):
                        continue
                    lang = detect_language(prog)
                    if not lang:
                        continue
                    key = f"{problem}/{role}/{prog}"
                    programs[key] = {"path": prog_path, "lang": lang}
    return programs

# ============ CES SIMILARITY ============

def load_ces(path, lang):
    fname = "ces_v2.json" if lang == "java" else "semantic.json"
    fpath = os.path.join(path, fname)
    if not os.path.exists(fpath):
        return [], {}
    try:
        with open(fpath) as f:
            raw = f.read().strip()
            lines = [l for l in raw.split('\n') if not re.match(r'^\[\w+\s*\]', l.strip())]
            raw = '\n'.join(lines).strip()
            if not raw: return [], {}
            data = json.loads(raw)
    except: return [], {}
    
    records = data if isinstance(data, list) else data.get("patterns", data.get("records", [data]))
    excluded = {"java_api","java_stream","java_collection","stl_algo","stl_container","raii","template_meta","operator_overload"}
    patterns, weights = [], {}
    for r in records:
        if not isinstance(r, dict): continue
        ctx = r.get("context","")
        if ctx in excluded: continue
        key = f"{ctx}::{r.get('evolution','')}::{r.get('operator','')}"
        patterns.append(key)
        w = float(r.get("importance", 1.0))
        weights[key] = weights.get(key, 0) + w
    return patterns, weights

def tversky(p1, w1, p2, w2, alpha=0.1, beta=0.9):
    s1, s2 = set(p1), set(p2)
    if not s1 and not s2: return 0.0
    inter = diff_ab = diff_ba = 0.0
    for p in s1 | s2:
        v1, v2 = w1.get(p, 0), w2.get(p, 0)
        inter += min(v1, v2)
        if v1 > v2: diff_ab += v1 - v2
        if v2 > v1: diff_ba += v2 - v1
    denom = inter + alpha * diff_ab + beta * diff_ba
    return inter / denom if denom > 0 else 0.0

# ============ WL SIMILARITY ============

def load_wl(path, lang):
    fname = "wl.json" if lang == "java" else "wl_ast.json"
    fpath = os.path.join(path, fname)
    if not os.path.exists(fpath):
        return {}
    try:
        with open(fpath) as f:
            raw = f.read().strip()
            lines = [l for l in raw.split('\n') if not re.match(r'^\[\w+\s*\]', l.strip())]
            raw = '\n'.join(lines).strip()
            data = json.loads(raw)
    except: return {}
    return data.get("i0", data) if isinstance(data, dict) else {}

def cosine(v1, v2):
    keys = set(v1) | set(v2)
    if not keys: return 0.0
    dot = sum(v1.get(k,0)*v2.get(k,0) for k in keys)
    m1 = sum(v**2 for v in v1.values())**0.5
    m2 = sum(v**2 for v in v2.values())**0.5
    return dot / (m1 * m2) if m1 * m2 > 0 else 0.0

# ============ BASELINE SIMILARITY ============

def load_baseline(path):
    fpath = os.path.join(path, "combined_features.json")
    if not os.path.exists(fpath):
        return {}
    try:
        with open(fpath) as f:
            data = json.load(f)
    except: return {}
    flat = {}
    for section, vals in data.items():
        if isinstance(vals, dict):
            for k, v in vals.items():
                if isinstance(v, (int, float)):
                    flat[f"{section}_{k}"] = v
    # Ratio normalize
    total = sum(abs(v) for v in flat.values())
    if total > 0:
        flat = {k: v/total for k, v in flat.items()}
    return flat

# ============ MAIN ============

programs = scan_programs(TEST_OUT)
print(f"\n[INFO] Found {len(programs)} programs:")
for k, v in sorted(programs.items()):
    print(f"  {k} ({v['lang']})")

if len(programs) < 2:
    print("[ERROR] Need at least 2 programs")
    sys.exit(1)

keys = sorted(programs.keys())

# Compute per-view matrices
ces_matrix = {}
wl_matrix = {}
bl_matrix = {}

for ka in keys:
    ces_matrix[ka] = {}
    wl_matrix[ka] = {}
    bl_matrix[ka] = {}
    pa, la = programs[ka]["path"], programs[ka]["lang"]
    ces_a = load_ces(pa, la)
    wl_a = load_wl(pa, la)
    bl_a = load_baseline(pa)
    
    for kb in keys:
        pb, lb = programs[kb]["path"], programs[kb]["lang"]
        if ka == kb:
            ces_matrix[ka][kb] = 1.0
            wl_matrix[ka][kb] = 1.0
            bl_matrix[ka][kb] = 1.0
            continue
        
        ces_b = load_ces(pb, lb)
        wl_b = load_wl(pb, lb)
        bl_b = load_baseline(pb)
        
        ces_matrix[ka][kb] = round(tversky(ces_a[0], ces_a[1], ces_b[0], ces_b[1]), 4)
        wl_matrix[ka][kb] = round(cosine(wl_a, wl_b), 4)
        bl_matrix[ka][kb] = round(cosine(bl_a, bl_b), 4)

# Aggregate: CES=25%, Baseline=35%, WL=40%
final = {}
for ka in keys:
    final[ka] = {}
    for kb in keys:
        score = 0.25 * ces_matrix[ka][kb] + 0.35 * bl_matrix[ka][kb] + 0.40 * wl_matrix[ka][kb]
        final[ka][kb] = round(score, 4)

# ============ DISPLAY ============

print("\n" + "="*80)
print(" CROSS-LANGUAGE SIMILARITY RESULTS")
print("="*80)

# Per-problem breakdown
problems_seen = {}
for k in keys:
    prob = k.split("/")[0]
    if prob not in problems_seen:
        problems_seen[prob] = {"refs": [], "students": []}
    role = k.split("/")[1]
    if role == "ref":
        problems_seen[prob]["refs"].append(k)
    else:
        problems_seen[prob]["students"].append(k)

for prob in sorted(problems_seen):
    info = problems_seen[prob]
    print(f"\n── {prob} ──────────────────────────────────────────")
    for sk in info["students"]:
        sname = sk.split("/")[-1]
        slang = programs[sk]["lang"]
        print(f"  Student: {sname} ({slang})")
        for rk in info["refs"]:
            rname = rk.split("/")[-1]
            rlang = programs[rk]["lang"]
            print(f"    vs {rname} ({rlang}):")
            print(f"      CES:      {ces_matrix[sk][rk]:.4f}")
            print(f"      WL:       {wl_matrix[sk][rk]:.4f}")
            print(f"      Baseline: {bl_matrix[sk][rk]:.4f}")
            print(f"      FINAL:    {final[sk][rk]:.4f}  {'✅ HIGH' if final[sk][rk] >= 0.7 else '❌ LOW'}")

# Cross-problem check (should be LOW)
print(f"\n── Cross-Problem Sanity Check (should be LOW) ──────────")
all_students = [k for k in keys if "/s/" in k]
all_refs = [k for k in keys if "/ref/" in k]
for sk in all_students:
    sprob = sk.split("/")[0]
    sname = sk.split("/")[-1]
    for rk in all_refs:
        rprob = rk.split("/")[0]
        if sprob == rprob:
            continue  # skip same-problem (already shown above)
        rname = rk.split("/")[-1]
        print(f"  {sname} ({sprob}) vs {rname} ({rprob}): FINAL={final[sk][rk]:.4f}  {'⚠️' if final[sk][rk] >= 0.7 else '✅ LOW'}")

# Save matrices
os.makedirs("evaluation/cross_test", exist_ok=True)
with open("evaluation/cross_test/ces_similarity_matrix.json", "w") as f:
    json.dump(ces_matrix, f, indent=2)
with open("evaluation/cross_test/wl_similarity_matrix.json", "w") as f:
    json.dump(wl_matrix, f, indent=2)
with open("evaluation/cross_test/baseline_similarity_matrix.json", "w") as f:
    json.dump(bl_matrix, f, indent=2)
with open("evaluation/cross_test/final_similarity_matrix.json", "w") as f:
    json.dump(final, f, indent=2)

print(f"\n{'='*80}")
print(f" Matrices saved to evaluation/cross_test/")
print(f"{'='*80}")
PYEOF

echo ""
echo "================================================================"
echo " CROSS-LANGUAGE TEST COMPLETE"
echo "================================================================"
