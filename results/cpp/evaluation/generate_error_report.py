#!/usr/bin/env python3
"""
Generate Error Analysis Report - Local (CES V3 Enhanced)

Generates a markdown report with:
1. Overall Accuracy Stats
2. Detailed Error Analysis (Student Code vs Expected Ref vs Predicted Ref)
"""

import json
from pathlib import Path
import sys

# Paths
GROUND_TRUTH_FILE = Path("data/ground_truth.json")
SIMILARITY_MATRIX_FILE = Path("evaluation/matrices/final_similarity_matrix_ces_v3_local.json")
DATA_DIR = Path("data")
OUTPUT_REPORT = Path("evaluation/error_analysis_report.md")

def load_json(path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

def load_file_content(path):
    if not path.exists():
        return "FILE NOT FOUND"
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"ERROR READING FILE: {e}"

def get_rank_1(scores):
    """Return list of references with the highest score"""
    if not scores:
        return []
    max_score = max(scores.values())
    return [ref for ref, score in scores.items() if score == max_score]

def main():
    print("=" * 80)
    print("GENERATING ERROR ANALYSIS REPORT")
    print("=" * 80)

    # Load Data
    ground_truth = load_json(GROUND_TRUTH_FILE)
    matrix = load_json(SIMILARITY_MATRIX_FILE)
    
    if not ground_truth or not matrix:
        print("[ERROR] Missing input files.")
        sys.exit(1)

    correct = 0
    total = 0
    errors = []
    
    # Analysis Loop
    for prob, submissions in ground_truth.items():
        if prob not in matrix:
            continue
            
        problem_matrix = matrix[prob]
        
        for item in submissions:
            if len(item) < 2: 
                continue
                
            student = item[0]
            expected_ref = item[1]
            
            total += 1
            
            if student not in problem_matrix:
                errors.append({
                    "problem": prob,
                    "student": student,
                    "expected": expected_ref,
                    "predicted": ["MISSING"],
                    "scores": {},
                    "reason": "Missing from matrix"
                })
                continue
            
            scores = problem_matrix[student]
            predicted_refs = get_rank_1(scores)
            
            if expected_ref in predicted_refs:
                correct += 1
            else:
                top_pred = predicted_refs[0] if predicted_refs else "NONE"
                errors.append({
                    "problem": prob,
                    "student": student,
                    "expected": expected_ref,
                    "predicted": predicted_refs,
                    "scores": scores,
                    "top_pred_ref": top_pred
                })

    accuracy = correct / total if total > 0 else 0

    # formatting report
    print(f"Generating report for {len(errors)} errors...")
    
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        # 1. Summary Section
        f.write("# Error Analysis Report\n\n")
        f.write("## 1. Overall Performance\n\n")
        f.write(f"- **Total Samples**: {total}\n")
        f.write(f"- **Correct Matches**: {correct}\n")
        f.write(f"- **Incorrect Matches**: {len(errors)}\n")
        f.write(f"- **Accuracy**: {accuracy:.2%}\n\n")
        
        f.write("---\n\n")
        f.write("## 2. Detailed Error Analysis\n\n")
        
        if not errors:
            f.write("**No errors found! Perfect score!**\n")
        
        for idx, err in enumerate(errors, 1):
            prob = err['problem']
            student = err['student']
            expected = err['expected']
            predicted_list = err['predicted']
            top_pred = err.get('top_pred_ref', predicted_list[0] if predicted_list else "NONE")
            scores = err['scores']
            
            f.write(f"### {idx}. {prob} / {student}\n\n")
            f.write(f"- **Expected**: `{expected}` (Score: {scores.get(expected, 0.0):.4f})\n")
            f.write(f"- **Predicted**: `{top_pred}` (Score: {scores.get(top_pred, 0.0):.4f})\n")
            f.write(f"- **All Predictions**: {predicted_list}\n\n")
            
            # Paths
            student_path = DATA_DIR / prob / "s" / f"{student}.c"
            expected_path = DATA_DIR / prob / "ref" / f"{expected}.c"
            predicted_path = DATA_DIR / prob / "ref" / f"{top_pred}.c"
            
            # Content
            s_code = load_file_content(student_path)
            exp_code = load_file_content(expected_path)
            pred_code = load_file_content(predicted_path)
            
            # Side by side (Student vs Expected)
            f.write("#### Comparison: Student vs Expected Reference\n\n")
            f.write("<table><tr><th>Student Code</th><th>Expected Reference</th></tr>\n")
            f.write("<tr><td valign='top'>\n\n")
            f.write("```c\n")
            f.write(s_code)
            f.write("\n```\n")
            f.write("</td><td valign='top'>\n\n")
            f.write("```c\n")
            f.write(exp_code)
            f.write("\n```\n")
            f.write("</td></tr></table>\n\n")
            
            # Side by side (Student vs Predicted) - only if different from expected
            if top_pred != expected:
                f.write("#### Comparison: Student vs Predicted Reference (Incorrect)\n\n")
                f.write("<table><tr><th>Student Code</th><th>Predicted Reference</th></tr>\n")
                f.write("<tr><td valign='top'>\n\n")
                f.write("```c\n")
                f.write(s_code)
                f.write("\n```\n")
                f.write("</td><td valign='top'>\n\n")
                f.write("```c\n")
                f.write(pred_code)
                f.write("\n```\n")
                f.write("</td></tr></table>\n\n")
            
            f.write("---\n\n")

    print(f"Report saved to: {OUTPUT_REPORT}")
    print(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    main()
