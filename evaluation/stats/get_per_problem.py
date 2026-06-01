import json
import re

def per_problem():
    with open('results/cross/evaluation/final_similarity_matrix_cross.json', 'r') as f:
        final_mat = json.load(f)
    with open('data/cross/ground_truth.json', 'r') as f:
        gt = json.load(f)
        
    for p in sorted(gt.keys(), key=lambda x: int(x[1:])):
        st_dict = gt[p]
        correct = 0
        total = 0
        
        for st_name, expected_ref in st_dict.items():
            s_key = f"{p}/s/{st_name}"
            s_lang = "None"
            if st_name.endswith("_java"): s_lang = "java"
            elif st_name.endswith("_cpp"): s_lang = "cpp"
            elif st_name.endswith("_c"): s_lang = "c"
            
            avail_final = []
            for ref_key, score in final_mat.get(s_key, {}).items():
                if not ref_key.startswith(f"{p}/ref/"): continue
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
                if best[0] == expected_ref: correct += 1
            total += 1
            
        print(f"{p}: {correct}/{total} ({correct/total*100:.2f}%)")

per_problem()
