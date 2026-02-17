# C++ Code Similarity Pipeline - User Guide

Complete guide for running the C++ implementation of the multi-view code similarity framework.

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
# Clean previous outputs and run pipeline
rm -rf outputs/cpp vectors/cpp cpgs/cpp evaluation/cpp/*.json
./run_cpp_pipeline.sh
```

```

---

## 🧠 Understanding CES v3 Enhanced (C++ Semantic Analysis)

### What is CES v3 Enhanced?

**CES v3 Enhanced** is an advanced version of Computational Expression Semantics specifically designed for C++ that captures **modern C++ idioms, design patterns, and computational strategies** beyond what general CES detects.

While standard CES focuses on algorithmic patterns (loops, accumulation, data access), **CES v3 Enhanced** adds:
- **C++11/14/17 features**: Move semantics, lambda expressions, auto type deduction
- **Template patterns**: Specialization, SFINAE, variadic templates
- **RAII patterns**: Resource management idioms
- **STL algorithm recognition**: 18+ standard algorithms (transform, accumulate, for_each, etc.)
- **Memory management patterns**: Smart pointers, custom deleters
- **Exception safety patterns**: Strong/weak/nothrow guarantees

### Why Enhanced Version for C++?

C++ has **unique semantic patterns** that don't exist in Java or C:

| Pattern Category | Java/C | C++ Enhanced |
|-----------------|--------|--------------|
| **Resource Management** | Manual/GC | **RAII** (constructor acquire, destructor release) |
| **Ownership Semantics** | References only | **Move semantics** (std::move, rvalue references) |
| **Generic Programming** | Generics/templates | **Advanced templates** (SFINAE, variadic, concepts) |
| **Functional Programming** | Streams/lambdas | **STL algorithms** + lambdas + function objects |
| **Memory Management** | GC/pointers | **Smart pointers** (unique_ptr, shared_ptr, weak_ptr) |

### CES v3 Enhanced vs Traditional Similarity

**Traditional similarity** would consider these **different**:
```cpp
// Program A: Manual loop
int sum = 0;
for (size_t i = 0; i < v.size(); i++) {
    sum += v[i];
}

//Program B: STL algorithm
int sum = std::accumulate(v.begin(), v.end(), 0);
```

**CES v3 Enhanced** recognizes both use **accumulation strategy** but:
- Program A: `INDEXED_LOOP` + `COMPOUND_ASSIGNMENT`
- Program B: `STL_ACCUMULATE` (functional composition)  
→ Same **computational goal** (sum), different **idiom level** (imperative vs declarative)

### What CES v3 Enhanced Detects - C++ Patterns

#### 1. Loop & Iteration Patterns
- **C-style indexed loop**: `for (size_t i = 0; i < v.size(); i++)`
- **Range-based for (C++11)**: `for (const auto& x : container)`
- **Iterator loops**: `for (auto it = v.begin(); it != v.end(); ++it)`
- **STL algorithm iteration**: `std::for_each`, `std::transform`

#### 2. STL Algorithm Patterns (18+ Algorithms)
- **Transformation**: `std::transform`, `std::generate`
- **Reduction**: `std::accumulate`, `std::reduce` (C++17)
- **Searching**: `std::find`, `std::find_if`, `std::binary_search`
- **Sorting**: `std::sort`, `std::stable_sort`, `std::partial_sort`
- **Filtering**: `std::copy_if`, `std::remove_if`
- **Aggregation**: `std::count`, `std::count_if`
- **Min/Max**: `std::min_element`, `std::max_element`

#### 3. Move Semantics & Ownership
- **Rvalue references**: `T&&`, perfect forwarding `std::forward`
- **Move operations**: `std::move`, move constructors/assignment
- **Return value optimization**: RVO/NRVO patterns
- **Value categories**: lvalue vs rvalue usage

#### 4. RAII Patterns
- **Constructor acquire**: Resource allocation in constructor
- **Destructor release**: Automatic cleanup in destructor
- **Scope-based resource management**: Lock guards, file handles
- **Custom deleters**: Smart pointers with custom cleanup

#### 5. Smart Pointer Patterns
- **unique_ptr**: Exclusive ownership, move-only semantics
- **shared_ptr**: Shared ownership with reference counting
- **weak_ptr**: Non-owning references to break cycles
- **make_unique/make_shared**: Factory function usage

#### 6. Template Patterns
- **Template specialization**: Full/partial specialization
- **SFINAE**: Substitution Failure Is Not An Error
- **Variadic templates**: Parameter packs, fold expressions
- **Template metaprogramming**: Compile-time computation

#### 7. Exception Safety Patterns
- **RAII-based safety**: Automatic cleanup via destructors
- **Strong guarantee**: Commit-or-rollback semantics
- **Noexcept specifications**: `noexcept` function qualifiers
- **Exception-neutral code**: Proper propagation

#### 8. Modern C++ Idioms
- **Auto type deduction**: `auto x = ...`
- **Lambda expressions**: `[capture](params) { body }`
- **Structured bindings (C++17)**: `auto [a, b] = pair`
- **Const-correctness**: `const` qualifiers throughout

### Real-World Example: CES v3 Enhanced in Action

```cpp
// ref1.cpp - C-style iteration
int sumArray(const std::vector<int>& arr) {
    int total = 0;
    for (size_t i = 0; i < arr.size(); i++) {
        total += arr[i];
    }
    return total;
}

// ref2.cpp - Range-based for (C++11)
int sumArray(const std::vector<int>& arr) {
    int sum = 0;
    for (const auto& val : arr) {
        sum = sum + val;
    }
    return sum;
}

// ref3.cpp - STL algorithm (Modern C++)
int sumArray(const std::vector<int>& arr) {
    return std::accumulate(arr.begin(), arr.end(), 0);
}
```

**CES v3 Enhanced Detection:**
- **ref1**: `INDEXED_LOOP` + `COMPOUND_ASSIGNMENT` + `SIZE_BASED_CHECK`
- **ref2**: `RANGE_BASED_FOR` + `EXPLICIT_ADDITION` + `AUTO_TYPE`
- **ref3**: `STL_ACCUMULATE` + `ITERATOR_PAIR` + `FUNCTIONAL_STYLE`

**Student matching:**
- s1 (uses indexed loop) → **ref1** ✓
- s2 (uses range-based for) → **ref2** ✓  
- s3 (uses std::accumulate) → **ref3** ✓

**Key insight**: CES v3 Enhanced correctly distinguishes between **imperative**, **iterator-based**, and **functional** approaches to the same problem!

---

## 📁 Data Folder Structure

### Expected Dataset Structure

```
data/cpp/
├── ground_truth.json          # Expected student→reference mappings
└── p1/                        # Problem 1
    ├── ref/                   # Reference implementations
    │   ├── ref1.cpp          # Reference strategy 1
    │   ├── ref2.cpp          # Reference strategy 2
    │   └── ref3.cpp          # Reference strategy 3
    └── s/                     # Student submissions
        ├── s1.cpp            # Student 1 submission
        ├── s2.cpp            # Student 2 submission
        ├── s3.cpp            # Student 3 submission
        └── s4.cpp            # Student 4 submission
```

### Ground Truth Format

**File**: `data/cpp/ground_truth.json`

```json
{
    "p1": {
        "s1": "ref1",
        "s2": "ref1",
        "s3": "ref2",
        "s4": "ref3"
    }
}
```

---

## ⚙️ Pipeline Execution

### Current Implementation Status

#### ✅ Phase 1: CPG Extraction (COMPLETE)
```bash
./experiments/cpp/run_joern_cpp.sh
```

**Features**:
- Parses C++ source files (`.cpp`, `.cc`, `.C`, `.cxx`)
- Generates Code Property Graphs using Joern
- Extracts baseline features (CFG, AST, PDG)
- **Uses CES v3 Enhanced** with advanced C++ pattern detection

**Output**: `outputs/cpp/p*/`{ref,s}`/*/`{baseline, structural, semantic, behavioral, canonical, variable_roles}`.json`

**CES v3 Enhanced Capabilities**:
- Template metaprogramming detection
- RA II pattern recognition
- Move semantics analysis
- STL algorithm extraction
- Smart pointer usage patterns
- Exception safety patterns

#### 🔧 Phase 2-6: Full Pipeline (REQUIRES CONFIGURATION)

The following phases require updating Python scripts in `similarity/cpp/` and `evaluation/cpp/` to use C++-specific paths before activation.

---

## 🔬 CES v3 Enhanced - C++ Specific Patterns

### Advanced C++ Features Detected

#### 1. Template Patterns
```cpp
// CES detects template specialization
template<typename T>
class Vector { /* ... */ };

template<>
class Vector<bool> { /* optimized */ };
```

**CES Output**:
```json
{
  "context": "template_SPECIALIZATION",
  "pattern": "type_PARAMETERIZATION",
  "importance": 0.9
}
```

#### 2. RAII Patterns
```cpp
// Resource Acquisition Is Initialization
class FileHandle {
    std::fstream file;
public:
    FileHandle(const std::string& path) : file(path) {}
    ~FileHandle() { if(file.is_open()) file.close(); }
};
```

**CES Output**:
```json
{
  "context": "resource_RAII",
  "pattern": "constructor_ACQUIRE",
  "destructor": "RELEASE",
  "importance": 0.95
}
```

#### 3. Move Semantics
```cpp
// Rvalue references and perfect forwarding
Vector(Vector&& other) noexcept 
    : data(std::exchange(other.data, nullptr)) {}
```

**CES Output**:
```json
{
  "context": "ownership_MOVE",
  "pattern": "rvalue_REFERENCE",
  "optimization": "ZERO_COPY",
  "importance": 0.85
}
```

#### 4. STL Algorithm Usage
```cpp
// STL algorithms vs manual loops
std::transform(vec.begin(), vec.end(), result.begin(),
               [](int x) { return x * 2; });
```

**CES Output**:
```json
{
  "context": "algorithm_STL",
  "pattern": "transform_FUNCTIONAL",
  "lambda": "INLINE_CLOSURE",
  "importance": 0.8
}
```

---

## 📊 Output Files

### Directory Structure After Execution

```
outputs/cpp/
└── p1/
    ├── ref/
    │   ├── ref1/
    │   │   ├── baseline.json        # Combined baseline features
    │   │   ├── canonical.json       # Canonicalized code
    │   │   ├── structural.json      # Structural features
    │   │   ├── semantic.json        # CES v3 Enhanced features
    │   │   ├── behavioral.json      # Behavioral features
    │   │   └── variable_roles.json  # Variable role analysis
    │   ├── ref2/
    │   └── ref3/
    └── s/
        ├── s1/
        ├── s2/
        ├── s3/
        └── s4/

cpgs/cpp/
└── p1/
    ├── ref/
    │   ├── ref1/cpg.bin
    │   ├── ref2/cpg.bin
    │   └── ref3/cpg.bin
    └── s/
        ├── s1/cpg.bin
        ├── s2/cpg.bin
        ├── s3/cpg.bin
        └── s4/cpg.bin
```

---

## 📝 Sample C++ Programs

### Problem: Array Sum Implementation

#### [ref1.cpp](./data/cpp/p1/ref/ref1.cpp) - Classic Iterator Loop
```cpp
#include <vector>

int sumArray(const std::vector<int>& arr) {
    int total = 0;
    for (size_t i = 0; i < arr.size(); i++) {
        total += arr[i];
    }
    return total;
}
```

**CES Pattern**:
- Control Flow: Index-based iteration
- Data Access: Random access (`arr[i]`)
- Accumulation: Compound assignment (`+=`)

#### [ref2.cpp](./data/cpp/p1/ref/ref2.cpp) - Range-Based For Loop
```cpp
#include <vector>

int sumArray(const std::vector<int>& arr) {
    int sum = 0;
    for (const auto& val : arr) {
        sum = sum + val;
    }
    return sum;
}
```

**CES Pattern**:
- Control Flow: Range-based iteration (C++11)
- Data Access: Sequential iterator
- Accumulation: Explicit addition

#### [ref3.cpp](./data/cpp/p1/ref/ref3.cpp) - STL Algorithm (Modern C++)
```cpp
#include <vector>
#include <numeric>

int sumArray(const std::vector<int>& arr) {
    return std::accumulate(arr.begin(), arr.end(), 0);
}
```

**CES Pattern**:
- Control Flow: **STL algorithm** (completely different!)
- Data Access: Iterator-based
- Accumulation: Functional composition
- **HIGH IMPORTANCE**: Modern C++ idiom

---

## 🎯 Understanding CES Similarity

### Example: Why s3 Matches ref3 Despite Different Syntax

**s3.cpp** (Student uses STL):
```cpp
int getTotal(const std::vector<int>& values) {
    return std::accumulate(values.begin(), values.end(), 0);
}
```

**Expected Similarity**:
- **s3 vs ref1**: Low CES (~0.10) - Manual loop vs STL algorithm
- **s3 vs ref2**: Low CES (~0.15) - Range-for vs STL algorithm  
- **s3 vs ref3**: **High CES (~0.95)** - Both use STL accumulate

**Why?** CES v3 Enhanced recognizes that both use the **same algorithmic strategy** (STL functional composition) even with different variable names.

---

## 🔧 Configuration Notes

### Activating Full Pipeline

To enable WL, SCDPS, and aggregation:

1. **Update similarity scripts** (`similarity/cpp/*.py`):
   ```python
   OUT_DIR = Path("outputs/cpp")
   VOCAB_FILE = Path("vocabulary/cpp/wl_vocab.json")
   VEC_DIR = Path("vectors/cpp/wl")
   ```

2. **Update evaluation script** (`evaluation/cpp/aggregate_all_features_cpp.py`):
   ```python
   SIMILARITY_DIR = Path("evaluation/cpp")
   GROUND_TRUTH = Path("data/cpp/ground_truth.json")
   ```

3. **Uncomment pipeline steps** in `run_cpp_pipeline.sh`

---

## 🚀 Next Steps

### Adding C++ Test Data
1. Create `data/cpp/p1/ref/` with reference implementations
2. Create `data/cpp/p1/s/` with student submissions
3. Add `data/cpp/ground_truth.json` with expected mappings
4. Run pipeline: `./run_cpp_pipeline.sh`

### Extending to More Problems
Follow the same pattern as Java:
- `data/cpp/p2/`, `p3/`, etc.
- Update ground truth file
- Run pipeline

---

## 🔍 Troubleshooting

### Issue: "joern-parse: command not found"
**Solution**: Add Joern to PATH or use full path

### Issue: CES not detecting C++ patterns
**Solution**: Verify `cpg/scripts/cpp/semantic/ces_v3_enhanced.sc` is being used (check logs)

### Issue: Compilation errors
**Note**: Joern parses source code, does NOT compile. Syntax errors may affect CPG quality.

---

For overall framework documentation, see [README.md](./README.md).
For Java-specific documentation, see [JAVA_README.md](./JAVA_README.md).
