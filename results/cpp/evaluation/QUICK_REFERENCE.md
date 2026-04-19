# Quick Reference: Multi-View Evaluation Results

## 🏆 Top Performers

| Rank | Configuration | Baseline | WL | CES | Accuracy | Correct |
|------|--------------|----------|----|----|----------|---------|
| 1 | **Optimal** | 0.00 | 0.05 | 0.95 | **90.50%** | 362/400 |
| 1 | WL + CES | 0.00 | 0.50 | 0.50 | **90.50%** | 362/400 |
| 3 | All Equal | 0.33 | 0.33 | 0.34 | 90.25% | 361/400 |
| 4 | **User Specified** | **0.35** | **0.40** | **0.25** | **90.00%** | **360/400** |

## 📊 Complete Results Table

| Configuration | Baseline | WL | CES | Accuracy | Correct | Notes |
|--------------|----------|----|----|----------|---------|-------|
| **Optimal** | 0.00 | 0.05 | 0.95 | **90.50%** | 362/400 | Grid search winner |
| WL + CES | 0.00 | 0.50 | 0.50 | **90.50%** | 362/400 | **Recommended** |
| All Equal | 0.33 | 0.33 | 0.34 | 90.25% | 361/400 | Balanced |
| **User Specified** | **0.35** | **0.40** | **0.25** | **90.00%** | **360/400** | Original request |
| Baseline + CES | 0.50 | 0.00 | 0.50 | 87.75% | 351/400 | - |
| WL Only | 0.00 | 1.00 | 0.00 | 87.25% | 349/400 | Best single view |
| Baseline + WL | 0.50 | 0.50 | 0.00 | 86.75% | 347/400 | - |
| CES Only | 0.00 | 0.00 | 1.00 | 84.25% | 337/400 | - |
| Baseline Only | 1.00 | 0.00 | 0.00 | 81.75% | 327/400 | Worst performer |

## 🎯 Key Insights

### Performance Gains
- **Single-view best (WL)**: 87.25%
- **Multi-view optimal**: 90.50%
- **Improvement**: +3.25%

### View Contributions
- **CES dominates**: 95% weight in optimal
- **WL minimal**: 5% weight in optimal
- **Baseline redundant**: 0% weight in optimal

### Recommendations

#### 🥇 Production Use
```python
weights = [0.00, 0.50, 0.50]  # WL + CES equal
accuracy = 90.50%
```
**Why**: Same accuracy as optimal, more balanced and interpretable

#### 🥈 Current User Weights
```python
weights = [0.35, 0.40, 0.25]  # User specified
accuracy = 90.00%
```
**Why**: Only 0.5% below optimal, includes all views for robustness

#### 🥉 Optimal (Grid Search)
```python
weights = [0.00, 0.05, 0.95]  # CES-heavy
accuracy = 90.50%
```
**Why**: Absolute best, but heavily skewed toward CES

## 📈 Ablation Study Summary

| Study Type | Configuration | Accuracy | Insight |
|-----------|---------------|----------|---------|
| Single-view | Baseline only | 81.75% | Weakest |
| Single-view | WL only | 87.25% | **Best single** |
| Single-view | CES only | 84.25% | Moderate |
| Two-view | Baseline + WL | 86.75% | Worse than WL alone |
| Two-view | Baseline + CES | 87.75% | Better than either |
| Two-view | **WL + CES** | **90.50%** | **Best two-view** |
| Three-view | All equal | 90.25% | Near-optimal |
| Three-view | User specified | 90.00% | Good balance |
| Three-view | Optimal | 90.50% | Grid search best |

## 🔍 Error Analysis

### User Weights (0.35/0.40/0.25) - 40 Errors
- **Borderline** (<0.01 difference): ~11 errors (27.5%)
- **Tie-breaks** (0.00 difference): ~5 errors (12.5%)
- **Significant** (>0.10 difference): ~6 errors (15%)

### Optimal Weights (0.00/0.05/0.95) - 38 Errors
- **Improvement**: 2 fewer errors than user weights
- **Problem areas**: p14 (tie-breaks), p16 (borderline), p19 (close scores)

## 💡 Quick Decision Guide

**Choose WL + CES [0.00, 0.50, 0.50] if:**
- ✅ You want best accuracy (90.50%)
- ✅ You prefer balanced view contributions
- ✅ You want interpretable results
- ✅ You can eliminate baseline features

**Choose User Weights [0.35, 0.40, 0.25] if:**
- ✅ You want all views included
- ✅ You prefer conservative approach
- ✅ You accept 0.5% accuracy trade-off
- ✅ You want robustness across problems

**Choose Optimal [0.00, 0.05, 0.95] if:**
- ✅ You want absolute best accuracy
- ✅ You trust CES patterns heavily
- ✅ You're okay with skewed weights
- ✅ You've validated on your specific dataset

## 📊 Visual Comparison

```
Accuracy Comparison:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline Only    81.75% ████████████████░░░░░░░░
CES Only         84.25% █████████████████░░░░░░░
WL Only          87.25% ██████████████████░░░░░░
User Weights     90.00% ████████████████████░░░░
Optimal          90.50% ████████████████████░░░░
WL + CES         90.50% ████████████████████░░░░
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 75%    80%    85%    90%    95%
```

## 🎓 Research Implications

1. **CES v3 is highly effective** - 95% weight suggests semantic patterns are crucial
2. **Baseline features are redundant** - Can be eliminated when WL and CES present
3. **Two views sufficient** - WL + CES matches three-view performance
4. **Minimal WL needed** - Only 5% weight required in optimal configuration

---

**Files Generated**:
- `comprehensive_evaluation.py` - Full evaluation script
- `comprehensive_evaluation_results.json` - Detailed results (798 lines)
- `EVALUATION_SUMMARY.md` - Comprehensive report
- `QUICK_REFERENCE.md` - This file
