#!/usr/bin/env python3
"""
verify_translation.py — Compile, run, and compare translated code.

Three verification levels:
  Level 1: Compilation check (gcc/g++/javac)
  Level 2: Output comparison (run both, diff outputs)
  Level 3: Similarity check (optional, requires Joern)

Usage:
  python3 verify_translation.py --source ref1_c.c --generated ref1_generated.java --target-lang java
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def run_cmd(cmd, cwd=None, timeout=30):
    """Run a command and return (return_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)


def compile_source(source_path, lang, output_dir):
    """Compile a source file. Returns (success, executable_path)."""
    basename = os.path.splitext(os.path.basename(source_path))[0]

    if lang == "c":
        exe = os.path.join(output_dir, f"{basename}_exe")
        rc, out, err = run_cmd(f'gcc "{source_path}" -o "{exe}"')
        return rc == 0, exe, err

    elif lang == "cpp":
        exe = os.path.join(output_dir, f"{basename}_exe")
        rc, out, err = run_cmd(f'g++ "{source_path}" -o "{exe}"')
        return rc == 0, exe, err

    elif lang == "java":
        rc, out, err = run_cmd(f'javac "{source_path}"', cwd=output_dir)
        # We need the actual class name, which might not match the basename if we dropped 'public'
        class_name = basename
        import re
        try:
            with open(source_path, "r") as f:
                content = f.read()
                match = re.search(r'class\s+([A-Za-z0-9_]+)', content)
                if match:
                    class_name = match.group(1)
        except Exception:
            pass
        return rc == 0, class_name, err

    return False, "", "Unknown language"

def run_program(path_or_class, lang, cwd=None):
    """Run a compiled program. Returns (success, output)."""
    if lang in ("c", "cpp"):
        rc, out, err = run_cmd(f'"{path_or_class}"', cwd=cwd)
        return rc == 0, out.strip()
    elif lang == "java":
        rc, out, err = run_cmd(f'java {path_or_class}', cwd=cwd)
        return rc == 0, out.strip()
    return False, ""


def detect_lang(filepath):
    """Detect language from file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    return {".c": "c", ".cpp": "cpp", ".cc": "cpp", ".java": "java"}.get(ext, "c")


def verify(source_path, generated_path, target_lang, verbose=False):
    """Run all verification levels."""
    results = {
        "source": source_path,
        "generated": generated_path,
        "target_lang": target_lang,
        "level1_compile": False,
        "level2_output_match": None,
        "compile_error": "",
        "source_output": "",
        "generated_output": "",
    }

    tmpdir = tempfile.mkdtemp(prefix="cpg_trans_verify_")
    source_lang = detect_lang(source_path)

    # -----------------------------------------------
    # Level 1: Compile the generated code
    # -----------------------------------------------
    print(f"[Level 1] Compiling {generated_path}...")

    # Copy generated file to temp dir
    gen_basename = os.path.basename(generated_path)
    gen_copy = os.path.join(tmpdir, gen_basename)
    with open(generated_path, "r") as f:
        content = f.read()
    with open(gen_copy, "w") as f:
        f.write(content)

    gen_ok, gen_exe, gen_err = compile_source(gen_copy, target_lang, tmpdir)
    results["level1_compile"] = gen_ok
    results["compile_error"] = gen_err if not gen_ok else ""

    if gen_ok:
        print(f"  [✓] Generated code compiles")
    else:
        print(f"  [✗] Compilation failed: {gen_err[:200]}")
        return results

    # -----------------------------------------------
    # Level 2: Compare outputs
    # -----------------------------------------------
    print(f"[Level 2] Comparing outputs...")

    # Compile and run source
    src_copy = os.path.join(tmpdir, os.path.basename(source_path))
    with open(source_path, "r") as f:
        src_content = f.read()
    with open(src_copy, "w") as f:
        f.write(src_content)

    src_ok, src_exe, src_err = compile_source(src_copy, source_lang, tmpdir)
    if src_ok:
        src_run_ok, src_output = run_program(src_exe, source_lang, cwd=tmpdir)
        results["source_output"] = src_output

        # Run generated
        gen_run_ok, gen_output = run_program(gen_exe, target_lang, cwd=tmpdir)
        results["generated_output"] = gen_output

        if src_run_ok and gen_run_ok:
            match = src_output == gen_output
            results["level2_output_match"] = match
            if match:
                print(f"  [✓] Outputs match: '{src_output[:50]}'")
            else:
                print(f"  [✗] Output mismatch:")
                print(f"      Source:    '{src_output[:100]}'")
                print(f"      Generated: '{gen_output[:100]}'")
        else:
            print(f"  [⚠] Could not compare outputs (runtime error)")
    else:
        print(f"  [⚠] Could not compile source for comparison")

    return results


def main():
    parser = argparse.ArgumentParser(description="Verify CPG translation")
    parser.add_argument("--source", "-s", required=True, help="Original source file")
    parser.add_argument("--generated", "-g", required=True, help="Generated target file")
    parser.add_argument("--target-lang", "-t", required=True, help="Target language (c/cpp/java)")
    parser.add_argument("--output", "-o", help="Save results JSON to this path")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    results = verify(args.source, args.generated, args.target_lang, args.verbose)

    # Print summary
    print("\n" + "=" * 40)
    print(f" Compile:     {'PASS' if results['level1_compile'] else 'FAIL'}")
    if results["level2_output_match"] is not None:
        print(f" Output:      {'MATCH' if results['level2_output_match'] else 'MISMATCH'}")
    print("=" * 40)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")

    # Exit code
    if results["level1_compile"] and results.get("level2_output_match", True):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
