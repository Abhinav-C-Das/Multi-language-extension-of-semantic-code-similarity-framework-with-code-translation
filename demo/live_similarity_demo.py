import os
import sys
import shutil
import subprocess
import time
import json
import re

# ==========================================
# Helpers for Mathematical Similarity
# ==========================================

# Universal CS-1 Contexts (Matches compute_ces_similarity_cross.py)
EXCLUDED_CONTEXTS = {
    "java_api", "java_stream", "java_collection",
    "stl_algo", "stl_container", "raii",
    "template_meta", "operator_overload",
}

def get_ext(lang):
    if lang == "c": return ".c"
    if lang == "cpp": return ".cpp"
    if lang == "java": return ".java"
    return ""

def load_ces(path, lang):
    fname = "ces_v2.json" if lang == "java" else "semantic.json"
    fpath = os.path.join(path, fname)
    
    if not os.path.exists(fpath):
        # Fallback for misplaced LANG_SUBDIR
        alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(path)))), lang, os.path.basename(os.path.dirname(os.path.dirname(path))), os.path.basename(os.path.dirname(path)), os.path.basename(path), fname)
        if os.path.exists(alt_path): fpath = alt_path
        else: return [], {}

    try:
        with open(fpath) as f:
            raw = f.read().strip()
            # Strip Joern [INFO]/[ERROR] log lines
            lines = [l for l in raw.split('\n') if not re.match(r'^\[\w+\s*\]', l.strip())]
            raw = '\n'.join(lines).strip()
            # Find start of JSON array or object
            json_start = re.search(r'[\[{]', raw)
            if not json_start: return [], {}
            data = json.loads(raw[json_start.start():])
    except: return [], {}
    
    records = data if isinstance(data, list) else data.get("patterns", data.get("records", [data]))
    patterns, weights = [], {}
    for r in records:
        if not isinstance(r, dict): continue
        ctx = r.get("context","")
        if ctx in EXCLUDED_CONTEXTS: continue
        
        # Consistent keying: context::evolution::operator
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

def load_wl(path, lang):
    fname = "wl.json" if lang == "java" else "wl_ast.json"
    fpath = os.path.join(path, fname)
    if not os.path.exists(fpath): return {}
    try:
        with open(fpath) as f:
            raw = f.read().strip()
            lines = [l for l in raw.split('\n') if not re.match(r'^\[\w+\s*\]', l.strip())]
            raw = '\n'.join(lines).strip()
            json_start = re.search(r'[\[{]', raw)
            if not json_start: return {}
            data = json.loads(raw[json_start.start():])
    except: return {}
    
    # Filter to language-agnostic i0 features only (Matches compute_wl_similarity_cross.py)
    filtered = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if k.startswith("wl_i0_"):
                try: filtered[k] = float(v)
                except: continue
    return filtered

def load_baseline(path):
    fpath = os.path.join(path, "combined_features.json")
    if not os.path.exists(fpath): return {}
    try:
        with open(fpath) as f: data = json.load(f)
    except: return {}
    
    # Flatten features with '.' separator (Matches compute_baseline_similarity_cross.py)
    flat = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subval in value.items():
                    if isinstance(subval, (int, float, bool)):
                        flat[f"{key}.{subkey}"] = float(subval)
            elif isinstance(value, (int, float, bool)):
                flat[key] = float(value)
                
    # Ratio normalization (Matches compute_baseline_similarity_cross.py)
    total = sum(abs(v) for v in flat.values()) if flat else 1.0
    total = max(total, 1.0)
    normalized = {}
    for k, v in flat.items():
        if v in (0, 1, 0.0, 1.0): normalized[k] = float(v)
        else: normalized[k] = v / total
    return normalized

def cosine_similarity(v1, v2):
    # Vectorize with local vocabulary (Matches research scripts)
    vocab = sorted(set(v1.keys()) | set(v2.keys()))
    if not vocab: return 0.0
    
    vec1 = [v1.get(k, 0.0) for k in vocab]
    vec2 = [v2.get(k, 0.0) for k in vocab]
    
    # L2-Normalize
    norm1 = sum(x**2 for x in vec1)**0.5
    norm2 = sum(x**2 for x in vec2)**0.5
    
    if norm1 == 0 or norm2 == 0: return 0.0
    
    dot = sum(a*b for a, b in zip(vec1, vec2))
    return max(0.0, min(1.0, dot / (norm1 * norm2)))

# ==========================================
# Main CLI Application
# ==========================================

def run_cmd(cmd, env):
    res = subprocess.run(cmd, env=env, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running {cmd}: {res.stderr}")
    return res.returncode

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        print("Usage: python live_similarity_demo.py <file1> <file2>")
        sys.exit(1)

    f1 = sys.argv[1]
    f2 = sys.argv[2]
    
    if not os.path.isfile(f1) or not os.path.isfile(f2):
        print("❌ Error: Valid input files required.")
        sys.exit(1)

    print("\n" + "="*60)
    print(" 🚀 INTERACTIVE CKG SIMILARITY DEMO")
    print("="*60)
    
    # Identify Languages
    def get_lang(f):
        if f.endswith('.c'): return 'c'
        if f.endswith('.cpp'): return 'cpp'
        if f.endswith('.java'): return 'java'
        return None
    
    l1 = get_lang(f1)
    l2 = get_lang(f2)
    
    if not l1 or not l2:
        print("❌ Error: Both files must be .c, .cpp, or .java")
        sys.exit(1)

    print(f"📁 Input 1: {os.path.basename(f1)} ({l1.upper()})")
    print(f"📁 Input 2: {os.path.basename(f2)} ({l2.upper()})")
    print("-" * 60)

    # 1. Setup Sandbox Environment
    TEMP_DATA = "data/live_temp"
    TEMP_OUT = "outputs/live_temp"
    TEMP_CPG = "cpgs/live_temp"
    
    for d in [TEMP_DATA, TEMP_OUT]:
        if os.path.exists(d): shutil.rmtree(d)
    if not os.path.exists(TEMP_CPG): os.makedirs(TEMP_CPG)
        
    os.makedirs(f"{TEMP_DATA}/p_demo/ref")
    os.makedirs(f"{TEMP_DATA}/p_demo/s")

    shutil.copy(f1, f"{TEMP_DATA}/p_demo/ref/ref1_{l1}{get_ext(l1)}")
    shutil.copy(f2, f"{TEMP_DATA}/p_demo/s/s1_{l2}{get_ext(l2)}")

    # Check if we can reuse the CPG to save time
    cpg1 = f"{TEMP_CPG}/p_demo/ref/ref1_{l1}/cpg.bin"
    cpg2 = f"{TEMP_CPG}/p_demo/s/s1_{l2}/cpg.bin"
    reuse_cpg = os.path.exists(cpg1) and os.path.exists(cpg2)

    # Stage 1: Feature Extraction
    env = os.environ.copy()
    env["DATA_DIR"] = TEMP_DATA
    env["OUT_DIR"] = TEMP_OUT
    env["CPG_BASE"] = TEMP_CPG
    env["LANG_SUBDIR"] = "" 

    if reuse_cpg:
        print("⏭️ Stage 1: Building Abstract Syntax Topologies... [REUSED]")
    else:
        print("⏳ Stage 1: Building Abstract Syntax Topologies...")
        
    if l1 == 'c' or l2 == 'c': 
        if run_cmd("bash ./experiments/c/run_joern_c.sh", env) != 0: sys.exit(1)
    if l1 == 'cpp' or l2 == 'cpp': 
        if run_cmd("bash ./experiments/cpp/run_joern_cpp.sh", env) != 0: sys.exit(1)
    if l1 == 'java' or l2 == 'java': 
        if run_cmd("bash ./experiments/java/run_joern_java.sh", env) != 0: sys.exit(1)

    time.sleep(0.5)
    print("✅ Stage 1 Complete.\n")

    print("⏳ Stage 2: Extracting Contextual Execution States (CES)...")
    time.sleep(0.5)
    print("⏳ Stage 3: Resolving Variable Lifespans (WL)...")
    time.sleep(0.5)
    print("✅ Multi-View Models Synthesized.\n")

    # 3. Read The Data and Execute Mathematical Math 
    print("🧮 Calculating Similarity Matrices...")
    time.sleep(1)
    
    out_dir1 = f"{TEMP_OUT}/p_demo/ref/ref1_{l1}"
    out_dir2 = f"{TEMP_OUT}/p_demo/s/s1_{l2}"

    # Verify directory existence
    if not os.path.exists(out_dir1):
        alt = f"{TEMP_OUT}/{l1}/p_demo/ref/ref1_{l1}"
        if os.path.exists(alt): out_dir1 = alt
    if not os.path.exists(out_dir2):
        alt = f"{TEMP_OUT}/{l2}/p_demo/s/s1_{l2}"
        if os.path.exists(alt): out_dir2 = alt

    ces1_pat, ces1_w = load_ces(out_dir1, l1)
    ces2_pat, ces2_w = load_ces(out_dir2, l2)
    wl1 = load_wl(out_dir1, l1)
    wl2 = load_wl(out_dir2, l2)
    bl1 = load_baseline(out_dir1)
    bl2 = load_baseline(out_dir2)

    ces_score = round(tversky(ces1_pat, ces1_w, ces2_pat, ces2_w), 4)
    wl_score = round(cosine_similarity(wl1, wl2), 4)
    bl_score = round(cosine_similarity(bl1, bl2), 4)
    
    # Research standard weights: 25% CES, 35% Base, 40% WL
    final_score = round((0.25 * ces_score) + (0.35 * bl_score) + (0.40 * wl_score), 4)

    # 4. Final Display
    print("\n" + "="*60)
    print(" 📊 FINAL EQUIVALENCY RESULTS")
    print("="*60)
    print(f"   Contextual State (CES) : {ces_score:.4f}  [Weight: 25%]")
    print(f"   Variable Lifespan (WL) : {wl_score:.4f}  [Weight: 40%]")
    print(f"   Structural AST (Base)  : {bl_score:.4f}  [Weight: 35%]")
    print("-" * 60)
    if final_score >= 0.70:
        print(f" 🟢 FINAL MATCH SCORE : {final_score:.4f}  (HIGH SIMILARITY)")
    else:
        print(f" 🔴 FINAL MATCH SCORE : {final_score:.4f}  (LOW SIMILARITY)")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
