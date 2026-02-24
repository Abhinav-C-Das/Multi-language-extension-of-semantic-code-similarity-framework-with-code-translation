# Translation Verification Workflow

## End-to-End Pipeline (e.g., `factorial.c → Java`)

### Step 1: CPG Generation
```
joern-parse factorial.c --output factorial_cpg.bin
```
- **Input:** Source file (`factorial.c`)
- **Output:** Code Property Graph binary (`factorial_cpg.bin`)
- Joern parses the source code into a graph representation containing AST, CFG, and PDG

### Step 2: APM Extraction
```
joern --script extract_apm.sc (on the CPG)
```
- **Input:** `factorial_cpg.bin`
- **Output:** `factorial_apm.json` (Abstract Program Model)
- Walks the CPG and extracts every:
  - Function name, return type, parameters (with roles like `ARRAY_SIZE`)
  - Statement (`DECLARE`, `ASSIGN`, `FOR_LOOP`, `WHILE_LOOP`, `IF`, `RETURN`)
  - Expression (`BINARY_OP`, `CALL_EXPR`, `LITERAL`, `IDENTIFIER`, `ARRAY_ACCESS`)
  - I/O call (`printf` → `PRINT` with format string + typed arguments)

### Step 3: Code Generation
```
python3 generate_java.py factorial_apm.json --output factorial_generated.java
```
- **Input:** `factorial_apm.json` + target language (`java`)
- **Output:** `factorial_generated.java`
- Language-specific adaptations:
  - **C → Java:** `int arr[]` → `int[] arr`, `printf` → `System.out.println`, class wrapper
  - **C → C++:** `printf` → `std::cout <<`, `#include <stdio.h>` → `#include <iostream>`
  - **Java → C:** `arr.length` → explicit `int n` parameter, `System.out.println` → `printf`
  - **Java → C++:** Same as Java→C but with `std::cout` instead of `printf`

### Step 4: Verification (`verify_translation.py`)

#### Level 1 — Compilation Check
```
javac factorial_generated.java
```
- Compiles the generated code using the target language compiler (`gcc` / `g++` / `javac`)
- **PASS:** Exit code = 0 (compiles without errors)
- **FAIL:** Exit code ≠ 0 (show compiler error message)

#### Level 2 — Output Comparison
```
1. gcc factorial.c -o factorial_exe        # Compile ORIGINAL
2. ./factorial_exe                          # Run ORIGINAL → "Factorial of 5 is 120"
3. java Factorial                           # Run GENERATED → "Factorial of 5 is 120"
4. original_output == generated_output ?    # Exact string comparison
```
- **MATCH:** Both programs produce identical stdout output → ✅
- **MISMATCH:** Outputs differ → ❌

## Concrete Example

```
factorial.c                      factorial_generated.java
─────────────                    ────────────────────────
gcc → ./a.out                    javac → java Factorial
     ↓                                ↓
"Factorial of 5 is 120"    ==   "Factorial of 5 is 120"
                            ↓
                      EXACT STRING MATCH → ✅ PASS
```

## Test Suite Execution

```bash
rm -rf cpg_t1/outputs/*
bash cpg_t1/scripts/run_custom_tests.sh
```

This runs all 9 source files × 2 target languages = **18 translation directions**, reporting compile status and output match for each.

## Current Results (18/18 ✅)

| Source | → C | → C++ | → Java |
|--------|-----|-------|--------|
| `factorial.c` | — | ✅ | ✅ |
| `is_prime.c` | — | ✅ | ✅ |
| `sum_array.c` | — | ✅ | ✅ |
| `bubble_sort.cpp` | ✅ | — | ✅ |
| `fibonacci.cpp` | ✅ | — | ✅ |
| `reverse_integer.cpp` | ✅ | — | ✅ |
| `MaxElement.java` | ✅ | ✅ | — |
| `SumOfDigits.java` | ✅ | ✅ | — |
| `VowelCounter.java` | ✅ | ✅ | — |
