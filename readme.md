# An Interpretable Deterministic Framework for Cross-Language Educational Code Similarity Using Code Property Graphs

<div align="center">
  <img src="assets/architecture1.png" alt="Multi-View Architecture Diagram" width="850">
</div>

## 📌 Overview

This repository contains the official implementation of the **CKG (Code Property Graph) Multi-View Code Similarity Framework**. This framework provides a high-fidelity, syntax-agnostic compiler-level abstraction capable of evaluating syntactic, semantic, and structural equivalencies across fundamentally diverse programming languages (C, C++, Java).

In addition to multi-view similarity evaluation, this repository introduces the **Abstract Program Model (APM)**—a zero-shot code translation and routing layer. The APM generates functionally equivalent source code across languages derived directly from deeply extracted semantic states, rather than relying on brittle raw syntax tree transformations or stochastic large language models.

---

## 🏆 Key Contributions & Empirical Findings

Our framework has been rigorously evaluated on a comprehensive **400-program dataset** ($N=400$, CS-1 algorithmic standards covering C, C++, and Java across 20 distinct problem domains).

### 1. Multi-View Fusion vs. Standalone Views ($N=400$ Hard-Filtering)
Evaluating standalone views against our late-fusion architecture ($w_{\text{BL}}=0.35, w_{\text{WL}}=0.40, w_{\text{CES}}=0.25$) confirms significant performance gains:

| Evaluation Setting | Top-1 Accuracy | 95% Wilson CI |
| :--- | :---: | :---: |
| **BL-only View** (Lexical TF-IDF) | 79.50% | [75.35%, 83.11%] |
| **WL-only View** (Structural Graph Kernel) | 71.68% | [67.07%, 75.88%] |
| **CES-only View** (Semantic Signatures) | 72.68% | [68.11%, 76.82%] |
| **Proposed Fused Framework (Full Corpus, N=400)** | **87.25%** | **[83.60%, 90.20%]** |
| **Proposed Fused Framework (Core Directions, n=386)** | **88.60%** | **[85.04%, 91.46%]** |
| **Java $\rightarrow$ C/C++ Cross-Frontend Direction (n=140)** | **91.43%** | **[85.61%, 95.04%]** |

Late fusion achieves a statistically significant **+7.75 pp gain** over the strongest standalone view (McNemar $p < 0.0001$, Odds Ratio $= 4.875$).

### 2. Neural Baseline Comparisons
The framework was empirically stress-tested against industry-standard pretrained neural models on the identical 400-program dataset under hard-cross filtering:
*   **JPlag / MOSS:** 51.50% / 54.20% (Non-semantic baseline lower bounds).
*   **GraphCodeBERT / CodeBERT (Zero-Shot):** 58.90% / 59.50% (CLS-token cosine similarity).
*   **CodeBERT (Fine-Tuned, n=80):** 66.25% [55.36%, 75.65%].
*   **UniXcoder (Zero-Shot / Fine-Tuned, n=80):** 68.92% / 71.37% [62.15%, 79.12%].
*   **Proposed Symbolic Framework:** **87.25%** (Zero-shot, gradient-free, requiring no GPUs or labeled fine-tuning data).

---

## 🔬 Core Technologies & Pipeline

The framework computes code similarity and translation via three weighted, interdependent algorithmic views evaluated locally via Joern Code Property Graphs (`cpg/`):

1.  **Baseline Path & Structural Similarity (35% Weight):** Standard AST (Abstract Syntax Tree) and CDG (Control Dependency Graph) metrics capturing the topological code flow.
2.  **Variable Lifespan (WL) Tracking (40% Weight):** Syntactically mapping variable declarations, structural mutations, and memory footprints regardless of localized naming conventions.
3.  **Contextual Execution State (CES) Tracing (25% Weight):** Tracking dynamic execution hierarchies (e.g., standard `for/while` loops vs. unrolled `if` jumps using `goto`).

### The APM Translation Module
Located in the `translation/` directory, the APM system intercepts standard CPG logic and flattens cross-language structural paradigms (e.g., resolving Java's OOP wrapper bounds against C's raw `malloc` procedural bounds). 
*   **Schema Map:** Standardized in `translation/resources/apm_schema.json`
*   **Code Generation:** Dedicated generation pipelines (`generate_cpp.py`, `generate_java.py`, `generate_c.py`) capable of mapping APM states back to highly accurate compilable code.

---

## 🚀 Live Interactive Demo

We have included interactive demonstration scripts in the `demo/` directory to allow researchers to test the multi-view similarity and APM translation locally:

1.  **Live Similarity Demo (`demo/live_similarity_demo.py`):**
    Input two source files (even in different languages) to compute the weighted similarity across the Baseline, WL, and CES matrices.
2.  **Live APM Translation (`demo/live_translate_demo.py`):**
    Input a source file and specify a target language (C, C++, or Java). The tool extracts the CPG, flattens it to an APM representation, and compiles the translated output.
3.  **APM Search & Indexing (`demo/search_apm.py`):**
    Query the internal APM structure map directly for specific algorithmic patterns.

---

## 📊 Dataset and Reproducibility

### The Evaluation Results (`results/`)
All mathematical outcomes, similarity matrices, and empirical logs generated for our publication are maintained immutably in the `results/` folder.
*   `results/cpp/`, `results/java/`, `results/cross/` — The complete single and cross-language aggregated similarity matrices predicting accurate algorithmic mappings.
*   `results/baselines/` — The empirical `.json` results from our neural baseline comparisons (CodeBERT, GraphCodeBERT, UniXCoder).
*   `results/translation/` — Comprehensive logs verifying compilation integrity and input-output matches for the 120-pair APM translation matrix.

### Reconstructing the Source Dataset (`data/`)
> [!IMPORTANT]
> For dataset preservation, privacy, and space concerns, the massive raw source code repository and intermediate components (`data/`) are strictly excluded via `.gitignore`. 

If you are expanding on this codebase locally and wish to run the `.sh` evaluation pipelines, you **must recreate the `data/` directory structure** at the root of the project. The framework expects the following hierarchy for evaluation:

```text
data/
 ├── c/
 │    └── p1/
 │         ├── ref/
 │         │    └── ref1_c.c
 │         └── s/
 │              ├── s1_c.c
 │              └── s2_c.c
 ├── cpp/
 └── java/
```
*(Where `p1` represents the algorithmic problem bucket, `ref` contains the baseline reference solutions, and `s` contains the student/target implementations to be evaluated).*

---

## 💻 Building and Execution



### Requirements
Refer to the `requirements.txt` to align module distributions for the Python evaluators and Joern environments. Ensure Joern is properly installed and globally accessible via the CLI.

```bash
pip install -r requirements.txt
```

### Reproducing Full-Scale Evaluation Pipelines

While the `demo/` folder allows for quick, interactive testing, the root directory contains the massive, automated shell scripts (`.sh`) designed to process and evaluate the entire dataset (e.g., the N=400 algorithmic repository) all at once.

If you have onboarded the full `data/` structure locally, you can execute these pipelines. Each script sequentially handles CPG extraction, Contextual Execution State (CES) tracing, Variable Lifespan (WL) tracking, and mathematical similarity scoring for its respective domain:

1.  **`./run_c_pipeline.sh`**: Executes the full extraction and similarity evaluation specifically for the C language dataset.
2.  **`./run_cpp_pipeline.sh`**: Executes the full extraction and baseline comparison suite for C++ paradigms.
3.  **`./run_java_pipeline.sh`**: Executes the Java-specific pipeline, handling complex Object-Oriented CES discrepancies.
4.  **`./run_cross_pipeline.sh`**: The ultimate multi-language pipeline. This script cross-references and evaluates equivalencies *between* languages (e.g., C vs. Java) using the 25/35/40 weighted multi-view algorithm.
5.  **`./run_cross_test.sh`**: A smaller, highly constrained subset of the cross-pipeline meant for rapid integrity testing before running the massive `run_cross_pipeline.sh`.

Accuracy and aggregated weighted values from these massive runs are automatically validated using explicitly constrained evaluation scripts located in `evaluation/`.
