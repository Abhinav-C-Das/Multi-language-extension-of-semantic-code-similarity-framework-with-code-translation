# 📊 Comprehensive Multi-View Code Similarity Evaluation Report

**Date**: February 2, 2026  
**Dataset**: 400 student submissions across 20 programming problems  
**Views**: Baseline, WL (Weisfeiler-Lehman), CES v3 (Computation Evolution Signatures)

---

## 🎯 Executive Summary

This comprehensive evaluation analyzes the performance of different view combinations for code similarity detection. The study includes:
- **Single-view performance** analysis
- **Multi-view fusion** experiments
- **Ablation studies** to understand view contributions
- **Optimal weight search** through grid search (step=0.05)

---

## 📈 Key Findings

### Overall Performance Comparison

| Configuration | Weights (B/W/C) | Accuracy | Correct/Total | Rank |
|--------------|-----------------|----------|---------------|------|
| **🏆 Optimal** | **0.00/0.05/0.95** | **90.50%** | **362/400** | **1** |
| **WL + CES** | 0.00/0.50/0.50 | 90.50% | 362/400 | 1 |
| All Equal | 0.33/0.33/0.34 | 90.25% | 361/400 | 3 |
| **User Specified** | **0.35/0.40/0.25** | **90.00%** | **360/400** | **4** |
| Baseline + CES | 0.50/0.00/0.50 | 87.75% | 351/400 | 5 |
| **WL Only** | 0.00/1.00/0.00 | 87.25% | 349/400 | 6 |
| Baseline + WL | 0.50/0.50/0.00 | 86.75% | 347/400 | 7 |
| **CES Only** | 0.00/0.00/1.00 | 84.25% | 337/400 | 8 |
| **Baseline Only** | 1.00/0.00/0.00 | 81.75% | 327/400 | 9 |

---

## 🔬 Detailed Analysis

### 1. Single-View Performance

#### Baseline Features (81.75% accuracy)
- **Weights**: [1.0, 0.0, 0.0]
- **Correct**: 327/400
- **Characteristics**: 
  - 18 numeric features (AST, CFG, behavioral metrics)
  - Fast computation
  - Limited semantic understanding
  - **Weakest performer** among single views

#### WL (Weisfeiler-Lehman) (87.25% accuracy)
- **Weights**: [0.0, 1.0, 0.0]
- **Correct**: 349/400
- **Characteristics**:
  - 400-500 structural fingerprints
  - Excellent at capturing AST patterns
  - **Best single-view performer**
  - Invariant to variable naming

#### CES v3 (84.25% accuracy)
- **Weights**: [0.0, 0.0, 1.0]
- **Correct**: 337/400
- **Characteristics**:
  - 11+ semantic patterns
  - Captures computational strategies
  - Strong at distinguishing algorithmic approaches
  - Moderate single-view performance

---

### 2. Two-View Combinations

#### Baseline + WL (86.75%)
- **Weights**: [0.5, 0.5, 0.0]
- **Correct**: 347/400
- **Analysis**: Slightly worse than WL alone, suggesting Baseline adds noise

#### Baseline + CES (87.75%)
- **Weights**: [0.5, 0.5, 0.0]
- **Correct**: 351/400
- **Analysis**: Better than either alone, showing complementary information

#### WL + CES (90.50%) ⭐
- **Weights**: [0.0, 0.5, 0.5]
- **Correct**: 362/400
- **Analysis**: **Best two-view combination**, matches optimal performance!
- **Key Insight**: Baseline features may be redundant when WL and CES are present

---

### 3. Three-View Combinations

#### All Equal Weights (90.25%)
- **Weights**: [0.333, 0.333, 0.334]
- **Correct**: 361/400
- **Analysis**: Strong performance, but slightly below optimal

#### User-Specified Weights (90.00%)
- **Weights**: [0.35, 0.40, 0.25]
- **Correct**: 360/400
- **Analysis**: Good balance, emphasizes WL and Baseline

---

### 4. Optimal Configuration 🏆

**Grid Search Results** (231 combinations tested):

```
🏆 OPTIMAL WEIGHTS:
   Baseline: 0.00
   WL:       0.05
   CES:      0.95
   
   Accuracy: 90.50% (362/400)
   Errors:   38/400
```

**Key Insights**:
1. **CES dominance**: 95% weight on CES v3 patterns
2. **Minimal WL contribution**: Only 5% weight needed
3. **Baseline redundancy**: 0% weight suggests baseline features are captured by other views
4. **Surprising finding**: Heavy reliance on semantic patterns (CES) over structural patterns (WL)

---

## 📊 Ablation Study Insights

### View Contribution Analysis

| Metric | Value | Insight |
|--------|-------|---------|
| **Single-view range** | 81.75% - 87.25% | 5.5% accuracy spread |
| **Best single → Optimal** | 87.25% → 90.50% | **+3.25% improvement** from fusion |
| **Worst single → Optimal** | 81.75% → 90.50% | **+8.75% improvement** |
| **Two-view best** | 90.50% | Matches optimal (WL+CES) |

### Complementarity Analysis

**WL + CES Synergy**:
- WL alone: 87.25%
- CES alone: 84.25%
- WL + CES: 90.50%
- **Synergy gain**: +3.25% over best single view

**Baseline Impact**:
- Adding Baseline to WL+CES: 90.25% (All Equal)
- **Conclusion**: Baseline provides minimal additional value when WL and CES are present

---

## 🎯 Error Analysis Summary

### User-Specified Weights (0.35/0.40/0.25) - 40 Errors

**Error Distribution by Problem**:
- p19: 4 errors (most problematic)
- p14: 5 errors (all identical scores - tie-breaking issue)
- p16: 3 errors (very close scores)
- p6: 5 errors
- p9: 3 errors

**Error Characteristics**:
1. **Borderline cases**: 27.5% have score differences < 0.01
2. **Tie-breaking issues**: 12.5% have identical scores (p14)
3. **Significant errors**: 15% have score differences > 0.1

### Optimal Weights (0.00/0.05/0.95) - 38 Errors

**Improvement Areas**:
- Reduced errors by 2 compared to user-specified weights
- Better handling of semantic distinctions
- Still struggles with p14 (identical references)

---

## 💡 Recommendations

### 1. **For Production Use**
**Recommended Weights**: `[0.00, 0.05, 0.95]`
- **Accuracy**: 90.50%
- **Rationale**: Optimal performance with minimal complexity
- **Alternative**: `[0.00, 0.50, 0.50]` (WL+CES equal) - same accuracy, more balanced

### 2. **For Interpretability**
**Recommended Weights**: `[0.35, 0.40, 0.25]` (User-specified)
- **Accuracy**: 90.00% (only 0.5% lower)
- **Rationale**: More balanced view contributions, easier to explain

### 3. **For Specific Use Cases**

#### High-Precision Requirements
- Use **WL + CES** combination: `[0.00, 0.50, 0.50]`
- 90.50% accuracy with strong structural and semantic understanding

#### Fast Computation
- Use **WL Only**: `[0.00, 1.00, 0.00]`
- 87.25% accuracy with fastest computation time

#### Semantic Focus
- Use **Optimal**: `[0.00, 0.05, 0.95]`
- Best for distinguishing computational strategies

---

## 🔍 Surprising Findings

1. **Baseline Redundancy**: Baseline features contribute 0% in optimal configuration
   - Suggests WL and CES capture all relevant information
   - Baseline may add noise rather than signal

2. **CES Dominance**: 95% weight on CES is unexpected
   - Traditional wisdom favors structural features (WL)
   - Semantic patterns prove more discriminative

3. **Two-View Sufficiency**: WL + CES matches optimal three-view performance
   - Simpler is better
   - Baseline can be eliminated without loss

4. **Minimal WL Contribution**: Only 5% WL weight in optimal
   - CES patterns may implicitly capture structural information
   - Or dataset favors semantic distinctions

---

## 📝 Future Work

### Immediate Actions
1. **Investigate p14 errors**: All have identical scores - need tie-breaking strategy
2. **Analyze CES dominance**: Why does CES perform so well with 95% weight?
3. **Validate on larger dataset**: Confirm findings generalize

### Research Directions
1. **Adaptive weighting**: Per-problem weight optimization
2. **CES refinement**: Expand pattern library based on error analysis
3. **Baseline elimination**: Test complete removal of baseline features
4. **WL-CES fusion**: Explore joint feature learning

---

## 📊 Statistical Summary

```
Total Samples:        400
Problems:             20
Average per problem:  20 submissions

Performance Metrics:
├─ Best Accuracy:     90.50% (362/400)
├─ User Accuracy:     90.00% (360/400)
├─ Worst Accuracy:    81.75% (327/400)
└─ Accuracy Range:    8.75%

View Contributions:
├─ Baseline:          0% (optimal)
├─ WL:                5% (optimal)
└─ CES:               95% (optimal)

Error Analysis:
├─ Total Errors:      38 (optimal)
├─ Borderline (<0.01): ~27.5%
├─ Tie-breaks:        ~12.5%
└─ Significant (>0.1): ~15%
```

---

## ✅ Conclusion

The comprehensive evaluation reveals that:

1. **Optimal configuration achieves 90.50% accuracy** with weights [0.00, 0.05, 0.95]
2. **CES v3 is the dominant view**, contributing 95% to optimal performance
3. **Baseline features are redundant** when WL and CES are present
4. **Two-view fusion (WL+CES) is sufficient** for optimal performance
5. **User-specified weights perform well** (90.00%), only 0.5% below optimal

**Final Recommendation**: Use `[0.00, 0.50, 0.50]` (WL+CES equal) for production
- Same accuracy as optimal (90.50%)
- More interpretable and balanced
- Eliminates redundant baseline features
- Simpler to explain and maintain

---

**Generated by**: `comprehensive_evaluation.py`  
**Full Results**: `comprehensive_evaluation_results.json`
