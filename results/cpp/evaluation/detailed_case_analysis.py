#!/usr/bin/env python3
"""
Detailed Case Analysis for Multi-View Code Similarity
======================================================
Analyzes specific cases to understand why similarities are low/high
and shows the breakdown of individual view contributions.
"""

import json
import os
from typing import Dict, Tuple


class DetailedCaseAnalyzer:
    """Analyzer for detailed case-by-case similarity breakdown"""
    
    def __init__(self, matrices_dir: str, ground_truth_path: str):
        self.matrices_dir = matrices_dir
        
        # Load all matrices
        self.baseline_matrix = self._load_matrix("similarity_matrix.json")
        self.wl_matrix = self._load_matrix("wl_similarity_matrix_local.json")
        self.ces_matrix = self._load_matrix("ces_v3_similarity_matrix_local.json")
        
        # Load ground truth
        with open(ground_truth_path, 'r') as f:
            self.ground_truth = json.load(f)
    
    def _load_matrix(self, filename: str) -> Dict:
        """Load a similarity matrix from JSON file"""
        path = os.path.join(self.matrices_dir, filename)
        with open(path, 'r') as f:
            return json.load(f)
    
    def analyze_case(self, problem: str, student: str, weights: Tuple[float, float, float]):
        """
        Analyze a specific case in detail
        
        Args:
            problem: Problem ID (e.g., 'p1')
            student: Student ID (e.g., 's18')
            weights: Tuple of (baseline_weight, wl_weight, ces_weight)
        """
        w_baseline, w_wl, w_ces = weights
        
        print("="*80)
        print(f"DETAILED ANALYSIS: {problem}/{student}")
        print("="*80)
        
        # Get expected reference from ground truth
        expected_ref = None
        for student_ref in self.ground_truth[problem]:
            if student_ref[0] == student:
                expected_ref = student_ref[1]
                break
        
        if not expected_ref:
            print(f"ERROR: No ground truth found for {problem}/{student}")
            return
        
        print(f"\n📌 Ground Truth: {student} should match {expected_ref}")
        print(f"⚖️  Weights: Baseline={w_baseline:.2f}, WL={w_wl:.2f}, CES={w_ces:.2f}")
        
        # Get all references for this problem
        refs = list(self.baseline_matrix[problem][student].keys())
        
        print(f"\n{'='*80}")
        print("SIMILARITY BREAKDOWN BY VIEW")
        print(f"{'='*80}")
        print(f"\n{'Reference':<12} {'Baseline':<12} {'WL':<12} {'CES':<12} {'Combined':<12} {'Status'}")
        print("-"*80)
        
        results = []
        for ref in refs:
            # Get individual scores
            baseline_score = self.baseline_matrix[problem][student].get(ref, 0.0)
            wl_score = self.wl_matrix[problem][student].get(ref, 0.0)
            ces_score = self.ces_matrix[problem][student].get(ref, 0.0)
            
            # Calculate combined score
            combined_score = (w_baseline * baseline_score + 
                            w_wl * wl_score + 
                            w_ces * ces_score)
            
            # Determine status
            status = "✅ EXPECTED" if ref == expected_ref else ""
            
            results.append({
                'ref': ref,
                'baseline': baseline_score,
                'wl': wl_score,
                'ces': ces_score,
                'combined': combined_score,
                'status': status
            })
            
            print(f"{ref:<12} {baseline_score:<12.4f} {wl_score:<12.4f} {ces_score:<12.4f} {combined_score:<12.4f} {status}")
        
        # Find predicted reference (highest combined score)
        predicted = max(results, key=lambda x: x['combined'])
        expected = next(r for r in results if r['ref'] == expected_ref)
        
        print("\n" + "="*80)
        print("PREDICTION ANALYSIS")
        print("="*80)
        
        print(f"\n🎯 Predicted: {predicted['ref']} (score: {predicted['combined']:.4f})")
        print(f"✓  Expected:  {expected['ref']} (score: {expected['combined']:.4f})")
        
        if predicted['ref'] != expected['ref']:
            print(f"\n❌ MISMATCH!")
            print(f"   Score difference: {predicted['combined'] - expected['combined']:.4f}")
            print(f"   Predicted is {predicted['combined'] - expected['combined']:.4f} higher")
        else:
            print(f"\n✅ CORRECT PREDICTION!")
        
        # Detailed view contribution analysis
        print("\n" + "="*80)
        print("VIEW CONTRIBUTION ANALYSIS")
        print("="*80)
        
        print(f"\n📊 For EXPECTED reference ({expected_ref}):")
        print(f"   Baseline: {expected['baseline']:.4f} × {w_baseline:.2f} = {expected['baseline'] * w_baseline:.4f}")
        print(f"   WL:       {expected['wl']:.4f} × {w_wl:.2f} = {expected['wl'] * w_wl:.4f}")
        print(f"   CES:      {expected['ces']:.4f} × {w_ces:.2f} = {expected['ces'] * w_ces:.4f}")
        print(f"   ─────────────────────────────────────────────────")
        print(f"   TOTAL:    {expected['combined']:.4f}")
        
        print(f"\n📊 For PREDICTED reference ({predicted['ref']}):")
        print(f"   Baseline: {predicted['baseline']:.4f} × {w_baseline:.2f} = {predicted['baseline'] * w_baseline:.4f}")
        print(f"   WL:       {predicted['wl']:.4f} × {w_wl:.2f} = {predicted['wl'] * w_wl:.4f}")
        print(f"   CES:      {predicted['ces']:.4f} × {w_ces:.2f} = {predicted['ces'] * w_ces:.4f}")
        print(f"   ─────────────────────────────────────────────────")
        print(f"   TOTAL:    {predicted['combined']:.4f}")
        
        # Explain why scores are low
        print("\n" + "="*80)
        print("WHY ARE SCORES LOW?")
        print("="*80)
        
        avg_score = sum(r['combined'] for r in results) / len(results)
        max_score = max(r['combined'] for r in results)
        
        print(f"\n📈 Score Statistics:")
        print(f"   Average combined score: {avg_score:.4f}")
        print(f"   Maximum combined score: {max_score:.4f}")
        print(f"   Expected score:         {expected['combined']:.4f}")
        
        if expected['combined'] < 0.6:
            print(f"\n⚠️  Expected score is LOW (<0.6)")
            print(f"\n🔍 Possible reasons:")
            
            # Check individual views
            if expected['baseline'] < 0.6:
                print(f"   • Baseline score is low ({expected['baseline']:.4f})")
                print(f"     → Structural/behavioral features differ significantly")
            
            if expected['wl'] < 0.6:
                print(f"   • WL score is low ({expected['wl']:.4f})")
                print(f"     → AST structure differs (different node types/patterns)")
            
            if expected['ces'] < 0.6:
                print(f"   • CES score is low ({expected['ces']:.4f})")
                print(f"     → Semantic patterns differ (different computational strategy)")
            
            # Check if it's a difficult case
            if max_score < 0.6:
                print(f"\n   💡 This appears to be a DIFFICULT case:")
                print(f"      All references have low similarity scores")
                print(f"      The student code may be significantly different from all references")
            
            # Check if it's a close call
            score_diff = predicted['combined'] - expected['combined']
            if score_diff < 0.01:
                print(f"\n   💡 This is a BORDERLINE case:")
                print(f"      Score difference is very small ({score_diff:.4f})")
                print(f"      Small changes in weights could flip the prediction")
        
        # View-specific insights
        print("\n" + "="*80)
        print("VIEW-SPECIFIC INSIGHTS")
        print("="*80)
        
        # Compare expected vs predicted for each view
        print(f"\n🔬 View-by-view comparison (Expected vs Predicted):")
        print(f"\n   Baseline: {expected['baseline']:.4f} vs {predicted['baseline']:.4f}")
        if predicted['baseline'] > expected['baseline']:
            print(f"             ⚠️  Predicted is {predicted['baseline'] - expected['baseline']:.4f} higher")
            print(f"             → Baseline features favor {predicted['ref']}")
        
        print(f"\n   WL:       {expected['wl']:.4f} vs {predicted['wl']:.4f}")
        if predicted['wl'] > expected['wl']:
            print(f"             ⚠️  Predicted is {predicted['wl'] - expected['wl']:.4f} higher")
            print(f"             → WL patterns favor {predicted['ref']}")
        
        print(f"\n   CES:      {expected['ces']:.4f} vs {predicted['ces']:.4f}")
        if predicted['ces'] > expected['ces']:
            print(f"             ⚠️  Predicted is {predicted['ces'] - expected['ces']:.4f} higher")
            print(f"             → CES patterns favor {predicted['ref']}")
        
        return results
    
    def analyze_all_low_scores(self, threshold: float = 0.6, weights: Tuple[float, float, float] = (0.35, 0.40, 0.25)):
        """Find all cases where expected similarity is below threshold"""
        w_baseline, w_wl, w_ces = weights
        
        print("="*80)
        print(f"FINDING ALL CASES WITH LOW EXPECTED SIMILARITY (< {threshold})")
        print("="*80)
        
        low_score_cases = []
        
        for problem, student_refs in self.ground_truth.items():
            for student_ref in student_refs:
                student = student_ref[0]
                expected_ref = student_ref[1]
                
                # Get scores
                baseline_score = self.baseline_matrix[problem][student].get(expected_ref, 0.0)
                wl_score = self.wl_matrix[problem][student].get(expected_ref, 0.0)
                ces_score = self.ces_matrix[problem][student].get(expected_ref, 0.0)
                
                combined_score = (w_baseline * baseline_score + 
                                w_wl * wl_score + 
                                w_ces * ces_score)
                
                if combined_score < threshold:
                    low_score_cases.append({
                        'problem': problem,
                        'student': student,
                        'expected_ref': expected_ref,
                        'baseline': baseline_score,
                        'wl': wl_score,
                        'ces': ces_score,
                        'combined': combined_score
                    })
        
        # Sort by combined score
        low_score_cases.sort(key=lambda x: x['combined'])
        
        print(f"\nFound {len(low_score_cases)} cases with expected similarity < {threshold}\n")
        print(f"{'Problem':<10} {'Student':<10} {'Exp Ref':<10} {'Baseline':<10} {'WL':<10} {'CES':<10} {'Combined':<10}")
        print("-"*80)
        
        for case in low_score_cases:
            print(f"{case['problem']:<10} {case['student']:<10} {case['expected_ref']:<10} "
                  f"{case['baseline']:<10.4f} {case['wl']:<10.4f} {case['ces']:<10.4f} {case['combined']:<10.4f}")
        
        return low_score_cases


def main():
    """Main execution"""
    
    MATRICES_DIR = "evaluation/matrices"
    GROUND_TRUTH_PATH = "data/ground_truth.json"
    
    analyzer = DetailedCaseAnalyzer(MATRICES_DIR, GROUND_TRUTH_PATH)
    
    # Analyze the specific case: p1/s18
    print("\n" + "🔍 " * 40)
    print("ANALYZING SPECIFIC CASE: p1/s18")
    print("🔍 " * 40 + "\n")
    
    # User-specified weights
    user_weights = (0.35, 0.40, 0.25)
    
    analyzer.analyze_case('p1', 's18', user_weights)
    
    # Also show with optimal weights for comparison
    print("\n\n" + "🔍 " * 40)
    print("SAME CASE WITH OPTIMAL WEIGHTS (for comparison)")
    print("🔍 " * 40 + "\n")
    
    optimal_weights = (0.00, 0.05, 0.95)
    analyzer.analyze_case('p1', 's18', optimal_weights)
    
    # Find all low-score cases
    print("\n\n" + "🔍 " * 40)
    print("ALL LOW-SCORE CASES")
    print("🔍 " * 40 + "\n")
    
    low_cases = analyzer.analyze_all_low_scores(threshold=0.6, weights=user_weights)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal low-score cases (< 0.6): {len(low_cases)}")
    print(f"This represents {len(low_cases)/400*100:.1f}% of all 400 submissions")
    
    print("\n💡 Key Insights:")
    print("   • Low scores indicate significant differences from reference solutions")
    print("   • This could be due to:")
    print("     - Different algorithmic approach")
    print("     - Different code structure (iterative vs recursive)")
    print("     - Additional helper functions or complexity")
    print("     - Novel implementation patterns")


if __name__ == "__main__":
    main()
