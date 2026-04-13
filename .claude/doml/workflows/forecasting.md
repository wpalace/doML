# DoML Forecasting Workflow

## Purpose
Run the time series forecasting phase end-to-end: config validation, time_factor guard,
argument parsing, input file resolution, notebook copy + parameter injection, Docker execution,
executive narrative insertion, HTML report, leaderboard verification, and STATE.md update.

## Invoked by: /doml-forecasting --horizon N --target COLUMN [--regressors COL1,COL2] [--seasonality PERIOD] [--guidance "..."]

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

### Step 2 — Read config.json and check time_factor (CMD-16 early-exit gate)

Read `.planning/config.json`. If missing:

```
config.json not found. Run /doml-new-project first.
```

Stop.

Check `time_factor`:

```bash
TIME_FACTOR=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('time_factor', False))")
```

If `TIME_FACTOR` is not `True`:

```
This dataset was not identified as time series.
Set time_factor=true in .planning/config.json to enable forecasting.
```

Stop.

### Step 3 — Parse and validate arguments

Parse `$ARGUMENTS` for the following flags:

- `--horizon N` — **required** integer. If absent:
  ```
  Forecast horizon required. Run: /doml-forecasting --horizon N --target COLUMN_NAME
  ```
  Stop.

- `--target COLUMN` — **required** string. If absent:
  ```
  Target column required. Run: /doml-forecasting --horizon N --target COLUMN_NAME
  ```
  Stop.

- `--regressors COL1,COL2` — optional. If absent: set `REGRESSORS=""`.

- `--seasonality daily|weekly|monthly|yearly|none` — optional. If absent: set `SEASONALITY="auto"`.

- `--guidance "..."` — optional. If absent: set `GUIDANCE=""`.

Store values in shell variables: `HORIZON`, `TARGET`, `REGRESSORS`, `SEASONALITY`, `GUIDANCE`.

**SECURITY:** `TARGET` and `REGRESSORS` values are used only in Python — never shell-interpolated
into commands. Pass them via Python `-c` inline or via a temporary `.py` script only. The same
principle applies to `GUIDANCE` — write it into a Python string variable, never into a shell
command directly. This prevents injection attacks from column names or analyst guidance strings
containing shell metacharacters.

### Step 4 — Resolve input file from data/processed/

```bash
DATASET_PATH=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c['dataset']['path'])")
BASENAME=$(basename "$DATASET_PATH")
STEM="${BASENAME%.*}"
EXT="${BASENAME##*.}"
```

Look for `data/processed/${STEM}.${EXT}` first, then `data/processed/preprocessed_${BASENAME}`
(prefer preprocessed if it exists). If neither found:

```
No processed dataset found in data/processed/.
Run /doml-data-understanding and preprocessing first, or ensure the file exists in data/processed/.
```

Stop.

Set `INPUT_FILE` to the resolved path. Verify it exists:

```bash
test -f "$INPUT_FILE" || { echo "Error: Input file not found: $INPUT_FILE"; exit 1; }
```

### Step 5 — Check for existing notebook

If `notebooks/forecasting.ipynb` already exists, ask via AskUserQuestion:

```
notebooks/forecasting.ipynb already exists. Overwrite? (yes / no)
```

If the user says no, stop without overwriting.

### Step 6 — Copy notebook template and inject parameters

```bash
mkdir -p notebooks
cp .claude/doml/templates/notebooks/forecasting.ipynb notebooks/forecasting.ipynb
```

If the template does not exist:

```
Notebook template not found: .claude/doml/templates/notebooks/forecasting.ipynb
Run plan 12-02 to generate the forecasting.ipynb template first.
```

Stop.

Inject runtime parameters by writing a temporary Python script (never shell-interpolate
column names or guidance strings):

```python
# /tmp/doml_inject_forecast_params.py
import nbformat, json, sys

PARAMS = {
    'HORIZON': int(sys.argv[1]),
    'TARGET_COL': sys.argv[2],
    'REGRESSORS': sys.argv[3],   # empty string if not provided
    'SEASONALITY': sys.argv[4],  # 'auto' or override value
    'INPUT_FILE': sys.argv[5],
}

with open('notebooks/forecasting.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

# Find and replace the PARAMS cell (cell containing HORIZON = None)
for cell in nb.cells:
    if cell.cell_type == 'code' and 'HORIZON = None' in cell.source:
        lines = [
            f"HORIZON = {PARAMS['HORIZON']}",
            f"TARGET_COL = {json.dumps(PARAMS['TARGET_COL'])}",
            f"REGRESSORS = {json.dumps(PARAMS['REGRESSORS'])}",
            f"SEASONALITY = {json.dumps(PARAMS['SEASONALITY'])}",
            f"INPUT_FILE_OVERRIDE = {json.dumps(PARAMS['INPUT_FILE'])}",
        ]
        cell.source = '\n'.join(lines)
        break

with open('notebooks/forecasting.ipynb', 'w') as f:
    nbformat.write(nb, f)

print('Parameters injected into notebooks/forecasting.ipynb')
```

Write that script to `/tmp/doml_inject_forecast_params.py`, then run:

```bash
python3 /tmp/doml_inject_forecast_params.py "$HORIZON" "$TARGET" "$REGRESSORS" "$SEASONALITY" "$INPUT_FILE"
```

### Step 7 — Execute notebook inside Docker

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/forecasting.ipynb \
  --ExecutePreprocessor.timeout=900
```

Timeout is 900 seconds (models may take significant time). If the container is not running:

```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-forecasting again.
```

Stop.

On non-zero exit code, display the nbconvert error output and stop. Do not generate HTML on
a failed execution.

### Step 8 — Verify notebook output

```bash
python3 -c "
import nbformat
with open('notebooks/forecasting.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Executed notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs — execution may have failed'
"
```

If verification fails, report the error and stop. Do not generate the HTML report on an
unexecuted notebook.

### Step 9 — Write forecasting narrative and insert as first cell

Generate a 2–3 paragraph executive summary interpreting the forecasting results for
non-technical stakeholders.

Read to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, decision framing
- `.planning/config.json` — problem_type, dataset.path, time_factor
- `notebooks/forecasting.ipynb` — executed cell outputs (model metrics, leaderboard, intervals)
- `models/forecast_leaderboard.csv` — final ranked results

The narrative must:
- State the forecast horizon and target in plain language
- Name the winning model and its accuracy (MAE/RMSE/MAPE) vs. the SeasonalNaive baseline
- Describe prediction interval width at the end of the horizon (are intervals tight or wide?)
- Note any seasonality detected and whether the seasonal pattern dominated accuracy
- Avoid jargon (no "pmdarima", "TimeSeriesSplit", "quantile regression" — say "confidence bands")
- Include one concrete recommendation (e.g., "The [model] forecast is suitable for operational
  planning; re-run after 4 weeks of new data to verify drift hasn't occurred")
- If `GUIDANCE` is non-empty, incorporate it as additional context

Write the narrative into a temporary Python script to avoid special-character quoting issues
(same pattern as anomaly-detection.md Step 7):

```python
# /tmp/doml_insert_forecast_summary.py
import nbformat, uuid

NARRATIVE = """[WRITE YOUR 2-3 PARAGRAPH EXECUTIVE NARRATIVE HERE]"""

with open('notebooks/forecasting.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

summary_cell = nbformat.v4.new_markdown_cell(source='## Executive Summary\n\n' + NARRATIVE)
summary_cell['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(0, summary_cell)

with open('notebooks/forecasting.ipynb', 'w') as f:
    nbformat.write(nb, f)

print('Forecasting executive narrative inserted as cell 0')
```

Write the actual narrative into `NARRATIVE` (never pass `$GUIDANCE` via shell interpolation —
always write the guidance content as a Python string literal in the script). Then run:

```bash
python3 /tmp/doml_insert_forecast_summary.py
```

### Step 10 — Generate HTML report

**Step 10a — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 10b — Convert notebook to HTML (code cells hidden)**

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/forecasting.ipynb \
  --output-dir reports \
  --output forecasting_report
```

This produces `reports/forecasting_report.html`. The `--no-input` flag hides all code cells (OUT-02).

If the container is not running:

```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-forecasting again.
```

Stop.

**Step 10c — Verify HTML report**

```bash
# Check 1: File exists
test -f reports/forecasting_report.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"

# Check 2: Code cells are hidden (OUT-02) — expected: 0 matches
grep -c 'class="input"' reports/forecasting_report.html && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"

# Check 3: Caveats section present (OUT-03) — expected: >= 1 match
grep -ci "correlation is not causation" reports/forecasting_report.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"

# Check 4: Executive summary present — expected: >= 1 match
grep -c "Executive Summary" reports/forecasting_report.html && echo "EXEC_SUMMARY_OK" || echo "EXEC_SUMMARY_MISSING"
```

If any check fails, report which check failed. Do not suppress failures.

### Step 11 — Verify leaderboard CSV and confirm

```bash
if [ -f "models/forecast_leaderboard.csv" ]; then
  ROWS=$(python3 -c "import csv; print(sum(1 for _ in open('models/forecast_leaderboard.csv')) - 1)")
  echo "FORE-01 OK: models/forecast_leaderboard.csv exists ($ROWS model rows)"
else
  echo "FORE-01 FAIL: models/forecast_leaderboard.csv not found"
fi
```

Update `.planning/STATE.md`: append to Decisions:
`[Phase 12]: doml-forecasting completed — notebooks/forecasting.ipynb + reports/forecasting_report.html + models/forecast_leaderboard.csv`

Display completion message:

```
Forecasting complete.

  Notebook:    notebooks/forecasting.ipynb
  Report:      reports/forecasting_report.html
  Leaderboard: models/forecast_leaderboard.csv

Review the report for model comparison and prediction interval analysis.
```

---

## Notes for Analysts

After adding `pmdarima` to `requirements.in`, regenerate the pinned dependencies and rebuild
the Docker image:

```bash
docker compose run --rm jupyter pip-compile requirements.in
docker compose build
```

This must be done before running `/doml-forecasting` for the first time, as `pmdarima` provides
the `auto_arima()` function used for automatic ARIMA/SARIMA order selection.
