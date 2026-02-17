# Multi-Language Code Similarity Framework

A **language-extensible framework** for detecting semantic code similarity using multi-view Code Property Graphs (CPG), designed to work across C, Java, and C++ with minimal modification.

---

## 🎯 Framework Overview

This project implements a **multi-view code similarity detection framework** that analyzes programs through multiple complementary perspectives:

1. **Baseline** - Structural similarity (CFG, AST, PDG)
2. **WL (Weisfeiler-Lehman)** - Graph kernel-based structural patterns
3. **CES (Computational Expression Semantics)** - Algorithmic strategy patterns
4. **SCDPS** - System call and data flow patterns

### Key Innovation: Language Extensibility

The framework is designed as a **layered architecture** where:
- **Core algorithms** remain language-agnostic
- **Language-specific extensions** add features unique to each language
- **Shared infrastructure** handles CPG generation, feature extraction, and similarity computation

---

## 🏗️ Architecture: Three-Phase Development

### Phase 1: C Language Foundation ✅
**Repository**: Separate C-focused repository

The foundation layer implements:
- Core CPG extraction using Joern
- Multi-view feature extraction (Baseline, WL, CES, SCDPS)
- Similarity computation using cosine/Tversky metrics
- Weighted aggregation and accuracy evaluation

**Validation**: Tested on 400 C programming assignment submissions

### Phase 2: Multi-Language Extensions 🚀
**This Repository**: Java + C++ (planned)

#### Java Extension ✅ COMPLETE
Extends the C foundation with Java-specific features:
- **Object-oriented patterns**: Class hierarchies, inheritance, polymorphism
- **Exception handling**: Try-catch blocks, exception flow
- **Generics and collections**: Type parameterization patterns
- **Concurrency**: Thread synchronization, concurrent data structures
- **Streams and lambdas**: Functional programming constructs

#### C++ Extension ✅ COMPLETE
Extends with C++ features while maintaining framework consistency:
- **Template metaprogramming**: Template specialization, SFINAE patterns
- **RAII patterns**: Resource Acquisition Is Initialization semantics
- **Move semantics**: Rvalue references, perfect forwarding, zero-copy optimization
- **STL algorithms**: Iterator-based computation patterns, functional composition
- **Smart pointers**: Ownership models (unique_ptr, shared_ptr, weak_ptr)
- **CES v3 Enhanced**: Advanced semantic pattern detection with Priority 1-4 fixes

**Both Java and C++ implementations use identical multi-view architecture:**
- Baseline (35%) + WL (40%) + CES (25%) weighted aggregation
- Same CPG extraction pipeline (Joern)
- Same similarity computation methodology
- Language-specific pattern extensions in CES layer

---

## 📊 Multi-View Feature Extraction

### 1. Baseline Features
**What**: Fundamental code graph properties  
**Captured**:
- Control Flow Graph (CFG) metrics
- Abstract Syntax Tree (AST) structure
- Program Dependence Graph (PDG) edges

### 2. Weisfeiler-Lehman (WL) 
**What**: Iterative graph kernel for structural similarity  
**Captured**:
- Node type distributions
- Neighborhood aggregation patterns
- Subgraph isomorphisms

### 3. Computational Expression Semantics (CES)
**What**: High-level algorithmic strategies  
**Captured**:
- Loop patterns (indexed, iterator, stream)
- Data access patterns (sequential, random)
- Accumulation strategies (compound assignment, explicit)
- Control flow strategies (conditional logic, branching)

**Example**: Distinguishes between:
```java
// Pattern A: Indexed loop
for (int i = 0; i < arr.length; i++) sum += arr[i];

// Pattern B: Enhanced for
for (int x : arr) sum = sum + x;

// Pattern C: Functional API
Arrays.stream(arr).sum();
```

### 4. SCDPS (System Call & Data Patterns)
**What**: External interactions and data flow  
**Captured**:
- System call sequences
- I/O patterns
- Data transformation pipelines

---

## 🎓 How It Works

### Step 1: CPG Generation
```
Source Code → Joern → Code Property Graph (CPG)
```
Joern parses source code into a unified CPG representation containing:
- AST nodes
- CFG edges
- PDG dependencies
- Type information
- Data flow

### Step 2: Feature Extraction
For each program, extract features through multiple views:
```
CPG → [Baseline, WL, CES, SCDPS] → Feature Vectors
```

### Step 3: Vectorization & Normalization
```
Features → Global Vocabulary → Dense Vectors → L2 Normalization
```

### Step 4: Similarity Computation
```
Normalized Vectors → Cosine Similarity → Similarity Matrices
```

### Step 5: Weighted Aggregation
```
Multiple Similarity Matrices → Weighted Combination → Final Similarity
```

Default weights:
- Baseline: 35%
- WL: 40%
- CES: 25%

### Step 6: Prediction & Evaluation
```
Final Similarity → Top-1 Prediction → Accuracy vs Ground Truth
```

---

## 📁 Repository Structure

```
ckg-multiview-code-similarity/
├── data/
│   └── java/                          # Java test programs
│       ├── ground_truth.json          # Expected similarity mappings
│       └── p1/                        # Problem 1
│           ├── ref/                   # Reference implementations
│           │   ├── ref1.java         # Reference strategy 1
│           │   └── ref2.java         # Reference strategy 2
│           └── s/                     # Student submissions
│               ├── s1.java           # Student 1
│               ├── s2.java           # Student 2
│               └── s3.java           # Student 3
│
├── cpg/
│   └── scripts/
│       └── java/                      # Java CPG extraction scripts
│           ├── baseline/              # Baseline feature extraction
│           ├── wl/                    # WL feature extraction
│           └── semantic/              # CES feature extraction
│
├── experiments/
│   ├── java/
│   │   └── run_joern_java.sh         # CPG generation for Java
│   └── pipeline/
│       └── java/                      # Java pipeline orchestration
│           ├── run_wl_extract_java.sh
│           ├── run_ces_extract_java.sh
│           └── run_scdps_extract_java.sh
│
├── similarity/
│   └── java/                          # Java similarity computation
│       ├── build_wl_vocab_java.py    # WL vocabulary builder
│       ├── vectorize_wl_java.py      # WL vectorization
│       ├── normalize_wl_java.py      # WL normalization
│       ├── compute_wl_similarity_java.py
│       ├── build_ces_vocab_java.py
│       ├── vectorize_ces_java.py
│       ├── normalize_ces_java.py
│       └── compute_ces_similarity_java.py
│
├── evaluation/
│   └── java/
│       ├── aggregate_all_features_java.py    # Weighted aggregation
│       └── compute_accuracy_weights_java.py   # Accuracy calculation
│
├── outputs/                           # Generated features (gitignored)
├── vectors/                           # Feature vectors (gitignored)
├── cpgs/                              # CPG binaries (gitignored)
├── evaluation/                        # Results (gitignored)
│
├── run_java_pipeline.sh               # Main Java pipeline executor
├── README.md                          # This file
└── JAVA_README.md                     # Java-specific documentation
```

---

## 🚀 Quick Start

### Prerequisites
- **Joern** (CPG extraction): https://joern.io
- **Python 3.8+**
- **Bash/WSL** (for pipeline scripts)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd ckg-multiview-code-similarity

# Install Python dependencies
pip install -r requirements.txt

# Verify Joern installation
joern-parse --version
```

### Running Java Pipeline
```bash
# Execute full pipeline
./run_java_pipeline.sh
```

See [JAVA_README.md](./JAVA_README.md) for detailed Java-specific instructions.

---

## 📈 Results & Validation

### Java Validation (Sample Dataset)
- **Dataset**: 1 problem, 3 students, 2 references
- **Accuracy**: 100% (3/3 correct predictions)
- **Features**: All views (Baseline, WL, CES) working correctly

### Expected Performance (Large-Scale)
Based on C implementation with 400 problems:
- Baseline-only: ~60-70% accuracy
- Multi-view: ~80-90% accuracy
- CES contribution: ~10-15% improvement

---

## 🔬 Research Background

This framework is based on research in:
- **Code Property Graphs**: Unified program representation
- **Multi-view Learning**: Combining complementary perspectives
- **Plagiarism Detection**: Semantic similarity beyond syntax
- **Program Analysis**: Static analysis for education

### Publications

This framework implements research in multi-view code similarity detection using Code Property Graphs. If you use this framework, please cite:

**Journal Papers:**
- *To be added upon publication*

**Conference Papers:**
- *To be added upon publication*

**Related Work:**
- Yamaguchi, F., Golde, N., Arp, D., & Rieck, K. (2014). Modeling and discovering vulnerabilities with code property graphs. In *IEEE Symposium on Security and Privacy*.
- Allamanis, M., Barr, E. T., Devanbu, P., & Sutton, C. (2018). A survey of machine learning for big code and naturalness. *ACM Computing Surveys*, 51(4), 1-37.
- Alon, U., Zilberstein, M., Levy, O., & Yahav, E. (2019). code2vec: Learning distributed representations of code. *Proceedings of the ACM on Programming Languages*, 3(POPL), 1-29.

---

## 🛠️ Extending to New Languages

To add a new language (e.g., Python, Rust):

1. **Create language directory structure**:
   ```bash
   mkdir -p data/{lang} experiments/{lang} similarity/{lang} cpg/scripts/{lang}
   ```

2. **Implement CPG extraction scripts** (Joern Scala):
   - Baseline features: `cpg/scripts/{lang}/baseline/`
   - WL features: `cpg/scripts/{lang}/wl/`
   - CES features: `cpg/scripts/{lang}/semantic/`

3. **Create pipeline scripts**:
   - Feature extraction: `experiments/pipeline/{lang}/`
   - Similarity computation: `similarity/{lang}/`

4. **Add language-specific patterns** to CES:
   - Identify unique idioms (e.g., list comprehensions in Python)
   - Extend CES extraction scripts
   - Test with diverse programs

5. **Validate**:
   - Create ground truth dataset
   - Run pipeline
   - Evaluate accuracy

---

## 📝 Citation

If you use this framework in your research, please cite:

```bibtex
@software{multiview_code_similarity,
  title={Multi-Language Code Similarity Detection Framework},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/ckg-multiview-code-similarity}
}
```

---

## 📜 License

MIT License

Copyright (c) 2026 [Author Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- New language extensions (Python, Rust, Go, etc.)
- Additional feature views
- Performance optimizations
- Evaluation on larger datasets

---

## 📧 Contact

For questions or collaboration:
- **Email**: your.email@example.com
- **Issues**: GitHub Issues tab

---

## 🙏 Acknowledgments

- **Joern Team** for the CPG extraction framework
- **Research Community** for foundational work in code similarity detection
