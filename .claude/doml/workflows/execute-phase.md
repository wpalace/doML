# DoML Execute Phase Workflow

## Purpose
Execute a planned DoML analysis phase end-to-end: run analysis tasks, produce Jupyter notebooks
in `notebooks/`, and generate stakeholder HTML reports in `reports/`.

## Invoked by: /doml-execute-phase [phase-number]

## Implementation Status

| Step | Implemented | Phase |
|------|-------------|-------|
| Read PLAN.md and validate | Phase 2 skeleton | — |
| Business Understanding notebook | DoML Phase 4 | BU-01–05 |
| Data Understanding notebook | DoML Phase 5 | EDA-01–10 |
| nbconvert HTML report generation | DoML Phase 4 | OUT-01–03 |
| STATE.md update on completion | Phase 2 skeleton | — |
| Preprocessing notebook | DoML Phase 6 | PREP-01–02 |
| Modelling notebooks (regression + classification) | DoML Phase 6 | MOD-01–02, 06–10 |
| Clustering/Dim Reduction notebooks | DoML Phase 7 | MOD-03, MOD-05 |

---

## Reproducibility Constraints (Non-Negotiable)

Before executing any notebook task, verify:
1. Random seed `SEED = 42` is set at the top of every Python notebook (REPR-01)
2. All paths use `PROJECT_ROOT` env var — no hardcoded absolute paths (REPR-02)
3. `nbstripout` pre-commit hook is active — outputs stripped before git commit (REPR-03)

If any constraint is violated, stop and alert the user before proceeding.

---

## Workflow

### Step 1 — Validate project state

Read `.planning/STATE.md`. If it does not exist:

```
No DoML project found. Run /doml-new-project first.
```

Stop.

### Step 2 — Determine target phase and executor

Determine target phase number from the argument or STATE.md `current_focus`.

**For analysis phases 1 (Business Understanding) and 2 (Data Understanding):** These phases use built-in executors embedded in this workflow (Step 3). No separate PLAN.md is required. Skip directly to Step 3.

**For all other phases:** Look for `.planning/phases/[N]-*/[N]-*-PLAN.md`. If no PLAN.md found:

```
No plan found for Phase [N]. Run /doml-plan-phase [N] first.
```

Stop.

### Step 3 — Route to phase executor *(DoML Phases 4–5 implement these)*

| Phase | Executor | Notebook | Report |
|-------|----------|----------|--------|
| 1 — Business Understanding | DoML Phase 4 | notebooks/01_business_understanding.ipynb | reports/business_summary.html |
| 2 — Data Understanding | DoML Phase 5 | notebooks/02_data_understanding.ipynb | reports/eda_report.html |
| 3 — Preprocessing & Modelling | DoML Phase 6 | notebooks/03_preprocessing.ipynb + notebooks/04_modelling_{type}_v{N}.ipynb | reports/model_report.html |
| 7 — Clustering/Dim Reduction | Phase 7 executor (Steps 3n–3t) | notebooks/0{N}_modelling_{type}_v{M}.ipynb | — (deferred to Phase 9) |

#### Phase 1 — Business Understanding executor

**Pre-condition:** `.planning/config.json` and `.planning/PROJECT.md` must exist (produced by `/doml-new-project`). If either is missing, display:
```
PROJECT.md or config.json not found. Run /doml-new-project first.
```
and stop.

**Step 3a — Copy notebook template**

Copy the BU notebook template into the project's notebooks directory:
```bash
mkdir -p notebooks
cp .claude/doml/templates/notebooks/business_understanding.ipynb \
   notebooks/01_business_understanding.ipynb
```

If `notebooks/01_business_understanding.ipynb` already exists, ask before overwriting:
```
notebooks/01_business_understanding.ipynb already exists. Overwrite? (yes / no)
```
Use AskUserQuestion for this. If the user says no, stop without overwriting.

**Step 3b — Execute the notebook inside Docker**

Run the notebook to populate all cells with output:
```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/01_business_understanding.ipynb \
  --ExecutePreprocessor.timeout=600
```

If the container is not running, display:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-execute-phase 1 again.
```
and stop.

On execution failure (non-zero exit code), display the nbconvert error output and stop. Do not proceed to HTML generation.

**Step 3c — Verify notebook output**

After execution, verify the notebook has cell outputs:
```bash
python3 -c "
import nbformat
with open('notebooks/01_business_understanding.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Executed notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs found — execution may have failed'
"
```

If verification fails, report the error and stop. Do not generate the HTML report on an unexecuted notebook.

#### Phase 2 — Data Understanding executor

**Pre-condition:** `.planning/config.json` must exist with `language` field. If missing, display:
```
PROJECT.md or config.json not found. Run /doml-new-project first.
```
and stop.

**Step 3d — Detect language + copy notebook template**

Read the `language` field from `.planning/config.json`:
```bash
LANG=$(python3 -c "import json; c = json.load(open('.planning/config.json')); print(c.get('language','python'))")
echo "Analysis language: $LANG"
```

Copy the appropriate template:
```bash
mkdir -p notebooks

if [ "$LANG" = "r" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/data_understanding_r.ipynb"
else
  TEMPLATE=".claude/doml/templates/notebooks/data_understanding_python.ipynb"
fi

echo "Using template: $TEMPLATE"
```

If `notebooks/02_data_understanding.ipynb` already exists, ask before overwriting:
```
notebooks/02_data_understanding.ipynb already exists. Overwrite? (yes / no)
```
Use AskUserQuestion for this. If the user says no, stop without overwriting.

Copy the template:
```bash
cp "$TEMPLATE" notebooks/02_data_understanding.ipynb
```

**Step 3e — Execute the notebook inside Docker**

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/02_data_understanding.ipynb \
  --ExecutePreprocessor.timeout=600
```

If the container is not running, display:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-execute-phase 2 again.
```
and stop.

On execution failure (non-zero exit code), display the nbconvert error output and stop. Do not proceed to HTML generation.

**Step 3f — Verify notebook output**

```bash
python3 -c "
import nbformat
with open('notebooks/02_data_understanding.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Executed notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs found — execution may have failed'
"
```

If verification fails, report the error and stop. Do not generate the HTML report on an unexecuted notebook.

#### Phase 3 — Preprocessing & Modelling executor

**Pre-condition:** `.planning/config.json` must exist with `problem_type` field. If missing:
```
PROJECT.md or config.json not found. Run /doml-new-project first.
```
and stop.

**Step 3g — Read problem_type + route unsupervised types**

```bash
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
echo "Problem type: $PROBLEM_TYPE"
```

If PROBLEM_TYPE is `clustering` or `dimensionality_reduction`:
  → Route to Phase 7 executor. Skip to Step 3n.

If PROBLEM_TYPE is `time_series`:
```
Time series detected. Use /doml-execute-phase 8 for time series problems.
```
Stop.

Note: This executor is Python-only. scikit-learn, SHAP, and Optuna do not have R equivalents. R projects that used the R EDA notebook (Phase 2) switch to Python for modelling (Decision 7).

**Step 3h — Copy + execute preprocessing notebook**

Copy template:
```bash
mkdir -p notebooks
cp .claude/doml/templates/notebooks/preprocessing.ipynb notebooks/03_preprocessing.ipynb
```

If `notebooks/03_preprocessing.ipynb` already exists, ask before overwriting:
```
notebooks/03_preprocessing.ipynb already exists. Overwrite? (yes / no)
```
Use AskUserQuestion. If the user says no, stop without overwriting.

Execute:
```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/03_preprocessing.ipynb \
  --ExecutePreprocessor.timeout=600
```

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-execute-phase 3 again.
```
Stop.

Verify:
```bash
python3 -c "
import nbformat
with open('notebooks/03_preprocessing.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Preprocessing notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs — execution may have failed'
"
```

After execution, verify the preprocessed dataset was written:
```bash
python3 -c "
import glob
files = glob.glob('data/processed/preprocessed_*')
assert files, 'No preprocessed_* file found in data/processed/ — preprocessing notebook did not complete Step PREP-02'
print(f'Preprocessed dataset: {files[0]}')
"
```

**Step 3i — Select modelling template + resolve version number**

```bash
NOTEBOOK_NUM=4

# Resolve next version number
VERSION=$(python3 -c "
import glob, re
pattern = 'notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v*.ipynb'
existing = glob.glob(pattern)
versions = [int(re.search(r'_v(\d+)\.ipynb', f).group(1)) for f in existing if re.search(r'_v(\d+)\.ipynb', f)]
print(max(versions) + 1 if versions else 1)
")

echo "Version: $VERSION"

# Select template
if [ "$PROBLEM_TYPE" = "regression" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_regression.ipynb"
elif [ "$PROBLEM_TYPE" = "binary_classification" ] || [ "$PROBLEM_TYPE" = "classification" ] || [ "$PROBLEM_TYPE" = "multiclass_classification" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_classification.ipynb"
  PROBLEM_TYPE="classification"  # normalize for filename
else
  echo "Unknown problem_type: $PROBLEM_TYPE — cannot select modelling template."
  exit 1
fi

MODELLING_NOTEBOOK="notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v${VERSION}.ipynb"
echo "Modelling notebook: $MODELLING_NOTEBOOK"
echo "Template: $TEMPLATE"
```

**Step 3j — Copy modelling template**

```bash
cp "$TEMPLATE" "$MODELLING_NOTEBOOK"
echo "Template copied to $MODELLING_NOTEBOOK"
```

Never overwrite a prior version (new version number always increments — no overwrite check needed here).

**Step 3k — Execute modelling notebook**

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  "$MODELLING_NOTEBOOK" \
  --ExecutePreprocessor.timeout=1200
```

Timeout is 1200s (20 min) — Optuna tuning adds execution time.

On failure, display the nbconvert error and stop.

**Step 3l — Verify modelling notebook output**

```bash
python3 -c "
import nbformat
with open('$MODELLING_NOTEBOOK') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Modelling notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs found — execution may have failed'
"

# Verify leaderboard was produced
python3 -c "
import os
assert os.path.exists('models/leaderboard.csv'), 'models/leaderboard.csv not found after modelling notebook execution'
import pandas as pd
lb = pd.read_csv('models/leaderboard.csv')
print(f'Leaderboard: {len(lb)} rows')
print(lb[['model','cv_primary_mean' if 'cv_primary_mean' in lb.columns else 'cv_rmse_mean']].to_string())
"
```

**Step 3m — Write Claude interpretation cell (Decision 8)**

After execution, Claude reads `models/leaderboard.csv` and `reports/shap_*.png` (file list only — not the images themselves), then writes an **Interpretation & Recommendations** Markdown cell as the final cell of the executed notebook.

The interpretation must include:
1. **Top model finding** — which model won, its CV score, and how much it beat the DummyRegressor/Classifier baseline
2. **Any anomalies** — e.g., "XGBoost CV std of 0.42 is high relative to its mean of 0.51 — possible overfitting", or "Only +3% improvement over baseline — features may be weak predictors of this target"
3. **Suggested next steps** — specific and actionable: e.g., "XGBoost dominates — try `/doml-iterate-model \"focus on XGBoost with engineered features\"`", or "Results look solid — proceed to `/doml-execute-phase 9` for reports"

Write the interpretation using a Python script (write to temp file to avoid quoting issues):

```python
# /tmp/doml_insert_modelling_interpretation.py
import nbformat, uuid

INTERPRETATION = """## Interpretation & Recommendations

[Claude writes this section based on leaderboard.csv and SHAP outputs]

**Top model finding:**
[Which model won, its CV score, gap over Dummy baseline]

**Anomalies / watch points:**
[High CV std, small baseline gap, overfitting signals, etc.]

**Suggested next steps:**
[Specific action: iterate, proceed to reports, or additional feature engineering]

*To iterate: `/doml-iterate-model "your direction"`*
"""

with open('[MODELLING_NOTEBOOK]') as f:
    nb = nbformat.read(f, as_version=4)

interp_cell = nbformat.v4.new_markdown_cell(source=INTERPRETATION)
interp_cell['id'] = uuid.uuid4().hex[:8]
nb.cells.append(interp_cell)

with open('[MODELLING_NOTEBOOK]', 'w') as f:
    nbformat.write(nb, f)

print('Interpretation cell appended')
```

Write the actual interpretation into `INTERPRETATION` (filled in from leaderboard data), replace `[MODELLING_NOTEBOOK]` with the actual path, then run:
```bash
python3 /tmp/doml_insert_modelling_interpretation.py
```

### Step 4 — Execute PLAN.md tasks

When a phase executor is available:
1. Read all `<task>` blocks from PLAN.md
2. Execute each task in wave order (wave 1 tasks first, then wave 2, etc.)
3. After each task, verify the `<verify><automated>` command passes
4. On verification failure, stop and report which task failed

### Step 5 — Generate HTML report

#### Step 5a — Write executive narrative (BU phase only)

Before converting to HTML, generate a 2–3 paragraph executive summary suitable for non-technical stakeholders.

Read the following to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, expected outcome, decision framing sentence
- `.planning/config.json` — problem type, time factor, language
- The executed notebook's cell outputs (`notebooks/01_business_understanding.ipynb`) for dataset counts

Write the narrative as plain Markdown. It must:
- Avoid technical jargon (no mentions of "DuckDB", "nbformat", "config.json")
- Address the stakeholder's business question in plain language
- Summarize what data was found (number of files, approximate row/column counts)
- State the confirmed ML problem type in plain terms (e.g., "This is a prediction problem" instead of "regression")
- Be 2–3 short paragraphs

Insert the narrative as the FIRST cell in the notebook using this Python script (write to a temp file to avoid quoting issues):

```python
# /tmp/doml_insert_summary.py
import nbformat

NARRATIVE = """[WRITE THE 2-3 PARAGRAPH EXECUTIVE SUMMARY HERE]"""

with open('notebooks/01_business_understanding.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

import uuid
summary_cell = nbformat.v4.new_markdown_cell(source='## Executive Summary\n\n' + NARRATIVE)
summary_cell['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(0, summary_cell)

with open('notebooks/01_business_understanding.ipynb', 'w') as f:
    nbformat.write(nb, f)

print('Executive narrative inserted as cell 0')
```

Write the actual narrative into the script, then run:
```bash
python3 /tmp/doml_insert_summary.py
```

#### Step 5b — Create reports/ directory

```bash
mkdir -p reports
```

#### Step 5c — Convert notebook to HTML (code cells hidden)

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/01_business_understanding.ipynb \
  --output-dir reports \
  --output business_summary
```

This produces `reports/business_summary.html`. The `--no-input` flag hides all code cells (OUT-02).

**If Docker is not running**, run on host as fallback:
```bash
jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/01_business_understanding.ipynb \
  --output-dir reports \
  --output business_summary
```

#### Step 5d — Verify HTML report

```bash
# Check 1: File exists
test -f reports/business_summary.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"

# Check 2: Code cells are hidden (OUT-02) — expected: 0 matches
grep -c 'class="input"' reports/business_summary.html && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"

# Check 3: Caveats section present (OUT-03) — expected: >= 1 match
grep -ci "correlation is not causation" reports/business_summary.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"

# Check 4: Executive summary present — expected: >= 1 match
grep -c "Executive Summary" reports/business_summary.html && echo "EXEC_SUMMARY_OK" || echo "EXEC_SUMMARY_MISSING"
```

If any check fails, report which check failed. Do not suppress failures.

#### Phase 2 — Data Understanding HTML report

**Step 5e — Write EDA executive narrative**

Before converting to HTML, generate a 2–3 paragraph executive summary interpreting EDA findings for non-technical stakeholders.

Read the following to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, decision framing
- `.planning/config.json` — problem_type, time_factor
- The executed notebook `notebooks/02_data_understanding.ipynb` — cell outputs showing DuckDB profiling results, normality tests, correlation values, and tidy violations

The EDA narrative must:
- Avoid technical jargon (no "DuckDB", "Shapiro-Wilk", "nbformat", "ADF")
- State dataset size in plain language (e.g., "The dataset contains 12,000 observations and 15 features")
- Highlight top correlated features in business terms
- Note whether key numeric features are normally distributed or skewed — use plain language ("most values cluster near the middle" vs "most values are low with a long tail of high values")
- If time_factor is true: state in plain language whether the series appears stationary or trending
- Flag any data quality issues found (missing values, tidy violations) in plain language
- Be 2–3 short paragraphs

Write the narrative to a temporary Python script to avoid special-character quoting issues, then run it:

```python
# /tmp/doml_insert_eda_summary.py
import nbformat, uuid

NARRATIVE = """[WRITE YOUR 2-3 PARAGRAPH EDA EXECUTIVE SUMMARY HERE]"""

with open('notebooks/02_data_understanding.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

summary_cell = nbformat.v4.new_markdown_cell(source='## Executive Summary\n\n' + NARRATIVE)
summary_cell['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(0, summary_cell)

with open('notebooks/02_data_understanding.ipynb', 'w') as f:
    nbformat.write(nb, f)

print('EDA executive narrative inserted as cell 0')
```

Write the actual narrative into `NARRATIVE`, then run:
```bash
python3 /tmp/doml_insert_eda_summary.py
```

**Step 5f — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 5g — Convert EDA notebook to HTML (code cells hidden)**

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/02_data_understanding.ipynb \
  --output-dir reports \
  --output eda_report
```

This produces `reports/eda_report.html`. The `--no-input` flag hides all code cells (OUT-02).

**If Docker is not running**, run on host as fallback:
```bash
jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/02_data_understanding.ipynb \
  --output-dir reports \
  --output eda_report
```

**Step 5h — Verify EDA HTML report**

```bash
# Check 1: File exists
test -f reports/eda_report.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"

# Check 2: Code cells are hidden (OUT-02) — expected: 0 matches
grep -c 'class="input"' reports/eda_report.html && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"

# Check 3: Caveats section present (OUT-03) — expected: >= 1 match
grep -ci "correlation is not causation" reports/eda_report.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"

# Check 4: Executive summary present — expected: >= 1 match
grep -c "Executive Summary" reports/eda_report.html && echo "EXEC_SUMMARY_OK" || echo "EXEC_SUMMARY_MISSING"
```

If any check fails, report which check failed. Do not suppress failures.

#### Phase 3 — Modelling HTML report

**Step 5i — Write model report narrative**

Generate a 2–3 paragraph executive summary of modelling results for non-technical stakeholders.

Read to inform the narrative:
- `models/leaderboard.csv` — all models, CV scores, test score
- `models/model_metadata.json` — best model name, problem_type, test_score
- `.planning/PROJECT.md` — business question, stakeholder

The model report narrative must:
- Avoid technical jargon (no "RMSE", "SHAP", "Optuna" — use plain language)
- State which model performed best in plain terms (e.g., "A gradient boosted tree model outperformed all others")
- Give the test score in context (e.g., "The model predicts sales within $450 on average")
- Note if performance is strong vs. weak relative to the dummy baseline
- Be 2–3 short paragraphs

Insert narrative into the modelling notebook as cell 0 using the same insert-script pattern as Phase 1 (Step 5a).

**Step 5j — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 5k — Convert modelling notebook to HTML**

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  "$MODELLING_NOTEBOOK" \
  --output-dir reports \
  --output model_report
```

If Docker is not running, run on host:
```bash
jupyter nbconvert --to html --no-input "$MODELLING_NOTEBOOK" --output-dir reports --output model_report
```

**Step 5l — Verify model_report.html**

```bash
test -f reports/model_report.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"
grep -c 'class="input"' reports/model_report.html && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"
grep -ci "correlation is not causation" reports/model_report.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"
grep -ci "leaderboard\|best model\|model" reports/model_report.html | head -1 && echo "MODEL_CONTENT_OK" || echo "MODEL_CONTENT_MISSING"
```

### Step 6 — Update STATE.md

Update `.planning/STATE.md`:
- Set `current_focus` to next phase
- Add completed phase to progress
- Record `last_activity` date
- Log any decisions made during execution

### Step 7 — Confirm

```
Phase [N] complete.

Produced:
  notebooks/[notebook].ipynb
  reports/[report].html

Next: Run /doml-progress to see project status, or /doml-execute-phase [N+1] to continue.
```

---

#### Phase 7 — Clustering & Dimensionality Reduction executor

**Pre-condition:** `.planning/config.json` must exist with `problem_type` field set to `clustering` or `dimensionality_reduction`. Phase 7 templates (`modelling_clustering.ipynb`, `modelling_dimreduction.ipynb`) must exist in `.claude/doml/templates/notebooks/`. If templates are missing:
```
Phase 7 templates not found. Run /doml-plan-phase 7 and /doml-execute-phase 7 plans 01-02 first.
```
and stop.

**Step 3n — Select template + auto-detect notebook number + resolve version**

```bash
# Auto-detect next available notebook number (do not hardcode)
NOTEBOOK_NUM=$(python3 -c "
import glob, re
existing = glob.glob('notebooks/0*_modelling_*.ipynb')
if existing:
    nums = [int(re.search(r'notebooks/0*(\d+)_', f).group(1)) for f in existing if re.search(r'notebooks/0*(\d+)_', f)]
    print(max(nums) + 1 if nums else 5)
else:
    print(5)
")

# Resolve next version number for this problem type
VERSION=$(python3 -c "
import glob, re
problem_type = '${PROBLEM_TYPE}'
pattern = f'notebooks/0*_modelling_{problem_type}_v*.ipynb'
existing = glob.glob(pattern)
versions = [int(re.search(r'_v(\d+)\.ipynb', f).group(1)) for f in existing if re.search(r'_v(\d+)\.ipynb', f)]
print(max(versions) + 1 if versions else 1)
")

echo "Notebook number: $NOTEBOOK_NUM, Version: $VERSION"

# Select template based on problem_type
if [ "$PROBLEM_TYPE" = "clustering" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_clustering.ipynb"
elif [ "$PROBLEM_TYPE" = "dimensionality_reduction" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_dimreduction.ipynb"
else
  echo "Unexpected problem_type: $PROBLEM_TYPE — expected clustering or dimensionality_reduction"
  exit 1
fi

MODELLING_NOTEBOOK="notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v${VERSION}.ipynb"
echo "Modelling notebook: $MODELLING_NOTEBOOK"
echo "Template: $TEMPLATE"
```

**Step 3o — Copy template to notebooks/**

```bash
mkdir -p notebooks
cp "$TEMPLATE" "$MODELLING_NOTEBOOK"
echo "Template copied to $MODELLING_NOTEBOOK"
```

Version number always increments — no overwrite check needed (new version number guarantees uniqueness).

**Step 3p — Execute unsupervised notebook inside Docker**

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  "$MODELLING_NOTEBOOK" \
  --ExecutePreprocessor.timeout=900
```

Timeout is 900s (15 min) — no Optuna hyperparameter tuning in unsupervised. Shorter than supervised (1200s).

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-execute-phase 7 again.
```
Stop.

On execution failure (non-zero exit code), display the nbconvert error output and stop.

**Step 3q — Verify notebook output**

```bash
python3 -c "
import nbformat
with open('$MODELLING_NOTEBOOK') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Unsupervised notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs found — execution may have failed'
"
```

After execution, verify the unsupervised leaderboard was produced:

```bash
python3 -c "
import os
assert os.path.exists('models/unsupervised_leaderboard.csv'), (
    'models/unsupervised_leaderboard.csv not found after unsupervised notebook execution'
)
import pandas as pd
lb = pd.read_csv('models/unsupervised_leaderboard.csv')
print(f'Unsupervised leaderboard: {len(lb)} rows')
print(lb[['method', 'n_clusters' if 'n_clusters' in lb.columns else 'n_components']].to_string())
"
```

If verification fails, report the error and stop.

**Step 3r — Verify expected output files exist**

For clustering:
```bash
if [ "$PROBLEM_TYPE" = "clustering" ]; then
  python3 -c "
import glob
files = glob.glob('data/processed/cluster_assignments.csv')
assert files, 'cluster_assignments.csv not found in data/processed/ — clustering notebook did not complete'
print(f'Cluster assignments: {files[0]}')
"
fi
```

For dimensionality_reduction:
```bash
if [ "$PROBLEM_TYPE" = "dimensionality_reduction" ]; then
  python3 -c "
import glob
umap_files = glob.glob('data/processed/umap_2d.csv')
pca_files = glob.glob('data/processed/pca_*d.csv')
assert umap_files, 'umap_2d.csv not found in data/processed/'
assert pca_files, 'pca_*d.csv not found in data/processed/'
print(f'UMAP 2D: {umap_files[0]}')
print(f'PCA: {pca_files[0]}')
"
fi
```

**Step 3s — Write Claude interpretation cell**

After execution, Claude reads `models/unsupervised_leaderboard.csv` and writes an **Interpretation & Recommendations** Markdown cell as the final cell of the executed notebook.

For clustering notebooks, the interpretation must include:
1. **Best clustering method** — which method won by silhouette score, the score value, Davies-Bouldin and Calinski-Harabasz
2. **Structure assessment** — e.g., "Silhouette of 0.42 indicates moderately well-defined clusters" or "Silhouette < 0.25 suggests overlapping structure — consider dimensionality reduction before clustering"
3. **Top separating features** — top 3 features by ANOVA F-statistic from the feature importance section
4. **Suggested next steps** — e.g., "Try `/doml-iterate-unsupervised \"explore DBSCAN with finer eps grid\"`" or "Cluster structure looks stable — proceed to Phase 9 reports"

For dimensionality reduction notebooks, the interpretation must include:
1. **Variance explained** — components needed for 80%/90% variance; comment on whether high dimensionality suggests noise
2. **Structure observations** — whether UMAP/t-SNE plots reveal visible groupings
3. **Recommended n_components** — practical recommendation based on scree plot
4. **Suggested next steps** — e.g., "Try `/doml-iterate-unsupervised \"explore 5-component PCA solution\"`"

Write the interpretation cell using a Python script (write to temp file to avoid quoting issues):

```python
# /tmp/doml_insert_unsupervised_interpretation.py
import nbformat

INTERPRETATION = """## Interpretation & Recommendations

[Claude writes this section based on unsupervised_leaderboard.csv and notebook outputs]

### Key Findings

[Method results, metric values, top features / variance explained]

### Anomalies or Concerns

[Low silhouette, all-noise DBSCAN, high-dimensional PCA, etc.]

### Recommended Next Steps

[Specific /doml-iterate-unsupervised direction or proceed to Phase 9]
"""

with open('NOTEBOOK_PATH') as f:
    nb = nbformat.read(f, as_version=4)

interp_cell = nbformat.v4.new_markdown_cell(source=INTERPRETATION)
nb.cells.append(interp_cell)

with open('NOTEBOOK_PATH', 'w') as f:
    nbformat.write(nb, f)

print("Interpretation cell appended.")
```

Replace `NOTEBOOK_PATH` with the actual `$MODELLING_NOTEBOOK` path before running.

**Step 3t — No HTML report (Phase 9)**

```
Unsupervised notebook execution complete.
No HTML report generated — unsupervised reports are handled by Phase 9 (Modelling Reports & Leaderboard UI).
To generate reports, run /doml-execute-phase 9 after completing all modelling phases.
```

Update STATE.md to record Phase 7 execution.
