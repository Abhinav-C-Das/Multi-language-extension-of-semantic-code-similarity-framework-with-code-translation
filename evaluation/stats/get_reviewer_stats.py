import json
import re

def get_mcnemar():
    with open('results/cross/evaluation/final_similarity_matrix_cross.json', 'r') as f:
        final_mat = json.load(f)
    with open('results/cross/evaluation/baseline_similarity_matrix_cross.json', 'r') as f:
        base_mat = json.load(f)
    with open('data/cross/ground_truth.json', 'r') as f:
        gt = json.load(f)
        
    core_students = []
    for p, st_dict in gt.items():
        for st_name, expected_ref in st_dict.items():
            core_students.append((p, st_name, expected_ref))
            
    final_correct = {}
    base_correct = {}
    
    for problem, student, expected_ref in core_students:
        s_key = f"{problem}/s/{student}"
        
        s_lang = "None"
        if student.endswith("_java"): s_lang = "java"
        elif student.endswith("_cpp"): s_lang = "cpp"
        elif student.endswith("_c"): s_lang = "c"
        
        # FINAL
        avail_final = []
        for ref_key, score in final_mat.get(s_key, {}).items():
            if not ref_key.startswith(f"{problem}/ref/"): continue
            ref_name = ref_key.split('/')[-1]
            r_lang = "None"
            if ref_name.endswith("_java.java") or ref_name.endswith("_java"): r_lang = "java"
            elif ref_name.endswith("_cpp.cpp") or ref_name.endswith("_cpp"): r_lang = "cpp"
            elif ref_name.endswith("_c.c") or ref_name.endswith("_c"): r_lang = "c"
            
            if s_lang == r_lang: continue
            
            strategy_match = re.match(r'(ref\d+)', ref_name)
            if strategy_match: avail_final.append((strategy_match.group(1), score))
            
        if avail_final:
            best = max(avail_final, key=lambda x: x[1])
            final_correct[s_key] = (best[0] == expected_ref)
        else:
            final_correct[s_key] = False
            
        # BASELINE
        avail_base = []
        for ref_key, score in base_mat.get(s_key, {}).items():
            if not ref_key.startswith(f"{problem}/ref/"): continue
            ref_name = ref_key.split('/')[-1]
            r_lang = "None"
            if ref_name.endswith("_java.java") or ref_name.endswith("_java"): r_lang = "java"
            elif ref_name.endswith("_cpp.cpp") or ref_name.endswith("_cpp"): r_lang = "cpp"
            elif ref_name.endswith("_c.c") or ref_name.endswith("_c"): r_lang = "c"
            
            if s_lang == r_lang: continue
            
            strategy_match = re.match(r'(ref\d+)', ref_name)
            if strategy_match: avail_base.append((strategy_match.group(1), score))
            
        if avail_base:
            best = max(avail_base, key=lambda x: x[1])
            base_correct[s_key] = (best[0] == expected_ref)
        else:
            base_correct[s_key] = False

    both_correct = 0
    final_only = 0
    base_only = 0
    neither = 0
    
    for s_key in final_correct.keys():
        f = final_correct[s_key]
        b = base_correct[s_key]
        if f and b: both_correct += 1
        elif f and not b: final_only += 1
        elif not f and b: base_only += 1
        else: neither += 1
        
    print(f"McNemar Table (n={len(final_correct)}):")
    print(f"Both Correct (a): {both_correct}")
    print(f"Final Only (b): {final_only}")
    print(f"Baseline Only (c): {base_only}")
    print(f"Neither (d): {neither}")

def get_ces_zeros():
    with open('results/cross/evaluation/ces_similarity_matrix_cross.json', 'r') as f:
        ces_mat = json.load(f)
        
    c_total = c_zeros = 0
    cpp_total = cpp_zeros = 0
    java_total = java_zeros = 0
    
    with open('data/cross/ground_truth.json', 'r') as f:
        gt = json.load(f)
        
    for p, st_dict in gt.items():
        for st_name in st_dict.keys():
            s_key = f"{p}/s/{st_name}"
            # Check if all scores for this student are 0 or below a tiny threshold
            student_scores = list(ces_mat.get(s_key, {}).values())
            is_zero = len(student_scores) > 0 and all(s < 1e-5 for s in student_scores)
            if not student_scores: is_zero = True
            
            if st_name.endswith('_c'):
                c_total += 1
                if is_zero: c_zeros += 1
            elif st_name.endswith('_cpp'):
                cpp_total += 1
                if is_zero: cpp_zeros += 1
            elif st_name.endswith('_java'):
                java_total += 1
                if is_zero: java_zeros += 1
                
    print("\nCES Failure Rates:")
    if c_total > 0: print(f"C: {c_zeros}/{c_total} ({c_zeros/c_total*100:.2f}%)")
    if cpp_total > 0: print(f"C++: {cpp_zeros}/{cpp_total} ({cpp_zeros/cpp_total*100:.2f}%)")
    if java_total > 0: print(f"Java: {java_zeros}/{java_total} ({java_zeros/java_total*100:.2f}%)")

if __name__ == "__main__":
    get_mcnemar()
    get_ces_zeros()
