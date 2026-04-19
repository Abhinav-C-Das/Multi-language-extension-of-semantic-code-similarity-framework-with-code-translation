import json
import re

def evaluate_hard_cross():
    print("=============================================================")
    print("  HARD CROSS-LANGUAGE EVALUATION REPORT (STRICT NO-MATCH)")
    print("=============================================================")

    try:
        with open("evaluation/cross/final_similarity_matrix_cross.json", "r") as f:
            matrix = json.load(f)
        with open("data/cross/ground_truth.json", "r") as f:
            gt = json.load(f)
    except Exception as e:
        print("Files missing:", e)
        return

    # Extract core students
    core_students = []
    for p, st_dict in gt.items():
        for st_name, expected_ref in st_dict.items():
            core_students.append((p, st_name, expected_ref))

    correct = 0
    total = 0
    results = []

    for problem, student, expected_ref in core_students:
        s_key = f"{problem}/s/{student}"
        
        # Extract student language
        s_lang = "None"
        if student.endswith("_java"): s_lang = "java"
        elif student.endswith("_cpp"): s_lang = "cpp"
        elif student.endswith("_c"): s_lang = "c"
        
        available_scores = []
        
        # Look at matrix available mappings
        for ref_key, score in matrix.get(s_key, {}).items():
            if not ref_key.startswith(f"{problem}/ref/"):
                continue
                
            ref_name = ref_key.split('/')[-1]
            
            # Check reference language
            r_lang = "None"
            if ref_name.endswith("_java.java") or ref_name.endswith("_java"): r_lang = "java"
            elif ref_name.endswith("_cpp.cpp") or ref_name.endswith("_cpp"): r_lang = "cpp"
            elif ref_name.endswith("_c.c") or ref_name.endswith("_c"): r_lang = "c"
            
            # ENFORCE HARD CONSTRAINT: Reject same-language matching!
            if s_lang == r_lang:
                continue
                
            strategy_match = re.match(r'(ref\d+)', ref_name)
            if not strategy_match:
                continue
                
            strategy = strategy_match.group(1)
            available_scores.append({
                "strategy": strategy,
                "ref_key": ref_name,
                "score": score,
                "r_lang": r_lang
            })
            
        if not available_scores:
            continue
            
        # Pick the prediction with the highest score
        best_prediction = max(available_scores, key=lambda x: x["score"])
        
        match = (best_prediction["strategy"] == expected_ref)
        
        total += 1
        if match: correct += 1
        
        results.append({
            "student": student,
            "s_lang": s_lang,
            "predicted_ref": best_prediction["ref_key"],
            "r_lang": best_prediction["r_lang"],
            "predicted_strategy": best_prediction["strategy"],
            "expected_strategy": expected_ref,
            "score": best_prediction["score"],
            "match": match
        })

    print(f"\nTotal Evaluated (Strict Hard-Cross Mode): {total}")
    if total > 0:
        print(f"Correct Predictions: {correct}/{total}")
        print(f"Accuracy: {correct/total*100:.2f}%\n")
        
        print("DETAILED MAPPINGS:")
        for r in results:
            status = "PASSED" if r["match"] else "FAILED"
            print(f"  [{status}] {r['student']} [{r['s_lang']}] -> Mapped to: {r['predicted_ref']} [{r['r_lang']}] (Score: {r['score']:.4f}) | Expected: {r['expected_strategy']}")

if __name__ == "__main__":
    evaluate_hard_cross()
