# Itemized Summary of Changes & Reviewer Response Letter
**Manuscript Title:** An Interpretable Deterministic Framework for Cross-Language Educational Code Similarity Using Code Property Graphs  
**Target Journal:** IEEE Access  

---

## Executive Summary of Remediation Strategy

In accordance with the editorial decision and strict post-acceptance constraints (**"Do not make any changes to the author list, and do not make any changes to references"**), all requested methodological clarifications, statistical sensitivity analyses, and table remediations have been executed purely through text, table, and LaTeX source updates. No references were modified, added, or deleted.

---

## Itemized Response Matrix

### 1. Reconciling Table 10 Aggregate Accuracy & Directional Disclosures
* **Reviewer/Editor Concern:** Table 10 footnote claimed directions $C \rightarrow \text{Java}$ ($n=11$) and $\text{C++} \rightarrow \text{Java}$ ($n=3$) were "excluded" from aggregate accuracy, despite $349/400 = 87.25\%$ arithmetically including them.
* **Remediation Action:**
  - Table 10 (now `tab:directional_results` in Section VI-A) has been relabeled with complete mathematical honesty.
  - **Full-Corpus Aggregate ($N=400$):** $349/400 = 87.25\%$ [95% Wilson CI: 83.60%, 90.20%].
  - **Core-Direction Aggregate ($n=386$):** $342/386 = 88.60\%$ [95% Wilson CI: 85.04%, 91.46%] (covering Java$\rightarrow$C/C++ and C$\leftrightarrow$C++).
  - All text references in Section VI-A, Abstract, and Section VIII (Conclusion) have been updated to report both full-corpus and core-direction metrics side-by-side.

### 2. Single-View Ablation Study
* **Reviewer Concern:** Isolation of individual representation views (BL, WL, CES) was needed to justify the multi-view late-fusion architecture.
* **Remediation Action:**
  - Added a dedicated **Single-View Ablation Study** table (`tab:single_view_ablation`) in Section VI-B:
    - **BL-only ($w_{\text{BL}}=1.0$):** $79.50\%$ [95% Wilson CI: 75.35%, 83.11%]
    - **WL-only ($w_{\text{WL}}=1.0$):** $71.68\%$ [95% Wilson CI: 67.07%, 75.88%]
    - **CES-only ($w_{\text{CES}}=1.0$):** $72.68\%$ [95% Wilson CI: 68.11%, 76.82%]
    - **Fused Framework ($0.35, 0.40, 0.25$):** $87.25\%$ [95% Wilson CI: 83.60%, 90.20%]
  - Demonstrates a statistically significant $+7.75\text{ pp}$ gain of late fusion over the strongest isolated view (lexical BL).

### 3. Reframing TF-IDF Baseline as Internal View Ablation
* **Reviewer Concern:** Clarify whether TF-IDF is an external baseline or an internal framework component.
* **Remediation Action:**
  - Relabeled `TF-IDF baseline` in Table 2 (`tab:baseline_comparison`) as `Framework BL-View Ablation (wBL=1)`.
  - Added a clear table row separator demarcating **External Baselines** (JPlag, MOSS, CodeBERT, UniXcoder) from **Internal Component Ablations**.
  - Reframed McNemar statistical analysis paragraph to explain that McNemar's test quantifies the incremental gain of fusing structural (WL) and semantic (CES) views over lexical TF-IDF alone ($p < 0.0001$, $\text{OR}=4.875$).

### 4. Adversarial Floor Bug Fix ($n=60$ IRR Grounding)
* **Reviewer Concern:** The 64.0% adversarial floor claim conflated $n=93$ zero-CES cases from an uncurated ablation set with $n=60$ IRR sample size.
* **Remediation Action:**
  - Withdrew the invalid $(349-93)/400 = 64.0\%$ formula in Threat Group 1 (Section VII-E).
  - Replaced with a mathematically grounded annotation-uncertainty floor: Inter-rater agreement on $n=60$ sample yielded $\kappa=0.86$ ($11.67\%$ discordant pairs).
  - Conservative bound assuming all inter-rater uncertainty pairs represent retrieval failures: $[349 - (0.1167 \times 400)]/400 \approx 75.58\%$.

### 5. Selection Bias & Construct Validity Threat Disclosure
* **Reviewer Concern:** Need explicit disclosure of selection bias between uncurated and curated benchmark datasets.
* **Remediation Action:**
  - Added named **Selection Bias** threat disclosure in Threat Group 2 (Section VII-E).
  - Explicitly cited the contrast between 23.25% zero-CES rate in uncurated data vs 0.25% in curated data, and documented that 90.3% WL fallback mitigates zero-CES cases.

### 6. Phase 1 Methodological Self-Containment
* **Reviewer/Editor Constraint:** Provide full Phase 1 details without altering references.
* **Remediation Action:**
  - Refactored Section III-A (`subsec:phase1_base`) to explicitly detail:
    1) 104-program C dataset collected across the same 20 CS-1 problem domains.
    2) Grid-search optimization (in 0.05 increments) yielding $(w_{\text{BL}}, w_{\text{WL}}, w_{\text{CES}}) = (0.35, 0.40, 0.25)$.
    3) Weisfeiler-Lehman graph kernel hop depth $h=2$ validation.
    4) Explicit cross-reference to Table `tab:ces_taxonomy` enumerating the 9 original Phase 1 CES patterns.

### 7. Formatting & Math Compliance
* **IEEE Standard:** Converted all multi-letter math subscripts ($w_{\text{BL}}, w_{\text{WL}}, w_{\text{CES}}, s_{\text{BL}}, s_{\text{WL}}, s_{\text{CES}}$) to upright (roman) font.

---
*Generated for IEEE Access Phase 2 Final Submission Package.*
