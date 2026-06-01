# -*- coding: utf-8 -*-
"""
Competitive Displacement Effect Analysis
=========================================
Uses the existing final_similarity_matrix_cross.json to quantify:
1. How often C/C++ queries displace a correct Java reference from top-1
2. What the mean score of the displaced Java match was vs the winning C/C++ match
3. Top-2 accuracy for C->Java and C++->Java directions

This provides the data for the "Competitive Displacement" table in §VI-B.
"""

import json
from collections import defaultdict

# ── Load data ──────────────────────────────────────────────────────────────────
with open('results/cross/evaluation/final_similarity_matrix_cross.json', 'r') as f:
    mat = json.load(f)

with open('data/cross/ground_truth.json', 'r') as f:
    gt = json.load(f)

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_lang(key):
    """Infer language from key suffix."""
    if '_java' in key or key.endswith('.java'):
        return 'java'
    if '_cpp' in key:
        return 'cpp'
    if '_c' in key:
        return 'c'
    return 'unknown'

def get_problem(key):
    return key.split('/')[0]  # e.g. 'p1'

def get_stem(key):
    """Get bare stem: p1/s/s3_c -> s3_c"""
    return key.split('/')[-1]

def get_ref_stem(key):
    """Get ref stem: p1/ref/ref1_c -> ref1"""
    stem = key.split('/')[-1]  # ref1_c
    # strip language suffix
    for suf in ['_java', '_cpp', '_c']:
        if stem.endswith(suf):
            return stem[:-len(suf)]
    return stem

# ── Build reference lookup per problem ────────────────────────────────────────
# references[problem][lang] = list of full keys
refs_by_problem_lang = defaultdict(lambda: defaultdict(list))
all_keys = list(mat.keys())
references = [k for k in all_keys if '/ref/' in k]
submissions = [k for k in all_keys if '/s/' in k]

for rk in references:
    prob = get_problem(rk)
    lang = get_lang(rk)
    refs_by_problem_lang[prob][lang].append(rk)

# ── Main displacement analysis ─────────────────────────────────────────────────
# For each C or C++ submission:
#   - Find the correct reference (from GT)
#   - Get scores for ALL references except same-language ones
#   - Find the top-1 cross-language match
#   - If top-1 is NOT Java but the correct Java ref exists, measure displacement

displacement_records = []
top1_correct = defaultdict(int)
top1_total   = defaultdict(int)
top2_correct = defaultdict(int)

# Also collect Java->C/C++ performance for comparison
java_records = []

for sk in submissions:
    prob = get_problem(sk)
    sub_lang = get_lang(sk)
    sub_stem = get_stem(sk)  # e.g. s3_c

    # Get ground truth reference stem for this submission
    if prob not in gt or sub_stem not in gt[prob]:
        continue
    gt_ref_stem = gt[prob][sub_stem]  # e.g. 'ref1'

    # Get all cross-language (different lang) reference keys
    cross_refs = []
    for rlang, rkeys in refs_by_problem_lang[prob].items():
        if rlang != sub_lang:
            for rk in rkeys:
                ref_stem = get_ref_stem(rk)
                score = mat.get(sk, {}).get(rk, 0.0)
                is_correct = (ref_stem == gt_ref_stem)
                cross_refs.append({
                    'ref_key': rk,
                    'ref_stem': ref_stem,
                    'ref_lang': rlang,
                    'score': score,
                    'is_correct': is_correct
                })

    if not cross_refs:
        continue

    # Sort by score descending
    cross_refs.sort(key=lambda x: -x['score'])
    top1 = cross_refs[0]
    top2 = cross_refs[1] if len(cross_refs) > 1 else None

    direction = f"{sub_lang}->cross"

    # Track top-1 accuracy by direction
    direction_key = f"{sub_lang}->{'java' if top1['ref_lang'] == 'java' else 'c_cpp'}"

    # For C and C++ submissions: analyze whether Java was displaced
    if sub_lang in ('c', 'cpp'):
        # Find the best-scoring CORRECT Java ref
        correct_java_refs = [r for r in cross_refs if r['ref_lang'] == 'java' and r['is_correct']]
        any_java_refs     = [r for r in cross_refs if r['ref_lang'] == 'java']
        winning_non_java  = [r for r in cross_refs if r['ref_lang'] != 'java']

        # What won top-1?
        winner_lang = top1['ref_lang']
        winner_correct = top1['is_correct']

        direction_label = f"{sub_lang}->java" if winner_lang == 'java' else f"{sub_lang}->c_cpp"
        top1_total[direction_label] += 1

        if winner_lang == 'java':
            # Java won top-1
            top1_correct[direction_label] += 1
            if winner_correct:
                top2_correct[direction_label] += 1  # trivially correct at top-2 too
        else:
            # Non-Java won top-1 — Java displaced
            winner_score = top1['score']
            best_java_score = any_java_refs[0]['score'] if any_java_refs else 0.0
            correct_java_score = correct_java_refs[0]['score'] if correct_java_refs else None

            # Is the correct Java ref in top-2?
            top2_is_java_correct = (top2 is not None and top2['ref_lang'] == 'java' and top2['is_correct'])

            if winner_correct:
                top1_correct[direction_label] += 1

            if top2_is_java_correct or winner_correct:
                top2_correct[direction_label] += 1

            displacement_records.append({
                'sub': sk,
                'sub_lang': sub_lang,
                'prob': prob,
                'winner_lang': winner_lang,
                'winner_score': winner_score,
                'best_java_score': best_java_score,
                'correct_java_score': correct_java_score,
                'score_gap': winner_score - best_java_score,
                'top2_java_correct': top2_is_java_correct,
            })

    # Track Java->C/C++ performance
    if sub_lang == 'java':
        top1_total['java->c_cpp'] += 1
        if top1['is_correct']:
            top1_correct['java->c_cpp'] += 1
        if top1['is_correct'] or (top2 and top2['is_correct']):
            top2_correct['java->c_cpp'] += 1

# ── Print Results ──────────────────────────────────────────────────────────────
print("=" * 70)
print("COMPETITIVE DISPLACEMENT EFFECT ANALYSIS")
print("=" * 70)

print(f"\nTotal C submissions analyzed:   {sum(1 for s in submissions if get_lang(s) == 'c')}")
print(f"Total C++ submissions analyzed: {sum(1 for s in submissions if get_lang(s) == 'cpp')}")
print(f"Total Java submissions:         {sum(1 for s in submissions if get_lang(s) == 'java')}")

print("\n-- Directional Top-1 Counts (outcomes) --")
for k, v in sorted(top1_total.items()):
    corr = top1_correct.get(k, 0)
    t2   = top2_correct.get(k, 0)
    acc  = corr / v * 100 if v > 0 else 0
    t2a  = t2 / v * 100 if v > 0 else 0
    print(f"  {k:<20}: n={v:>4}  Top-1 correct={corr:>3} ({acc:5.1f}%)  Top-2 correct={t2:>3} ({t2a:5.1f}%)")

print(f"\n-- Displacement Records: {len(displacement_records)} C/C++ queries where Java was NOT top-1 --")

if displacement_records:
    gaps = [r['score_gap'] for r in displacement_records]
    winner_scores = [r['winner_score'] for r in displacement_records]
    java_scores   = [r['best_java_score'] for r in displacement_records]
    t2_correct    = sum(1 for r in displacement_records if r['top2_java_correct'])

    print(f"  Mean winning C/C++ score:    {sum(winner_scores)/len(winner_scores):.4f}")
    print(f"  Mean displaced Java score:   {sum(java_scores)/len(java_scores):.4f}")
    print(f"  Mean score gap (C/C++ - Java): {sum(gaps)/len(gaps):.4f}")
    print(f"  Max gap: {max(gaps):.4f}  Min gap: {min(gaps):.4f}")
    print(f"  Displaced Java in top-2 (correct): {t2_correct}/{len(displacement_records)} ({t2_correct/len(displacement_records)*100:.1f}%)")

    # Split by source language
    c_disp  = [r for r in displacement_records if r['sub_lang'] == 'c']
    cp_disp = [r for r in displacement_records if r['sub_lang'] == 'cpp']
    print(f"\n  C->Java displaced:   {len(c_disp)}")
    if c_disp:
        print(f"    Mean winner score: {sum(r['winner_score'] for r in c_disp)/len(c_disp):.4f}")
        print(f"    Mean Java score:   {sum(r['best_java_score'] for r in c_disp)/len(c_disp):.4f}")
        print(f"    Mean gap:          {sum(r['score_gap'] for r in c_disp)/len(c_disp):.4f}")
        t2c = sum(1 for r in c_disp if r['top2_java_correct'])
        print(f"    Java correct in top-2: {t2c}/{len(c_disp)} ({t2c/len(c_disp)*100:.1f}%)")

    print(f"\n  C++->Java displaced: {len(cp_disp)}")
    if cp_disp:
        print(f"    Mean winner score: {sum(r['winner_score'] for r in cp_disp)/len(cp_disp):.4f}")
        print(f"    Mean Java score:   {sum(r['best_java_score'] for r in cp_disp)/len(cp_disp):.4f}")
        print(f"    Mean gap:          {sum(r['score_gap'] for r in cp_disp)/len(cp_disp):.4f}")
        t2cp = sum(1 for r in cp_disp if r['top2_java_correct'])
        print(f"    Java correct in top-2: {t2cp}/{len(cp_disp)} ({t2cp/len(cp_disp)*100:.1f}%)")

print("\n-- Java->C/C++ direction --")
print(f"  n={top1_total.get('java->c_cpp',0)}")
print(f"  Top-1 accuracy: {top1_correct.get('java->c_cpp',0)}/{top1_total.get('java->c_cpp',1)} = {top1_correct.get('java->c_cpp',0)/max(top1_total.get('java->c_cpp',1),1)*100:.2f}%")

print("\n" + "=" * 70)
print("RAW DATA SAVED to displacement_results.json")
print("=" * 70)

# Save raw for verification
with open('displacement_results.json', 'w') as f:
    json.dump({
        'top1_total': dict(top1_total),
        'top1_correct': dict(top1_correct),
        'top2_correct': dict(top2_correct),
        'displacement_summary': {
            'total_displaced': len(displacement_records),
            'c_displaced': len(c_disp) if displacement_records else 0,
            'cpp_displaced': len(cp_disp) if displacement_records else 0,
            'mean_winner_score': sum(winner_scores)/len(winner_scores) if displacement_records else 0,
            'mean_java_score': sum(java_scores)/len(java_scores) if displacement_records else 0,
            'mean_gap': sum(gaps)/len(gaps) if displacement_records else 0,
            'top2_correct_pct': t2_correct/len(displacement_records)*100 if displacement_records else 0,
        }
    }, f, indent=2)
