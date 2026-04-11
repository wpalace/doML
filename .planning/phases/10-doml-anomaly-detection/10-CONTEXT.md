# Phase 10: doml-anomaly-detection — Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement an optional post-EDA anomaly detection skill. When invoked, it runs Isolation Forest, Local Outlier Factor (LOF), and DBSCAN-based flagging on a dataset, producing a dedicated notebook (`notebooks/anomaly_detection.ipynb`), an HTML report (`reports/anomaly_report.html`) with code hidden and Claude narrative, and an anomaly flag CSV (`data/processed/anomaly_flags_{filename}.csv`).

This is not a modelling phase — it produces diagnostic artifacts and a reusable flag file, not a trained predictive model. It runs after `doml-data-understanding` but before (or independently of) preprocessing and modelling.

</domain>

<decisions>
## Implementation Decisions

### D-01: Input source — raw file by default, overridable
- Default input: the raw dataset from `data/raw/` identified by `config.json`'s `dataset.path`
- Override: `--file path/to/file` flag lets the analyst point at any file in `data/raw/` or `data/processed/`
- Same input contract as `doml-data-understanding` when no `--file` is given — consistent with EDA-first workflow
- Catches data collection anomalies before any cleaning has occurred

### D-02: Flag output format — all scores + consensus flag
- `data/processed/anomaly_flags_{filename}.csv` contains:
  - `isolation_forest_score` — continuous score (lower = more anomalous)
  - `lof_score` — continuous score (higher = more anomalous)
  - `dbscan_label` — integer cluster label (-1 = noise/anomaly)
  - `anomaly_flag` — binary consensus: 1 if flagged anomalous by 2+ algorithms, 0 otherwise
- Row index aligns with the input dataset rows for easy merging downstream
- Downstream modelling notebooks can use `anomaly_flag` for simple filtering or `_score` columns for weighted approaches

### D-03: Report narrative — findings + treatment recommendations
- HTML report narrative goes beyond describing what was found
- Claude narrative interprets each anomaly cluster and suggests how to handle it:
  - "These 8 rows have extreme values across 3+ features — likely data entry errors. Consider dropping before modelling."
  - "These 14 rows are valid edge-case observations — keep in training data but flag for sensitivity analysis."
  - "These 5 rows cluster together and may represent a legitimate minority subgroup."
- Treatment options framed as suggestions, not instructions — analyst makes final call
- Consistent with DoML's goal of actionable, stakeholder-ready reports (established in BU and EDA phases)

### D-04: Algorithm parameters — sensible defaults, `--guidance` for direction
- Isolation Forest: `contamination='auto'`, `n_estimators=100`, `random_state=42` (REPR-01)
- LOF: `n_neighbors=20`, `contamination='auto'`
- DBSCAN: `eps` and `min_samples` determined heuristically (k-distance plot to suggest eps)
- Analyst can pass `--guidance "..."` to shape the run (e.g. "focus on numeric columns only", "use contamination=0.05", "flag conservatively") — follows Phase 8 pattern

### D-05: Notebook structure — follows established template pattern
- Static nbformat v4 template at `.claude/doml/templates/notebooks/anomaly_detection.ipynb`
- Seeds at top: `SEED = 42`, `random.seed(SEED)`, `np.random.seed(SEED)` (REPR-01)
- `PROJECT_ROOT` via env var, all paths relative (REPR-02)
- Tidy data validation before analysis (ANOM-02) — same pattern as EDA notebook
- Sections: Setup → Data Load → Tidy Validation → Isolation Forest → LOF → DBSCAN → Consensus → Save Flags → Summary
- `parameters` cell for `nbconvert --execute` compatibility

### Claude's Discretion
- Exact visualization choices (scatter plots, heatmaps, pair plots for anomaly visualization)
- How to handle datasets with mixed types (numeric columns only, or encode categoricals)
- Exact k-distance plot heuristic for DBSCAN eps selection
- HTML report CSS/styling — follows existing report pattern

</decisions>

<specifics>
## Specific Ideas

- User confirmed: "default is to run on raw data but can be override with a parameter" — the `--file` flag is the override mechanism
- Consensus flag: anomaly_flag = 1 if 2+ algorithms agree — majority vote across 3 algorithms

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Reproducibility rules (apply to all notebooks)
- `CLAUDE.md` §"Reproducibility Rules" — REPR-01 (random seeds), REPR-02 (PROJECT_ROOT paths), REPR-03 (nbstripout), REPR-04 (pinned deps)

### Established notebook template pattern
- `.claude/doml/templates/notebooks/data_understanding_python.ipynb` — reference for notebook cell structure, DuckDB data loading, tidy validation pattern, nbconvert compatibility
- `.claude/doml/templates/notebooks/business_understanding.ipynb` — reference for `parameters` cell, PROJECT_ROOT pattern, IPython.display.Markdown usage

### Established workflow file pattern
- `.claude/doml/workflows/data-understanding.md` — reference for workflow file structure: SKILL.md invocation → Steps 1–N → nbconvert execute → HTML report → verification
- `.claude/doml/workflows/modelling.md` — reference for `--guidance` flag handling pattern and problem-type routing

### Existing skill structure
- `.claude/skills/doml-data-understanding/SKILL.md` — reference SKILL.md frontmatter pattern (name, argument-hint, execution_context)
- `.claude/skills/doml-modelling/SKILL.md` — reference for `--guidance` argument-hint format

### Output conventions
- `.planning/REQUIREMENTS.md` §"Anomaly Detection" — ANOM-01 through ANOM-04 requirements
- `.planning/REQUIREMENTS.md` §"Outputs" — OUT-01 through OUT-03 (HTML report code-hidden requirement)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `doml/data_scan.py` — `scan_data_folder()` / `format_scan_report()` for locating the input file from `config.json`
- `.claude/doml/templates/notebooks/data_understanding_python.ipynb` — tidy validation cell pattern, DuckDB loading cell, `parameters` cell
- `requirements.in` — `scikit-learn` already installed (Isolation Forest, LOF, DBSCAN all in `sklearn.ensemble`, `sklearn.neighbors`, `sklearn.cluster`)

### Established Patterns
- Standalone workflow file per skill: `business-understanding.md`, `data-understanding.md`, `modelling.md` — Phase 10 follows same pattern with `anomaly-detection.md`
- Static nbformat v4 template: no Jinja2, dynamic content via Python code cells — already established in Phases 4–7
- `--guidance "..."` flag: already in `modelling.md` and `iterate-model.md` — apply same pattern
- nbconvert execute → nbconvert --no-input → HTML verify: established in `data-understanding.md` Steps 3a–5d

### Integration Points
- `config.json` `dataset.path` and `dataset.format` — used to locate the default input file
- `data/processed/` — output landing zone for `anomaly_flags_{filename}.csv`
- `reports/` — output landing zone for `anomaly_report.html`
- `notebooks/` — output landing zone for `anomaly_detection.ipynb`

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 10-doml-anomaly-detection*
*Context gathered: 2026-04-11*
