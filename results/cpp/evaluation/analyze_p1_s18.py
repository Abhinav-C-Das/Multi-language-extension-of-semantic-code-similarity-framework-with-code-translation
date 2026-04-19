#!/usr/bin/env python3
"""
Quick Case Analysis: p1/s18
"""

import json

# Load matrices
with open('evaluation/matrices/similarity_matrix.json', 'r') as f:
    baseline = json.load(f)
with open('evaluation/matrices/wl_similarity_matrix_local.json', 'r') as f:
    wl = json.load(f)
with open('evaluation/matrices/ces_v3_similarity_matrix_local.json', 'r') as f:
    ces = json.load(f)

# User weights
w_b, w_w, w_c = 0.35, 0.40, 0.25

problem = 'p1'
student = 's18'

print("="*80)
print(f"CASE ANALYSIS: {problem}/{student}")
print("="*80)
print(f"\nWeights: Baseline={w_b}, WL={w_w}, CES={w_c}")
print(f"Expected: ref3 (tail recursion)")
print()

refs = ['ref1', 'ref2', 'ref3']
print(f"{'Reference':<12} {'Baseline':<12} {'WL':<12} {'CES':<12} {'Combined':<12}")
print("-"*80)

for ref in refs:
    b_score = baseline[problem][student][ref]
    w_score = wl[problem][student][ref]
    c_score = ces[problem][student][ref]
    combined = w_b * b_score + w_w * w_score + w_c * c_score
    
    print(f"{ref:<12} {b_score:<12.4f} {w_score:<12.4f} {c_score:<12.4f} {combined:<12.4f}")

print("\n" + "="*80)
print("EXPLANATION: Why is p1/s18 → ref3 similarity LOW?")
print("="*80)

print("""
📌 Student Code (s18): TAIL RECURSION with helper function
   - Uses sumTail(arr, startIdx, endIdx, accumulator)
   - Forward iteration with accumulator parameter
   - Tail-recursive pattern

📌 Expected Reference (ref3): SIMPLE RECURSION
   - Direct recursive call: arr[n-1] + arraySum(arr, n-1)
   - Backward iteration (n-1, n-2, ...)
   - No helper function, no accumulator

📌 Predicted Reference (ref1): ITERATIVE LOOP
   - Uses for loop with sum += arr[i]
   - Forward iteration
   - Accumulative pattern

WHY SCORES ARE LOW (~0.49):

1. BASELINE (Structural/Behavioral):
   • ref1: 0.6310 - Higher because both use forward iteration
   • ref3: 0.5031 - Lower because different recursion style
   
2. WL (AST Patterns):
   • ref1: 0.9409 - Very high! Similar AST structure despite loop vs recursion
   • ref3: 0.9352 - Also high, but slightly lower
   • WL sees structural similarity, not semantic difference

3. CES (Semantic Patterns):
   • ref1: 0.0000 - Zero! Completely different patterns
   • ref3: 0.0000 - Zero! Also different
   • CES correctly identifies that s18's tail recursion is DIFFERENT from both

COMBINED SCORE CALCULATION:
   ref1: 0.35×0.6310 + 0.40×0.9409 + 0.25×0.0000 = 0.4929 ✗ PREDICTED
   ref3: 0.35×0.5031 + 0.40×0.9352 + 0.25×0.0000 = 0.4906 ✓ EXPECTED

DIFFERENCE: Only 0.0023 (0.23%)!

ROOT CAUSE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The student's TAIL RECURSION pattern is NOT in the CES pattern library!

s18 uses:  sumTail(arr, startIdx + 1, endIdx, accumulator + arr[startIdx])
ref3 uses: arr[n - 1] + arraySum(arr, n - 1)

These are FUNDAMENTALLY DIFFERENT recursive patterns:
• s18: Tail recursion (accumulator-based, can be optimized to iteration)
• ref3: Head recursion (builds up stack, computes on return)

CES v3 doesn't distinguish between these, so both get 0.0 similarity!

SOLUTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add new CES patterns:
1. TAIL_RECURSIVE - Recursion with accumulator parameter
2. HEAD_RECURSIVE - Traditional recursion with computation on return

This would give s18 and ref3 non-zero CES similarity and fix the prediction!
""")

print("\n" + "="*80)
print("FINDING ALL LOW-SCORE CASES")
print("="*80)

low_cases = []
with open('data/ground_truth.json', 'r') as f:
    gt = json.load(f)

for prob, student_refs in gt.items():
    for s_ref in student_refs:
        s, ref = s_ref[0], s_ref[1]
        if prob in baseline and s in baseline[prob] and ref in baseline[prob][s]:
            b = baseline[prob][s][ref]
            w = wl[prob][s][ref]
            c = ces[prob][s][ref]
            combined = w_b * b + w_w * w + w_c * c
            
            if combined < 0.6:
                low_cases.append({
                    'problem': prob,
                    'student': s,
                    'ref': ref,
                    'baseline': b,
                    'wl': w,
                    'ces': c,
                    'combined': combined
                })

low_cases.sort(key=lambda x: x['combined'])

print(f"\nFound {len(low_cases)} cases with expected similarity < 0.6")
print(f"This is {len(low_cases)/400*100:.1f}% of all submissions\n")

print(f"{'Problem':<10} {'Student':<10} {'Ref':<8} {'Baseline':<10} {'WL':<10} {'CES':<10} {'Combined':<10}")
print("-"*90)

for case in low_cases[:20]:  # Show top 20
    print(f"{case['problem']:<10} {case['student']:<10} {case['ref']:<8} "
          f"{case['baseline']:<10.4f} {case['wl']:<10.4f} {case['ces']:<10.4f} {case['combined']:<10.4f}")

if len(low_cases) > 20:
    print(f"\n... and {len(low_cases) - 20} more cases")

# Save detailed report
with open('evaluation/p1_s18_analysis.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("DETAILED ANALYSIS: p1/s18 Low Similarity Case\n")
    f.write("="*80 + "\n\n")
    
    f.write("STUDENT CODE (s18): Tail Recursion\n")
    f.write("-" * 80 + "\n")
    with open('data/p1/s/s18.cpp', 'r') as code:
        f.write(code.read())
    
    f.write("\n\nEXPECTED REFERENCE (ref3): Head Recursion\n")
    f.write("-" * 80 + "\n")
    with open('data/p1/ref/ref3.cpp', 'r') as code:
        f.write(code.read())
    
    f.write("\n\nPREDICTED REFERENCE (ref1): Iterative Loop\n")
    f.write("-" * 80 + "\n")
    with open('data/p1/ref/ref1.cpp', 'r') as code:
        f.write(code.read())
    
    f.write("\n\n" + "="*80 + "\n")
    f.write("SIMILARITY SCORES\n")
    f.write("="*80 + "\n\n")
    
    for ref in refs:
        b_score = baseline[problem][student][ref]
        w_score = wl[problem][student][ref]
        c_score = ces[problem][student][ref]
        combined = w_b * b_score + w_w * w_score + w_c * c_score
        
        f.write(f"{ref}:\n")
        f.write(f"  Baseline: {b_score:.4f}\n")
        f.write(f"  WL:       {w_score:.4f}\n")
        f.write(f"  CES:      {c_score:.4f}\n")
        f.write(f"  Combined: {combined:.4f}\n\n")
    
    f.write("\n" + "="*80 + "\n")
    f.write("CONCLUSION\n")
    f.write("="*80 + "\n\n")
    f.write("The low similarity (0.49) is due to:\n")
    f.write("1. CES v3 doesn't recognize tail recursion pattern (gives 0.0 for all refs)\n")
    f.write("2. WL scores are very close (0.9409 vs 0.9352) - can't distinguish\n")
    f.write("3. Baseline slightly favors ref1 due to forward iteration similarity\n\n")
    f.write("RECOMMENDATION: Add TAIL_RECURSIVE and HEAD_RECURSIVE patterns to CES v3\n")

print(f"\n✓ Detailed analysis saved to: evaluation/p1_s18_analysis.txt")
