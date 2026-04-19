#!/usr/bin/env python3
"""
Comprehensive Multi-View Code Similarity Evaluation Script
===========================================================
This script performs:
1. Multi-view fusion with custom weights (Baseline, WL, CES)
2. Accuracy calculation against ground truth
3. Ablation studies (single-view and multi-view combinations)
4. Optimal weight search through grid search
5. Detailed performance analysis and reporting
"""

import json
import os
from typing import Dict, List, Tuple
from itertools import product


class MultiViewEvaluator:
    """Comprehensive evaluator for multi-view code similarity"""
    
    def __init__(self, matrices_dir: str, ground_truth_path: str):
        """
        Initialize evaluator with paths to matrices and ground truth
        
        Args:
            matrices_dir: Directory containing similarity matrices
            ground_truth_path: Path to ground_truth.json
        """
        self.matrices_dir = matrices_dir
        self.ground_truth_path = ground_truth_path
        
        # Load all matrices
        self.baseline_matrix = self._load_matrix("similarity_matrix.json")
        self.wl_matrix = self._load_matrix("wl_similarity_matrix_local.json")
        self.ces_matrix = self._load_matrix("ces_v3_similarity_matrix_local.json")
        
        # Load ground truth
        with open(ground_truth_path, 'r') as f:
            self.ground_truth = json.load(f)
        
        print(f"✓ Loaded Baseline matrix")
        print(f"✓ Loaded WL matrix")
        print(f"✓ Loaded CES v3 matrix")
        print(f"✓ Loaded Ground Truth ({len(self.ground_truth)} problems)")
    
    def _load_matrix(self, filename: str) -> Dict:
        """Load a similarity matrix from JSON file"""
        path = os.path.join(self.matrices_dir, filename)
        with open(path, 'r') as f:
            return json.load(f)
    
    def combine_matrices(self, w_baseline: float, w_wl: float, w_ces: float) -> Dict:
        """
        Combine three similarity matrices with given weights
        
        Args:
            w_baseline: Weight for baseline features
            w_wl: Weight for WL features
            w_ces: Weight for CES features
        
        Returns:
            Combined similarity matrix
        """
        combined = {}
        
        # Iterate through all problems
        for problem in self.baseline_matrix.keys():
            combined[problem] = {}
            
            # Iterate through all students
            for student in self.baseline_matrix[problem].keys():
                combined[problem][student] = {}
                
                # Iterate through all references
                for ref in self.baseline_matrix[problem][student].keys():
                    # Get scores from each view (default to 0 if missing)
                    baseline_score = self.baseline_matrix.get(problem, {}).get(student, {}).get(ref, 0.0)
                    wl_score = self.wl_matrix.get(problem, {}).get(student, {}).get(ref, 0.0)
                    ces_score = self.ces_matrix.get(problem, {}).get(student, {}).get(ref, 0.0)
                    
                    # Weighted combination
                    combined_score = (w_baseline * baseline_score + 
                                    w_wl * wl_score + 
                                    w_ces * ces_score)
                    
                    combined[problem][student][ref] = combined_score
        
        return combined
    
    def evaluate_accuracy(self, similarity_matrix: Dict) -> Tuple[float, int, int, List]:
        """
        Evaluate accuracy against ground truth
        
        Args:
            similarity_matrix: Combined similarity matrix
        
        Returns:
            Tuple of (accuracy, correct_count, total_count, errors_list)
        """
        correct = 0
        total = 0
        errors = []
        
        for problem, student_refs in self.ground_truth.items():
            for student_ref in student_refs:
                student = student_ref[0]
                expected_ref = student_ref[1]
                
                # Get similarity scores for this student
                if problem in similarity_matrix and student in similarity_matrix[problem]:
                    scores = similarity_matrix[problem][student]
                    
                    # Find the reference with highest similarity
                    predicted_ref = max(scores.items(), key=lambda x: x[1])[0]
                    
                    total += 1
                    if predicted_ref == expected_ref:
                        correct += 1
                    else:
                        errors.append({
                            'problem': problem,
                            'student': student,
                            'expected': expected_ref,
                            'predicted': predicted_ref,
                            'expected_score': scores[expected_ref],
                            'predicted_score': scores[predicted_ref],
                            'difference': scores[predicted_ref] - scores[expected_ref]
                        })
        
        accuracy = correct / total if total > 0 else 0.0
        return accuracy, correct, total, errors
    
    def ablation_study(self) -> Dict:
        """
        Perform comprehensive ablation study
        
        Returns:
            Dictionary with results for all view combinations
        """
        results = {}
        
        print("\n" + "="*70)
        print("ABLATION STUDY: Single-View and Multi-View Analysis")
        print("="*70)
        
        # Single-view evaluations
        print("\n--- SINGLE-VIEW PERFORMANCE ---")
        
        # Baseline only
        acc, correct, total, _ = self.evaluate_accuracy(self.baseline_matrix)
        results['baseline_only'] = {
            'weights': {'baseline': 1.0, 'wl': 0.0, 'ces': 0.0},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"Baseline Only:     {acc*100:.2f}% ({correct}/{total})")
        
        # WL only
        acc, correct, total, _ = self.evaluate_accuracy(self.wl_matrix)
        results['wl_only'] = {
            'weights': {'baseline': 0.0, 'wl': 1.0, 'ces': 0.0},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"WL Only:           {acc*100:.2f}% ({correct}/{total})")
        
        # CES only
        acc, correct, total, _ = self.evaluate_accuracy(self.ces_matrix)
        results['ces_only'] = {
            'weights': {'baseline': 0.0, 'wl': 0.0, 'ces': 1.0},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"CES Only:          {acc*100:.2f}% ({correct}/{total})")
        
        # Two-view combinations
        print("\n--- TWO-VIEW COMBINATIONS ---")
        
        # Baseline + WL
        combined = self.combine_matrices(0.5, 0.5, 0.0)
        acc, correct, total, _ = self.evaluate_accuracy(combined)
        results['baseline_wl'] = {
            'weights': {'baseline': 0.5, 'wl': 0.5, 'ces': 0.0},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"Baseline + WL:     {acc*100:.2f}% ({correct}/{total})")
        
        # Baseline + CES
        combined = self.combine_matrices(0.5, 0.0, 0.5)
        acc, correct, total, _ = self.evaluate_accuracy(combined)
        results['baseline_ces'] = {
            'weights': {'baseline': 0.5, 'wl': 0.0, 'ces': 0.5},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"Baseline + CES:    {acc*100:.2f}% ({correct}/{total})")
        
        # WL + CES
        combined = self.combine_matrices(0.0, 0.5, 0.5)
        acc, correct, total, _ = self.evaluate_accuracy(combined)
        results['wl_ces'] = {
            'weights': {'baseline': 0.0, 'wl': 0.5, 'ces': 0.5},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"WL + CES:          {acc*100:.2f}% ({correct}/{total})")
        
        # Three-view combination (equal weights)
        print("\n--- THREE-VIEW COMBINATION ---")
        combined = self.combine_matrices(0.333, 0.333, 0.334)
        acc, correct, total, _ = self.evaluate_accuracy(combined)
        results['all_equal'] = {
            'weights': {'baseline': 0.333, 'wl': 0.333, 'ces': 0.334},
            'accuracy': acc,
            'correct': correct,
            'total': total
        }
        print(f"All Equal (1/3):   {acc*100:.2f}% ({correct}/{total})")
        
        return results
    
    def grid_search_optimal_weights(self, step: float = 0.05) -> Dict:
        """
        Find optimal weights through grid search
        
        Args:
            step: Step size for weight grid (default: 0.05)
        
        Returns:
            Dictionary with best weights and their performance
        """
        print("\n" + "="*70)
        print(f"GRID SEARCH: Finding Optimal Weights (step={step})")
        print("="*70)
        
        best_accuracy = 0.0
        best_weights = None
        best_results = None
        
        # Generate all weight combinations that sum to 1.0
        weight_range = [round(x * step, 2) for x in range(int(1.0 / step) + 1)]
        
        total_combinations = 0
        tested_combinations = 0
        
        for w_baseline in weight_range:
            for w_wl in weight_range:
                for w_ces in weight_range:
                    # Check if weights sum to approximately 1.0
                    if abs(w_baseline + w_wl + w_ces - 1.0) < 0.01:
                        total_combinations += 1
                        
                        # Combine matrices with these weights
                        combined = self.combine_matrices(w_baseline, w_wl, w_ces)
                        acc, correct, total, errors = self.evaluate_accuracy(combined)
                        
                        tested_combinations += 1
                        
                        # Update best if this is better
                        if acc > best_accuracy:
                            best_accuracy = acc
                            best_weights = (w_baseline, w_wl, w_ces)
                            best_results = {
                                'accuracy': acc,
                                'correct': correct,
                                'total': total,
                                'errors': errors
                            }
                            
                            print(f"New Best: [{w_baseline:.2f}, {w_wl:.2f}, {w_ces:.2f}] → {acc*100:.2f}% ({correct}/{total})")
        
        print(f"\nTested {tested_combinations} weight combinations")
        print(f"\n🏆 OPTIMAL WEIGHTS FOUND:")
        print(f"   Baseline: {best_weights[0]:.2f}")
        print(f"   WL:       {best_weights[1]:.2f}")
        print(f"   CES:      {best_weights[2]:.2f}")
        print(f"   Accuracy: {best_accuracy*100:.2f}% ({best_results['correct']}/{best_results['total']})")
        
        return {
            'weights': {
                'baseline': best_weights[0],
                'wl': best_weights[1],
                'ces': best_weights[2]
            },
            'accuracy': best_accuracy,
            'correct': best_results['correct'],
            'total': best_results['total'],
            'errors': best_results['errors']
        }
    
    def evaluate_custom_weights(self, w_baseline: float, w_wl: float, w_ces: float) -> Dict:
        """
        Evaluate with custom weights
        
        Args:
            w_baseline: Weight for baseline
            w_wl: Weight for WL
            w_ces: Weight for CES
        
        Returns:
            Evaluation results dictionary
        """
        print("\n" + "="*70)
        print(f"CUSTOM WEIGHTS EVALUATION")
        print("="*70)
        print(f"Weights: Baseline={w_baseline:.2f}, WL={w_wl:.2f}, CES={w_ces:.2f}")
        
        combined = self.combine_matrices(w_baseline, w_wl, w_ces)
        acc, correct, total, errors = self.evaluate_accuracy(combined)
        
        print(f"Accuracy: {acc*100:.2f}% ({correct}/{total})")
        
        return {
            'weights': {
                'baseline': w_baseline,
                'wl': w_wl,
                'ces': w_ces
            },
            'accuracy': acc,
            'correct': correct,
            'total': total,
            'errors': errors
        }
    
    def save_results(self, results: Dict, output_path: str):
        """Save evaluation results to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {output_path}")
    
    def print_summary_report(self, results: Dict):
        """Print a comprehensive summary report"""
        print("\n" + "="*70)
        print("COMPREHENSIVE EVALUATION SUMMARY")
        print("="*70)
        
        # Sort results by accuracy
        sorted_results = sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True)
        
        print(f"\n{'Configuration':<25} {'Weights (B/W/C)':<20} {'Accuracy':<12} {'Correct/Total'}")
        print("-" * 70)
        
        for name, data in sorted_results:
            weights_str = f"{data['weights']['baseline']:.2f}/{data['weights']['wl']:.2f}/{data['weights']['ces']:.2f}"
            acc_str = f"{data['accuracy']*100:.2f}%"
            count_str = f"{data['correct']}/{data['total']}"
            print(f"{name:<25} {weights_str:<20} {acc_str:<12} {count_str}")


def main():
    """Main execution function"""
    
    # Configuration
    MATRICES_DIR = "evaluation/matrices"
    GROUND_TRUTH_PATH = "data/ground_truth.json"
    OUTPUT_DIR = "evaluation"
    
    print("="*70)
    print("MULTI-VIEW CODE SIMILARITY COMPREHENSIVE EVALUATION")
    print("="*70)
    
    # Initialize evaluator
    evaluator = MultiViewEvaluator(MATRICES_DIR, GROUND_TRUTH_PATH)
    
    # 1. Evaluate with user-specified weights
    print("\n" + "="*70)
    print("1. EVALUATING USER-SPECIFIED WEIGHTS")
    print("="*70)
    
    user_results = evaluator.evaluate_custom_weights(
        w_baseline=0.35,
        w_wl=0.40,
        w_ces=0.25
    )
    
    # 2. Perform ablation study
    print("\n" + "="*70)
    print("2. ABLATION STUDY")
    print("="*70)
    
    ablation_results = evaluator.ablation_study()
    
    # 3. Find optimal weights
    print("\n" + "="*70)
    print("3. OPTIMAL WEIGHT SEARCH")
    print("="*70)
    
    optimal_results = evaluator.grid_search_optimal_weights(step=0.05)
    
    # Combine all results
    all_results = {
        'user_specified': user_results,
        **ablation_results,
        'optimal': optimal_results
    }
    
    # 4. Print comprehensive summary
    evaluator.print_summary_report(all_results)
    
    # 5. Save results
    output_path = os.path.join(OUTPUT_DIR, "comprehensive_evaluation_results.json")
    evaluator.save_results(all_results, output_path)
    
    print("\n" + "="*70)
    print("EVALUATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Key Findings:")
    print(f"   User Weights (0.35/0.40/0.25): {user_results['accuracy']*100:.2f}%")
    print(f"   Optimal Weights ({optimal_results['weights']['baseline']:.2f}/{optimal_results['weights']['wl']:.2f}/{optimal_results['weights']['ces']:.2f}): {optimal_results['accuracy']*100:.2f}%")
    print(f"   Best Single View: WL at {ablation_results['wl_only']['accuracy']*100:.2f}%")
    print(f"\n   Improvement from single-view to optimal: +{(optimal_results['accuracy'] - ablation_results['wl_only']['accuracy'])*100:.2f}%")


if __name__ == "__main__":
    main()
