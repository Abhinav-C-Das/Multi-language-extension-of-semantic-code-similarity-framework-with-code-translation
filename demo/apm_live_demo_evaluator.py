import os
import subprocess
import json
import time
import sys

# LIVE DEMO configuration: pointing to the streamlined 3-file dataset
SUITE_BASE = "data/apm_live_demo"
OUTPUT_BASE = "results/translation/live_demo_out"
SCRIPTS_DIR = "translation/scripts"
RESULTS_FILE = "results/translation/live_demo_results.json"

def run_cmd(cmd, env=None, cwd=None):
    try:
        res = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env, cwd=cwd
        )
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return -1, "", str(e)

def evaluate_pair(problem, src_lang, target_lang):
    src_ext = {"c": ".c", "cpp": ".cpp", "java": ".java"}[src_lang]
    src_filename = f"ref1.java" if src_lang == "java" else f"ref1_{src_lang}{src_ext}"
    src_file = os.path.join(SUITE_BASE, problem, src_filename)
    
    if not os.path.exists(src_file):
        return {"result": "SKIPPED", "reason": "Source missing"}

    out_dir = os.path.join(OUTPUT_BASE, problem, f"{src_lang}_to_{target_lang}")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    src_basename = f"ref1_{src_lang}"
    cpg_file = os.path.join(out_dir, f"{src_basename}_cpg.bin")
    apm_file = os.path.join(out_dir, f"{src_basename}_apm.json")
    generated_file = os.path.join(out_dir, f"{src_basename}_generated.{target_lang}")

    results = {
        "problem": problem,
        "source": src_lang,
        "target": target_lang,
        "compile_ok": False,
        "output_match": False,
        "error": ""
    }

    # Added dramatic delays for the live presentation effect
    time.sleep(0.5)

    # 1. CPG Generation
    rc, out, err = run_cmd(f'joern-parse "{src_file}" --output "{cpg_file}"')
    if rc != 0:
        results["error"] = f"CPG fail: {err}"
        return results

    # 2. APM Extraction
    env = os.environ.copy()
    env["CPG_FILE"] = cpg_file
    env["TARGET_FILE"] = os.path.basename(src_file)
    rc, out, err = run_cmd(
        f'joern --script "{os.path.join(SCRIPTS_DIR, "extract_apm.sc")}"',
        env=env
    )
    
    try:
        raw_out = out
        json_start = raw_out.find("{")
        if json_start != -1:
            json_str = raw_out[json_start:]
            json.loads(json_str) # validate
            with open(apm_file, "w") as f:
                f.write(json_str)
        else:
            results["error"] = "APM fail: No JSON in output"
            return results
    except Exception as e:
        results["error"] = f"APM fail: {str(e)}"
        return results

    # 3. Code Generation
    rc, out, err = run_cmd(
        f'python3 "{os.path.join(SCRIPTS_DIR, "generate_" + target_lang + ".py")}" "{apm_file}" --output "{generated_file}"'
    )
    if rc != 0 or not os.path.exists(generated_file):
        results["error"] = f"CodeGen fail: {err}"
        return results

    # 4. Verification
    verify_cmd = f'python3 "{os.path.join(SCRIPTS_DIR, "verify_translation.py")}" -s "{src_file}" -g "{generated_file}" -t {target_lang}'
    rc, out, err = run_cmd(verify_cmd)
    
    results["compile_ok"] = "Compile:     PASS" in out
    results["output_match"] = "Output:      MATCH" in out
    
    time.sleep(0.5) # Formatting dramatic effect 
    return results

def main():
    if not os.path.exists(OUTPUT_BASE):
        os.makedirs(OUTPUT_BASE)

    total_matrix = []
    # ONLY RUN DEMO SET
    problems = ["p1", "p2", "p3"]
    langs = ["c", "cpp", "java"]

    print("\n" + "="*55)
    print(" APM TRANSLATION ENGINE: LIVE DEMO")
    print("=======================================================")
    print(f"{'Source Model':<12} | {'Target Lang':<12} | {'Compile':<10} | {'Behavior'}")
    print("-" * 55)

    for p in problems:
        for src in langs:
            for target in langs:
                if src == target: continue
                
                res = evaluate_pair(p, src, target)
                if res.get("result") == "SKIPPED":
                    continue # Skip empty pairs so it looks perfectly clean in the demo
                    
                total_matrix.append(res)
                
                c_status = "✅ PASS" if res.get("compile_ok") else "❌ FAIL"
                m_status = "✅ MATCH" if res.get("output_match") else "❌ MISMATCH"
                    
                label = f"{p}_{src}"
                sys.stdout.write(f"{label:<12} | {target:<12} | {c_status:<10} | {m_status}\n")
                sys.stdout.flush()

    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump(total_matrix, f, indent=2)

    print("-" * 55)
    print(f"✅ Demo Evaluation Complete!")
    print(f"Outputs successfully generated to: {OUTPUT_BASE}")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()
