# Interactive Framework Demonstrations

This directory contains live, interactive scripts allowing researchers to test the CKG Multi-View Code Similarity framework and the APM translation layer in real-time. 

These scripts completely bypass the need to run the massive `.sh` data pipelines located at the root of the repository, allowing you to manually feed in source code and see the underlying algorithmic mathematics and translation outputs directly in your terminal.

## 1. APM Translation Demonstrations

The Abstract Program Model (APM) flattens code syntax and allows zero-shot deterministic translation across C, C++, and Java.

### The Automated 6-Pair Matrix Evaluator
If you want to view a fast, automated test of the translation matrix, run the live evaluator. It will process 3 separate algorithmic problems across all 6 directional language mappings (e.g., C→Java, Java→C++) and print a beautiful compilation and behavioral match status table to your terminal.
```bash
python3 apm_live_demo_evaluator.py
```

### The Interactive Single-File Translator
If you want to translate a single file, use the interactive translator. It takes a source file and a target language (`c`, `cpp`, or `java`).
```bash
# Translates the dummy C file into Java
python3 live_translate_demo.py verbose_mode/inputs/random_code.c java
```
*Note: The generated output code will be safely saved in the same directory as your input file.*

---

## 2. Multi-View Similarity Demonstrations

This script allows you to mathematically compare two source code files (even if they are written in different languages) to see if they execute the same algorithmic logic.

```bash
# Compares a C file against a Java file
python3 live_similarity_demo.py verbose_mode/inputs/demo_student.c verbose_mode/inputs/demo_reference.java
```
**What happens behind the scenes?**
The script utilizes Joern to generate Code Property Graphs for both inputs. It then extracts the three structural views: Contextual Execution States (CES), Variable Lifespans (WL), and Topological ASTs (Baseline). Finally, it computes the final weighted score (25% CES, 40% WL, 35% Base).

---

## 3. The `verbose_mode/` Directory

If you are presenting this framework live, or you want to see exactly what the algorithms are processing, use the scripts located in the `verbose_mode/` directory.

These scripts perform the exact same mathematical and translational logic as the standard demos, but they will actively **print the raw source code** and **generated target code** directly to your terminal so you can visually verify the semantic mappings side-by-side.

*   **Verbose Similarity:** `python3 verbose_mode/verbose_similarity_demo.py <file1> <file2>`
*   **Verbose Translation:** `python3 verbose_mode/verbose_translate_demo.py <file> <target_lang>`
*(Dummy input files for testing are safely stored in `verbose_mode/inputs/`)*
