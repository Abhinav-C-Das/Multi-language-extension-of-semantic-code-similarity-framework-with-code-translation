# 🚀 CES v3 Enhancement - Quick Reference

## 📊 **10 Fixes to Implement**

| # | Fix | Impact | Effort | Priority | Cases Fixed |
|---|-----|--------|--------|----------|-------------|
| **1** | 🐛 Recursion classification bug | 🔴 Critical | 2-3h | P1 | 33+ |
| **2** | 🔧 Normalize recursive contexts | 🔴 Critical | 1-2h | P1 | 33+ |
| **3** | 🆕 Add TAIL_RECURSIVE pattern | 🟡 High | 3-4h | P2 | 1+ |
| **4** | 🔧 Detect recursive helpers | 🟡 High | 2-3h | P2 | 10+ |
| **5** | 🆕 Multi-function analysis | 🟡 High | 1-2d | P4 | 32 |
| **6** | 🆕 Enhanced STL detection | 🟡 High | 4-6h | P2 | 16 |
| **7** | 🐛 Improve recursion detection | 🟡 Medium | 2-3h | P1 | 33 |
| **8** | 🆕 Add DIRECT_FORMULA | 🟢 Low | 2-3h | P3 | 5-10 |
| **9** | 🆕 Add RECURSIVE_BINARY_SEARCH | 🟢 Low | 2-3h | P3 | 6 |
| **10** | 🔧 Improve BOUNDARY_CHECK | 🟢 Low | 1-2h | P3 | Quality |

---

## ⚡ **Quick Win Strategy** (11-12 hours total)

### **Step 1: Fix Recursion Bugs** (4-5 hours)
```
✅ Fix 2: Normalize contexts (1-2h)
✅ Fix 1: Fix accumulative detection (2-3h)  
✅ Fix 7: Better recursion detection (2-3h)
```
**Impact**: 40-50 cases fixed, +1.5% accuracy

### **Step 2: Add STL Support** (4-6 hours)
```
✅ Fix 6: Enhanced STL algorithms
```
**Impact**: 16 cases fixed (all of p3!), +0.5% accuracy

### **Step 3: Complete Recursion** (3-4 hours)
```
✅ Fix 3: TAIL_RECURSIVE pattern
```
**Impact**: 1+ cases fixed, better pattern quality

---

## 🎯 **Expected Results**

| Phase | Zero Cases | Accuracy | Time |
|-------|------------|----------|------|
| **Before** | 93 (23.2%) | 90.50% | - |
| **After Quick Wins** | ~40 (10%) | ~92% | 11-12h |
| **After Phase 2** | ~30 (7.5%) | ~92.5% | +8-10h |
| **After All** | ~15 (3.8%) | ~93.5% | +10-15h |

---

## 📝 **Code Changes Summary**

### **Fix 1: Recursion Classification** (Line 398-402)
```scala
// BEFORE
val accumulative = calls.exists(c =>
  (c.name == "<operator>.addition" || ...) && c.code.contains(name + "(")
)

// AFTER
val accumulative = 
  calls.exists(...) ||  // Existing
  recursive.exists(call =>  // NEW
    call.argument.code.exists(arg => arg.contains("+") || arg.contains("*"))
  )
```

### **Fix 2: Normalize Contexts** (Line 405-408)
```scala
// BEFORE
cesRecords += CESRecord(s"rec_${name}", ...)

// AFTER
cesRecords += CESRecord("rec_ANY", ...)  // Like loop_ANY
```

### **Fix 6: STL Algorithms** (Line 437-441)
```scala
// BEFORE
cpg.call.filter(c => c.name.contains("accumulate"))

// AFTER
val stlMap = Map(
  "accumulate" -> ("ACCUMULATIVE", "ADD", 1.0),
  "find" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  // ... 7 more
)
cpg.call.filter(c => c.name.startsWith("std::"))
  .foreach { call => /* map to pattern */ }
```

---

## 🧪 **Testing Commands**

### **Test Single Case**:
```bash
# Re-extract CES for p1/s18
./experiments/pipeline/run_ces_v3_extract.sh p1 s18 s

# Check output
cat outputs/p1/s/s18/ces_v3.json
# Should show: "evolution": "ACCUMULATIVE" (not RECOMPUTED)
```

### **Test Full Pipeline**:
```bash
# Re-run CES v3 pipeline
./experiments/pipeline/run_ces_v3_pipeline_local.sh

# Check accuracy
python evaluation/comprehensive_evaluation.py

# Compare results
cat evaluation/comprehensive_evaluation_results.json | grep accuracy
```

### **Test Specific Problems**:
```bash
# p3 (STL) - should go from 15 zeros to 0 zeros
# p13 (recursive binary search) - should go from 6 zeros to 0 zeros
# p1 (recursion) - should go from 6 zeros to 0-1 zeros
```

---

## 📂 **Files to Modify**

1. **`cpg/scripts/semantic/ces_v3_semantic.sc`** - Main implementation
   - Backup first: `cp ces_v3_semantic.sc ces_v3_semantic.sc.backup`
   - Lines to modify: 394-410 (recursion), 437-441 (STL)

2. **Test after changes**:
   - Run extraction: `./experiments/pipeline/run_ces_v3_all_extract.sh`
   - Compute similarity: `python similarity/compute_ces_v3_similarity_local.py`
   - Evaluate: `python evaluation/comprehensive_evaluation.py`

---

## ✅ **Validation Checklist**

After implementing fixes, verify:

- [ ] **p1/s18**: CES output has `"evolution": "ACCUMULATIVE"` (not RECOMPUTED)
- [ ] **p1/s18**: Similarity to ref3 > 0.0 (currently 0.0)
- [ ] **p3/s1**: CES output has STL pattern (currently empty)
- [ ] **p13/s10**: CES output has recursive pattern (currently 0.0)
- [ ] **Overall accuracy**: > 92% (currently 90.5%)
- [ ] **Zero cases**: < 40 (currently 93)

---

## 🔗 **Related Files**

- **Analysis**: `evaluation/CES_ZERO_ANALYSIS_REPORT.txt`
- **Summary**: `evaluation/CES_ZERO_SUMMARY.md`
- **Comparison**: `evaluation/CES_VERSION_COMPARISON.md`
- **Full Plan**: `evaluation/CES_IMPLEMENTATION_PLAN.md` (this file's detailed version)

---

## 💡 **Pro Tips**

1. **Start small**: Fix 2 first (30 min), test immediately
2. **Test incrementally**: Don't implement all fixes at once
3. **Keep backups**: Each fix should have a backup
4. **Monitor accuracy**: Run evaluation after each fix
5. **Focus on ROI**: Fixes 1, 2, 6 give 80% of the gain

---

**Ready to start?** → Begin with **Fix 2** (easiest, immediate impact)
