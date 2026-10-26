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
3. Notebooks are plain-Python marimo files: outputs are never stored in git, only in `reports/*.html` (REPR-03)

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
pattern = f'notebooks/0*_modelling_{problem_type}_v*.py'
existing = sorted(glob.glob(pattern))
if not existing:
    print('')
else:
    # Sort by version number descending, pick highest
    def get_version(f):
        m = re.search(r'_v(\d+)\.py', f)
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

Read the prior interpretation sidecar of `$LATEST_NOTEBOOK`
(`notebooks/narratives/<stem>/interpretation.md`, written by the previous run):

```bash
STEM=$(basename "$LATEST_NOTEBOOK" .py)
cat "notebooks/narratives/${STEM}/interpretation.md" 2>/dev/null || echo "No prior interpretation found."
```

Save the output as `PRIOR_INTERPRETATION`.

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
pattern = f'notebooks/0*_modelling_{problem_type}_v*.py'
existing = glob.glob(pattern)
versions = [int(re.search(r'_v(\d+)\.py', f).group(1)) for f in existing if re.search(r'_v(\d+)\.py', f)]
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
  TEMPLATE=".claude/doml/templates/notebooks/modelling_regression.py"
elif [ "$PROBLEM_TYPE" = "classification" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_classification.py"
elif [ "$PROBLEM_TYPE" = "clustering" ]; then
  TEMPLATE=".claude/doml/templates/notebooks/modelling_clustering.py"
else
  TEMPLATE=".claude/doml/templates/notebooks/modelling_dimreduction.py"
fi

NEW_NOTEBOOK="notebooks/0${NOTEBOOK_NUM}_modelling_${PROBLEM_TYPE}_v${NEXT_VERSION}.py"
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

Parse the analyst's direction string (from `{{args}}`) and modify the new notebook. A marimo
notebook is a plain Python file, so every change is a text edit done by
`.claude/doml/bin/doml_nb.py` (`narrative`, `sub`, `append`). The direction string is used in
Python string operations only — it is NEVER passed to a shell command.

marimo rule: a name may be defined in one cell only. So never add a new cell that reassigns an
existing variable (for example `X = X.drop(...)`). Append the code to the cell that defines the
variable instead (`doml_nb.py append NOTEBOOK MARKER`), then `marimo check` confirms the graph.

**For unsupervised (clustering/dimensionality_reduction):** Write and run the
`/tmp/doml_modify_unsupervised_notebook.py` script below:

```python
# /tmp/doml_modify_unsupervised_notebook.py
import re, subprocess, sys

direction = sys.argv[1] if len(sys.argv) > 1 else ""
problem_type = sys.argv[2] if len(sys.argv) > 2 else "clustering"
notebook_path = sys.argv[3]
TOOL = [sys.executable, '.claude/doml/bin/doml_nb.py']

def tool(*args, stdin=None):
    return subprocess.run([*TOOL, *args], input=stdin, text=True).returncode

# Direction documentation: rendered under the title by the "direction" narrative cell
tool('narrative', notebook_path, 'direction', '-', stdin=(
    f"## Iteration Direction\n\n**Analyst direction:** {direction}\n\n"
    f"*Automated modifications were applied where patterns were recognized. "
    f"Review the notebook before executing.*\n"))

if problem_type == "clustering":
    k_match = re.search(r'\bk\s*=\s*(\d+)', direction, re.IGNORECASE)
    if k_match:
        tool('sub', notebook_path, r'best_k = list\(K_RANGE\)\[np\.argmax\(silhouettes\)\]',
             f'best_k = {k_match.group(1)}  # Analyst override from direction')
    eps_match = re.search(r'\beps\s*[=~]\s*([\d.]+)', direction, re.IGNORECASE)
    if eps_match:
        eps_val = float(eps_match.group(1))
        tool('sub', notebook_path, r'eps_candidates = \[.*?\]',
             f'eps_candidates = [{round(eps_val*0.8,4)}, {round(eps_val,4)}, {round(eps_val*1.2,4)}]  # Direction: eps around {eps_val}')
elif problem_type == "dimensionality_reduction":
    nn_match = re.search(r'n_neighbors\s*=\s*(\d+)', direction, re.IGNORECASE)
    if nn_match:
        tool('sub', notebook_path, r'(reducer_2d = umap\.UMAP\(n_components=2, )n_neighbors=15',
             rf'\g<1>n_neighbors={nn_match.group(1)}')
    nc_match = re.search(r'n_components\s*=\s*(\d+)|(\d+)-component', direction, re.IGNORECASE)
    if nc_match:
        nc_val = nc_match.group(1) or nc_match.group(2)
        tool('sub', notebook_path, r'PCA\(n_components=n_90', f'PCA(n_components={nc_val}')

subprocess.run([*TOOL, 'check', notebook_path], check=True)
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
| Model name (XGBoost, LightGBM, RandomForest, Ridge, Lasso, LogisticRegression) | Append a filter to the cell that defines `models = {` |
| `trials=N` | Override `n_trials` in the Optuna cell |
| `max_depth=N`, `n_estimators=N`, `learning_rate=N`, etc. | Note in the direction narrative (narrow the Optuna search space by hand) |
| `drop {feature}` | Append the drop to the cell that defines `X` (before the holdout split) |
| `add polynomial` | Append polynomial features to the cell that defines `X` |
| No pattern matches | Claude edits the `.py` notebook directly (fallback) |

```python
# /tmp/doml_modify_supervised_notebook.py
import re, subprocess, sys

direction = sys.argv[1] if len(sys.argv) > 1 else ""
problem_type = sys.argv[2] if len(sys.argv) > 2 else "regression"
notebook_path = sys.argv[3]
TOOL = [sys.executable, '.claude/doml/bin/doml_nb.py']

def tool(*args, stdin=None):
    return subprocess.run([*TOOL, *args], input=stdin, text=True).returncode

notes = []
matched = False

if direction:
    model_match = re.search(
        r'\b(XGBoost|XGBRegressor|XGBClassifier|LightGBM|LGBMRegressor|LGBMClassifier|'
        r'RandomForest|RandomForestRegressor|RandomForestClassifier|Ridge|Lasso|'
        r'LogisticRegression|LinearRegression)\b',
        direction, re.IGNORECASE
    )
    if model_match:
        matched = True
        focus = model_match.group(1)
        # Keep the Dummy baseline so the leaderboard still shows the gap over it.
        tool('append', notebook_path, 'models = {', '-', stdin=(
            f"# Direction override: focusing on {focus}\n"
            f"models = {{k: v for k, v in models.items() if {focus!r}.lower() in k.lower() or 'Dummy' in k}}\n"))

    trials_match = re.search(r'\btrials\s*=\s*(\d+)', direction, re.IGNORECASE)
    if trials_match:
        matched = True
        tool('sub', notebook_path, r'n_trials\s*=\s*\d+', f'n_trials={trials_match.group(1)}')

    hp_match = re.search(
        r'\b(max_depth|n_estimators|learning_rate|C|alpha|min_samples_split)\s*=\s*([\d.]+)',
        direction, re.IGNORECASE
    )
    if hp_match:
        matched = True
        notes.append(f"**Direction override:** `{hp_match.group(1)}={hp_match.group(2)}` — "
                     f"narrow the Optuna search space around this value.")

    drop_match = re.search(r'\bdrop\s+["\']?(\w+)["\']?', direction, re.IGNORECASE)
    if drop_match:
        matched = True
        feat = drop_match.group(1)
        tool('append', notebook_path, "X = df.drop(columns=[TARGET])", '-', stdin=(
            f"# Direction: drop feature '{feat}'\n"
            f"X = X.drop(columns=['{feat}'], errors='ignore')\n"
            f"print(f'Dropped {feat}. Remaining features: {{X.shape[1]}}')\n"))

    if re.search(r'\badd polynomial\b', direction, re.IGNORECASE):
        matched = True
        tool('append', notebook_path, "X = df.drop(columns=[TARGET])", '-', stdin=(
            "# Direction: add polynomial features\n"
            "from sklearn.preprocessing import PolynomialFeatures\n"
            "_poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)\n"
            "X = pd.DataFrame(_poly.fit_transform(X), columns=_poly.get_feature_names_out(X.columns))\n"
            "print(f'Polynomial features added. Shape: {X.shape}')\n"))

    if not matched:
        notes.append("**Fallback:** no structured pattern matched. Claude edits the notebook "
                     "`.py` file directly to apply this direction.")

tool('narrative', notebook_path, 'direction', '-', stdin=(
    f"## Iteration Direction\n\n**Analyst direction:** {direction}\n\n"
    + "\n\n".join(notes)
    + "\n\n*Automated modifications applied where patterns matched.*\n"))
subprocess.run([*TOOL, 'check', notebook_path], check=True)
print(f"Notebook modified: {notebook_path}")
print(f"Direction: '{direction}' | Regex matched: {matched}")
```

Run as:
```bash
python3 /tmp/doml_modify_supervised_notebook.py "$DIRECTION" "$PROBLEM_TYPE" "$NEW_NOTEBOOK"
```

If no regex matched and the direction is non-empty, Claude reads the notebook and applies the
direction by editing `$NEW_NOTEBOOK` directly (it is plain Python): change code inside the cell
that defines a variable, never redefine a variable in a second cell. Then run
`python3 .claude/doml/bin/doml_nb.py check "$NEW_NOTEBOOK"` and fix any reported issue.

---

### Step 7 — Execute the new notebook inside Docker

Determine the versioned report name (per D-02):

```bash
if [ "$PROBLEM_TYPE" = "regression" ] || [ "$PROBLEM_TYPE" = "classification" ]; then
  REPORT_NAME="model_report_v${NEXT_VERSION}"
elif [ "$PROBLEM_TYPE" = "clustering" ]; then
  REPORT_NAME="clustering_report_v${NEXT_VERSION}"
else
  REPORT_NAME="dimreduction_report_v${NEXT_VERSION}"
fi
```

```bash
docker compose exec doml \
  python .claude/doml/bin/doml_nb.py run "$NEW_NOTEBOOK" \
  --report reports/$REPORT_NAME.html --timeout ${TIMEOUT}
```

Timeout: 1200s (supervised — Optuna adds execution time); 900s (unsupervised — no Optuna).

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-iterate again.
```
Stop.

On execution failure (non-zero exit code), display the cell error. Stop — do not append to leaderboard on failed execution.

Verify notebook executed:
```bash
# The run step exits non-zero on any cell error; this re-checks the exported report.
python3 .claude/doml/bin/doml_nb.py verify-report reports/$REPORT_NAME.html
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

The report name `$REPORT_NAME` was set in Step 7.

Write an executive narrative comparing this iteration vs the prior one. It is saved as the `summary` sidecar, which the notebook renders near the top, after the direction cell. The narrative:
- Summarises what changed (direction applied, parameters modified)
- Compares key metrics to the prior version: for supervised — RMSE delta (regression) or ROC-AUC delta (classification); for unsupervised — silhouette/Davies-Bouldin/Calinski-Harabasz delta (clustering) or variance-explained delta (dimensionality_reduction)
- States whether results improved
- Written for a non-technical stakeholder audience

```bash
# Narrative sidecar: the notebook renders notebooks/narratives/<stem>/summary.md
cat > /tmp/doml_summary.md <<'DOML_EOF'
## Executive Summary

[WRITE THE TEXT HERE]
DOML_EOF
python3 .claude/doml/bin/doml_nb.py narrative "$NEW_NOTEBOOK" summary /tmp/doml_summary.md
```

---

### Step 10 — Write interpretation (sidecar) comparing v{N+1} vs v{N}

Read both the prior leaderboard (from Step 3) and new leaderboard (from Step 8). Claude writes an **Iteration Interpretation** Markdown section comparing the two runs.

The interpretation must include:
1. **What changed** — which direction was applied, what parameters were modified
2. **Metric delta** — comparing new vs prior metrics (regression: RMSE; classification: ROC-AUC; clustering: silhouette/Davies-Bouldin/Calinski-Harabasz; dimensionality_reduction: variance explained / n_components at 90%)
3. **Assessment** — whether the change improved results; whether to continue this direction
4. **Next iteration suggestion** — specific next `/doml-iterate` direction if warranted

Save the interpretation as the `interpretation` sidecar:

```bash
# Narrative sidecar: the notebook renders notebooks/narratives/<stem>/interpretation.md
cat > /tmp/doml_interpretation.md <<'DOML_EOF'
[WRITE THE TEXT HERE]
DOML_EOF
python3 .claude/doml/bin/doml_nb.py narrative "$NEW_NOTEBOOK" interpretation /tmp/doml_interpretation.md
```

Re-export the report so it shows the direction, summary and interpretation sidecars (code hidden):

```bash
# marimo re-runs the notebook (seeded, so results are identical; leaderboard rows are
# replaced, not duplicated).
docker compose exec doml \
  python .claude/doml/bin/doml_nb.py run "$NEW_NOTEBOOK" \
  --report "reports/${REPORT_NAME}.html" --timeout ${TIMEOUT}
python3 .claude/doml/bin/doml_nb.py verify-report "reports/${REPORT_NAME}.html" --require "not causation"
```

If the container is not running, display the standard container-not-running error (same as Step 7).

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

- **Never pass the direction string to a shell command** — use Python `doml_nb.py` API only (`sys.argv[1]` to receive direction in scripts — it is NEVER interpolated into a bash string)
- **Never overwrite leaderboard CSVs** — always `pd.concat` append; never `pd.to_csv` without the prior data concatenated
- **Never hardcode version numbers** — always glob and increment from existing notebooks
- **Never include accuracy/F1/ROC-AUC in unsupervised metrics** — internal metrics only (silhouette, Davies-Bouldin, Calinski-Harabasz)
- **Never compute silhouette on DBSCAN with noise points** — always mask `labels != -1` before calling `silhouette_score`
- **Never overwrite existing versioned notebooks** — `v{N+1}` is always a new file copied from the template, never a modification of `v{N}`
- **Never generate reports with code visible** — `doml_nb.py run` exports with `--no-include-code`; never pass `--with-code` for a stakeholder report
- **Report names must be versioned** — `model_report_v{N}.html`, `clustering_report_v{N}.html`, `dimreduction_report_v{N}.html` — never `model_report.html` (that is only for initial runs via `/doml-modelling`)
