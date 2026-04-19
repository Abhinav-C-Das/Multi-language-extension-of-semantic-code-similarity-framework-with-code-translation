#!/usr/bin/env python3
"""
CES Zero-Score Analysis
=======================
Finds all cases where CES v3 gives 0.0 for ALL references,
analyzes the code to understand why, and provides fix recommendations.
"""

import json
import os
from typing import List, Dict, Tuple


class CESZeroAnalyzer:
    """Analyzer for CES zero-score cases"""
    
    def __init__(self, ces_matrix_path: str, data_dir: str):
        self.data_dir = data_dir
        
        # Load CES matrix
        with open(ces_matrix_path, 'r') as f:
            self.ces_matrix = json.load(f)
        
        print(f"✓ Loaded CES matrix from {ces_matrix_path}")
    
    def find_all_zero_cases(self) -> List[Dict]:
        """Find all cases where CES = 0.0 for ALL references"""
        zero_cases = []
        
        for problem, students in self.ces_matrix.items():
            for student, refs in students.items():
                # Check if ALL references have 0.0 score
                all_zero = all(score == 0.0 for score in refs.values())
                
                if all_zero:
                    zero_cases.append({
                        'problem': problem,
                        'student': student,
                        'refs': refs
                    })
        
        return zero_cases
    
    def read_code(self, problem: str, code_type: str, code_id: str) -> str:
        """Read source code file"""
        # Try .cpp first, then .c
        for ext in ['.cpp', '.c']:
            path = os.path.join(self.data_dir, problem, code_type, f"{code_id}{ext}")
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except:
                    pass
        return "FILE NOT FOUND"
    
    def analyze_code_patterns(self, code: str) -> Dict:
        """Analyze code to identify patterns"""
        patterns = {
            'has_recursion': False,
            'has_loop': False,
            'has_helper_function': False,
            'has_accumulator': False,
            'has_array_access': False,
            'has_conditional': False,
            'has_early_return': False,
            'has_swap': False,
            'has_comparison': False,
            'is_empty_or_trivial': False,
            'has_stl_algorithm': False,
            'code_length': len(code.split('\n'))
        }
        
        if code == "FILE NOT FOUND" or len(code.strip()) < 50:
            patterns['is_empty_or_trivial'] = True
            return patterns
        
        code_lower = code.lower()
        
        # Check for recursion (function calling itself)
        # Look for function name in code
        lines = code.split('\n')
        for line in lines:
            if 'int ' in line and '(' in line and '{' not in line:
                # Found function definition
                func_name = line.split('(')[0].split()[-1]
                if func_name in code[code.index(line):]:
                    patterns['has_recursion'] = True
                    break
        
        # Check for loops
        patterns['has_loop'] = any(keyword in code for keyword in ['for (', 'while (', 'do {'])
        
        # Check for helper functions (multiple function definitions)
        func_count = code.count('int ') + code.count('void ') + code.count('bool ')
        func_count -= code.count('int main')
        patterns['has_helper_function'] = func_count > 1
        
        # Check for accumulator pattern
        patterns['has_accumulator'] = any(keyword in code_lower for keyword in 
            ['accumulator', 'acc', 'sum', 'total', 'result', 'count'])
        
        # Check for array access
        patterns['has_array_access'] = '[' in code and ']' in code
        
        # Check for conditionals
        patterns['has_conditional'] = 'if (' in code or 'switch (' in code
        
        # Check for early return
        patterns['has_early_return'] = 'return' in code and patterns['has_conditional']
        
        # Check for swap
        patterns['has_swap'] = 'swap' in code_lower or 'temp' in code_lower
        
        # Check for comparisons
        patterns['has_comparison'] = any(op in code for op in ['==', '!=', '<', '>', '<=', '>='])
        
        # Check for STL algorithms
        patterns['has_stl_algorithm'] = any(alg in code_lower for alg in 
            ['accumulate', 'sort', 'find', 'count', 'transform'])
        
        return patterns
    
    def diagnose_why_zero(self, student_code: str, ref_codes: Dict[str, str]) -> Dict:
        """Diagnose why CES gave 0.0"""
        student_patterns = self.analyze_code_patterns(student_code)
        
        diagnosis = {
            'reason': 'UNKNOWN',
            'explanation': '',
            'student_patterns': student_patterns,
            'missing_ces_patterns': [],
            'fix_recommendation': ''
        }
        
        # Check if code is empty/trivial
        if student_patterns['is_empty_or_trivial']:
            diagnosis['reason'] = 'EMPTY_OR_TRIVIAL'
            diagnosis['explanation'] = 'Code is empty, too short, or file not found'
            diagnosis['fix_recommendation'] = 'Check if file exists and has valid code'
            return diagnosis
        
        # Check for tail recursion
        if student_patterns['has_recursion'] and student_patterns['has_helper_function']:
            if 'accumulator' in student_code.lower() or 'acc' in student_code.lower():
                diagnosis['reason'] = 'TAIL_RECURSION'
                diagnosis['explanation'] = 'Uses tail recursion with accumulator parameter'
                diagnosis['missing_ces_patterns'].append('TAIL_RECURSIVE')
                diagnosis['fix_recommendation'] = 'Add TAIL_RECURSIVE pattern to CES v3'
                return diagnosis
        
        # Check for simple recursion without patterns
        if student_patterns['has_recursion'] and not student_patterns['has_loop']:
            diagnosis['reason'] = 'SIMPLE_RECURSION'
            diagnosis['explanation'] = 'Uses simple recursion without accumulation patterns'
            diagnosis['missing_ces_patterns'].append('HEAD_RECURSIVE')
            diagnosis['fix_recommendation'] = 'Add HEAD_RECURSIVE pattern to CES v3'
            return diagnosis
        
        # Check for no loops or recursion (direct computation)
        if not student_patterns['has_loop'] and not student_patterns['has_recursion']:
            diagnosis['reason'] = 'DIRECT_COMPUTATION'
            diagnosis['explanation'] = 'No loops or recursion - direct formula/computation'
            diagnosis['missing_ces_patterns'].append('DIRECT_FORMULA')
            diagnosis['fix_recommendation'] = 'Add DIRECT_FORMULA pattern or accept 0.0 as correct'
            return diagnosis
        
        # Check for STL algorithms
        if student_patterns['has_stl_algorithm']:
            diagnosis['reason'] = 'STL_ALGORITHM'
            diagnosis['explanation'] = 'Uses STL algorithms (accumulate, sort, etc.)'
            diagnosis['missing_ces_patterns'].append('STL_ALGORITHM')
            diagnosis['fix_recommendation'] = 'Enhance STL algorithm detection in CES v3'
            return diagnosis
        
        # Check for complex patterns not captured
        if student_patterns['has_loop'] and student_patterns['has_helper_function']:
            diagnosis['reason'] = 'COMPLEX_STRUCTURE'
            diagnosis['explanation'] = 'Complex code structure with helper functions'
            diagnosis['missing_ces_patterns'].append('HELPER_FUNCTION_PATTERN')
            diagnosis['fix_recommendation'] = 'Analyze helper function patterns separately'
            return diagnosis
        
        # Check for simple loop without clear patterns
        if student_patterns['has_loop'] and not student_patterns['has_array_access']:
            diagnosis['reason'] = 'SIMPLE_LOOP_NO_ARRAY'
            diagnosis['explanation'] = 'Loop without array access - may use different data structure'
            diagnosis['fix_recommendation'] = 'Check if CES patterns match loop body operations'
            return diagnosis
        
        # Default case
        diagnosis['reason'] = 'PATTERN_MISMATCH'
        diagnosis['explanation'] = 'Code has patterns but they don\'t match CES v3 definitions'
        diagnosis['fix_recommendation'] = 'Review CES pattern matching logic for this case'
        
        return diagnosis
    
    def analyze_all_zero_cases(self) -> List[Dict]:
        """Analyze all zero-score cases"""
        zero_cases = self.find_all_zero_cases()
        
        print(f"\n{'='*80}")
        print(f"Found {len(zero_cases)} cases where CES = 0.0 for ALL references")
        print(f"{'='*80}\n")
        
        analyzed_cases = []
        
        for i, case in enumerate(zero_cases, 1):
            problem = case['problem']
            student = case['student']
            
            print(f"[{i}/{len(zero_cases)}] Analyzing {problem}/{student}...")
            
            # Read student code
            student_code = self.read_code(problem, 's', student)
            
            # Read all reference codes
            ref_codes = {}
            for ref in case['refs'].keys():
                ref_codes[ref] = self.read_code(problem, 'ref', ref)
            
            # Diagnose why zero
            diagnosis = self.diagnose_why_zero(student_code, ref_codes)
            
            analyzed_cases.append({
                'problem': problem,
                'student': student,
                'student_code_preview': student_code[:200] if student_code != "FILE NOT FOUND" else "FILE NOT FOUND",
                'diagnosis': diagnosis,
                'refs': list(case['refs'].keys())
            })
        
        return analyzed_cases
    
    def generate_report(self, analyzed_cases: List[Dict], output_path: str):
        """Generate comprehensive report"""
        
        # Group by reason
        by_reason = {}
        for case in analyzed_cases:
            reason = case['diagnosis']['reason']
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(case)
        
        # Generate report
        with open(output_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("CES v3 ZERO-SCORE ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total cases with CES = 0.0 for all references: {len(analyzed_cases)}\n")
            f.write(f"Percentage of dataset: {len(analyzed_cases)/400*100:.1f}%\n\n")
            
            f.write("="*80 + "\n")
            f.write("SUMMARY BY REASON\n")
            f.write("="*80 + "\n\n")
            
            for reason, cases in sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"\n{reason}: {len(cases)} cases ({len(cases)/len(analyzed_cases)*100:.1f}%)\n")
                f.write("-"*80 + "\n")
                
                # Get explanation from first case
                explanation = cases[0]['diagnosis']['explanation']
                f.write(f"Explanation: {explanation}\n")
                
                # Get missing patterns
                missing = cases[0]['diagnosis']['missing_ces_patterns']
                if missing:
                    f.write(f"Missing CES patterns: {', '.join(missing)}\n")
                
                # Get fix recommendation
                fix = cases[0]['diagnosis']['fix_recommendation']
                f.write(f"Fix: {fix}\n")
                
                # List all cases
                f.write(f"\nCases:\n")
                for case in cases:
                    f.write(f"  - {case['problem']}/{case['student']}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("DETAILED CASE ANALYSIS\n")
            f.write("="*80 + "\n\n")
            
            for i, case in enumerate(analyzed_cases, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"CASE {i}: {case['problem']}/{case['student']}\n")
                f.write(f"{'='*80}\n\n")
                
                f.write(f"Reason: {case['diagnosis']['reason']}\n")
                f.write(f"Explanation: {case['diagnosis']['explanation']}\n")
                f.write(f"References: {', '.join(case['refs'])}\n\n")
                
                f.write("Student Code Patterns:\n")
                for key, value in case['diagnosis']['student_patterns'].items():
                    f.write(f"  {key}: {value}\n")
                
                f.write(f"\nMissing CES Patterns: {', '.join(case['diagnosis']['missing_ces_patterns']) if case['diagnosis']['missing_ces_patterns'] else 'None identified'}\n")
                f.write(f"Fix Recommendation: {case['diagnosis']['fix_recommendation']}\n")
                
                f.write(f"\nCode Preview:\n")
                f.write("-"*80 + "\n")
                f.write(case['student_code_preview'])
                f.write("\n...\n")
            
            # Add recommendations section
            f.write("\n\n" + "="*80 + "\n")
            f.write("RECOMMENDATIONS FOR CES v3 ENHANCEMENT\n")
            f.write("="*80 + "\n\n")
            
            # Collect all missing patterns
            all_missing = set()
            for case in analyzed_cases:
                all_missing.update(case['diagnosis']['missing_ces_patterns'])
            
            f.write("New patterns to add to CES v3:\n\n")
            for i, pattern in enumerate(sorted(all_missing), 1):
                f.write(f"{i}. {pattern}\n")
                
                # Add implementation hints
                if pattern == 'TAIL_RECURSIVE':
                    f.write("   Implementation: Detect recursion with accumulator parameter\n")
                    f.write("   Pattern: function(params..., accumulator) with recursive call\n\n")
                elif pattern == 'HEAD_RECURSIVE':
                    f.write("   Implementation: Detect recursion with computation on return\n")
                    f.write("   Pattern: return value + recursive_call(n-1)\n\n")
                elif pattern == 'DIRECT_FORMULA':
                    f.write("   Implementation: Detect direct computation without loops\n")
                    f.write("   Pattern: Single return statement with formula\n\n")
                elif pattern == 'STL_ALGORITHM':
                    f.write("   Implementation: Enhance detection of std::accumulate, etc.\n")
                    f.write("   Pattern: std::algorithm_name(...)\n\n")
                else:
                    f.write("\n")
        
        print(f"\n✓ Report saved to: {output_path}")


def main():
    """Main execution"""
    
    CES_MATRIX = "evaluation/matrices/ces_v3_similarity_matrix_local.json"
    DATA_DIR = "data"
    OUTPUT_REPORT = "evaluation/CES_ZERO_ANALYSIS_REPORT.txt"
    OUTPUT_JSON = "evaluation/ces_zero_cases.json"
    
    print("="*80)
    print("CES v3 ZERO-SCORE COMPREHENSIVE ANALYSIS")
    print("="*80)
    
    analyzer = CESZeroAnalyzer(CES_MATRIX, DATA_DIR)
    
    # Analyze all zero cases
    analyzed_cases = analyzer.analyze_all_zero_cases()
    
    # Generate report
    analyzer.generate_report(analyzed_cases, OUTPUT_REPORT)
    
    # Save JSON for programmatic access
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(analyzed_cases, f, indent=2)
    
    print(f"✓ JSON data saved to: {OUTPUT_JSON}")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    # Group by reason
    by_reason = {}
    for case in analyzed_cases:
        reason = case['diagnosis']['reason']
        by_reason[reason] = by_reason.get(reason, 0) + 1
    
    print(f"\nTotal zero-score cases: {len(analyzed_cases)} ({len(analyzed_cases)/400*100:.1f}% of dataset)")
    print("\nBreakdown by reason:")
    for reason, count in sorted(by_reason.items(), key=lambda x: x[1], reverse=True):
        print(f"  {reason:<30} {count:>3} cases ({count/len(analyzed_cases)*100:>5.1f}%)")
    
    # Collect missing patterns
    missing_patterns = set()
    for case in analyzed_cases:
        missing_patterns.update(case['diagnosis']['missing_ces_patterns'])
    
    print(f"\n🔧 Missing CES patterns identified: {len(missing_patterns)}")
    for pattern in sorted(missing_patterns):
        print(f"   • {pattern}")
    
    print(f"\n📄 Full report: {OUTPUT_REPORT}")
    print(f"📊 JSON data: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
