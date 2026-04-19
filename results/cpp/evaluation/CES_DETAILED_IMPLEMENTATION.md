# 🔧 CES v3 Priority Fixes - Detailed Implementation Guide

## 🎯 Overview

This guide provides step-by-step implementation details for Priority 1-4 fixes to CES v3.

**File to modify**: `cpg/scripts/semantic/ces_v3_semantic.sc`  
**Backup command**: `cp cpg/scripts/semantic/ces_v3_semantic.sc cpg/scripts/semantic/ces_v3_semantic.sc.backup`

---

## 🔴 PRIORITY 1: FIX 2 - Normalize Recursive Contexts

### **Objective**
Change recursive context from function-specific (`rec_sumTail`, `rec_arraySum`) to normalized (`rec_ANY`), matching the loop normalization strategy.

### **Current Code** (Lines 405-408)
```scala
if (accumulative) {
  cesRecords += CESRecord(s"rec_${name}", "return", "ACCUMULATIVE", "ADD", 1.0)
} else {
  cesRecords += CESRecord(s"rec_${name}", "return", "RECOMPUTED", "ASSIGN", 0.9)
}
```

### **New Code**
```scala
// Use normalized context (like loop_ANY)
val recContext = "rec_ANY"

if (accumulative) {
  cesRecords += CESRecord(recContext, "return", "ACCUMULATIVE", "ADD", 1.0)
} else {
  cesRecords += CESRecord(recContext, "return", "RECOMPUTED", "ASSIGN", 0.9)
}
```

### **Testing**
```bash
# Test p1/s18
./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s
cat outputs/p1/s/s18/ces_v3.json
# Expected: {"context": "rec_ANY", ...}

# Test p1/ref3
./experiments/pipeline/run_ces_v3_extract.sh p1 ref3 ref
cat outputs/p1/ref/ref3/ces_v3.json
# Expected: {"context": "rec_ANY", ...}

# Now they should match!
```

### **Impact**: Fixes context mismatch for all 33+ recursive cases

---

## 🔴 PRIORITY 1: FIX 1 - Fix Recursion Classification

### **Objective**
Detect accumulative recursion when `+` or `*` appears in recursive call arguments, not just as separate operator nodes.

### **Problem Analysis**
```cpp
// p1/s18
return sumTail(arr, startIdx + 1, endIdx, accumulator + arr[startIdx]);
                                           ^^^^^^^^^^^^^^^^^^^^^^
// The + is in the ARGUMENT, not a separate operator node!
```

### **Current Code** (Lines 398-402)
```scala
val accumulative =
  calls.exists(c =>
    (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
    c.code.contains(name + "(")
  )
```

### **New Code** (Replace lines 398-408)
```scala
// Check for accumulative pattern in multiple ways
val accumulative =
  // Method 1: Operator nodes (existing)
  calls.exists(c =>
    (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
    c.code.contains(name + "(")
  ) ||
  // Method 2: Check arguments of recursive calls
  recursive.exists { call =>
    val args = call.argument.code.l
    args.exists(arg =>
      (arg.contains("+") || arg.contains("*")) &&
      !arg.contains("++") &&  // Exclude increment
      !arg.contains("--")     // Exclude decrement
    )
  } ||
  // Method 3: Check return statements with arithmetic
  method.ast.isReturn.exists { ret =>
    val retCode = ret.code
    (retCode.contains("+") || retCode.contains("*")) &&
    retCode.contains(name + "(")
  }

val recContext = "rec_ANY"

if (accumulative) {
  cesRecords += CESRecord(recContext, "return", "ACCUMULATIVE", "ADD", 1.0)
} else {
  cesRecords += CESRecord(recContext, "return", "RECOMPUTED", "ASSIGN", 0.9)
}
```

### **Testing**
```bash
# Test cases that should be ACCUMULATIVE
./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s
cat outputs/p1/s/s18/ces_v3.json
# Expected: "evolution": "ACCUMULATIVE" (not RECOMPUTED)

./experiments/pipeline/run_ces_v3_extract.sh p1 s4 s
./experiments/pipeline/run_ces_v3_extract.sh p1 s9 s
# Both should show ACCUMULATIVE
```

### **Impact**: Fixes 33+ cases misclassified as RECOMPUTED

---

## 🔴 PRIORITY 1: FIX 7 - Improve Recursion Detection

### **Objective**
More robust detection of recursive methods, handling edge cases.

### **Current Code** (Line 394)
```scala
val recursive = calls.filter(_.name == name)
```

### **New Code** (Replace line 394)
```scala
// More robust recursion detection
val recursive = calls.filter { call =>
  val callName = call.name
  // Direct match
  callName == name ||
  // Match with parameters (overloaded functions)
  callName.startsWith(name + "(") ||
  // Match with namespace/class prefix
  callName.endsWith("::" + name) ||
  callName.endsWith("." + name) ||
  // Match base name (strip qualifiers)
  callName.split("::").lastOption.contains(name) ||
  callName.split("\\.").lastOption.contains(name)
}
```

### **Testing**
```bash
# Test various recursion styles
./experiments/pipeline/run_ces_v3_extract.sh p13 s2 s  # Binary search
./experiments/pipeline/run_ces_v3_extract.sh p10 s7 s  # Prime check
# Both should detect recursion
```

### **Impact**: Fixes edge cases in recursion detection

---

## 🟡 PRIORITY 2: FIX 3 - Add TAIL_RECURSIVE Pattern

### **Objective**
Distinguish tail recursion (accumulator parameter) from head recursion (computation on return).

### **Implementation** (Add after line 396, inside `if (recursive.nonEmpty)`)

```scala
if (recursive.nonEmpty) {
  
  // === NEW: Detect tail recursion ===
  val paramNames = method.parameter.name.l.map(_.toLowerCase)
  
  val hasAccumulator = paramNames.exists(p =>
    p.contains("acc") ||
    p.contains("accumulator") ||
    p.contains("result") ||
    p.contains("sum") ||
    p.contains("total") ||
    p.contains("product") ||
    p.contains("count")
  )
  
  // Check if recursive call is in tail position (direct return)
  val isTailCall = method.ast.isReturn.exists { ret =>
    // Return directly calls the recursive function
    ret.ast.isCall.exists(c =>
      c.name == name &&
      ret.code.trim.startsWith("return " + name + "(")
    )
  }
  
  // Check for accumulative pattern (from Fix 1)
  val accumulative = // ... (use enhanced logic from Fix 1)
  
  val recContext = "rec_ANY"
  
  // === Pattern Classification ===
  if (hasAccumulator && isTailCall) {
    // Tail recursion with accumulator parameter
    cesRecords += CESRecord(recContext, "return", "TAIL_RECURSIVE", "ACCUMULATE", 1.0)
    
  } else if (accumulative && !isTailCall) {
    // Head recursion: computation happens on return
    cesRecords += CESRecord(recContext, "return", "HEAD_RECURSIVE", "ADD", 1.0)
    
  } else if (accumulative) {
    // Generic accumulative recursion
    cesRecords += CESRecord(recContext, "return", "ACCUMULATIVE", "ADD", 1.0)
    
  } else {
    // Simple recursion without accumulation
    cesRecords += CESRecord(recContext, "return", "SIMPLE_RECURSIVE", "CALL", 0.9)
  }
}
```

### **Pattern Examples**

**TAIL_RECURSIVE**:
```cpp
int sumTail(int arr[], int i, int n, int acc) {
  if (i >= n) return acc;
  return sumTail(arr, i+1, n, acc + arr[i]);  // Tail call with accumulator
}
```

**HEAD_RECURSIVE**:
```cpp
int sumHead(int arr[], int n) {
  if (n == 0) return 0;
  return arr[n-1] + sumHead(arr, n-1);  // Computation on return
}
```

**SIMPLE_RECURSIVE**:
```cpp
int factorial(int n) {
  if (n <= 1) return 1;
  return n * factorial(n-1);  // Simple recursion
}
```

### **Testing**
```bash
# Tail recursion
./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s
# Expected: "evolution": "TAIL_RECURSIVE"

# Head recursion
./experiments/pipeline/run_ces_v3_extract.sh p1 s4 s
# Expected: "evolution": "HEAD_RECURSIVE"

# Simple recursion
./experiments/pipeline/run_ces_v3_extract.sh p13 s2 s
# Expected: "evolution": "SIMPLE_RECURSIVE"
```

### **Impact**: Better pattern granularity, fixes 1+ cases, improves quality

---

## 🟡 PRIORITY 2: FIX 4 - Detect Recursive Helper Functions

### **Objective**
Detect when main function uses recursion via helper function.

### **Implementation** (Add after recursive CES section, around line 410)

```scala
// =======================================================
// RECURSIVE HELPER DETECTION
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>
    val name = method.name
    
    // Skip if already detected as directly recursive
    val isDirectlyRecursive = method.ast.isCall.exists(_.name == name)
    
    if (!isDirectlyRecursive) {
      // Get all non-operator methods this method calls
      val calledMethods = method.ast.isCall
        .name
        .filterNot(_.startsWith("<operator>"))
        .filterNot(_.startsWith("<"))
        .filterNot(_ == name)
        .toSet
      
      // Check if any called method is recursive
      val callsRecursiveHelper = calledMethods.exists { calledName =>
        cpg.method.name(calledName).exists { calledMethod =>
          // Check if called method calls itself
          calledMethod.ast.isCall.exists(c =>
            c.name == calledName ||
            c.name.contains(calledName)
          )
        }
      }
      
      if (callsRecursiveHelper) {
        // This method uses recursion via helper
        cesRecords += CESRecord("rec_ANY", "return", "RECURSIVE_HELPER", "CALL", 0.9)
      }
    }
  }
```

### **Example**
```cpp
// Helper is recursive
int sumHelper(int arr[], int n, int i) {
  if (i == n) return 0;
  return arr[i] + sumHelper(arr, n, i+1);  // Recursive
}

// Main calls helper (not directly recursive)
int arraySum(int arr[], int n) {
  return sumHelper(arr, n, 0);  // Should get RECURSIVE_HELPER pattern
}
```

### **Testing**
```bash
# Test p1/s18 (arraySum calls sumTail)
./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s
cat outputs/p1/s/s18/ces_v3.json
# Expected: Two patterns - one for sumTail (TAIL_RECURSIVE), one for arraySum (RECURSIVE_HELPER)
```

### **Impact**: Fixes 10+ cases where main function uses recursive helper

---

## 🟡 PRIORITY 2: FIX 6 - Enhanced STL Algorithm Detection

### **Objective**
Detect and map 10 common STL algorithms to CES patterns.

### **Current Code** (Lines 437-441)
```scala
cpg.call
  .filter(c => c.name.contains("accumulate"))
  .foreach { call =>
    cesRecords += CESRecord("stl_algo", "return", "ACCUMULATIVE", "ADD", 1.0)
  }
```

### **New Code** (Replace lines 437-441)

```scala
// =======================================================
// ENHANCED STL ALGORITHM DETECTION
// =======================================================

// Map STL algorithms to CES patterns
val stlPatternMap = Map(
  // Accumulation algorithms
  "accumulate" -> ("ACCUMULATIVE", "ADD", 1.0),
  "reduce" -> ("ACCUMULATIVE", "ADD", 1.0),
  "count" -> ("ACCUMULATIVE", "ADD", 0.9),
  "count_if" -> ("ACCUMULATIVE", "ADD", 0.9),
  
  // Search algorithms
  "find" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "find_if" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "find_if_not" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "search" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 0.9),
  "binary_search" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  
  // Min/Max algorithms
  "max_element" -> ("MAX_UPDATE", "COMPARE", 1.0),
  "min_element" -> ("MIN_UPDATE", "COMPARE", 1.0),
  "minmax_element" -> ("MAX_UPDATE", "COMPARE", 0.9),
  
  // Sorting algorithms
  "sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "stable_sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "partial_sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 0.9),
  
  // Transformation algorithms
  "transform" -> ("RECOMPUTED", "ASSIGN", 0.8),
  "for_each" -> ("RECOMPUTED", "ASSIGN", 0.7),
  "copy" -> ("RECOMPUTED", "ASSIGN", 0.6),
  "fill" -> ("RECOMPUTED", "ASSIGN", 0.6)
)

// Detect STL algorithm calls
cpg.call
  .filter { c =>
    c.name.startsWith("std::") ||
    c.name.contains("::") ||
    stlPatternMap.keys.exists(algo => c.name.contains(algo))
  }
  .foreach { call =>
    // Extract algorithm name
    val algoName = if (call.name.contains("::")) {
      call.name.split("::").last
    } else {
      call.name
    }
    
    // Map to CES pattern
    stlPatternMap.get(algoName).foreach { case (evolution, operator, importance) =>
      cesRecords += CESRecord("stl_algo", "return", evolution, operator, importance)
    }
  }
```

### **Testing**
```bash
# Test p3 cases (heavy STL usage)
./experiments/pipeline/run_ces_v3_extract.sh p3 s1 s
cat outputs/p3/s/s1/ces_v3.json
# Expected: STL pattern detected

# Test all p3 students
for i in {1..20}; do
  ./experiments/pipeline/run_ces_v3_extract.sh p3 s$i s 2>/dev/null
  echo "s$i: $(cat outputs/p3/s/s$i/ces_v3.json | grep evolution)"
done
```

### **Impact**: Fixes all 16 p3 cases using STL algorithms

---

## 🔵 PRIORITY 4: FIX 5 - Multi-Function Pattern Analysis

### **Objective**
Analyze patterns in ALL functions (including helpers), not just main function.

### **Current Approach**
```scala
// Only analyzes loops in main/top-level code
cpg.controlStructure.filter(...).foreach { loop => ... }
```

### **New Approach**

```scala
// =======================================================
// MULTI-FUNCTION LOOP ANALYSIS
// =======================================================

// Get all non-external methods
val allMethods = cpg.method.filter(!_.isExternal).l

// Track which methods are helpers vs main
val mainMethods = Set("main", "arraySum", "binarySearch", "reverseString", "isPrime")
val isMainMethod = (name: String) => mainMethods.exists(m => name.contains(m))

// Analyze loops in ALL methods
allMethods.foreach { method =>
  val methodName = method.name
  val isMain = isMainMethod(methodName)
  
  // Find loops in this method
  method.controlStructure
    .filter(cs =>
      cs.controlStructureType == "FOR" ||
      cs.controlStructureType == "WHILE" ||
      cs.controlStructureType == "DO"
    )
    .foreach { loop =>
      
      val canonVars = canonIdMap.getOrElse(methodName, Map())
      val loopContext = "loop_ANY"
      
      // ... (existing loop pattern extraction logic)
      // All the SEARCH_WITH_RETURN, COMPARISON_CHAIN, etc. patterns
      
      // Mark patterns from helper functions with lower importance
      val importanceMultiplier = if (isMain) 1.0 else 0.8
      
      // When recording patterns, adjust importance
      cesRecords += CESRecord(
        loopContext,
        lhs,
        evolution,
        operator,
        baseImportance * importanceMultiplier
      )
    }
}
```

### **Alternative: Pattern Aggregation**

```scala
// Simpler approach: Aggregate all patterns from all functions
val allPatterns = mutable.Set[CESRecord]()

cpg.method.filter(!_.isExternal).foreach { method =>
  // Extract patterns from this method
  val methodPatterns = extractPatternsFromMethod(method)
  allPatterns ++= methodPatterns
}

// Deduplicate and output
allPatterns.foreach { pattern =>
  cesRecords += pattern
}
```

### **Testing**
```bash
# Test p12/s10 (has helper swap function)
./experiments/pipeline/run_ces_v3_extract.sh p12 s10 s
cat outputs/p12/s/s10/ces_v3.json
# Expected: Should detect CONDITIONAL_SWAP from swap helper

# Test p20 cases (many use helpers)
./experiments/pipeline/run_ces_v3_extract.sh p20 s10 s
```

### **Impact**: Fixes 32 cases with helper functions

---

## 📋 Implementation Checklist

### **Phase 1: Quick Wins** (Day 1)
- [ ] Backup ces_v3_semantic.sc
- [ ] Implement Fix 2 (normalize contexts)
- [ ] Test p1/s18 vs ref3 similarity
- [ ] Implement Fix 1 (fix accumulative detection)
- [ ] Test p1/s18, s4, s9 classification
- [ ] Implement Fix 7 (better recursion detection)
- [ ] Run full pipeline, check accuracy

### **Phase 2: Enhancements** (Day 2-3)
- [ ] Implement Fix 6 (STL algorithms)
- [ ] Test all p3 cases
- [ ] Implement Fix 3 (tail recursion pattern)
- [ ] Test p1/s18 pattern type
- [ ] Implement Fix 4 (recursive helpers)
- [ ] Run full pipeline, check accuracy

### **Phase 3: Advanced** (Day 4-5)
- [ ] Implement Fix 5 (multi-function analysis)
- [ ] Test p12, p20 cases
- [ ] Run full pipeline
- [ ] Final accuracy check
- [ ] Document results

---

## 🧪 Complete Testing Workflow

```bash
# 1. Backup
cp cpg/scripts/semantic/ces_v3_semantic.sc cpg/scripts/semantic/ces_v3_semantic.sc.backup

# 2. Implement fixes

# 3. Test single case
./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s
cat outputs/p1/s/s18/ces_v3.json

# 4. Run full extraction
./experiments/pipeline/run_ces_v3_all_extract.sh

# 5. Compute similarity
python similarity/compute_ces_v3_similarity_local.py

# 6. Evaluate accuracy
python evaluation/comprehensive_evaluation.py

# 7. Check results
cat evaluation/comprehensive_evaluation_results.json | grep accuracy

# 8. Re-run zero analysis
python evaluation/analyze_ces_zeros.py
cat evaluation/CES_ZERO_ANALYSIS_REPORT.txt | head -20
```

---

## 📊 Expected Results

| After Phase | Zero Cases | Accuracy | Fixes Applied |
|-------------|------------|----------|---------------|
| **Baseline** | 93 (23.2%) | 90.50% | None |
| **Phase 1** | ~40 (10%) | ~92% | Fix 1,2,7 |
| **Phase 2** | ~25 (6.2%) | ~92.5% | + Fix 3,4,6 |
| **Phase 3** | ~15 (3.8%) | ~93% | + Fix 5 |

---

**File**: `cpg/scripts/semantic/ces_v3_semantic.sc`  
**Total Changes**: ~150-200 lines added/modified  
**Estimated Time**: 20-30 hours total
