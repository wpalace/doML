# DoML Iterate Unsupervised Workflow

## Purpose
Generate a new unsupervised modelling iteration notebook with analyst-supplied direction.

Reads the most recent modelling notebook (clustering or dimensionality reduction), generates a new version incorporating the direction, executes it, appends results to `models/unsupervised_leaderboard.csv`, and reports metric deltas.

## Invoked by: /doml-iterate-unsupervised [direction]

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
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','clustering'))")
echo "Problem type: $PROBLEM_TYPE"
```

If `problem_type` is not `clustering` or `dimensionality_reduction`:
```
This command is for unsupervised problems only.
For regression/classification, use /doml-iterate-model.
For time series, use /doml-iterate-model (or the Phase 8 equivalent when available).
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

Read `models/unsupervised_leaderboard.csv` for prior metrics:

```bash
python3 -c "
import pandas as pd, os
lb_path = 'models/unsupervised_leaderboard.csv'
if os.path.exists(lb_path):
    lb = pd.read_csv(lb_path)
    print('Prior leaderboard (last run):')
    # Show most recent iteration rows
    max_iter = lb['iteration'].max()
    print(lb[lb['iteration'] == max_iter].to_string(index=False))
else:
    print('No unsupervised leaderboard found yet.')
"
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
print(m.group(1) if m else '5')
")

# Select template
if [ "$PROBLEM_TYPE" = "clustering" ]; then
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

**Direction parsing rules (apply all that match):**

For **clustering** directions:

| Direction contains | Modification |
|-------------------|--------------|
| "k=N" or "k = N" | In the KMeans cell, change `K_RANGE = range(2, 13)` and set `best_k = N` in a new cell after the sweep; add a Markdown note "Analyst override: k={N}" |
| "DBSCAN" or "dbscan" | In the DBSCAN grid cell, adjust `eps_candidates` and/or `minpts_candidates` based on any numeric values in the direction (e.g., "finer eps grid around 0.3" → `eps_candidates = [0.25, 0.30, 0.35]`) |
| "eps=X" | In the DBSCAN grid cell, set `eps_candidates = [X*0.8, X, X*1.2]` |
| "hierarchical" or "ward" | In the hierarchical_k cell, set `hierarchical_k = N` if a number is mentioned in direction |
| other | Add a Markdown cell at the top of the algorithm section documenting the direction; no code change (analyst reviews and modifies manually) |

For **dimensionality_reduction** directions:

| Direction contains | Modification |
|-------------------|--------------|
| "n_components=N" or "N-component" | In PCA output cell, change `pca_out = PCA(n_components=N)` |
| "n_neighbors=N" or "UMAP" + "n_neighbors" | In the UMAP 2D cell, change `n_neighbors=15` to `n_neighbors=N` |
| "perplexity" + "N" | In the t-SNE sweep cell, add `N` to the perplexity list or replace the default list |
| "PCA" focus | Reorder sections: move PCA to first place; add loadings deeper analysis |
| other | Add a Markdown cell at the top documenting the direction for analyst review |

**Implementation — use nbformat API:**

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

where `$DIRECTION` is the analyst's direction string (from `{{args}}`).

---

### Step 7 — Execute the new notebook inside Docker

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  "$NEW_NOTEBOOK" \
  --ExecutePreprocessor.timeout=900
```

Timeout: 900s (15 min). No Optuna in unsupervised — shorter than supervised (1200s).

If the container is not running:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-iterate-unsupervised again.
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

### Step 8 — Append results to models/unsupervised_leaderboard.csv

The executed notebook already appends to `models/unsupervised_leaderboard.csv` (the append cell is inside the template). Verify the append happened:

```bash
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
```

Save the latest iteration rows as `NEW_METRICS` for Step 9.

---

### Step 9 — Write interpretation Markdown cell comparing v{N+1} vs v{N}

Read both the prior leaderboard (from Step 3) and new leaderboard (from Step 8). Claude writes an **Iteration Interpretation** Markdown cell comparing the two runs.

The interpretation must include:
1. **What changed** — which direction was applied, what parameters were modified
2. **Metric delta** — new vs prior silhouette/Davies-Bouldin/Calinski-Harabasz (clustering) or variance-explained (dim reduction)
3. **Recommendation** — whether the change improved results; whether to continue this direction
4. **Next iteration suggestion** — specific next `/doml-iterate-unsupervised` direction if warranted

Write the interpretation cell using nbformat API (same pattern as execute-phase.md Step 3s):

```python
# /tmp/doml_insert_iteration_interpretation.py
import nbformat

INTERPRETATION = """## Iteration v{NEW_VERSION} — Interpretation

**Direction applied:** {DIRECTION}

### Metric Comparison

{METRIC_TABLE}

### What Changed

{CHANGE_DESCRIPTION}

### Assessment

{ASSESSMENT}

### Next Steps

{NEXT_STEPS}
"""

with open('NEW_NOTEBOOK_PATH') as f:
    nb = nbformat.read(f, as_version=4)

interp_cell = nbformat.v4.new_markdown_cell(source=INTERPRETATION)
nb.cells.append(interp_cell)

with open('NEW_NOTEBOOK_PATH', 'w') as f:
    nbformat.write(nb, f)

print("Iteration interpretation cell appended.")
```

---

### Step 10 — Report to analyst

Display a structured summary to the analyst:

```
## Iteration Complete

**Notebook:** {NEW_NOTEBOOK}
**Problem type:** {PROBLEM_TYPE}
**Direction:** {DIRECTION}

### Metric Delta (prior → new)

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
- models/unsupervised_leaderboard.csv (appended)

### Next Actions
- Continue iterating: /doml-iterate-unsupervised "next direction"
- View leaderboard summary: /doml-progress
- View leaderboard: cat models/unsupervised_leaderboard.csv
```

---

## Anti-Patterns to Avoid

- **Never pass the direction string to a shell command** — use Python nbformat API only (no injection risk)
- **Never overwrite unsupervised_leaderboard.csv** — always pd.concat append
- **Never include accuracy/F1/ROC-AUC** in metrics or iteration comparison — unsupervised only
- **Never compute silhouette on DBSCAN with noise points** — always mask `labels != -1` first
- **Never hardcode version numbers** — always glob and increment
