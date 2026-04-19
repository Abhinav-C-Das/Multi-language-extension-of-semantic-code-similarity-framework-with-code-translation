# CKG Framework Evaluation Results

This directory contains the definitive, final empirical validation artifacts mapping the outputs of the syntax-agnostic similarity algorithms alongside our advanced Abstract Program Model (APM) translation layer. 

## Experimental Parameters & Dataset Profile
The datasets deployed across this evaluation represent **N=400 isolated logic implementations**, mapping back to **20 universal algorithmic standard problems** (e.g. Bubble Sort, Breadth-First Search). Against each problem, an exhaustive benchmark mapping was completed utilizing **120 reference solution permutations** mapped across C, C++, and Java paradigms.

## Directory Structure
*   `cpp/` - Similarity results analyzing exclusively the C++ feature vectors vs. canonical reference code bases. Contains isolated vectors, final evaluations, and a sub-readme (`cpp_dataset.txt`).
*   `java/` - Extrapolated Java structural equivalents with specific focus on Object-Oriented paradigm variances versus structural flattening techniques.
*   `cross/` - Cross-language feature combinations proving that syntax-agnostic vectors generated in C/C++ can correlate perfectly to behavioral matches encoded in Java without any raw translation.
*   `translation/` - The comprehensive empirical suite analyzing the 120-translation matrix generated via our APM module. Proves 100% syntactic preservation and compiler validity metrics as finalized in our publication.

## Verification
All logs stored inside these subset subdirectories are strictly immutable evaluation objects meant to serve as transparent, empirical proof aligned directly with our submitted manuscript outcomes.
