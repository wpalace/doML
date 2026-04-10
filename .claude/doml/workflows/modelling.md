# DoML Modelling Workflow

## Purpose
Run the Modelling phase end-to-end for any problem type. Reads config.json to determine
the problem type and routes to the supervised or unsupervised execution path.

## Invoked by: /doml-modelling [--guidance "..."]

---

## Reproducibility Constraints (Non-Negotiable)

Before executing any notebook task, verify:
1. Random seed `SEED = 42` is set at the top of every Python notebook (REPR-01)
2. All paths use `PROJECT_ROOT` env var — no hardcoded absolute paths (REPR-02)
3. `nbstripout` pre-commit hook is active — outputs stripped before git commit (REPR-03)

If any constraint is violated, stop and alert the user before proceeding.

Note: This executor is Python-only. scikit-learn, SHAP, and Optuna do not have R equivalents.
R projects that used the R EDA notebook switch to Python for modelling.

---

## Workflow

### Step 1 — Validate project state

Read `.planning/STATE.md`. If it does not exist:

```
No DoML project found. Run /doml-new-project first.
```

Stop.

### Step 2 — Read project config

Read `.planning/config.json`. If missing:

```
config.json not found. Run /doml-new-project first.
```

Stop.

Extract optional `--guidance` from `$ARGUMENTS`. If present, save to a `GUIDANCE` variable
for use in interpretation steps. If `$ARGUMENTS` is empty or does not contain `--guidance`,
set `GUIDANCE=""`.

### Step 3 — Route by problem_type

```bash
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
echo "Problem type: $PROBLEM_TYPE"
```

Route:
- `regression` or `classification` or `binary_classification` or `multiclass_classification` → **Step 4 (Supervised path)**
- `clustering` or `dimensionality_reduction` → **Step 7 (Unsupervised path)**
- `time_series` → display message and stop:
  ```
  Time series detected. Use /doml-forecasting for time series problems.
  /doml-forecasting is available in Phase 12 of the DoML roadmap.
  ```
- anything else → display unknown problem_type error and stop:
  ```
  Unknown problem_type: {PROBLEM_TYPE}
  Valid values: regression, classification, clustering, dimensionality_reduction, time_series
  Update .planning/config.json and run /doml-modelling again.
  ```

---

## Supervised Path (regression / classification)

### Step 4 — Copy and execute preprocessing notebook

**Step 4a — Copy template**

```bash
mkdir -p notebooks
cp .claude/doml/templates/notebooks/preprocessing.ipynb notebooks/03_preprocessing.ipynb
```

If `notebooks/03_preprocessing.ipynb` already exists, ask before overwriting:
```
notebooks/03_preprocessing.ipynb already exists. Overwrite? (yes / no)
```
Use AskUserQuestion. If the user says no, stop without overwriting.

**Step 4b — Execute preprocessing notebook**

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
Then run /doml-modelling again.
```
Stop.

**Step 4c — Verify preprocessing output**

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

### Step 5 — Copy, execute, and verify modelling notebook

**Step 5a — Select template and resolve version**

```bash
NOTEBOOK_NUM=4

# Normalize classification variants
if [ "$PROBLEM_TYPE" = "binary_classification" ] || [ "$PROBLEM_TYPE" = "multiclass_classification" ]; then
  PROBLEM_TYPE="classification"
fi

# Resolve next version number
VERSION=$(python3 -c "
import glob, re
problem_type = '${PROBLEM_TYPE}'
pattern = f'notebooks/0*_modelling_{problem_type}_v*.ipynb'
existing = glob.glob(pattern)
versions = [int(re.search(r'_v(\d+)\.ipynb', f).group(1)) for f in existing if re.search(r'_v(\d+)\.ipynb', f)]
print(max(versions) + 1 if versions else 1)
")

echo "Version: $VERSION"

# Select template
if [ "$PROBLEM_TYPE" = "regression" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_regression.ipynb"
elif [ "$PROBLEM_TYPE" = "classification" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_classification.ipynb"
else
  echo "Unknown supervised problem_type: $PROBLEM_TYPE"
  exit 1
fi

MODELLING_NOTEBOOK="notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v${VERSION}.ipynb"
echo "Modelling notebook: $MODELLING_NOTEBOOK"
echo "Template: $TEMPLATE"
```

**Step 5b — Copy modelling template**

```bash
cp "$TEMPLATE" "$MODELLING_NOTEBOOK"
echo "Template copied to $MODELLING_NOTEBOOK"
```

Version number always increments — no overwrite check needed (new version number guarantees
uniqueness).

**Step 5c — Execute modelling notebook**

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  "$MODELLING_NOTEBOOK" \
  --ExecutePreprocessor.timeout=1200
```

Timeout is 1200s (20 min) — Optuna tuning adds execution time.

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-modelling again.
```
Stop.

On failure, display the nbconvert error and stop.

**Step 5d — Verify modelling notebook output**

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

### Step 6 — Write interpretation, generate HTML report

**Step 6a — Write Claude interpretation cell**

After execution, Claude reads `models/leaderboard.csv` and `reports/shap_*.png` (file list
only — not the images themselves), then writes an **Interpretation & Recommendations**
Markdown cell as the final cell of the executed notebook.

The interpretation must include:
1. **Top model finding** — which model won, its CV score, and how much it beat the
   DummyRegressor/Classifier baseline
2. **Any anomalies** — e.g., "XGBoost CV std of 0.42 is high relative to its mean of 0.51
   — possible overfitting", or "Only +3% improvement over baseline — features may be weak
   predictors of this target"
3. **Suggested next steps** — specific and actionable: e.g., "XGBoost dominates — try
   `/doml-iterate-model \"focus on XGBoost with engineered features\"`", or "Results look
   solid — proceed to next phase"

If `GUIDANCE` is non-empty, incorporate it to shape the recommendations section
(e.g., if guidance says "prioritise interpretability", bias recommendations toward simpler
models and SHAP analysis).

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

# Replace the template placeholder if present; otherwise append
placeholder_idx = next(
    (i for i, c in enumerate(nb.cells)
     if c.cell_type == 'markdown' and c.source.startswith('## Interpretation & Recommendations')),
    None
)
if placeholder_idx is not None:
    nb.cells[placeholder_idx] = interp_cell
else:
    nb.cells.append(interp_cell)

with open('[MODELLING_NOTEBOOK]', 'w') as f:
    nbformat.write(nb, f)

print('Interpretation cell written')
```

Write the actual interpretation into `INTERPRETATION`, replace `[MODELLING_NOTEBOOK]` with
the actual path, then run:
```bash
python3 /tmp/doml_insert_modelling_interpretation.py
```

**Step 6b — Write model report narrative**

Generate a 2–3 paragraph executive summary of modelling results for non-technical
stakeholders.

Read to inform the narrative:
- `models/leaderboard.csv` — all models, CV scores, test score
- `models/model_metadata.json` — best model name, problem_type, test_score
- `.planning/PROJECT.md` — business question, stakeholder

The model report narrative must:
- Avoid technical jargon (no "RMSE", "SHAP", "Optuna" — use plain language)
- State which model performed best in plain terms (e.g., "A gradient boosted tree model
  outperformed all others")
- Give the test score in context (e.g., "The model predicts sales within $450 on average")
- Note if performance is strong vs. weak relative to the dummy baseline
- Be 2–3 short paragraphs

If `GUIDANCE` is non-empty, shape the narrative accordingly.

Insert the narrative as cell 0 of the modelling notebook:

```python
# /tmp/doml_insert_model_narrative.py
import nbformat, uuid

NARRATIVE = """[WRITE THE 2-3 PARAGRAPH EXECUTIVE SUMMARY HERE]"""

with open('[MODELLING_NOTEBOOK]') as f:
    nb = nbformat.read(f, as_version=4)

summary_cell = nbformat.v4.new_markdown_cell(source='## Executive Summary\n\n' + NARRATIVE)
summary_cell['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(0, summary_cell)

with open('[MODELLING_NOTEBOOK]', 'w') as f:
    nbformat.write(nb, f)

print('Executive narrative inserted as cell 0')
```

Write the actual narrative into `NARRATIVE`, replace `[MODELLING_NOTEBOOK]` with the actual
path, then run:
```bash
python3 /tmp/doml_insert_model_narrative.py
```

**Step 6c — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 6d — Convert modelling notebook to HTML**

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  "$MODELLING_NOTEBOOK" \
  --output-dir reports \
  --output model_report
```

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-modelling again.
```
Stop.

**Step 6e — Verify model_report.html**

```bash
test -f reports/model_report.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"
grep -c 'class="input"' reports/model_report.html && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"
grep -ci "correlation is not causation" reports/model_report.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"
grep -ci "leaderboard\|best model\|model" reports/model_report.html | head -1 && echo "MODEL_CONTENT_OK" || echo "MODEL_CONTENT_MISSING"
```

→ After Step 6e, jump to **Step 9** (STATE.md update).

---

## Unsupervised Path (clustering / dimensionality_reduction)

### Step 7 — Verify unsupervised templates exist

Check that the appropriate template exists:

```bash
if [ "$PROBLEM_TYPE" = "clustering" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_clustering.ipynb"
elif [ "$PROBLEM_TYPE" = "dimensionality_reduction" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_dimreduction.ipynb"
fi

test -f "$TEMPLATE" && echo "Template found: $TEMPLATE" || {
  echo "Template not found: $TEMPLATE"
  echo "This template should have been created during the DoML framework setup."
  exit 1
}
```

### Step 8 — Copy, execute, verify, and interpret unsupervised notebook

**Step 8a — Select template + auto-detect notebook number + resolve version**

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

MODELLING_NOTEBOOK="notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v${VERSION}.ipynb"
echo "Modelling notebook: $MODELLING_NOTEBOOK"
echo "Template: $TEMPLATE"
```

**Step 8b — Copy template to notebooks/**

```bash
mkdir -p notebooks
cp "$TEMPLATE" "$MODELLING_NOTEBOOK"
echo "Template copied to $MODELLING_NOTEBOOK"
```

Version number always increments — no overwrite check needed.

**Step 8c — Execute unsupervised notebook inside Docker**

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  "$MODELLING_NOTEBOOK" \
  --ExecutePreprocessor.timeout=900
```

Timeout is 900s (15 min) — no Optuna hyperparameter tuning in unsupervised.

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-modelling again.
```
Stop.

On execution failure (non-zero exit code), display the nbconvert error output and stop.

**Step 8d — Verify notebook output**

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

**Step 8e — Verify expected output files exist**

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

**Step 8f — Write Claude interpretation cell**

After execution, Claude reads `models/unsupervised_leaderboard.csv` and writes an
**Interpretation & Recommendations** Markdown cell as the final cell of the executed
notebook.

For clustering notebooks, the interpretation must include:
1. **Best clustering method** — which method won by silhouette score, the score value,
   Davies-Bouldin and Calinski-Harabasz
2. **Structure assessment** — e.g., "Silhouette of 0.42 indicates moderately well-defined
   clusters" or "Silhouette < 0.25 suggests overlapping structure"
3. **Top separating features** — top 3 features by ANOVA F-statistic
4. **Suggested next steps** — e.g., "Try `/doml-iterate-unsupervised \"explore DBSCAN with
   finer eps grid\"`"

For dimensionality reduction notebooks, the interpretation must include:
1. **Variance explained** — components needed for 80%/90% variance
2. **Structure observations** — whether UMAP/t-SNE plots reveal visible groupings
3. **Recommended n_components** — practical recommendation based on scree plot
4. **Suggested next steps** — e.g., "Try `/doml-iterate-unsupervised \"explore 5-component
   PCA solution\"`"

If `GUIDANCE` is non-empty, incorporate it to shape the interpretation section accordingly.

Write the interpretation cell using a Python script:

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

[Specific /doml-iterate-unsupervised direction or note that a report will be generated separately]
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

---

## Completing the workflow

### Step 9 — Update STATE.md

Write to `.planning/STATE.md`:
- Update `current_focus` to reflect modelling complete
- Append to Decisions section:
  `[Phase 08]: doml-modelling completed — {problem_type} notebook executed`
- Update `last_activity` with today's date

### Step 10 — Confirm

For supervised:
```
Modelling complete ({problem_type}).

  Preprocessing:  notebooks/03_preprocessing.ipynb
  Modelling:      {MODELLING_NOTEBOOK}
  Report:         reports/model_report.html
  Leaderboard:    models/leaderboard.csv

To iterate: /doml-iterate-model "your direction"
```

For unsupervised:
```
Modelling complete ({problem_type}).

  Notebook:    {MODELLING_NOTEBOOK}
  Leaderboard: models/unsupervised_leaderboard.csv

To iterate: /doml-iterate-unsupervised "your direction"
```
