# Java Equivalency & Structural Mapping Results

## The Java Dataset Profile
The Java dataset tracks the exact same **20 fundamental algorithmic challenges** as the C++ baseline, but features distinctly different architectural profiles.

**The Challenge of Java Evaluation:**
Where C/C++ utilizes raw pointer mechanics, procedural standardizations, and dynamic memory allocations (`malloc`), Java heavily forces Object-Oriented limits. 
*   Our dataset tracks how `Scanner` classes alter standard I/O Variable Lifespans (WL).
*   It tracks how Java `.length` attributes map identically in logic—but not syntax—to C++ `sizeof()` operations.
*   The data pipeline successfully maps these N=400 cohorts across paradigm boundaries without relying on textual tokenizers.

## The Results Explained
Inside the `evaluation/` directory, the JSON matrices display the raw similarity score aggregations:
*   `ces_similarity_matrix_java.json`: Focuses explicitly on loop control flow and object instantiation mapping.
*   `wl_similarity_matrix_java.json`: Validates that variable lifecycles (like accumulators across a `while` loop) map accurately regardless of object scope.
*   `final_similarity_matrix_java.json`: The aggregated baseline providing our final academic accuracy metrics utilizing the 35/40/25% scaling weights.
