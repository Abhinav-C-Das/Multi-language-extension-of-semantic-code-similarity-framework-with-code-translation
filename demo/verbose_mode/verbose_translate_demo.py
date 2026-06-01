import os
import sys
import shutil
import subprocess
import time
import json

def run_cmd(cmd, env=None):
    try:
        res = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env
        )
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return -1, "", str(e)

def main():
    if len(sys.argv) < 3:
        print("Usage: python verbose_translate_demo.py <input_file> <target_language>")
        print("Example: python verbose_translate_demo.py live_input_translation/random_code.c java")
        sys.exit(1)

    src_file = sys.argv[1]
    target_lang = sys.argv[2].lower()
    
    if not os.path.exists(src_file):
        print(f"❌ Error: File not found: {src_file}")
        sys.exit(1)
        
    if target_lang not in ["c", "cpp", "java"]:
        print("❌ Error: Target language must be 'c', 'cpp', or 'java'")
        sys.exit(1)

    print("\n" + "="*60)
    print(" 🚀 INTERACTIVE FRAMEWORK: APM CODE TRANSLATION (VERBOSE)")
    print("="*60)
    print(f"📁 Source Model  : {os.path.basename(src_file)}")
    print(f"🎯 Target Target : {target_lang.upper()}")
    print("-" * 60)

    TEMP_OUT = "outputs/live_translate_temp"
    SCRIPTS_DIR = "translation/scripts"
    
    if os.path.exists(TEMP_OUT):
        shutil.rmtree(TEMP_OUT)
    os.makedirs(TEMP_OUT)

    src_basename = os.path.basename(src_file).split('.')[0]
    src_dir = os.path.dirname(src_file)
    
    cpg_file = os.path.join(TEMP_OUT, f"{src_basename}_cpg.bin")
    apm_file = os.path.join(TEMP_OUT, f"{src_basename}_apm.json")
    
    generated_file = os.path.join(src_dir, f"{src_basename}_generated.{target_lang}")

    time.sleep(0.5)
    print("⏳ Stage 1: Parsing Abstract Code Property Graph...")
    
    rc, out, err = run_cmd(f'joern-parse "{src_file}" --output "{cpg_file}"')
    if rc != 0:
        print(f"❌ CPG Build Failed: {err}")
        sys.exit(1)
    
    time.sleep(0.5)
    print("⏳ Stage 2: Extracting Abstract Program Schema (APM)...")
    
    env = os.environ.copy()
    env["CPG_FILE"] = cpg_file
    env["TARGET_FILE"] = os.path.basename(src_file)
    rc, out, err = run_cmd(f'joern --script "{os.path.join(SCRIPTS_DIR, "extract_apm.sc")}"', env=env)
    
    raw_out = out
    json_start = raw_out.find("{")
    if json_start != -1:
        json_str = raw_out[json_start:]
        with open(apm_file, "w") as f:
            f.write(json_str)
    else:
        print("❌ APM Extraction Failed: No JSON returned.")
        sys.exit(1)

    time.sleep(0.5)
    print(f"⏳ Stage 3: Synthesizing {target_lang.upper()} Language Output...")
    
    rc, out, err = run_cmd(f'python3 "{os.path.join(SCRIPTS_DIR, "generate_" + target_lang + ".py")}" "{apm_file}" --output "{generated_file}"')
    if rc != 0 or not os.path.exists(generated_file):
        print(f"❌ Code Generation Failed: {err}")
        sys.exit(1)
        
    time.sleep(0.5)
    print("⏳ Stage 4: Verifying Compilation and I/O Behavior...")
    
    verify_cmd = f'python3 "{os.path.join(SCRIPTS_DIR, "verify_translation.py")}" -s "{src_file}" -g "{generated_file}" -t {target_lang}'
    rc, out, err = run_cmd(verify_cmd)
    
    compile_ok = "Compile:     PASS" in out
    output_match = "Output:      MATCH" in out

    c_status = "✅ PASS" if compile_ok else "❌ FAIL"
    m_status = "✅ MATCH" if output_match else "❌ MISMATCH"

    time.sleep(0.5)
    print("✅ Translation Pipeline Complete.\n")

    # Final Display!
    print("="*60)
    print(f" 📄 ORIGINAL SOURCE CODE ({os.path.basename(src_file)}):")
    print("="*60)
    with open(src_file, 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read().strip())

    print("\n" + "="*60)
    print(f" 🌟 GENERATED {target_lang.upper()} CODE:")
    print("="*60)
    
    with open(generated_file, 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read().strip())
        
    print("\n" + "="*60)
    print(" 🛠️ VERIFICATION BENCHMARK:")
    print("="*60)
    print(f"   Compilation Integrity  : {c_status}")
    print(f"   I/O Behavioral Match   : {m_status}")
    print("="*60 + "\n")
    
    print(f"Tip: The new code is located right next to your input: {generated_file}")

if __name__ == "__main__":
    main()
