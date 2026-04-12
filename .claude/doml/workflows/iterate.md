# DoML Iterate Workflow

## Purpose

Generate a new modelling iteration notebook with analyst-supplied direction, for any problem type. Reads the most recent modelling notebook, creates a new version incorporating the direction, executes it inside Docker, appends results to the appropriate leaderboard, generates a versioned HTML report, and reports metric deltas to the analyst.

Replaces both `iterate-model.md` (supervised stub) and `iterate-unsupervised.md` (fully implemented unsupervised workflow).

## Invoked by: /doml-iterate [direction]

---

## Reproducibility Constraints (Non-Negotiable)

Before generating any notebook, verify:
1. New notebook has `SEED = 42` at top (REPR-01)
2. All file paths use `PROJECT_ROOT` env var — no hardcoded absolute paths (REPR-02)
3. `nbstripout` pre-commit hook is active — outputs stripped before git commit (REPR-03)

---

## Workflow

### Step 1 — Read config.json and determine problem type

```bash
PROJECT_ROOT=$(python3 -c "import os; print(os.environ.get('PROJECT_ROOT', os.getcwd()))")
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
echo "Problem type: $PROBLEM_TYPE"
```

Route:
- `regression` or `classification` → set `IS_SUPERVISED=true`, continue to Step 2
- `clustering` or `dimensionality_reduction` → set `IS_SUPERVISED=false`, continue to Step 2
- Anything else → display error and stop:

```
Unknown problem_type: {PROBLEM_TYPE}
Valid values: regression, classification, clustering, dimensionality_reduction
Update .planning/config.json and run /doml-iterate again.
```

Stop.

---

### Step 2 — Find most recent modelling notebook for this problem type

```bash
LATEST_NOTEBOOK=$(python3 -c "
import glob, re
problem_type = '${PROBLEM_TYPE}'
pattern = f'notebooks/0*_modelling_{problem_type}_v*.ipynb'
existing = sorted(glob.glob(pattern))
if not existing:
    print('')
else:
    # Sort by version number descending, pick highest
    def get_version(f):
        m = re.search(r'_v(\d+)\.ipynb', f)
        return int(m.group(1)) if m else 0
    print(sorted(existing, key=get_version)[-1])
")

if [ -z "$LATEST_NOTEBOOK" ]; then
  echo "No ${PROBLEM_TYPE} notebook found in notebooks/."
  echo "Run /doml-modelling first to create an initial notebook."
  exit 1
fi

echo "Most recent notebook: $LATEST_NOTEBOOK"
```

---

### Step 3 — Read prior interpretation + prior leaderboard metrics

Read the last Markdown cell of `$LATEST_NOTEBOOK` as the prior interpretation:

```python
# /tmp/doml_read_prior_interpretation.py
import nbformat

with open('LATEST_NOTEBOOK_PATH') as f:
    nb = nbformat.read(f, as_version=4)

# Last Markdown cell = interpretation from prior run
md_cells = [c for c in nb.cells if c.cell_type == 'markdown']
prior_interpretation = md_cells[-1]['source'] if md_cells else 'No prior interpretation found.'
print(prior_interpretation)
```

Replace `LATEST_NOTEBOOK_PATH` with `$LATEST_NOTEBOOK` before running. Save the output as `PRIOR_INTERPRETATION`.

Read the appropriate leaderboard CSV for prior metrics:

```bash
# For supervised (regression/classification):
if [ "$IS_SUPERVISED" = "true" ]; then
  python3 -c "
import pandas as pd, os
lb_path = 'models/leaderboard.csv'
if os.path.exists(lb_path):
    lb = pd.read_csv(lb_path)
    print('Prior leaderboard (last run):')
    max_iter = lb['iteration'].max() if 'iteration' in lb.columns else lb.index.max()
    print(lb[lb['iteration'] == max_iter].to_string(index=False) if 'iteration' in lb.columns else lb.tail(5).to_string(index=False))
else:
    print('No leaderboard found yet.')
"
else
  # For unsupervised (clustering/dimensionality_reduction):
  python3 -c "
import pandas as pd, os
lb_path = 'models/unsupervised_leaderboard.csv'
if os.path.exists(lb_path):
    lb = pd.read_csv(lb_path)
    print('Prior unsupervised leaderboard (last run):')
    max_iter = lb['iteration'].max()
    print(lb[lb['iteration'] == max_iter].to_string(index=False))
else:
    print('No unsupervised leaderboard found yet.')
"
fi
```

---

### Step 4 — Resolve next version number

```bash
NEXT_VERSION=$(python3 -c "
import glob, re
problem_type = '${PROBLEM_TYPE}'
pattern = f'notebooks/0*_modelling_{problem_type}_v*.ipynb'
existing = glob.glob(pattern)
versions = [int(re.search(r'_v(\d+)\.ipynb', f).group(1)) for f in existing if re.search(r'_v(\d+)\.ipynb', f)]
print(max(versions) + 1 if versions else 1)
")

# Detect notebook number prefix from latest notebook
NOTEBOOK_NUM=$(python3 -c "
import re
nb = '${LATEST_NOTEBOOK}'
m = re.search(r'notebooks/0*(\d+)_', nb)
print(m.group(1) if m else '4')
")

# Select template by problem type
if [ "$PROBLEM_TYPE" = "regression" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_regression.ipynb"
elif [ "$PROBLEM_TYPE" = "classification" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_classification.ipynb"
elif [ "$PROBLEM_TYPE" = "clustering" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_clustering.ipynb"
else
  TEMPLATE=".claude/doml/templates/notebooks/modelling_dimreduction.ipynb"
fi

NEW_NOTEBOOK="notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v${NEXT_VERSION}.ipynb"
echo "New notebook: $NEW_NOTEBOOK (from template: $TEMPLATE)"
```

---

### Step 5 — Copy template to new version notebook

```bash
cp "$TEMPLATE" "$NEW_NOTEBOOK"
echo "Template copied to $NEW_NOTEBOOK"
```

---

### Step 6 — Modify notebook cells based on direction string

Parse the analyst's direction string (from `{{args}}`) and modify cells in the new notebook using Python's `nbformat` API. The direction string is used in Python string operations only — it is NEVER passed to a shell command.

**For unsupervised (clustering/dimensionality_reduction):** Copy the `/tmp/doml_modify_unsupervised_notebook.py` script below and run it:

```python
# /tmp/doml_modify_unsupervised_notebook.py
import nbformat, re, json, sys

direction = sys.argv[1] if len(sys.argv) > 1 else ""
problem_type = sys.argv[2] if len(sys.argv) > 2 else "clustering"
notebook_path = sys.argv[3]

with open(notebook_path) as f:
    nb = nbformat.read(f, as_version=4)

# Add direction documentation cell after the header
direction_note = nbformat.v4.new_markdown_cell(
    source=f"## Iteration Direction\n\n**Analyst direction:** {direction}\n\n"
           f"*Automated modifications were applied where patterns were recognized. "
           f"Review cells below before executing.*"
)
# Insert after Cell 0 (header)
nb.cells.insert(1, direction_note)

# Apply clustering-specific modifications
if problem_type == "clustering":
    # K override
    k_match = re.search(r'\bk\s*=\s*(\d+)', direction, re.IGNORECASE)
    if k_match:
        k_val = k_match.group(1)
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'best_k =' in cell['source']:
                cell['source'] = re.sub(
                    r'best_k = list\(K_RANGE\)\[np\.argmax\(silhouettes\)\]',
                    f'best_k = {k_val}  # Analyst override from direction',
                    cell['source']
                )
    # DBSCAN eps override
    eps_match = re.search(r'\beps\s*[=~]\s*([\d.]+)', direction, re.IGNORECASE)
    if eps_match:
        eps_val = float(eps_match.group(1))
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'eps_candidates' in cell['source']:
                cell['source'] = re.sub(
                    r'eps_candidates = \[.*?\]',
                    f'eps_candidates = [{round(eps_val*0.8,4)}, {round(eps_val,4)}, {round(eps_val*1.2,4)}]  # Direction: eps around {eps_val}',
                    cell['source']
                )

# Apply dim reduction-specific modifications
elif problem_type == "dimensionality_reduction":
    # n_neighbors override
    nn_match = re.search(r'n_neighbors\s*=\s*(\d+)', direction, re.IGNORECASE)
    if nn_match:
        nn_val = nn_match.group(1)
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'n_neighbors=15' in cell['source'] and 'reducer_2d' in cell['source']:
                cell['source'] = cell['source'].replace(
                    'n_neighbors=15',
                    f'n_neighbors={nn_val}  # Direction override'
                )
    # n_components override
    nc_match = re.search(r'n_components\s*=\s*(\d+)|(\d+)-component', direction, re.IGNORECASE)
    if nc_match:
        nc_val = nc_match.group(1) or nc_match.group(2)
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'pca_out = PCA' in cell['source']:
                cell['source'] = re.sub(
                    r'PCA\(n_components=n_90',
                    f'PCA(n_components={nc_val}  # Direction override: {nc_val} components',
                    cell['source']
                )

with open(notebook_path, 'w') as f:
    nbformat.write(nb, f)

print(f"Notebook modified: {notebook_path}")
print(f"Direction applied: {direction}")
```

Run as:
```bash
python3 /tmp/doml_modify_unsupervised_notebook.py "$DIRECTION" "$PROBLEM_TYPE" "$NEW_NOTEBOOK"
```

**For supervised (regression/classification):** Write and run `/tmp/doml_modify_supervised_notebook.py` using regex-first direction parsing with Claude fallback:

**Direction parsing rules for supervised:**

| Direction contains | Modification |
|-------------------|--------------|
| Model name (XGBoost, LightGBM, RandomForest, Ridge, Lasso, LogisticRegression) | Filter `models` dict to named model only |
| `trials=N` | Override `n_trials` in Optuna cell |
| `max_depth=N`, `n_estimators=N`, `learning_rate=N`, etc. | Insert note cell before Optuna search space cell |
| `drop {feature}` | Insert new code cell before CV loop to drop that feature |
| `add polynomial` | Insert polynomial feature engineering cell before CV loop |
| No pattern matches | Add Claude fallback cell for natural language interpretation |

```python
# /tmp/doml_modify_supervised_notebook.py
import nbformat, re, sys, uuid

direction = sys.argv[1] if len(sys.argv) > 1 else ""
problem_type = sys.argv[2] if len(sys.argv) > 2 else "regression"
notebook_path = sys.argv[3]

with open(notebook_path) as f:
    nb = nbformat.read(f, as_version=4)

# Always add direction annotation cell after header (cell 0)
direction_note = nbformat.v4.new_markdown_cell(
    source=f"## Iteration Direction\n\n**Analyst direction:** {direction}\n\n"
           f"*Automated modifications applied where patterns matched. "
           f"Review cells below before executing.*"
)
direction_note['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(1, direction_note)

matched = False

if direction:
    # 1. Model focus: narrow models dict to named models
    model_match = re.search(
        r'\b(XGBoost|XGBRegressor|XGBClassifier|LightGBM|LGBMRegressor|LGBMClassifier|'
        r'RandomForest|RandomForestRegressor|RandomForestClassifier|Ridge|Lasso|'
        r'LogisticRegression|LinearRegression)\b',
        direction, re.IGNORECASE
    )
    if model_match:
        matched = True
        focus_model = model_match.group(1)
        for cell in nb.cells:
            if cell.cell_type == 'code' and 'models = {' in cell['source']:
                cell['source'] = (
                    f"# Direction override: focusing on {focus_model}\n"
                    + cell['source']
                    + f"\n# Filter to focus model only\n"
                    + f"models = {{k: v for k, v in models.items() if '{focus_model}' in k}}"
                )
                break

    # 2. Optuna trial count override
    trials_match = re.search(r'\btrials\s*=\s*(\d+)', direction, re.IGNORECASE)
    if trials_match:
        matched = True
        n_trials = trials_match.group(1)
        for cell in nb.cells:
            if cell.cell_type == 'code' and 'n_trials' in cell['source']:
                cell['source'] = re.sub(
                    r'n_trials\s*=\s*\d+',
                    f'n_trials = {n_trials}  # Direction override',
                    cell['source']
                )

    # 3. Hyperparameter overrides
    hp_match = re.search(
        r'\b(max_depth|n_estimators|learning_rate|C|alpha|min_samples_split)\s*=\s*([\d.]+)',
        direction, re.IGNORECASE
    )
    if hp_match:
        matched = True
        hp_name = hp_match.group(1)
        hp_val = hp_match.group(2)
        for cell in nb.cells:
            if cell.cell_type == 'code' and 'param_distributions' in cell['source']:
                note = nbformat.v4.new_markdown_cell(
                    source=f"**Direction override:** `{hp_name}={hp_val}` — narrow Optuna search space around this value."
                )
                note['id'] = uuid.uuid4().hex[:8]
                idx = nb.cells.index(cell)
                nb.cells.insert(idx, note)
                break

    # 4. Feature directives
    drop_match = re.search(r'\bdrop\s+["\']?(\w+)["\']?', direction, re.IGNORECASE)
    if drop_match:
        matched = True
        feat = drop_match.group(1)
        drop_cell = nbformat.v4.new_code_cell(
            source=f"# Direction: drop feature '{feat}'\nX = X.drop(columns=['{feat}'], errors='ignore')\nprint(f'Dropped {feat}. Remaining features: {{X.shape[1]}}')"
        )
        drop_cell['id'] = uuid.uuid4().hex[:8]
        # Insert before the first CV cell
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'cross_val' in cell.get('source', ''):
                nb.cells.insert(i, drop_cell)
                break

    poly_match = re.search(r'\badd polynomial\b', direction, re.IGNORECASE)
    if poly_match:
        matched = True
        poly_cell = nbformat.v4.new_code_cell(
            source="# Direction: add polynomial features\nfrom sklearn.preprocessing import PolynomialFeatures\npoly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)\nX = pd.DataFrame(poly.fit_transform(X), columns=poly.get_feature_names_out(X.columns))\nprint(f'Polynomial features added. Shape: {X.shape}')"
        )
        poly_cell['id'] = uuid.uuid4().hex[:8]
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and 'cross_val' in cell.get('source', ''):
                nb.cells.insert(i, poly_cell)
                break

    # If no regex matched: Claude fallback — add instruction cell for Claude to interpret
    if not matched:
        fallback_cell = nbformat.v4.new_markdown_cell(
            source=f"## Claude Fallback: Natural Language Direction\n\n"
                   f"**Direction:** {direction}\n\n"
                   f"No structured pattern matched. Claude should read this direction and insert "
                   f"the appropriate code cells directly above this cell using the nbformat API, "
                   f"then remove this fallback cell before saving."
        )
        fallback_cell['id'] = uuid.uuid4().hex[:8]
        nb.cells.append(fallback_cell)

with open(notebook_path, 'w') as f:
    nbformat.write(nb, f)

print(f"Notebook modified: {notebook_path}")
print(f"Direction: '{direction}' | Regex matched: {matched}")
```

Run as:
```bash
python3 /tmp/doml_modify_supervised_notebook.py "$DIRECTION" "$PROBLEM_TYPE" "$NEW_NOTEBOOK"
```

If the fallback cell was added (no regex matched and direction is non-empty), Claude reads the notebook and writes appropriate code cells using `nbformat.v4.new_code_cell()`, replacing the fallback cell before saving with `nbformat.write()`.

---

### Step 7 — Execute the new notebook inside Docker

```bash
if [ "$IS_SUPERVISED" = "true" ]; then
  TIMEOUT=1200
else
  TIMEOUT=900
fi

docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  "$NEW_NOTEBOOK" \
  --ExecutePreprocessor.timeout=${TIMEOUT}
```

Timeout: 1200s (supervised — Optuna adds execution time); 900s (unsupervised — no Optuna).

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-iterate again.
```
Stop.

On execution failure (non-zero exit code), display the nbconvert error. Stop — do not append to leaderboard on failed execution.

Verify notebook executed:
```bash
python3 -c "
import nbformat
with open('$NEW_NOTEBOOK') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
assert code_cells_with_output > 0, 'No cell outputs — execution failed'
print(f'Executed: {code_cells_with_output} code cells with output')
"
```

---

### Step 8 — Append results to leaderboard CSV

The executed notebook already appends to the leaderboard CSV (the append cell is inside the template). Verify the append happened:

```bash
if [ "$IS_SUPERVISED" = "true" ]; then
  # Supervised: verify models/leaderboard.csv was appended
  python3 -c "
import pandas as pd, os
lb_path = 'models/leaderboard.csv'
assert os.path.exists(lb_path), 'leaderboard.csv not found after execution'
lb = pd.read_csv(lb_path)
print('Leaderboard updated. All iterations:')
print(lb.sort_values('cv_primary_mean' if 'cv_primary_mean' in lb.columns else lb.columns[0]).to_string(index=False))
print(f'Total entries: {len(lb)}')
"
else
  # Unsupervised: verify models/unsupervised_leaderboard.csv was appended
  python3 -c "
import pandas as pd, os
lb_path = 'models/unsupervised_leaderboard.csv'
assert os.path.exists(lb_path), 'unsupervised_leaderboard.csv not found after execution'
lb = pd.read_csv(lb_path)
max_iter = lb['iteration'].max()
latest_rows = lb[lb['iteration'] == max_iter]
print(f'Leaderboard updated. Latest iteration: {max_iter}')
print(latest_rows.to_string(index=False))
"
fi
```

Save the latest iteration rows as `NEW_METRICS` for Step 10.

---

### Step 9 — Write versioned HTML report

Determine report name based on problem type and version (per D-02):

```bash
if [ "$PROBLEM_TYPE" = "regression" ] || [ "$PROBLEM_TYPE" = "classification" ]; then
  REPORT_NAME="model_report_v${NEXT_VERSION}"
elif [ "$PROBLEM_TYPE" = "clustering" ]; then
  REPORT_NAME="clustering_report_v${NEXT_VERSION}"
else
  REPORT_NAME="dimreduction_report_v${NEXT_VERSION}"
fi
```

Write an executive narrative Markdown cell comparing this iteration vs the prior one (insert as a new cell near the top of the executed notebook, after the direction cell). The narrative:
- Summarises what changed (direction applied, parameters modified)
- Compares key metrics to the prior version: for supervised — RMSE delta (regression) or ROC-AUC delta (classification); for unsupervised — silhouette/Davies-Bouldin/Calinski-Harabasz delta (clustering) or variance-explained delta (dimensionality_reduction)
- States whether results improved
- Written for a non-technical stakeholder audience

```python
# /tmp/doml_insert_report_narrative.py
import nbformat, sys

new_notebook_path = sys.argv[1]
narrative_text = sys.argv[2]  # Passed via sys.argv — never shell-interpolated

with open(new_notebook_path) as f:
    nb = nbformat.read(f, as_version=4)

narrative_cell = nbformat.v4.new_markdown_cell(source=narrative_text)
# Insert at position 0 (executive summary first in report)
nb.cells.insert(0, narrative_cell)

with open(new_notebook_path, 'w') as f:
    nbformat.write(nb, f)

print("Executive narrative cell inserted.")
```

Generate the HTML report with code hidden:

```bash
mkdir -p reports
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  "$NEW_NOTEBOOK" \
  --output-dir reports \
  --output "$REPORT_NAME"
```

If the container is not running, display the standard container-not-running error (same as Step 7).

Verify report:
```bash
test -f "reports/${REPORT_NAME}.html" && echo "REPORT_OK" || echo "REPORT_MISSING"
grep -ci "correlation is not causation" "reports/${REPORT_NAME}.html" && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"
grep -c 'class="input"' "reports/${REPORT_NAME}.html" && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"
```

---

### Step 10 — Write interpretation Markdown cell comparing v{N+1} vs v{N}

Read both the prior leaderboard (from Step 3) and new leaderboard (from Step 8). Claude writes an **Iteration Interpretation** Markdown cell comparing the two runs.

The interpretation must include:
1. **What changed** — which direction was applied, what parameters were modified
2. **Metric delta** — comparing new vs prior metrics (regression: RMSE; classification: ROC-AUC; clustering: silhouette/Davies-Bouldin/Calinski-Harabasz; dimensionality_reduction: variance explained / n_components at 90%)
3. **Assessment** — whether the change improved results; whether to continue this direction
4. **Next iteration suggestion** — specific next `/doml-iterate` direction if warranted

Write the interpretation cell using the nbformat API:

```python
# /tmp/doml_insert_iteration_interpretation.py
import nbformat, sys

new_notebook_path = sys.argv[1]
new_version = sys.argv[2]
direction = sys.argv[3]

INTERPRETATION = f"""## Iteration v{new_version} — Interpretation

**Direction applied:** {direction}

### Metric Comparison

[Insert metric comparison table here — regression: RMSE delta; classification: ROC-AUC delta;
clustering: silhouette/DB/CH delta; dimensionality_reduction: variance explained delta]

| Metric | Prior | New | Delta |
|--------|-------|-----|-------|
| [primary metric] | [prior value] | [new value] | [+/-delta] |

### What Changed

[Describe which regex patterns fired (or fallback was used), what cells were inserted or modified]

### Assessment

[Whether direction improved primary metric; whether noise or instability was introduced;
whether further iterations in this direction are warranted]

### Next Steps

[Specific next /doml-iterate direction, or recommendation to proceed to /doml-progress]
"""

with open(new_notebook_path) as f:
    nb = nbformat.read(f, as_version=4)

interp_cell = nbformat.v4.new_markdown_cell(source=INTERPRETATION)
nb.cells.append(interp_cell)

with open(new_notebook_path, 'w') as f:
    nbformat.write(nb, f)

print("Iteration interpretation cell appended.")
```

Run:
```bash
python3 /tmp/doml_insert_iteration_interpretation.py "$NEW_NOTEBOOK" "$NEXT_VERSION" "$DIRECTION"
```

---

### Step 11 — Report to analyst

Display a structured summary:

```
## Iteration Complete

**Notebook:** {NEW_NOTEBOOK}
**HTML Report:** reports/{REPORT_NAME}.html
**Problem type:** {PROBLEM_TYPE}
**Direction:** {DIRECTION}

### Metric Delta (prior → new)

[For regression]
| Model | Prior RMSE | New RMSE | Delta |
|-------|-----------|---------|-------|
| Best  | {prior_rmse} | {new_rmse} | {delta:+.4f} |

[For classification]
| Model | Prior ROC-AUC | New ROC-AUC | Delta |
|-------|-------------|-----------|-------|
| Best  | {prior_auc} | {new_auc} | {delta:+.4f} |

[For clustering]
| Method | Silhouette | Davies-Bouldin ↓ | Calinski-Harabasz |
|--------|-----------|-----------------|------------------|
| Prior best | {prior_sil} | {prior_db} | {prior_ch} |
| New best   | {new_sil}   | {new_db}   | {new_ch}   |
| Delta      | {dsil:+.4f} | {ddb:+.4f} | {dch:+.2f} |

[For dimensionality reduction]
| Method | n_components (90%) | Notes |
|--------|-------------------|-------|
| Prior  | {prior_n90}       | {prior_notes} |
| New    | {new_n90}         | {new_notes}   |

### Files Updated
- {NEW_NOTEBOOK}
- reports/{REPORT_NAME}.html
- {'models/leaderboard.csv' if IS_SUPERVISED else 'models/unsupervised_leaderboard.csv'} (appended)

### Next Actions
- Continue iterating: /doml-iterate "next direction"
- View project status: /doml-progress
- View leaderboard: cat {'models/leaderboard.csv' if IS_SUPERVISED else 'models/unsupervised_leaderboard.csv'}
```

---

## Anti-Patterns to Avoid

- **Never pass the direction string to a shell command** — use Python `nbformat` API only (`sys.argv[1]` to receive direction in scripts — it is NEVER interpolated into a bash string)
- **Never overwrite leaderboard CSVs** — always `pd.concat` append; never `pd.to_csv` without the prior data concatenated
- **Never hardcode version numbers** — always glob and increment from existing notebooks
- **Never include accuracy/F1/ROC-AUC in unsupervised metrics** — internal metrics only (silhouette, Davies-Bouldin, Calinski-Harabasz)
- **Never compute silhouette on DBSCAN with noise points** — always mask `labels != -1` before calling `silhouette_score`
- **Never overwrite existing versioned notebooks** — `v{N+1}` is always a new file copied from the template, never a modification of `v{N}`
- **Never generate reports with code visible** — always pass `--no-input` to `nbconvert`
- **Report names must be versioned** — `model_report_v{N}.html`, `clustering_report_v{N}.html`, `dimreduction_report_v{N}.html` — never `model_report.html` (that is only for initial runs via `/doml-modelling`)
