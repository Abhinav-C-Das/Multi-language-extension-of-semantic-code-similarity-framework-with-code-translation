import numpy as np

def calc_java_cv():
    # Read the Java results to get actual mismatches
    with open('results/java/results.txt.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract mismatches which are formatted like: "p7/s14:"
    mismatches = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('p') and '/' in line and line.endswith(':'):
            mismatches.append(line[:-1]) # remove colon
            
    print(f"Found {len(mismatches)} mismatches")
    
    # Map to problems
    problem_mismatches = {}
    for p in range(1, 21):
        problem_mismatches[f'p{p}'] = 0
        
    for m in mismatches:
        prob = m.split('/')[0]
        if prob in problem_mismatches:
            problem_mismatches[prob] += 1
            
    # Calculate fold accuracies
    problems = [f'p{i}' for i in range(1, 21)]
    folds = [problems[i:i+4] for i in range(0, 20, 4)]
    
    fold_accuracies = []
    for fold in folds:
        total_in_fold = 4 * 20 # 4 problems, 20 students each = 80 queries
        errors_in_fold = sum(problem_mismatches[p] for p in fold)
        acc = (total_in_fold - errors_in_fold) / total_in_fold
        fold_accuracies.append(acc)
        
    mean_acc = np.mean(fold_accuracies) * 100
    std_acc = np.std(fold_accuracies) * 100
    print(f"ACTUAL Java 5-Fold CV Accuracy: {mean_acc:.2f}% ± {std_acc:.2f}%")

if __name__ == '__main__':
    calc_java_cv()
