# 📁 File Locations - Multi-View Similarity Evaluation

## 🎯 Combined Similarity Matrices (Your Weights: 0.35/0.40/0.25)

### Main Combined Matrix
**File**: `evaluation/matrices/final_similarity_matrix_ces_v3_local.json`

This file contains the **pre-computed combined similarities** using the weights:
- Baseline: 0.35
- WL: 0.40  
- CES: 0.25

**Structure**:
```json
{
  "p1": {
    "s1": {
      "ref1": 0.8809669320314605,
      "ref2": 0.6309669320314604,
      "ref3": 0.5046237406898074
    },
    "s18": {
      "ref1": 0.4929244937888247,  ← PREDICTED (highest)
      "ref2": 0.49292449378882464,
      "ref3": 0.49062513343243325  ← EXPECTED (should be highest)
    },
    ...
  },
  ...
}
```

**Usage**: This is the file used by the existing evaluation scripts.

---

## 📊 Individual View Matrices

### 1. Baseline Similarity Matrix
**File**: `evaluation/matrices/similarity_matrix.json`

Contains baseline feature similarities (18 numeric features):
- AST metrics
- CFG metrics
- Behavioral features

**Example for p1/s18**:
```json
"s18": {
  "ref1": 0.3330,
  "ref2": 0.3330,
  "ref3": 0.3330
}
```

---

### 2. WL (Weisfeiler-Lehman) Similarity Matrix
**File**: `evaluation/matrices/wl_similarity_matrix_local.json`

Contains WL structural similarities (400-500 features):
- AST node patterns
- Structural fingerprints

**Example for p1/s18**:
```json
"s18": {
  "ref1": 0.9408937946088745,
  "ref2": 0.9408937946088745,
  "ref3": 0.9351705169692799
}
```

---

### 3. CES v3 Similarity Matrix
**File**: `evaluation/matrices/ces_v3_similarity_matrix_local.json`

Contains CES semantic similarities (11+ patterns):
- ACCUMULATIVE
- RECOMPUTED
- MAX_UPDATE, MIN_UPDATE
- NARROWING_WINDOW
- SEARCH_WITH_RETURN
- etc.

**Example for p1/s18**:
```json
"s18": {
  "ref1": 0.0,  ← No matching patterns!
  "ref2": 0.0,
  "ref3": 0.0
}
```

---

## 🔧 Evaluation Results

### Comprehensive Evaluation Results
**File**: `evaluation/comprehensive_evaluation_results.json`

Contains all evaluation results including:
- User-specified weights (0.35/0.40/0.25)
- Optimal weights (0.00/0.05/0.95)
- All ablation study results
- Detailed error lists

**Size**: 798 lines, 22.5 KB

---

### Summary Reports
1. **`evaluation/EVALUATION_SUMMARY.md`** - Comprehensive analysis report
2. **`evaluation/QUICK_REFERENCE.md`** - Quick lookup tables
3. **`evaluation/WHY_LOW_SIMILARITY.md`** - Explanation of low-score cases

---

## 🔍 Case-Specific Analysis

### p1/s18 Detailed Analysis
**File**: `evaluation/p1_s18_analysis.txt`

Contains:
- Full source code comparison
- Similarity score breakdown
- Explanation of why scores are low

---

## 📝 Scripts

### 1. Comprehensive Evaluation Script
**File**: `evaluation/comprehensive_evaluation.py`

**What it does**:
- Combines matrices with custom weights
- Calculates accuracy
- Performs ablation studies
- Finds optimal weights via grid search

**Usage**:
```bash
python evaluation/comprehensive_evaluation.py
```

---

### 2. Detailed Case Analysis Script
**File**: `evaluation/detailed_case_analysis.py`

**What it does**:
- Analyzes specific cases in detail
- Shows view-by-view breakdown
- Explains why scores are low/high
- Finds all low-score cases

**Usage**:
```python
from evaluation.detailed_case_analysis import DetailedCaseAnalyzer

analyzer = DetailedCaseAnalyzer("evaluation/matrices", "data/ground_truth.json")
analyzer.analyze_case('p1', 's18', weights=(0.35, 0.40, 0.25))
```

---

### 3. Quick p1/s18 Analysis
**File**: `evaluation/analyze_p1_s18.py`

**What it does**:
- Focused analysis of the p1/s18 case
- Shows all similarity scores
- Identifies low-score cases

**Usage**:
```bash
python evaluation/analyze_p1_s18.py
```

---

## 📂 Directory Structure

```
evaluation/
├── matrices/                          # Similarity matrices
│   ├── similarity_matrix.json         # Baseline (pre-existing)
│   ├── wl_similarity_matrix_local.json    # WL
│   ├── ces_v3_similarity_matrix_local.json # CES v3
│   └── final_similarity_matrix_ces_v3_local.json  # Combined (0.35/0.40/0.25)
│
├── comprehensive_evaluation.py        # Main evaluation script
├── comprehensive_evaluation_results.json  # All results (798 lines)
├── detailed_case_analysis.py          # Detailed case analyzer
├── analyze_p1_s18.py                  # Quick p1/s18 analysis
│
├── EVALUATION_SUMMARY.md              # Comprehensive report
├── QUICK_REFERENCE.md                 # Quick lookup tables
├── WHY_LOW_SIMILARITY.md              # Low-score explanation
├── p1_s18_analysis.txt                # p1/s18 detailed analysis
└── FILE_LOCATIONS.md                  # This file
```

---

## 🎯 Quick Access Guide

### To see combined similarities with your weights (0.35/0.40/0.25):
```bash
# View the pre-computed combined matrix
cat evaluation/matrices/final_similarity_matrix_ces_v3_local.json | jq '.p1.s18'
```

**Output**:
```json
{
  "ref1": 0.4929244937888247,
  "ref2": 0.49292449378882464,
  "ref3": 0.49062513343243325
}
```

---

### To compute combined similarities with custom weights:
```python
import json

# Load matrices
baseline = json.load(open('evaluation/matrices/similarity_matrix.json'))
wl = json.load(open('evaluation/matrices/wl_similarity_matrix_local.json'))
ces = json.load(open('evaluation/matrices/ces_v3_similarity_matrix_local.json'))

# Your custom weights
w_b, w_w, w_c = 0.35, 0.40, 0.25

# Compute for p1/s18
problem, student = 'p1', 's18'
for ref in baseline[problem][student].keys():
    b = baseline[problem][student][ref]
    w = wl[problem][student][ref]
    c = ces[problem][student][ref]
    combined = w_b * b + w_w * w + w_c * c
    print(f"{ref}: {combined:.4f}")
```

---

### To analyze any case in detail:
```bash
# Edit analyze_p1_s18.py and change:
problem = 'p5'   # Your problem
student = 's12'  # Your student

# Then run:
python evaluation/analyze_p1_s18.py
```

---

## ✅ Summary

**Main combined similarity file**: `evaluation/matrices/final_similarity_matrix_ces_v3_local.json`

This file was **generated by the pipeline** and contains similarities using:
- Baseline weight: 0.35
- WL weight: 0.40
- CES weight: 0.25

**To use different weights**, run:
```python
python evaluation/comprehensive_evaluation.py
```

This will compute similarities with any weights you specify and save results to `comprehensive_evaluation_results.json`.
