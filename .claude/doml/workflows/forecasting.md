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
3. Notebooks are plain-Python marimo files: outputs are never stored in git, only in `reports/*.html` (REPR-03)

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

If `notebooks/forecasting.py` already exists, ask via AskUserQuestion:

```
notebooks/forecasting.py already exists. Overwrite? (yes / no)
```

If the user says no, stop without overwriting.

### Step 6 — Copy notebook template and inject parameters

```bash
mkdir -p notebooks
cp .claude/doml/templates/notebooks/forecasting.py notebooks/forecasting.py
```

If the template does not exist:

```
Notebook template not found: .claude/doml/templates/notebooks/forecasting.py
Run plan 12-02 to generate the forecasting.py template first.
```

Stop.

Inject runtime parameters by writing a temporary Python script (never shell-interpolate
column names or guidance strings). The marimo notebook is plain Python, so injection is a
text edit of the parameter assignments (`HORIZON = None`, ...) done by `doml_nb.py set-param`:

```python
# /tmp/doml_inject_forecast_params.py
import json, subprocess, sys

PARAMS = {
    'HORIZON': int(sys.argv[1]),
    'TARGET_COL': sys.argv[2],
    'REGRESSORS': sys.argv[3],   # empty string if not provided
    'SEASONALITY': sys.argv[4],  # 'auto' or override value
    'INPUT_FILE_OVERRIDE': sys.argv[5],
}

for name, value in PARAMS.items():
    subprocess.run(
        [sys.executable, '.claude/doml/bin/doml_nb.py', 'set-param',
         'notebooks/forecasting.py', name, json.dumps(value)],
        check=True,
    )
print('Parameters injected into notebooks/forecasting.py')
```

Write that script to `/tmp/doml_inject_forecast_params.py`, then run:

```bash
python3 /tmp/doml_inject_forecast_params.py "$HORIZON" "$TARGET" "$REGRESSORS" "$SEASONALITY" "$INPUT_FILE"
```

### Step 7 — Execute notebook inside Docker

```bash
docker compose exec doml \
  python .claude/doml/bin/doml_nb.py run notebooks/forecasting.py \
  --report reports/forecasting_report.html --timeout 900
```

Timeout is 900 seconds (models may take significant time). If the container is not running:

```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-forecasting again.
```

Stop.

On non-zero exit code, display the cell error output and stop. Do not generate HTML on
a failed execution.

### Step 8 — Verify notebook output

```bash
# The run step exits non-zero on any cell error; this re-checks the exported report.
python3 .claude/doml/bin/doml_nb.py verify-report reports/forecasting_report.html
```

If verification fails, report the error and stop. Do not generate the HTML report on an
unexecuted notebook.

### Step 9 — Write forecasting narrative (summary sidecar)

Generate a 2–3 paragraph executive summary interpreting the forecasting results for
non-technical stakeholders.

Read to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, decision framing
- `.planning/config.json` — problem_type, dataset.path, time_factor
- `notebooks/forecasting.py` — executed cell outputs (model metrics, leaderboard, intervals)
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

Save the narrative as the notebook's `summary` sidecar (rendered directly below the title). The quoted
heredoc avoids special-character quoting issues:

```bash
# Narrative sidecar: the notebook renders notebooks/narratives/<stem>/summary.md
cat > /tmp/doml_summary.md <<'DOML_EOF'
## Executive Summary

[WRITE YOUR 2-3 PARAGRAPH EXECUTIVE NARRATIVE HERE]
DOML_EOF
python3 .claude/doml/bin/doml_nb.py narrative notebooks/forecasting.py summary /tmp/doml_summary.md
```

Write the actual narrative text into the quoted heredoc above before running it. The quoted
`'DOML_EOF'` delimiter means no shell interpolation happens (never pass `$GUIDANCE` through the shell).

### Step 10 — Generate HTML report

**Step 10a — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 10b — Convert notebook to HTML (code cells hidden)**

```bash
# Re-export so the report shows the narrative cells written above.
# marimo re-runs the notebook (seeded, so results are identical; leaderboard
# rows are replaced, not duplicated).
docker compose exec doml \
  python .claude/doml/bin/doml_nb.py run notebooks/forecasting.py \
  --report reports/forecasting_report.html
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
python3 .claude/doml/bin/doml_nb.py verify-report reports/forecasting_report.html  # prints CODE_HIDDEN_OK and NO_CELL_ERRORS_OK

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
`[Phase 12]: doml-forecasting completed — notebooks/forecasting.py + reports/forecasting_report.html + models/forecast_leaderboard.csv`

Display completion message:

```
Forecasting complete.

  Notebook:    notebooks/forecasting.py
  Report:      reports/forecasting_report.html
  Leaderboard: models/forecast_leaderboard.csv

Review the report for model comparison and prediction interval analysis.
```

---

## Notes for Analysts

`pmdarima` (for `auto_arima()` ARIMA/SARIMA order selection) and `prophet` are part of the
locked DoML image (`pyproject.toml` / `uv.lock`). No extra install step is needed.
