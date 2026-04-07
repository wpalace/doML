# Phase 5 Context: Data Understanding

**Phase:** 05 — Data Understanding
**Goal:** Implement the Data Understanding (EDA) analysis phase — producing `notebooks/02_data_understanding.ipynb` and `reports/eda_report.html` when a data scientist runs `/doml-execute-phase 2`.
**Requirements:** EDA-01 through EDA-10, OUT-01, OUT-02, OUT-03

---

## Prior Phase Outputs (Carrying Forward)

From Phase 3:
- `doml/data_scan.py` — `scan_data_folder()` / `format_scan_report()` reusable for initial file detection
- `.planning/config.json` — `problem_type`, `time_factor`, `analysis_language`, `dataset.path`, `dataset.format`
- `.planning/PROJECT.md` — business question, stakeholder, dataset description, provenance

From Phase 4:
- BU notebook pattern: PROJECT_ROOT env var, `parameters` cell, IPython.display.Markdown, DuckDB per-file connection
- execute-phase.md Steps 3a/3b/3c pattern (copy template → nbconvert --execute → verify)
- execute-phase.md Steps 5a–5d pattern (executive narrative → nbconvert --no-input → 4 checks)

Packages available (requirements.txt — pinned):
- `duckdb==1.5.1`, `scipy==1.16.3`, `statsmodels==0.14.4`, `seaborn==0.13.2`
- `matplotlib==3.10.0`, `pandas==2.3.3`, `numpy==2.3.5`
- `nbformat==5.10.4`, `nbconvert==7.16.4`, `papermill==2.6.0`

---

<decisions>

## Decision 1: No ydata-profiling

**Resolved:** Remove entirely. Do not use in Phase 5.

ydata-profiling (`pkg_resources` dependency) fails to import inside the Docker container (conda Python 3.13 environment). It was removed from `requirements.in` and `requirements.txt` in the discuss-phase session (2026-04-07, commit e0abcaa).

Phase 5 EDA is implemented manually with DuckDB + scipy + statsmodels + seaborn. This aligns with DoML's traceable analysis philosophy — every finding is tied to visible, citable code.

**How to apply:** No import of `ydata_profiling` anywhere in Phase 5. No fallback attempt. Use DuckDB for profiling queries (EDA-02), scipy for statistical tests (EDA-03, EDA-04), seaborn/matplotlib for visualizations.

---

## Decision 2: MCAR/MAR/MNAR Assessment — Visual + Guided Text (No Little's Test)

**Resolved:** Implement missingness analysis as:
1. Missingness heatmap (seaborn `heatmap` of boolean null mask)
2. Percentage missing per column (sorted bar chart)
3. Correlation-of-missingness matrix — which columns tend to be missing together (`df.isnull().corr()`)
4. A Markdown cell explaining the MCAR/MAR/MNAR framework and asking the analyst to interpret the patterns

No Little's MCAR test. `pingouin` is not in requirements.txt and adding another dependency has a history of container friction in this project.

**How to apply:** EDA-05 is satisfied by visual output + interpretive guidance. The Markdown cell should explain: MCAR (missingness unrelated to any data) → safe to use complete-case analysis; MAR (missingness related to observed variables) → look for correlating columns in the matrix; MNAR (missingness related to the missing value itself) → requires domain knowledge to detect.

---

## Decision 3: Language-Adaptive Notebooks — Honour `analysis_language` from config.json

**Resolved:** Phase 5 is the first phase to honour the user's language preference set at kickoff.

- If `config.json` `analysis_language == "python"` (default): generate a Python notebook with IRkernel `python3`
- If `config.json` `analysis_language == "r"`: generate an R notebook with IRkernel `ir`

**Why Phase 5 and not Phase 4:** BU (Phase 4) is primarily narrative — the language choice matters less. EDA is where statistical test APIs and visualization libraries diverge significantly between Python and R. R's ggplot2 + tidyverse is arguably better suited for EDA than Python's scipy + seaborn.

**Implementation:** The execute-phase.md Phase 2 executor reads `analysis_language` from config.json before selecting which template to copy:
- Python: `.claude/doml/templates/notebooks/data_understanding_python.ipynb`
- R: `.claude/doml/templates/notebooks/data_understanding_r.ipynb`

**R package availability:** The R stack in the container has known installation issues (arrow, prophet deferred to Milestone 2). Verify the following R packages are available before committing to the R template: `tidyverse`, `corrplot`, `tseries` (for ADF), `urca` (for KPSS), `naniar` (for missingness visualization). If any fail, document in SUMMARY and fall back to Python.

**How to apply:** Two notebook templates needed for Phase 5 (one Python, one R). The execute-phase.md Phase 2 executor checks `analysis_language` and copies the appropriate one.

---

## Decision 4: Cleaned Dataset — Structural Only, No Imputation

**Resolved:** The dataset written to `data/processed/` at the end of EDA (EDA-08) applies structural cleaning only:
1. Drop fully duplicate rows
2. Parse columns that are clearly date strings to datetime dtype (where unambiguous)
3. Write the result to `data/processed/[original_filename]` preserving the original format where possible (CSV → CSV, Parquet → Parquet)

**No imputation in Phase 5.** Imputation is deferred to Phase 6 (Modelling) where it belongs inside a scikit-learn `Pipeline` (or R `recipes` package for R projects). The choice of imputation strategy depends on the model — information not available at EDA time.

**EDA documents but does not fix:** For every data quality issue found (nulls, outliers, type mismatches, tidy violations), the notebook flags it in a Markdown cell and suggests a course of action. The processed dataset reflects only the structural changes above.

**How to apply:** Final EDA notebook section: (1) apply structural cleaning, (2) write to `data/processed/`, (3) print confirmation with row/col counts before and after. Markdown cell above summarises all flagged issues and deferred decisions.

---

## Decision 5: DuckDB / pandas Split

**Resolved:** DuckDB for all initial profiling on raw files (EDA-02). Pandas for statistical computation and visualization.

- DuckDB: schema, row/null counts, unique counts, value frequency distributions (SQL GROUP BY) — zero-copy on raw files
- pandas: load a sample (or full dataset if < ~500k rows) for scipy statistical tests, seaborn visualizations
- Threshold for full load vs. sample: if `row_count > 500_000`, use `LIMIT 50000` DuckDB sample for statistical tests and visualizations; note the sample size in the notebook

**How to apply:** EDA notebook structure — DuckDB profiling section first (no pandas load), then one `pd.DataFrame` load (or DuckDB sample) used for the rest of the notebook.

---

## Decision 6: Statistical Tests Library Choices

**Resolved (no user input needed — standard choices):**

| Test | Requirement | Library | Function |
|------|-------------|---------|---------|
| Normality | EDA-03 | `scipy.stats` | `shapiro()` (n≤5000), `normaltest()` (n>5000) |
| Pearson correlation | EDA-04 | `scipy.stats` | `pearsonr()` |
| Cramér's V | EDA-04 | manual | `chi2_contingency` → Cramér's formula |
| Point-biserial | EDA-04 | `scipy.stats` | `pointbiserialr()` |
| ADF stationarity | EDA-06 | `statsmodels.tsa.stattools` | `adfuller()` |
| KPSS stationarity | EDA-06 | `statsmodels.tsa.stattools` | `kpss()` |
| Time series decomposition | EDA-06 | `statsmodels.tsa.seasonal` | `seasonal_decompose()` |

**Correlation method selection rule (EDA-04):**
- Both columns numeric → Pearson
- Both columns categorical (dtype object/category or cardinality < 10% of rows) → Cramér's V
- One numeric, one binary → point-biserial

---

## Decision 7: Tidy Data Validation Scope (EDA-07)

**Resolved:** Check for these three tidy violations:
1. **Duplicate rows** — `df.duplicated().sum()` — report count and show examples
2. **Multiple values in one cell** — detect comma/semicolon-separated values in string columns — flag columns where > 5% of non-null values match `r'[,;|]'`
3. **Mixed observation types** — flag if a single table appears to contain multiple entity types (heuristic: check if column name prefixes suggest different entities, e.g., `customer_*` and `product_*` coexisting)

Flag violations in a Markdown cell with suggested remediation. Do not silently reshape or fix.

</decisions>

---

<canonical_refs>
- `.planning/config.json` — `analysis_language`, `problem_type`, `time_factor`, `dataset.path`
- `.planning/PROJECT.md` — business context, provenance, known biases
- `.claude/doml/templates/notebooks/business_understanding.ipynb` — reference for cell structure patterns
- `.claude/doml/workflows/execute-phase.md` — Phase 2 executor stub (to be replaced in Plan 05-02)
- `CLAUDE.md` — REPR-01 (seeds), REPR-02 (PROJECT_ROOT), INFR-05 (data/raw read-only), OUT-03 (caveats)
</canonical_refs>

---

<deferred>
## Deferred to Phase 6 (Modelling)

- **Imputation** — belongs inside the preprocessing Pipeline, strategy depends on model choice
- **Feature engineering** — EDA identifies candidates; Modelling implements them
- **R package availability verification** — if R template is needed, verify tidyverse/tseries/urca/naniar in container before Phase 5 execute

## Deferred to Milestone 2

- R EDA packages: arrow, prophet, forecast — compilation issues in conda environment
</deferred>
