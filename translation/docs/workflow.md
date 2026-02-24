# CPG Translation Module (`cpg_t1`) Workflow

The `cpg_t1` module represents the core translation logic mapping source code from one language to another (C, C++, Java) at the Abstract Program Model (APM) level using Code Property Graphs (CPGs).

This document explains the step-by-step workflow, intermediate files generated, and how verification is performed.

## 1. Single-File Translation Workflow (`run_translation.sh`)

When translating a single file via `cpg_t1/run_translation.sh <source_file> <target_lang> [output_dir]`, the system performs the following 4 stages:

### Stage 1: CPG Generation
- **What it does**: Reads the raw original source code and uses `joern-parse` to construct a language-specific Code Property Graph.
- **Output File**: `<output_dir>/<basename>_cpg.bin`
- **Why**: The CPG serves as the unified graph representation containing AST, control flow, and data flow.

### Stage 2: APM Extraction
- **What it does**: Joern runs a Scala script (`cpg_t1/extract_apm.sc`) against the generated CPG. It walks the syntax trees and control flows, abstracting away language-specific quirks (like array lengths or specific IO syntaxes) into a language-neutral format called the Abstract Program Model (APM).
- **Core Output File**: `<output_dir>/<basename>_apm.json`
- **Secondary Logs**: `<output_dir>/apm_raw.out` and `<output_dir>/apm_err.log`

### Stage 3: Target Code Generation
- **What it does**: A python generator specific to the target language (`generate_c.py`, `generate_cpp.py`, or `generate_java.py`) reads the `apm.json`. These scripts subclass `codegen_base.py`. They iterate over APM declarations, statements, and expressions to output valid, idiomatic code for the target language.
- **Output File**: `<output_dir>/<basename>_generated.<ext>` (e.g., `_generated.java`)

### Stage 4: Verification (Level 1 - Compilation)
- **What it does**: Immediately validates the generated code by attempting to compile it using standard compilers (`gcc`, `g++`, or `javac`).
- **Output**: The compiler output is logged. If successful an executable or `.class` file is left in the target directory (e.g., `<basename>_gen`).

---

## 2. Batch Translation Workflow (`run_all_translations.sh`)

This script loops over the entire cross-language dataset natively, testing the robustness of the APM logic across all language permutations:
- **What it does**: Iterates through `data/cross/p*` across all roles (`ref`, `s`) and triggers `run_translation.sh` for every permissible translation direction (e.g. `C -> Java, C++`, `Java -> C, C++`).
- **Outputs**:
  - Populates `cpg_t1/output/<problem>/<role>/src_to_target/` with all the intermediate assets (`cpg.bin`, `apm.json`, generated code, compiler logs).
  - Writes a final consolidated JSON list: `cpg_t1/output/translation_results.json`. This tracks the `<problem>`, `<source>`, `<target>`, and the `PASS/FAIL` boolean reflecting compilation success.

---

## 3. Advanced Verification Workflow (`verify_translation.py`)

A distinct Python utility reserved for high-fidelity confirmation of the translation.
- **Level 1 (Compile)**: Checks if the generated code parses and compiles securely.
- **Level 2 (Output Match)**: Actually executes *both* the original source logic and the generated target logic in a sandboxed temporary directory. It strictly diffs the stdout of both processes. If outputs match verbatim, the translation is determined to be 100% behaviorally accurate.
