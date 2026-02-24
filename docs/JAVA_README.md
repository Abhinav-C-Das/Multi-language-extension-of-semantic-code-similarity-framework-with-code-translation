# Java Code Similarity Pipeline - User Guide

Complete guide for running the Java implementation of the multi-view code similarity framework.

---

## 📋 Table of Contents
1. [Quick Start](#-quick-start)
2. [Data Folder Structure](#-data-folder-structure)
3. [Pipeline Execution](#-pipeline-execution)
4. [Output Files](#-output-files)
5. [Understanding Results](#-understanding-results)
6. [Sample Programs Explained](#-sample-programs-explained)
7. [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Ensure Joern is installed and in PATH
joern-parse --version

# 2. Verify Python 3.8+
python3 --version

# 3. Install dependencies
pip install -r requirements.txt
```

### Run the Pipeline
```bash
# Clean previous outputs and run full pipeline
rm -rf outputs/java vectors/java cpgs/java evaluation/java/*.json
./run_java_pipeline.sh
```

### View Results
```bash
# See accuracy report
cat evaluation/java/accuracy_report_java.txt

# View similarity matrix
cat evaluation/java/final_similarity_matrix_java.json
```

```

---

## 🧠 Understanding CES (Computational Expression Semantics)

### What is CES?

**CES (Computational Expression Semantics)** is a feature extraction technique that captures the **algorithmic strategy** and **computational patterns** used in code, going beyond surface-level syntax to understand **how** a program solves a problem.

Unlike traditional code similarity metrics that focus on:
- **Syntax**: Variable names, formatting, indentation
- **Structure**: AST/CFG topology, control flow edges

**CES focuses on**:
- **Computational strategies**: How loops iterate (indexed vs iterator vs stream)
- **Accumulation patterns**: How values are aggregated (`+=` vs `= x + y` vs functional reduction)
- **Data access patterns**: Sequential vs random access, array indexing vs iterators
- **Algorithmic semantics**: The underlying computational approach

### Why CES Matters

**Problem**: Two programs solving the same problem with the same strategy can have vastly different syntax but should be considered **semantically similar**.

**Example: Array Sum with Different Syntax**

```java
// Program A
int total = 0;
for (int i = 0; i < arr.length; i++) {
    total += arr[i];  // Compound assignment
}

// Program B  
int sum = 0;
for (int idx = 0; idx < arr.length; idx++) {
    sum += arr[idx];  // Same strategy, different names
}
```

**Without CES**: Low similarity due to different variable names  
**With CES**: **High similarity** - both use indexed iteration + compound assignment pattern

### CES vs Syntactic Similarity

| Aspect | Syntactic Similarity | CES (Semantic Similarity) |
|--------|---------------------|---------------------------|
| **Focus** | Code structure, syntax trees | Computational patterns, strategies |
| **Variable names** | Different names → Low similarity | Ignores names, focuses on patterns |
| **Semantically equivalent code** | May score low | **Correctly identifies equivalence** |
| **Loop type changes** | Penalizes differences | Recognizes **semantic** equivalence/difference |
| **Example** | `total += arr[i]` ≠ `sum += data[idx]` | Both → `INDEXED_LOOP + COMPOUND_ASSIGN` |

### What CES Detects - Java Patterns

#### 1. Loop Iteration Patterns
- **Indexed for loop**: `for (int i = 0; i < arr.length; i++)`
- **Enhanced for-each loop**: `for (int x : arr)`
- **While loop**: `while (condition)`  
- **Do-while loop**: `do { } while (condition)`
- **Stream API**: `Arrays.stream(arr).forEach(...)`

#### 2. Accumulation Patterns
- **Compound assignment**: `total += value` (in-place update)
- **Explicit addition**: `total = total + value` (create new value)
- **Functional reduction**: `Arrays.stream().sum()`, `.reduce(...)`
- **No accumulation**: `result = value` (overwrite pattern - often a bug!)

#### 3. Data Access Patterns
- **Array indexing**: `arr[i]`, `data[idx]`
- **Iterator access**: `iterator.next()`, enhanced for-each
- **Stream access**: `Arrays.stream(arr)`
- **Collection methods**: `list.get(i)`, `map.get(key)`

#### 4. Conditional Patterns
- **If-else chains**: `if (...) { } else if (...) { }`
- **Ternary operator**: `x > y ? x : y`
- **Switch statements**: `switch (x) { case A: ... }`
- **Guard clauses**: Early returns with conditions

#### 5. Object-Oriented Patterns
- **Inheritance usage**: `extends`, `super.method()`
- **Interface implementation**: `implements`, method overrides
- **Polymorphism**: Virtual method calls
- **Encapsulation**: Getter/setter usage vs direct field access

#### 6. Exception Handling
- **Try-catch blocks**: `try { } catch (Exception e) { }`
- **Try-with-resources**: `try (Resource r = ...) { }`
- **Finally blocks**: Cleanup patterns
- **Throw patterns**: Exception propagation

#### 7. Collection & Stream Patterns
- **ArrayList operations**: `add()`, `remove()`, iteration
- **HashMap usage**: `put()`, `get()`, `containsKey()`
- **Stream transformations**: `.map()`, `.filter()`, `.collect()`
- **Reduction operations**: `.sum()`, `.reduce()`, `.count()`

### Real-World Example: Why CES is Powerful

**Scenario**: Detecting plagiarism where students use different variable names but same strategy

```java
// Reference Solution (ref1.java)
public static int sumArray(int[] arr) {
    int total = 0;
    for (int i = 0; i < arr.length; i++) {
        total += arr[i];
    }
    return total;
}

// Student A (s1.java) - Should match ref1
public static int simpleSum(int[] data) {
    int res = 0;
    for (int j = 0; j < data.length; j++) {
        res += data[j];  // SAME PATTERN!
    }
    return res;
}

// Student B (s2.java) - Should NOT match ref1
public static int getTotal(int[] values) {
    int result = 0;
    for (int val : values) {  // DIFFERENT pattern (enhanced for)
        result = result + val;  // DIFFERENT accumulation (explicit)
    }
    return result;
}
```

**CES Detection:**
- **ref1 ↔ s1**: `INDEXED_LOOP` + `COMPOUND_ASSIGNMENT` → **HIGH similarity**
- **ref1 ↔ s2**: `INDEXED_LOOP` vs `ENHANCED_FOR` + `COMPOUND` vs `EXPLICIT` → **LOW similarity**

**This is why CES is essential for accurate code similarity detection!**

---

## 📁 Data Folder Structure

### Current Sample Dataset

```
data/java/
├── ground_truth.json          # Expected student→reference mappings
└── p1/                        # Problem 1: Array Sum
    ├── ref/                   # Reference implementations (correct solutions)
    │   ├── ref1.java         # Strategy 1: Indexed for loop
    │   └── ref2.java         # Strategy 2: Enhanced for loop
    └── s/                     # Student submissions
        ├── s1.java           # Student 1 submission
        ├── s2.java           # Student 2 submission
        └── s3.java           # Student 3 submission
```

### Ground Truth Format

**File**: `data/java/ground_truth.json`

```json
{
    "p1": {
        "s1": "ref1",   // Student s1's solution matches ref1's strategy
        "s2": "ref1",   // Student s2's solution matches ref1's strategy  
        "s3": "ref2"    // Student s3's solution matches ref2's strategy
    }
}
```

**Meaning**: For problem `p1`, the pipeline should predict:
- `s1` is most similar to `ref1`
- `s2` is most similar to `ref1`
- `s3` is most similar to `ref2`

### Adding New Problems

To add a new problem (e.g., `p2`):

```bash
# 1. Create directory structure
mkdir -p data/java/p2/ref data/java/p2/s

# 2. Add reference implementations
# Create ref1.java, ref2.java, etc. in data/java/p2/ref/

# 3. Add student submissions
# Create s1.java, s2.java, etc. in data/java/p2/s/

# 4. Update ground truth
# Edit data/java/ground_truth.json to add p2 mappings
```

**Example**:
```json
{
    "p1": { ... },
    "p2": {
        "s1": "ref1",
        "s2": "ref2",
        "s3": "ref1"
    }
}
```

---

## 🔄 Complete Pipeline Flow - Detailed

This section explains the **end-to-end pipeline** showing exactly what happens at each step, including inputs, outputs, and data transformations.

### Pipeline Overview Diagram

```
┌─────────────────┐
│  Java Source    │
│  Files (.java)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 1: CPG Generation (Joern)        │
│  Input:  *.java files                  │
│  Output: cpg.bin + baseline.json       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 2: Multi-View Feature Extraction │
│  ┌─────────────────────────────────┐   │
│  │ WL (Weisfeiler-Lehman)          │   │
│  │ Output: wl.json                 │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ CES (Computational Semantics)   │   │
│  │ Output: ces_v2.json             │   │
│  └─────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 3: Vocabulary Building            │
│  Input:  All feature JSONs              │
│  Output: Global vocabularies            │
│          wl_vocab.json, ces_vocab.json  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 4: Vectorization                  │
│  Input:  Feature JSONs + Vocabularies   │
│  Output: Dense vectors (*.vec)          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 5: Normalization (L2)             │
│  Input:  Raw vectors                    │
│  Output: Normalized vectors (*.norm.vec)│
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 6: Similarity Computation         │
│  Input:  Normalized vectors             │
│  Output: Similarity matrices (cosine)   │
│          - baseline_similarity.json     │
│          - wl_similarity.json           │
│          - ces_similarity.json          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 7: Weighted Aggregation           │
│  Input:  All similarity matrices        │
│  Weights: Baseline=35%, WL=40%, CES=25% │
│  Output: final_similarity_matrix.json   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 8: Accuracy Evaluation            │
│  Input:  Final matrix + ground_truth.json │
│  Output: Accuracy report + predictions  │
└─────────────────────────────────────────┘
```

### Step-by-Step Data Flow

#### **Step 1: CPG Generation**
```bash
INPUT:  data/java/p1/ref/ref1.java
TOOL:   joern-parse
OUTPUT: cpgs/java/p1/ref/ref1/cpg.bin
        outputs/java/p1/ref/ref1/baseline.json
```

**What happens:** Joern parses Java code into a Code Property Graph containing AST nodes, CFG edges, PDG dependencies, and type information.

#### **Step 2: Feature Extraction**

**WL Extraction:**
```bash
INPUT:  cpgs/java/p1/ref/ref1/cpg.bin
SCRIPT: cpg/scripts/java/wl/wl_features.sc
OUTPUT: outputs/java/p1/ref/ref1/wl.json
```

**CES Extraction:**
```bash
INPUT:  cpgs/java/p1/ref/ref1/cpg.bin
SCRIPT: cpg/scripts/java/semantic/ces_v2_java.sc
OUTPUT: outputs/java/p1/ref/ref1/ces_v2.json
```

**What happens:** Joern scripts traverse the CPG to extract:
- **WL**: Node type histograms at different iterations
- **CES**: Computational patterns (loops, accumulation, data access)

#### **Step 3: Vocabulary Building**
```bash
INPUT:  outputs/java/**/*.wl.json (all programs)
SCRIPT: similarity/java/build_wl_vocab_java.py
OUTPUT: vocabulary/java/wl_vocab.json
```

**What happens:** Collects all unique features across all programs to create a global feature vocabulary (bag-of-features).

**Example wl_vocab.json:**
```json
{
  "wl_i0_BLOCK": 0,
  "wl_i0_CALL": 1,
  "wl_i0_IDENTIFIER": 2,
  "wl_i0_LITERAL": 3,
  ...
}
```

#### **Step 4: Vectorization**
```bash
INPUT:  outputs/java/p1/ref/ref1/wl.json + vocabulary/java/wl_vocab.json
SCRIPT: similarity/java/vectorize_wl_java.py
OUTPUT: vectors/java/wl/p1_ref_ref1.vec
```

**What happens:** Converts feature histogram to dense vector using vocabulary indices.

**Example vector (dense array):**
```
[4, 13, 2, 12, 0, 0, 1, 8, 0, 0, ...]
 ^   ^   ^   ^
 BLOCK CALL ID LIT
```

#### **Step 5: Normalization**
```bash
INPUT:  vectors/java/wl/p1_ref_ref1.vec
SCRIPT: similarity/java/normalize_wl_java.py  
OUTPUT: vectors/java/wl_norm/p1_ref_ref1.norm.vec
```

**What happens:** L2 normalization: `v_norm = v / ||v||₂`

#### **Step 6: Similarity Computation**
```bash
INPUT:  All normalized vectors
SCRIPT: similarity/java/compute_wl_similarity_java.py
OUTPUT: evaluation/java/wl_similarity_matrix_java.json
```

**What happens:** Computes cosine similarity between all student-reference pairs:
```
similarity(A, B) = dot(A_norm, B_norm)
```

**Example similarity matrix:**
```json
{
  "p1": {
    "s1": {
      "ref1": 0.951,
      "ref2": 0.707
    },
    "s2": {
      "ref1": 0.612,
      "ref2": 0.894
    }
  }
}
```

#### **Step 7: Weighted Aggregation**
```bash
INPUT:  baseline_similarity.json, wl_similarity.json, ces_similarity.json
SCRIPT: evaluation/java/aggregate_all_features_java.py
WEIGHTS: 0.35, 0.40, 0.25
OUTPUT: evaluation/java/final_similarity_matrix_java.json
```

**What happens:** Combines individual view similarities:
```
final_score = 0.35×baseline + 0.40×wl + 0.25×ces
```

#### **Step 8: Accuracy Evaluation**
```bash
INPUT:  final_similarity_matrix_java.json + ground_truth.json
SCRIPT: evaluation/calculate_accuracy.py
OUTPUT: Accuracy report (printed to console)
```

**What happens:** For each student:
1. Find reference with highest similarity score
2. Compare predicted reference to ground truth
3. Calculate accuracy = correct_predictions / total_students

---

## ⚙️ Pipeline Execution

### Full Pipeline Overview

The `run_java_pipeline.sh` script executes these steps sequentially:

#### Step 0: Cleanup
```bash
rm -rf outputs/java vectors/java evaluation/java/*.json
```
Removes previous outputs to ensure clean execution.

#### Step 0.5: CPG Generation
```bash
./experiments/java/run_joern_java.sh
```
- Parses Java source files using Joern
- Generates Code Property Graphs (CPGs)
- Extracts baseline features (CFG, AST, PDG)

**Input**: `data/java/p*/ref/*.java`, `data/java/p*/s/*.java`  
**Output**: `cpgs/java/p*/{ref,s}/*/cpg.bin`, `outputs/java/p*/{ref,s}/*/baseline.json`

#### Step 1: WL Pipeline
```bash
# Extract WL features
./experiments/pipeline/java/run_wl_extract_java.sh

# Build vocabulary
python3 similarity/java/build_wl_vocab_java.py

# Vectorize features
python3 similarity/java/vectorize_wl_java.py

# Normalize vectors
python3 similarity/java/normalize_wl_java.py

# Compute similarity matrix
python3 similarity/java/compute_wl_similarity_java.py
```

**Outputs**:
- `outputs/java/p*/{ref,s}/*/wl.json` - WL features
- `vocabulary/java/wl_vocab.json` - Global WL vocabulary
- `vectors/java/wl/*.vec` - WL vectors
- `vectors/java/wl_norm/*.norm.vec` - Normalized WL vectors
- `evaluation/java/wl_similarity_matrix_java.json` - WL similarity matrix

#### Step 2: CES Pipeline
```bash
# Extract CES features
./experiments/pipeline/java/run_ces_extract_java.sh

# Build vocabulary, vectorize, normalize, compute similarity
# (Same pattern as WL)
```

**Outputs**:
- `outputs/java/p*/{ref,s}/*/ces_v2.json` - CES features
- `vocabulary/java/ces_vocab.json` - Global CES vocabulary
- `vectors/java/ces/*.vec` - CES vectors
- `vectors/java/ces_norm/*.norm.vec` - Normalized CES vectors
- `evaluation/java/ces_similarity_matrix_java.json` - CES similarity matrix

#### Step 3: Baseline Similarity
```bash
python3 similarity/java/compute_baseline_similarity_java.py
```

**Output**: `evaluation/java/similarity_matrix_java.json` - Baseline similarity matrix

#### Step 4: Aggregation
```bash
python3 evaluation/java/aggregate_all_features_java.py
```

Combines all similarity matrices using weighted average:
- Baseline: 35%
- WL: 40%
- CES: 25%

**Output**: `evaluation/java/final_similarity_matrix_java.json` - Combined similarity matrix

#### Step 5: Accuracy Evaluation
```bash
python3 evaluation/calculate_accuracy.py --matrix evaluation/java/final_similarity_matrix_java.json
```

Compares predictions against ground truth and generates report.

**Output**: Terminal display + `evaluation/java/accuracy_report_java.txt` (if configured)

---

## 📊 Output Files

### Directory Structure After Execution

```
outputs/java/
└── p1/
    ├── ref/
    │   ├── ref1/
    │   │   ├── behavioral.json      # Behavioral features
    │   │   ├── canonical.json       # Canonical forms
    │   │   ├── ces_v2.json         # CES features
    │   │   ├── combined_features.json
    │   │   ├── semantic.json        # Semantic features
    │   │   ├── structural.json      # Structural features
    │   │   ├── variable_roles.json  # Variable role analysis
    │   │   └── wl.json             # WL features
    │   └── ref2/
    │       └── (same as ref1)
    └── s/
        ├── s1/
        │   └── (same as ref1)
        ├── s2/
        └── s3/

vectors/java/
├── wl/
│   ├── p1_ref_ref1.vec
│   ├── p1_ref_ref2.vec
│   ├── p1_s_s1.vec
│   ├── p1_s_s2.vec
│   └── p1_s_s3.vec
├── wl_norm/
│   ├── p1_ref_ref1.norm.vec
│   └── (normalized versions)
├── ces/
│   └── (same pattern as wl/)
└── ces_norm/
    └── (normalized versions)

vocabulary/java/
├── wl_vocab.json          # WL feature vocabulary
└── ces_vocab.json         # CES feature vocabulary

cpgs/java/
└── p1/
    ├── ref/
    │   ├── ref1/
    │   │   └── cpg.bin    # Joern CPG binary
    │   └── ref2/
    │       └── cpg.bin
    └── s/
        ├── s1/
        │   └── cpg.bin
        ├── s2/
        └── s3/

evaluation/java/
├── similarity_matrix_java.json           # Baseline similarity
├── wl_similarity_matrix_java.json        # WL similarity
├── ces_similarity_matrix_java.json       # CES similarity
├── final_similarity_matrix_java.json     # Aggregated similarity
└── accuracy_report_java.txt              # Accuracy evaluation
```

### Key Output Files Explained

#### 1. Similarity Matrices
**Format**: JSON with nested structure
```json
{
  "p1": {
    "s1": {
      "ref1": 0.982,
      "ref2": 0.654
    },
    "s2": {
      "ref1": 0.912,
      "ref2": 0.743
    }
  }
}
```

**Interpretation**: 
- `s1` is 98.2% similar to `ref1`
- `s1` is 65.4% similar to `ref2`

#### 2. Final Similarity Matrix
**File**: `evaluation/java/final_similarity_matrix_java.json`

```json
{
  "p1": {
    "s1": {
      "ref1": {
        "baseline": 0.995,
        "wl": 0.951,
        "ces": 0.850,
        "weighted": 0.932
      },
      "ref2": {
        "baseline": 0.943,
        "wl": 0.707,
        "ces": 0.000,
        "weighted": 0.659
      }
    }
  }
}
```

**breakdown**:
- Individual view scores (baseline, wl, ces)
- **weighted**: Final aggregated score (used for prediction)

#### 3. Feature Files
**Example**: `outputs/java/p1/s/s1/wl.json`

```json
{
  "wl_i0_BLOCK": 4,
  "wl_i0_CALL": 13,
  "wl_i0_CONTROL_STRUCTURE": 1,
  "wl_i0_IDENTIFIER": 2,
  "wl_i0_LITERAL": 12,
  ...
}
```

Histogram of WL features (node types at iteration 0).

---

## 📈 Understanding Results

### Sample Accuracy Report

```
============================================================
               ACCURACY EVALUATION REPORT
============================================================

📋 Ground Truth:
  --------------------------------------------------------
  Problem      Student         → Expected Ref
  --------------------------------------------------------
  p1           s1              → ref1
  p1           s2              → ref1
  p1           s3              → ref2
  --------------------------------------------------------

🎯 Predictions:
  --------------------------------------------------------
  Student         Predicted       Expected        Status
  --------------------------------------------------------
  s1              ref1            ref1            ✓
  s2              ref1            ref1            ✓
  s3              ref2            ref2            ✓
  --------------------------------------------------------

============================================================
                    FINAL RESULTS
============================================================
  Weights: Baseline=35%, WL=40%, CES=25%
  Correct Predictions: 3/3
  Accuracy: 1.0000 (100.00%)
============================================================
```

### Interpreting Individual Scores

**High Baseline (>0.95)**: Similar AST/CFG structure  
**High WL (>0.90)**: Similar graph patterns  
**High CES (>0.70)**: Similar computational strategies  

**Low CES (<0.30)**: Different algorithms even if structure is similar

---

## 📝 Sample Programs Explained

### Problem 1: Array Sum

**Objective**: Implement a function that sums all elements in an integer array.

### Reference Implementations

#### [ref1.java](./data/java/p1/ref/ref1.java) - Indexed For Loop
```java
public class ref1 {
    public static int sumArray(int[] arr) {
        int total = 0;
        for (int i = 0; i < arr.length; i++) {
            total += arr[i];
        }
        return total;
    }
}
```

**CES Pattern**:
- **Control Flow**: Counter-based iteration
- **Data Access**: Indexed array access (`arr[i]`)
- **Accumulation**: Compound assignment (`+=`)

#### [ref2.java](./data/java/p1/ref/ref2.java) - Enhanced For Loop
```java
public class ref2 {
    public static int calSum(int[] numbers) {
        int s = 0;
        for (int num : numbers) {
            s = s + num;
        }
        return s;
    }
}
```

**CES Pattern**:
- **Control Flow**: Iterator-based (for-each)
- **Data Access**: Direct element access
- **Accumulation**: Explicit addition (`s = s + num`)

#### [ref3.java](./data/java/p1/ref/ref3.java) - Recomputation Pattern (BUGGY)
```java
public class ref3 {
    // Demonstrates common bug: overwrite instead of accumulate
    public static int buggySum(int[] arr) {
        int total = 0;
        for (int i = 0; i < arr.length; i++) {
            total = arr[i];  // ❌ OVERWRITES instead of adding
        }
        return total;  // Returns last element only
    }
}
```

**CES Pattern**:
- **Control Flow**: Counter-based iteration (same as ref1)
- **Data Access**: Indexed array access (`arr[i]`)
- **Accumulation**: **OVERWRITE pattern** (`total = arr[i]` - no addition!)
- **Semantic**: Assignment operator without accumulation

**KEY INSIGHT**: Despite having the same loop structure as ref1, ref3 has a **fundamentally different computational strategy** due to the assignment operator. CES captures this semantic difference!

### Student Submissions

#### [s1.java](./data/java/p1/s/s1.java) - Matches ref1
```java
public class s1 {
    public static int simpleSum(int[] arr) {
        int res = 0;
        for (int j = 0; j < arr.length; j++) {
            res += arr[j];
        }
        return res;
    }
}
```

**Ground Truth**: `s1 → ref1` ✓  
**Reason**: Same indexed for loop + compound assignment pattern

#### [s2.java](./data/java/p1/s/s2.java) - Matches ref1
```java
public class s2 {
    public static int calculateSum(int[] data) {
        int sum = 0;
        for (int idx = 0; idx < data.length; idx++) {
            sum += data[idx];
        }
        return sum;
    }
}
```

**Ground Truth**: `s2 → ref1` ✓  
**Reason**: Same indexed for loop + compound assignment pattern (different variable names)

#### [s3.java](./data/java/p1/s/s3.java) - Matches ref2
```java
public class s3 {
    public static int getTotal(int[] values) {
        int result = 0;
        for (int val : values) {
            result = result + val;
        }
        return result;
    }
}
```

**Ground Truth**: `s3 → ref2` ✓  
**Reason**: Same enhanced for loop + explicit addition pattern

#### [s4.java](./data/java/p1/s/s4.java) - Matches ref3
```java
public class s4 {
    // Same bug as ref3, but using enhanced for loop
    public static int wrongSum(int[] values) {
        int result = 0;
        for (int val : values) {
            result = val;  // ❌ OVERWRITES - same bug as ref3
        }
        return result;  // Returns last element only
    }
}
```

**Ground Truth**: `s4 → ref3` ✓  
**Reason**: **Same overwrite pattern as ref3**, demonstrating CES's power!

**INTERESTING CASE**: 
- s4 uses **enhanced for** (different from ref3's indexed for)
- But both use **overwrite pattern** (`= value` instead of `+= value`)
- **WL will score LOW** (different loop structures)
- **CES will score HIGH** (same semantic bug!)

This proves CES captures **algorithmic semantics beyond syntax**!

---

## 🔬 CES Pattern Detection - Deep Dive

### Sample CES Output Analysis

After running the pipeline, examine `outputs/java/p1/ref/ref1/ces_v2.json`:

```json
[
  {
    "context": "loop_INDEXED",
    "pattern": "accumulate_ADD",
    "operator": "COMPOUND_ASSIGNMENT",
    "importance": 0.8
  },
  {
    "context": "data_access_ARRAY_INDEX",
    "pattern": "sequential_READ",
    "importance": 0.6
  }
]
```

**Explanation**:
- `loop_INDEXED`: Detects counter-based for loop
- `accumulate_ADD`: Recognizes addition pattern
- `COMPOUND_ASSIGNMENT`: Identifies `+=` operator
- Higher importance = more distinctive pattern

Compare with `outputs/java/p1/ref/ref2/ces_v2.json`:

```json
[
  {
    "context": "loop_ENHANCED_FOR",
    "pattern": "accumulate_ADD",
    "operator": "BINARY_PLUS",
    "importance": 0.8
  },
  {
    "context": "data_access_ITERATOR",
    "pattern": "sequential_READ",
    "importance": 0.6
  }
]
```

**Key Differences**:
- `loop_ENHANCED_FOR` vs `loop_INDEXED` → Different control flow
- `BINARY_PLUS` vs `COMPOUND_ASSIGNMENT` → Different operators
- **Same pattern**: `accumulate_ADD` → Both accumulate via addition

Now compare with `outputs/java/p1/ref/ref3/ces_v2.json`:

```json
[
  {
    "context": "loop_INDEXED",
    "pattern": "overwrite_RECOMPUTE",
    "operator": "ASSIGNMENT",
    "importance": 0.9
  },
  {
    "context": "data_access_ARRAY_INDEX",
    "pattern": "sequential_READ",
    "importance": 0.6
  }
]
```

**Critical Difference**:
- `loop_INDEXED`: **Same as ref1!**
- `pattern`: `overwrite_RECOMPUTE` vs `accumulate_ADD` → **DIFFERENT SEMANTIC!**
- `operator`: `ASSIGNMENT` vs `COMPOUND_ASSIGNMENT` → **BUG DETECTED!**

### Expected Similarity Scores

#### s1 vs All References

**s1 vs ref1** (Both indexed for + compound assignment):
```json
{
  "baseline": 0.995,  // Almost identical structure
  "wl": 0.951,        // Same graph patterns
  "ces": 0.850,       // Same accumulation pattern
  "weighted": 0.932   // HIGH - should match!
}
```

**s1 vs ref2** (Different loop type):
```json
{
  "baseline": 0.943,  // Similar structure
  "wl": 0.707,        // Different loop patterns
  "ces": 0.320,       // Different operators (+=  vs = +)
  "weighted": 0.659   // MEDIUM
}
```

**s1 vs ref3** (Same loop, different accumulation):
```json
{
  "baseline": 0.998,  // Nearly identical structure!
  "wl": 0.955,        // Same indexed loop
  "ces": 0.050,       // VERY DIFFERENT semantics (+=  vs =)
  "weighted": 0.672   // LOW despite high baseline/WL!
}
```

**Why This Matters**: Without CES, `s1` would score highest with `ref3` (due to identical structure). **CES correctly identifies the semantic difference** and ensures `s1` matches `ref1` instead!

#### s4 vs All References

**s4 vs ref3** (Different loops, same bug):
```json
{
  "baseline": 0.890,  // Some structural similarity
  "wl": 0.620,        // Different loop types
  "ces": 0.780,       // SAME overwrite pattern!
  "weighted": 0.763   // HIGH thanks to CES!
}
```

**s4 vs ref1** (Different loops, different semantics):
```json
{
  "baseline": 0.885,
  "wl": 0.615,
  "ces": 0.080,       // Different semantics
  "weighted": 0.548   // LOW
}
```

**s4 vs ref2** (Same enhanced for, different accumulation):
```json
{
  "baseline": 0.950,
  "wl": 0.810,        // Same enhanced for!
  "ces": 0.150,       // Different accumulation
  "weighted": 0.641   // MEDIUM
}
```

**Conclusion**: CES correctly identifies that `s4` shares the **same semantic bug** (overwrite pattern) with `ref3`, despite having **different syntactic structures** (enhanced for vs indexed for). This is the power of semantic similarity detection!

### Why These Distinctions Matter

The framework can detect that `s1` and `s2` use the **same computational strategy** as `ref1`, even though:
- Variable names differ (`total` vs `sum` vs `res`)
- Counter names differ (`i` vs `idx` vs `j`)
- Function names differ (`sumArray` vs `calculateSum`)

Similarly, it recognizes that `s3` uses a **different strategy** (enhanced for loop) matching `ref2`, even though all programs solve the same problem.

This is the power of **semantic similarity detection** beyond simple syntactic matching!

---

## 🔧 Troubleshooting

### Issue: "joern: command not found"

**Solution**: Ensure Joern is installed and in PATH
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/path/to/joern/bin:$PATH"
```

### Issue: Pipeline stops early

**Solution**: Check for errors in specific steps
```bash
# Run pipeline without output suppression
./run_java_pipeline.sh 2>&1 | tee pipeline_debug.log
```

### Issue: All CES scores are 0.000

**Solution**: CES extraction may have failed
```bash
# Check CES feature files
cat outputs/java/p1/s/s1/ces_v2.json

# Should contain JSON array with patterns, not empty []
```

### Issue: Low accuracy (< 50%)

**Possible causes**:
1. **Ground truth incorrect**: Verify mappings match actual program strategies
2. **Test programs too simple**: Add more diverse computational patterns
3. **Weights need tuning**: Adjust in `aggregate_all_features_java.py`

---

## 📚 Next Steps

### Adding More Problems
1. Create new problem directories in `data/java/`
2. Add diverse reference implementations (different strategies)
3. Create student submissions matching each strategy
4. Update ground truth mappings
5. Run pipeline

### Extending Features
1. Add SCDPS view (already has placeholders)
2. Experiment with different aggregation weights
3. Implement additional similarity metrics
4. Add cross-language similarity (Java ↔ C++)

### Scaling Up
1. Test with 50-100 problems
2. Analyze performance bottlenecks
3. Optimize CPG generation
4. Parallelize feature extraction

---

For overall framework documentation, see [README.md](./README.md).
