import os
import subprocess
import json
import time

SUITE_BASE = "data/apm_evaluation_suite"
OUTPUT_BASE = "translation/output/apm_v2_eval"
SCRIPTS_DIR = "translation/scripts"
RESULTS_FILE = "translation/output/apm_final_evaluation_results.json"

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
        "cpg_gen": False,
        "apm_extract": False,
        "code_gen": False,
        "compile_ok": False,
        "output_match": False,
        "error": ""
    }

    # 1. CPG Generation
    rc, out, err = run_cmd(f'joern-parse "{src_file}" --output "{cpg_file}"')
    if rc != 0:
        results["error"] = f"CPG fail: {err}"
        return results
    results["cpg_gen"] = True

    # 2. APM Extraction
    env = os.environ.copy()
    env["CPG_FILE"] = cpg_file
    env["TARGET_FILE"] = os.path.basename(src_file)
    
    # Run joern script
    rc, out, err = run_cmd(
        f'joern --script "{os.path.join(SCRIPTS_DIR, "extract_apm.sc")}"',
        env=env
    )
    
    # Extract JSON content from stdout
    try:
        raw_out = out
        json_start = raw_out.find("{")
        if json_start != -1:
            json_str = raw_out[json_start:]
            # Validate JSON
            json.loads(json_str)
            with open(apm_file, "w") as f:
                f.write(json_str)
            results["apm_extract"] = True
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
    results["code_gen"] = True

    # 4. Verification (Level 1 & 2)
    verify_cmd = f'python3 "{os.path.join(SCRIPTS_DIR, "verify_translation.py")}" -s "{src_file}" -g "{generated_file}" -t {target_lang}'
    rc, out, err = run_cmd(verify_cmd)
    
    # verify_translation returns 0 on success, 1 on fail (printed to stdout)
    results["compile_ok"] = "Compile:     PASS" in out
    results["output_match"] = "Output:      MATCH" in out
    
    if not results["compile_ok"]:
        results["error"] = "Compile failed"
    elif not results["output_match"]:
        results["error"] = "Output mismatch"

    return results

def main():
    if not os.path.exists(OUTPUT_BASE):
        os.makedirs(OUTPUT_BASE)

    total_matrix = []
    problems = [f"p{i}" for i in range(1, 21)]
    langs = ["c", "cpp", "java"]

    start_time = time.time()
    
    print(f"{'Problem':<10} | {'Pair':<15} | {'Compile':<10} | {'Match':<10}", flush=True)
    print("-" * 55, flush=True)

    for p in problems:
        for src in langs:
            for target in langs:
                if src == target: continue
                
                res = evaluate_pair(p, src, target)
                total_matrix.append(res)
                
                c_status = "PASS" if res.get("compile_ok") else "FAIL"
                m_status = "MATCH" if res.get("output_match") else "MISMATCH"
                if res.get("result") == "SKIPPED":
                    c_status = "SKIP"
                    m_status = "SKIP"
                    
                print(f"{p:<10} | {src + ' -> ' + target:<15} | {c_status:<10} | {m_status:<10}", flush=True)

    duration = time.time() - start_time
    
    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump(total_matrix, f, indent=2)

    print("\n" + "="*55, flush=True)
    print(f"Evaluation Complete in {duration:.2f}s", flush=True)
    print(f"Results saved to: {RESULTS_FILE}", flush=True)
    print("="*55, flush=True)

if __name__ == "__main__":
    main()
