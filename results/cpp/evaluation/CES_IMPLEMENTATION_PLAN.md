# 🛠️ CES v3 Enhancement Implementation Plan

## 📊 Overview

**Current State**: 93 cases with CES = 0.0 (23.2% of dataset)  
**Target State**: < 20 cases with CES = 0.0 (< 5% of dataset)  
**Expected Accuracy Gain**: +2-3% (90.5% → 92-93.5%)

---

## 🔴 **PRIORITY 1: Critical Fixes (Immediate Impact)**

### **Fix 1: Recursion Pattern Classification Bug** 🐛
**Impact**: Fixes 33+ cases  
**Effort**: 2-3 hours  
**Difficulty**: ⭐⭐ Medium

**Problem**: 
- s18 has `accumulator + arr[startIdx]` but classified as RECOMPUTED
- Detection only finds `<operator>.addition` nodes, not additions in arguments

**Current Code** (Lines 398-402):
```scala
val accumulative =
  calls.exists(c =>
    (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
    c.code.contains(name + "(")
  )
```

**Fixed Code**:
```scala
val accumulative =
  // Check for operator nodes
  calls.exists(c =>
    (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
    c.code.contains(name + "(")
  ) ||
  // Check for + or * in recursive call arguments
  recursive.exists(call =>
    call.argument.code.exists(arg =>
      arg.contains("+") || arg.contains("*")
    )
  )
```

**Test Cases**:
- p1/s18: Should be ACCUMULATIVE (has `accumulator + arr[startIdx]`)
- p1/s4: Should be ACCUMULATIVE (has `arr[index] + sumArray`)
- p1/s9: Should be ACCUMULATIVE (has `arr[index] + sumHelper`)

---

### **Fix 2: Normalize Recursive Contexts** 🔧
**Impact**: Fixes 33+ cases  
**Effort**: 1-2 hours  
**Difficulty**: ⭐ Easy

**Problem**: 
- Context uses function name: `rec_sumTail` vs `rec_arraySum`
- Helper functions never match main functions

**Current Code** (Lines 405-408):
```scala
if (accumulative) {
  cesRecords += CESRecord(s"rec_${name}", "return", "ACCUMULATIVE", "ADD", 1.0)
} else {
  cesRecords += CESRecord(s"rec_${name}", "return", "RECOMPUTED", "ASSIGN", 0.9)
}
```

**Fixed Code**:
```scala
// Use normalized context like loops
val recContext = "rec_ANY"  // Instead of rec_${name}

if (accumulative) {
  cesRecords += CESRecord(recContext, "return", "ACCUMULATIVE", "ADD", 1.0)
} else {
  cesRecords += CESRecord(recContext, "return", "RECOMPUTED", "ASSIGN", 0.9)
}
```

**Rationale**: Same as loop normalization (loop_FOR → loop_ANY)

---

### **Fix 3: Add TAIL_RECURSIVE Pattern** 🆕
**Impact**: Fixes 1+ cases (p3/s20, potentially more)  
**Effort**: 3-4 hours  
**Difficulty**: ⭐⭐⭐ Hard

**Problem**: Tail recursion with accumulator not distinguished from head recursion

**Implementation**:
```scala
// After line 396 (inside recursive method check)
if (recursive.nonEmpty) {
  
  // Check for accumulator parameter
  val hasAccumulator = method.parameter.name.exists(p =>
    p.toLowerCase.contains("acc") ||
    p.toLowerCase.contains("accumulator") ||
    p.toLowerCase.contains("result") ||
    p.toLowerCase.contains("sum") ||
    p.toLowerCase.contains("total")
  )
  
  // Check if recursive call is in tail position (return statement)
  val isTailCall = method.ast.isReturn
    .exists(ret =>
      ret.ast.isCall.exists(_.name == name)
    )
  
  val accumulative = // ... (existing logic)
  
  if (hasAccumulator && isTailCall) {
    // Tail recursion with accumulator
    cesRecords += CESRecord("rec_ANY", "return", "TAIL_RECURSIVE", "ACCUMULATE", 1.0)
  } else if (accumulative) {
    // Head recursion with computation on return
    cesRecords += CESRecord("rec_ANY", "return", "HEAD_RECURSIVE", "ADD", 1.0)
  } else {
    // Simple recursion
    cesRecords += CESRecord("rec_ANY", "return", "SIMPLE_RECURSIVE", "CALL", 0.9)
  }
}
```

**New Patterns**:
1. **TAIL_RECURSIVE**: `func(arr, i+1, n, acc + arr[i])`
2. **HEAD_RECURSIVE**: `arr[n-1] + func(arr, n-1)`
3. **SIMPLE_RECURSIVE**: Everything else

---

### **Fix 4: Detect Recursive Helper Functions** 🔧
**Impact**: Fixes 10+ cases  
**Effort**: 2-3 hours  
**Difficulty**: ⭐⭐ Medium

**Problem**: `arraySum` calls `sumHelper`, but only `sumHelper` is detected as recursive

**Implementation**:
```scala
// After recursive CES section (line 410)

// Detect methods that call recursive helpers
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>
    val name = method.name
    
    // Get all methods this method calls
    val calledMethods = method.ast.isCall
      .name.filterNot(_.startsWith("<operator>"))
      .filterNot(_ == name)  // Exclude self
      .toSet
    
    // Check if any called method is recursive
    val callsRecursiveHelper = calledMethods.exists { calledName =>
      cpg.method.name(calledName).exists { calledMethod =>
        calledMethod.ast.isCall.name(calledName).nonEmpty
      }
    }
    
    if (callsRecursiveHelper) {
      // This method uses recursion via helper
      cesRecords += CESRecord("rec_ANY", "return", "RECURSIVE_HELPER", "CALL", 0.9)
    }
  }
```

**Test Cases**:
- p1/s18: `arraySum` should get RECURSIVE_HELPER pattern
- p1/s13: `arraySum` should get RECURSIVE_HELPER pattern

---

## 🟡 **PRIORITY 2: Important Enhancements (High Value)**

### **Fix 6: Enhanced STL Algorithm Detection** 🆕
**Impact**: Fixes 16 cases (all of p3!)  
**Effort**: 4-6 hours  
**Difficulty**: ⭐⭐⭐ Hard

**Current Code** (Lines 437-441):
```scala
cpg.call
  .filter(c => c.name.contains("accumulate"))
  .foreach { call =>
    cesRecords += CESRecord("stl_algo", "return", "ACCUMULATIVE", "ADD", 1.0)
  }
```

**Enhanced Code**:
```scala
// Map STL algorithms to CES patterns
val stlPatternMap = Map(
  "accumulate" -> ("ACCUMULATIVE", "ADD", 1.0),
  "find" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "find_if" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "count" -> ("ACCUMULATIVE", "ADD", 0.9),
  "count_if" -> ("ACCUMULATIVE", "ADD", 0.9),
  "sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "max_element" -> ("MAX_UPDATE", "COMPARE", 1.0),
  "min_element" -> ("MIN_UPDATE", "COMPARE", 1.0),
  "transform" -> ("RECOMPUTED", "ASSIGN", 0.8),
  "for_each" -> ("RECOMPUTED", "ASSIGN", 0.7)
)

cpg.call
  .filter(c => c.name.startsWith("std::") || c.name.contains("::"))
  .foreach { call =>
    val algoName = call.name.split("::").last
    
    stlPatternMap.get(algoName).foreach { case (evolution, operator, importance) =>
      cesRecords += CESRecord("stl_algo", "return", evolution, operator, importance)
    }
  }
```

**Test Cases**:
- p3/s1: `std::accumulate` → ACCUMULATIVE
- p3/s10: `std::max_element` → MAX_UPDATE

---

### **Fix 7: Improve Recursion Detection** 🐛
**Impact**: Fixes 33 "DIRECT_COMPUTATION" misclassifications  
**Effort**: 2-3 hours  
**Difficulty**: ⭐⭐ Medium

**Problem**: Simple name matching fails for many cases

**Current Code** (Line 394):
```scala
val recursive = calls.filter(_.name == name)
```

**Enhanced Code**:
```scala
// More robust recursion detection
val recursive = calls.filter { call =>
  // Direct self-call
  call.name == name ||
  // Call to overloaded version (same base name)
  call.name.startsWith(name + "(") ||
  // Call with namespace/class prefix
  call.name.endsWith("::" + name) ||
  call.name.endsWith("." + name)
}

// Also check if method is called from within itself (AST-based)
val isRecursive = recursive.nonEmpty || 
  method.ast.isCall.exists(c =>
    c.methodFullName.contains(method.fullName)
  )
```

---

## 🟢 **PRIORITY 3: Nice-to-Have (Polish)**

### **Fix 8: Add DIRECT_FORMULA Pattern** 🆕
**Impact**: Fixes 5-10 cases (true direct computations)  
**Effort**: 2-3 hours  
**Difficulty**: ⭐⭐ Medium

**Implementation**:
```scala
// After recursive CES section
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>
    val hasLoops = method.controlStructure
      .exists(cs =>
        cs.controlStructureType == "FOR" ||
        cs.controlStructureType == "WHILE" ||
        cs.controlStructureType == "DO"
      )
    
    val isRecursive = method.ast.isCall.exists(_.name == method.name)
    
    // No loops, no recursion, has return with computation
    if (!hasLoops && !isRecursive) {
      val hasComputation = method.ast.isReturn.exists(ret =>
        ret.ast.isCall.exists(c =>
          c.name.contains("operator") ||
          c.name.contains("*") ||
          c.name.contains("+") ||
          c.name.contains("/")
        )
      )
      
      if (hasComputation) {
        cesRecords += CESRecord("direct", "return", "DIRECT_FORMULA", "COMPUTE", 0.8)
      }
    }
  }
```

**Examples**:
- `return n * (n + 1) / 2` (sum formula)
- `return (high + low) / 2` (average)

---

### **Fix 9: Add RECURSIVE_BINARY_SEARCH Pattern** 🆕
**Impact**: Fixes 6 cases (p13)  
**Effort**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ Hard

**Implementation**:
```scala
// Inside recursive method check
if (recursive.nonEmpty) {
  // Check for binary search pattern
  val hasMidpoint = method.ast.isIdentifier.name
    .exists(n => n == "mid" || n == "m" || n == "middle")
  
  val hasConditionalRecursion = method.ast.isControlStructure
    .exists(cs =>
      cs.controlStructureType == "IF" &&
      cs.ast.isCall.exists(_.name == name)
    )
  
  if (hasMidpoint && hasConditionalRecursion) {
    cesRecords += CESRecord("rec_ANY", "return", "RECURSIVE_BINARY_SEARCH", "NARROW", 1.0)
  }
}
```

---

### **Fix 10: Improve BOUNDARY_CHECK Detection** 🔧
**Impact**: Better pattern quality  
**Effort**: 1-2 hours  
**Difficulty**: ⭐ Easy

**Current Code** (Lines 212-228):
```scala
val boundaryChecks = loop.ast.isControlStructure
  .filter(_.controlStructureType == "IF")
  .condition.code
  .filter(c => c.contains("<") || c.contains(">") || c.contains("length"))
  .l

if (boundaryChecks.nonEmpty) {
  cesRecords += CESRecord(loopContext, "BOUNDARY", "BOUNDARY_CHECK", "guard", 0.8)
}
```

**Problem**: Records once per loop, even if multiple boundary checks

**Enhanced Code**:
```scala
// Only record if boundary check is INSIDE loop body (not loop condition)
val boundaryChecks = loop.ast.isControlStructure
  .filter(_.controlStructureType == "IF")
  .filterNot(_.inAst.isControlStructure.exists(_.eq(loop)))  // Not the loop condition itself
  .condition.code
  .filter(c =>
    (c.contains("<") || c.contains(">")) &&
    (c.contains("length") || c.contains("size") || c.contains("n"))
  )
  .l

// Only record if there are actual boundary checks (not just loop condition)
if (boundaryChecks.nonEmpty) {
  cesRecords += CESRecord(loopContext, "BOUNDARY", "BOUNDARY_CHECK", "guard", 0.8)
}
```

---

## 🔵 **PRIORITY 4: Advanced (Optional)**

### **Fix 5: Multi-Function Pattern Analysis** 🆕
**Impact**: Fixes 32 cases  
**Effort**: 1-2 days  
**Difficulty**: ⭐⭐⭐⭐ Very Hard

**Problem**: Patterns in helper functions (swap, reverse) not detected

**Current Limitation**:
```scala
// Only analyzes loops at top level
cpg.controlStructure.filter(...).foreach { loop => ... }
```

This misses patterns like:
```cpp
// Helper function with swap pattern
void swap(char *a, char *b) {
  char temp = *a;  // CONDITIONAL_SWAP pattern here!
  *a = *b;
  *b = temp;
}

// Main function calls helper
void reverseString(char str[]) {
  // ... calls swap() but CES doesn't see the swap pattern
}
```

**Implementation Strategy**:
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

**Alternative Approach (Simpler)**:
```scala
// Aggregate all patterns from all functions
val allPatterns = mutable.Set[CESRecord]()

cpg.method.filter(!_.isExternal).foreach { method =>
  // Extract patterns from this method
  val methodPatterns = extractPatternsFromMethod(method)
  allPatterns ++= methodPatterns
}

// Deduplicate and output
allPatterns.toSeq.distinct.foreach { pattern =>
  cesRecords += pattern
}
```

**Challenges**:
- Need to aggregate patterns from multiple functions
- Avoid double-counting when main calls helper
- Determine which patterns are "core" vs "utility"
- Handle recursive helper calls

**Test Cases**:
- p12/s10: Helper swap function (should detect CONDITIONAL_SWAP)
- p20/s10-s20: Various helper patterns
- p4/s13, s16, s19, s20: Helper functions

**Impact**: Fixes 32 COMPLEX_STRUCTURE cases

---

## 📋 **Implementation Checklist**

### **Phase 1: Quick Wins (1-2 days)**
- [ ] Fix 1: Recursion pattern classification bug
- [ ] Fix 2: Normalize recursive contexts
- [ ] Fix 7: Improve recursion detection
- [ ] **Expected Impact**: Fix 40-50 cases, +1.5% accuracy

### **Phase 2: Major Enhancements (3-5 days)**
- [ ] Fix 3: Add TAIL_RECURSIVE pattern
- [ ] Fix 4: Detect recursive helper functions
- [ ] Fix 6: Enhanced STL algorithm detection
- [ ] **Expected Impact**: Fix 20-30 cases, +1% accuracy

### **Phase 3: Polish (2-3 days)**
- [ ] Fix 8: Add DIRECT_FORMULA pattern
- [ ] Fix 9: Add RECURSIVE_BINARY_SEARCH pattern
- [ ] Fix 10: Improve BOUNDARY_CHECK detection
- [ ] **Expected Impact**: Fix 5-10 cases, +0.5% accuracy

### **Phase 4: Advanced (Optional, 5-7 days)**
- [ ] Fix 5: Multi-function pattern analysis
- [ ] **Expected Impact**: Fix 30+ cases, +1% accuracy

---

## 🎯 **Expected Results**

### **Before Fixes**:
- Zero-score cases: 93 (23.2%)
- Accuracy: 90.50%

### **After Phase 1+2**:
- Zero-score cases: ~30-40 (7.5-10%)
- Accuracy: ~92-93%

### **After All Phases**:
- Zero-score cases: ~10-20 (2.5-5%)
- Accuracy: ~93-94%

---

## 📝 **Testing Strategy**

### **For Each Fix**:
1. Implement the fix in `ces_v3_semantic.sc`
2. Re-run extraction for test cases:
   ```bash
   ./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s
   cat outputs/p1/s/s18/ces_v3.json
   ```
3. Verify pattern is correct
4. Re-run full pipeline:
   ```bash
   ./experiments/pipeline/run_ces_v3_pipeline_local.sh
   ```
5. Check accuracy:
   ```bash
   python evaluation/comprehensive_evaluation.py
   ```
6. Compare before/after

### **Key Test Cases**:
- **p1/s18**: Tail recursion (should be TAIL_RECURSIVE or ACCUMULATIVE)
- **p3/s1**: STL accumulate (should be ACCUMULATIVE)
- **p13/s10**: Recursive binary search (should be RECURSIVE_BINARY_SEARCH)
- **p12/s10**: Helper swap function (should detect swap in helper)
- **p16/s1**: Recursive linear search (should be HEAD_RECURSIVE)

---

## 💡 **Recommendations**

### **Start With**:
1. Fix 1 + Fix 2 (recursion bugs) - **Highest ROI**
2. Fix 6 (STL support) - **Fixes entire p3**
3. Fix 3 (tail recursion) - **Completes recursion support**

### **Skip For Now**:
- Fix 5 (multi-function) - Too complex, save for later
- Fix 10 (boundary check) - Low impact

### **Quick Win Order**:
1. Fix 2 (30 min) → Normalize contexts
2. Fix 1 (2 hours) → Fix accumulative detection
3. Fix 7 (2 hours) → Better recursion detection
4. Fix 6 (4 hours) → STL algorithms
5. Fix 3 (3 hours) → Tail recursion pattern

**Total Time for Quick Wins**: ~11-12 hours  
**Expected Gain**: +2-2.5% accuracy

---

**File Location**: `cpg/scripts/semantic/ces_v3_semantic.sc`  
**Backup First**: `cp ces_v3_semantic.sc ces_v3_semantic.sc.backup`
