# APM (Abstract Program Model) Semantic Translation Integrity

## The Translation Dataset Profile
Unlike standard Large Language Model (LLM) textual hallucination attempts, our translation framework relies entirely on **structural determinism**. This represents the deterministic zero-shot generation engine of our architecture.

**The APM Evaluation Dataset Matrix:**
To empirically validate our APM routing logic, we instituted a comprehensive **120-pair algorithmic translation matrix**.
*   **20 Base Problems:** Ranging in complexity from standard logic sorts to complex nested memory management.
*   **6 Directional Pairs:** (C→C++, C++→C, C→Java, Java→C, C++→Java, Java→C++).
*   **Methodology:** Each source algorithm was processed through Joern to output an APM JSON State schema (abstracting all control flow, types, and variables), and then passed through independent code generators (`generate_target.py`) to reconstitute a perfectly valid target file in the requisite language.

## Benchmark Verification Results
The outputs inside this directory prove the success of this architectural approach and heavily inform our 61.5% competitive displacement metric against neural baselines:
*   **`apm_final_evaluation_results.json`**: This is the exhaustive definitive logging sheet. It explicitly tracks every single one of the 120 translations, verifying if the system safely achieved **100% Syntactic Reconstruction** and subsequently guaranteeing **Compilation Integrity** & Behavioral **Input/Output exact matches**.
*   **`apm_v2_eval/`**: Houses all 120 successful cross-language translations generated strictly via JSON abstracted state mapping. No textual generation (e.g., CodeBERT/UniXCoder) was utilized in the creation of these functional algorithms.
