import json
import re
import os
from collections import Counter

def tokenize(code):
    return [t for t in re.split(r'\W+', code.lower()) if t]

def get_moss_simulation():
    with open('data/cross/ground_truth.json', 'r') as f:
        gt = json.load(f)
        
    correct = 0
    total = 0
    
    for problem, st_dict in gt.items():
        ref_dir = f'data/cross/{problem}/ref'
        s_dir = f'data/cross/{problem}/s'
        
        refs = {}
        for r_file in os.listdir(ref_dir):
            r_lang = "None"
            if r_file.endswith("_java.java") or r_file.endswith("_java"): r_lang = "java"
            elif r_file.endswith("_cpp.cpp") or r_file.endswith("_cpp"): r_lang = "cpp"
            elif r_file.endswith("_c.c") or r_file.endswith("_c"): r_lang = "c"
            
            with open(os.path.join(ref_dir, r_file), 'r', encoding='utf-8', errors='ignore') as f:
                refs[r_file] = (r_lang, set(tokenize(f.read())))
                
        # To match s_file without extension
        s_files_actual = os.listdir(s_dir)
        
        for s_file_base, expected in st_dict.items():
            s_file = next((f for f in s_files_actual if f.startswith(s_file_base)), None)
            if not s_file: continue
            
            s_lang = "None"
            if s_file.endswith(".java") or s_file_base.endswith("_java"): s_lang = "java"
            elif s_file.endswith(".cpp") or s_file_base.endswith("_cpp"): s_lang = "cpp"
            elif s_file.endswith(".c") or s_file_base.endswith("_c"): s_lang = "c"
            
            with open(os.path.join(s_dir, s_file), 'r', encoding='utf-8', errors='ignore') as f:
                s_tokens = set(tokenize(f.read()))
                
            avail_scores = []
            for r_file, (r_lang, r_tokens) in refs.items():
                if s_lang == r_lang: continue 
                
                score = len(s_tokens & r_tokens) / max(1, len(s_tokens | r_tokens))
                strategy_match = re.match(r'(ref\d+)', r_file)
                if strategy_match:
                    avail_scores.append((strategy_match.group(1), score))
                    
            if avail_scores:
                best = max(avail_scores, key=lambda x: x[1])
                if best[0] == expected: correct += 1
            total += 1
            
    print(f"Token Jaccard (MOSS/JPlag Textual Simulation) Accuracy: {correct}/{total} ({correct/total*100:.2f}%)")

if __name__ == "__main__":
    get_moss_simulation()
