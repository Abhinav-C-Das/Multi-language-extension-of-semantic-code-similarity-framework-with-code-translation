# Multi-Language Code Similarity Framework

A **language-extensible framework** for detecting semantic code similarity using multi-view Code Property Graphs (CPG). Supports **C, C++, and Java** with cross-language similarity and CPG-based translation.

---

## 🎯 Overview

This project implements four integrated pipelines for code analysis:

| Pipeline | Description | Accuracy |
|---|---|---|
| **C++ Similarity** | Detects similar C++ programs via CPG analysis | 100% (90/90) |
| **Java Similarity** | Detects similar Java programs via CPG analysis | 100% (90/90) |
| **Cross-Language** | Matches semantically equivalent code across C/C++/Java | 98.89% (89/90) |
| **Translation** | Translates programs between C, C++, and Java via CPG | Validated on 10 CS-1 problems |

### Multi-View Approach

Programs are analyzed through **three complementary views**:

- **Baseline (35%)** — Structural graph properties (CFG nodes/edges, AST depth, PDG dependencies)
- **WL (40%)** — Weisfeiler-Lehman graph kernel capturing neighborhood structure patterns
- **CES (25%)** — Computational Expression Semantics detecting algorithmic strategies

---

## 📁 Repository Structure

```
ckg-multiview-code-similarity/
├── README.md                          # This file
├── LICENSE / CITATION.cff             # License and citation
├── requirements.txt                   # Dependencies
├── run_cpp_pipeline.sh                # C++ pipeline executor
├── run_java_pipeline.sh               # Java pipeline executor
├── run_c_pipeline.sh                  # C pipeline executor
├── run_cross_pipeline.sh              # Cross-language pipeline
├── run_cross_test.sh                  # Cross-language test suite
│
├── cpg/scripts/                       # Joern feature extraction (Scala)
│   ├── c/                             #   C: preprocess, structural, semantic, wl, behavioral
│   ├── cpp/                           #   C++: same structure
│   └── java/                          #   Java: same structure
│
├── similarity/                        # Similarity computation (Python)
│   ├── aggregate_baseline.py          #   Baseline aggregation
│   ├── cpp/                           #   C++ similarity scripts
│   ├── java/                          #   Java similarity scripts
│   └── cross/                         #   Cross-language similarity scripts
│
├── evaluation/                        # Accuracy evaluation (Python)
│   ├── calculate_accuracy.py          #   Main accuracy calculator
│   ├── cpp/ / java/ / cross/          #   Per-pipeline evaluation + ablation
│   └── cross_test/                    #   Cross-language test evaluation
│
├── experiments/                       # Pipeline orchestration (Bash)
│   ├── c/ / cpp/ / java/              #   Per-language Joern scripts
│   └── pipeline/                      #   Pipeline step scripts
│
├── data/                              # Input datasets
│   ├── cpp/ / java/                   #   Language-specific problems (p1-p10)
│   ├── cross/                         #   Cross-language problems + ground_truth.json
│   └── cross_test/                    #   Dedicated test data
│
├── translation/                       # CPG-based code translation
│   ├── scripts/                       #   APM extraction, code generators
│   ├── input/ / resources/ / tests/   #   Translation data and tests
│   └── docs/                          #   Translation documentation
│
└── docs/                              # Documentation
    ├── CPP_README.md                  #   C++ pipeline details
    ├── JAVA_README.md                 #   Java pipeline details
    ├── CROSS_LANGUAGE_README.md        #   Cross-language details
    ├── TRANSLATION_README.md          #   Translation details
    ├── INSTRUCTIONS.md                #   Setup instructions
    └── archives/                      #   Internal planning docs
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (standard library only — no pip packages required)
- **Joern 2.x** — [Installation Guide](https://docs.joern.io/installation)
- **Java JDK 11+** (required by Joern)
- **Bash** (WSL on Windows, native on Linux/macOS)

### Running a Pipeline

```bash
# Clone and enter project
git clone https://github.com/Abhinav-C-Das/Multi-Language-Extension-of-Semantic-Code-Similarity-Framework.git
cd ckg-multiview-code-similarity

# Run any single-language pipeline
bash run_java_pipeline.sh     # Java
bash run_cpp_pipeline.sh      # C++

# Run cross-language pipeline
bash run_cross_pipeline.sh
```

Each pipeline:
1. Generates CPGs via Joern
2. Extracts features (Baseline, WL, CES)
3. Computes similarity matrices
4. Aggregates with optimal weights
5. Evaluates accuracy against ground truth

---

## 📊 Sample Outputs

### CES Feature Extraction

For a Java array summation function:
```json
[{"context": "loop_ANY", "variable": "total", "evolution": "ACCUMULATIVE", "operator": "ADD", "importance": 0.7}]
```

For a C find-max function:
```json
[{"context": "loop_ANY", "variable": "max", "evolution": "MAX_UPDATE", "operator": "COMPARE", "importance": 0.8}]
```

### WL Feature Extraction

Graph neighborhood hash counts (iteration 0):
```json
{"wl_i0_BLOCK": 1, "wl_i0_CALL": 8, "wl_i0_CONTROL_STRUCTURE": 1, "wl_i0_IDENTIFIER": 12, "wl_i0_LITERAL": 3, "wl_i0_LOCAL": 3, "wl_i0_METHOD": 1, "wl_i0_METHOD_RETURN": 1, "wl_i0_RETURN": 1}
```

### Similarity Matrix (Cross-Language)

Student `s1_java` against references in all languages:
```
          ref1_c    ref1_cpp    ref1_java    ref2_c    ref2_cpp    ref2_java
s1_java   0.9002    0.9039      0.9817       0.8781    0.8806      0.9215
```
→ Highest match: `ref1_java` (0.9817), but **cross-language ref1_c (0.9002) still scores high** — demonstrating language agnosticism.

### Accuracy Report

```
============================================================
             ACCURACY EVALUATION REPORT
============================================================
  Weights: Baseline=35%, WL=40%, CES=25%
  Correct Predictions: 89/90
  Accuracy: 0.9889 (98.89%)
============================================================
```

### Translation Output

Input (C):
```c
int arraySum(int arr[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) total += arr[i];
    return total;
}
```

Translated (Java):
```java
public static int arraySum(int[] arr, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) { total += arr[i]; }
    return total;
}
```

---

## 🏗️ Architecture

### Three-Phase Development

```
Phase 1: C Foundation       → Core CPG extraction + multi-view similarity
Phase 2: Language Extension  → Java + C++ with language-specific CES patterns
Phase 3: Cross-Language      → 3-way matching + CPG-based translation
```

### How It Works

```
Source Code → Joern → CPG → Feature Extraction → Vectorization → Similarity → Prediction
                            ├── Baseline (35%)
                            ├── WL (40%)
                            └── CES (25%)
```

1. **CPG Generation** — Joern parses source code into a unified Code Property Graph
2. **Feature Extraction** — Joern Scala scripts extract features through 3 views
3. **Similarity Computation** — Python scripts compute pairwise cosine/Tversky similarity
4. **Weighted Aggregation** — Views are combined: `0.35×Baseline + 0.40×WL + 0.25×CES`
5. **Prediction** — Each student program is matched to its most similar reference

---

## 🔬 Multi-View Feature Details

### Baseline Features
Structural graph properties: CFG node/edge counts, AST depth, PDG dependency ratios. Computed as normalized ratio vectors.

### WL (Weisfeiler-Lehman) Features
Iterative graph kernel that captures node type distributions and neighborhood aggregation patterns. Uses iteration 0 (node type counts) for cross-language similarity to avoid language-specific hash explosion.

### CES (Computational Expression Semantics)
Language-agnostic algorithmic pattern detection. Identifies:
- **ACCUMULATIVE** — Loop accumulations (`sum += x`)
- **MAX_UPDATE / MIN_UPDATE** — Conditional extremum tracking
- **CONDITIONAL_SWAP** — Sorting swap patterns
- **NARROWING_WINDOW** — Binary search convergence
- **SEARCH_WITH_RETURN** — Early exit search patterns
- **HEAD_RECURSIVE / TAIL_RECURSIVE** — Recursion strategies

---

## 🛠️ Extending to New Languages

1. Create extraction scripts in `cpg/scripts/{lang}/`
2. Add similarity scripts in `similarity/{lang}/`
3. Create pipeline script `run_{lang}_pipeline.sh`
4. Add test data in `data/{lang}/` with `ground_truth.json`
5. Run pipeline and evaluate accuracy

---

## 📖 Detailed Documentation

| Document | Description |
|---|---|
| [C++ Pipeline](docs/CPP_README.md) | C++ feature extraction and evaluation details |
| [Java Pipeline](docs/JAVA_README.md) | Java feature extraction and evaluation details |
| [Cross-Language](docs/CROSS_LANGUAGE_README.md) | Cross-language matching methodology |
| [Translation](docs/TRANSLATION_README.md) | CPG-based code translation pipeline |
| [Instructions](docs/INSTRUCTIONS.md) | Setup and environment instructions |

---

## 📝 Citation

```bibtex
@software{multiview_code_similarity,
  title={Multi-Language Extension of Semantic Code Similarity Framework},
  author={Abhinav C Das},
  year={2026},
  url={https://github.com/Abhinav-C-Das/Multi-Language-Extension-of-Semantic-Code-Similarity-Framework}
}
```

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Areas: new language extensions, additional feature views, performance optimizations, larger dataset evaluations.

## 🙏 Acknowledgments

- **Joern Team** for the CPG analysis framework
- Research community for foundational work in code similarity detection
