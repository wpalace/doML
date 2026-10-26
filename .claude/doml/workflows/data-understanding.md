# DoML Data Understanding Workflow

## Purpose
Run the Data Understanding (EDA) phase end-to-end: headerless CSV check,
notebook copy, Docker execution, executive narrative, HTML report generation.

## Invoked by: /doml-data-understanding [--guidance "..."]

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

### Step 2 — Read project config

Read `.planning/config.json`. If missing:

```
config.json not found. Run /doml-new-project first.
```

Stop.

Extract optional `--guidance` from `$ARGUMENTS`. If present, save to a `GUIDANCE` variable
for use in Step 7. If `$ARGUMENTS` is empty or does not contain `--guidance`, set
`GUIDANCE=""`.

### Step 3 — Check for headerless CSVs without column names

Before proceeding, scan `data/raw/` for any CSVs that have no header row and no
`column_names` entry in `config.json`. The EDA notebook will show auto-named columns
(`column0`, `column1`, ...) throughout all analysis sections without proper names, making
results uninterpretable.

```bash
python3 -c "
import duckdb, pathlib, json, re

raw = pathlib.Path('data/raw')
config_path = pathlib.Path('.planning/config.json')
config = json.loads(config_path.read_text()) if config_path.exists() else {}
known_names = config.get('column_names', {})

for csv in sorted(raw.glob('**/*.csv')):
    con = duckdb.connect()
    try:
        cols = con.execute(f\"DESCRIBE SELECT * FROM read_csv_auto('{csv}')\").df()['column_name'].tolist()
        auto_named = all(re.match(r'^column\d+\$', c) for c in cols)
        if auto_named and csv.stem not in known_names and csv.name not in known_names:
            print(f'HEADERLESS:{csv.name}:{len(cols)}')
    finally:
        con.close()
"
```

If any `HEADERLESS:` lines appear, for each affected file use AskUserQuestion to strongly
encourage the user to provide column names:

```
'{filename}' has no header row — the EDA report will show column0, column1, ... throughout all analysis sections.
data/raw/ is read-only, so you cannot add headers to the source file.

Providing column names now will give you a meaningful, readable report.
Please enter the {N} column names as a comma-separated list, or type 'skip' to proceed with auto-names:
```

If the user provides names (not 'skip'), save them to `.planning/config.json` under
`column_names`:

```python
# /tmp/doml_set_column_names.py
import json, pathlib

config_path = pathlib.Path('.planning/config.json')
config = json.loads(config_path.read_text())
config.setdefault('column_names', {})
config['column_names']['{stem}'] = [n.strip() for n in '{user_response}'.split(',')]
config_path.write_text(json.dumps(config, indent=2))
print('column_names saved to config.json')
```

Replace `{stem}` and `{user_response}` with actual values before running:
```bash
python3 /tmp/doml_set_column_names.py
```

If the user skips, proceed but note that column names will appear as `column0..N`.

### Step 4 — Copy notebook template

Data understanding is Python only (a marimo notebook):
```bash
mkdir -p notebooks
TEMPLATE=".claude/doml/templates/notebooks/data_understanding.py"
echo "Using template: $TEMPLATE"
```

If `notebooks/02_data_understanding.py` already exists, ask before overwriting:
```
notebooks/02_data_understanding.py already exists. Overwrite? (yes / no)
```
Use AskUserQuestion for this. If the user says no, stop without overwriting.

Copy the template:
```bash
cp "$TEMPLATE" notebooks/02_data_understanding.py
```

### Step 5 — Execute the notebook inside Docker

```bash
docker compose exec doml \
  python .claude/doml/bin/doml_nb.py run notebooks/02_data_understanding.py \
  --report reports/eda_report.html --timeout 600
```

If the container is not running, display:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-data-understanding again.
```
and stop.

On execution failure (non-zero exit code), display the cell error output and stop.
Do not proceed to HTML generation.

### Step 6 — Verify notebook output

```bash
# The run step exits non-zero on any cell error; this re-checks the exported report.
python3 .claude/doml/bin/doml_nb.py verify-report reports/eda_report.html
```

If verification fails, report the error and stop. Do not generate the HTML report on an
unexecuted notebook.

### Step 7 — Write EDA executive narrative

Generate a 2–3 paragraph executive summary interpreting EDA findings for non-technical
stakeholders.

Read the following to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, decision framing
- `.planning/config.json` — problem_type, time_factor
- The executed notebook `notebooks/02_data_understanding.py` — cell outputs showing
  DuckDB profiling results, normality tests, correlation values, and tidy violations

The EDA narrative must:
- Avoid technical jargon (no "DuckDB", "Shapiro-Wilk", "marimo", "ADF")
- State dataset size in plain language (e.g., "The dataset contains 12,000 observations
  and 15 features")
- Highlight top correlated features in business terms
- Note whether key numeric features are normally distributed or skewed — use plain language
  ("most values cluster near the middle" vs "most values are low with a long tail of high
  values")
- If time_factor is true: state in plain language whether the series appears stationary or
  trending
- Flag any data quality issues found (missing values, tidy violations) in plain language
- Be 2–3 short paragraphs

If `GUIDANCE` is non-empty, incorporate it as additional context shaping the EDA narrative
(e.g., if guidance says "focus on outlier impact", ensure the narrative highlights outlier
findings prominently).

Save the narrative as the notebook's `summary` sidecar (rendered directly below the title). The quoted
heredoc avoids special-character quoting issues:

```bash
# Narrative sidecar: the notebook renders notebooks/narratives/<stem>/summary.md
cat > /tmp/doml_summary.md <<'DOML_EOF'
## Executive Summary

[WRITE YOUR 2-3 PARAGRAPH EDA EXECUTIVE SUMMARY HERE]
DOML_EOF
python3 .claude/doml/bin/doml_nb.py narrative notebooks/02_data_understanding.py summary /tmp/doml_summary.md
```

Write the actual narrative text into the quoted heredoc above before running it. The quoted
`'DOML_EOF'` delimiter means no shell interpolation happens (never pass `$GUIDANCE` through the shell).

### Step 8 — Generate HTML report

**Step 8a — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 8b — Convert EDA notebook to HTML (code cells hidden)**

```bash
# Re-export so the report shows the narrative cells written above.
# marimo re-runs the notebook (seeded, so results are identical; leaderboard
# rows are replaced, not duplicated).
docker compose exec doml \
  python .claude/doml/bin/doml_nb.py run notebooks/02_data_understanding.py \
  --report reports/eda_report.html
```

This produces `reports/eda_report.html`. The `--no-input` flag hides all code cells (OUT-02).

If the container is not running, display:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-data-understanding again.
```
and stop.

**Step 8c — Verify EDA HTML report**

```bash
# Check 1: File exists
test -f reports/eda_report.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"

# Check 2: Code cells are hidden (OUT-02) — expected: 0 matches
python3 .claude/doml/bin/doml_nb.py verify-report reports/eda_report.html  # prints CODE_HIDDEN_OK and NO_CELL_ERRORS_OK

# Check 3: Caveats section present (OUT-03) — expected: >= 1 match
grep -ci "correlation is not causation" reports/eda_report.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"

# Check 4: Executive summary present — expected: >= 1 match
grep -c "Executive Summary" reports/eda_report.html && echo "EXEC_SUMMARY_OK" || echo "EXEC_SUMMARY_MISSING"
```

If any check fails, report which check failed. Do not suppress failures.

### Step 9 — Update STATE.md

Write to `.planning/STATE.md`:
- Update `current_focus` to "Modelling (next) — run /doml-modelling"
- Append to Decisions section:
  `[Phase 08]: doml-data-understanding completed — notebooks/02_data_understanding.py + reports/eda_report.html generated`
- Update `last_activity` with today's date

### Step 10 — Confirm

Display:
```
Data Understanding complete.

  Notebook: notebooks/02_data_understanding.py
  Report:   reports/eda_report.html

Next step: /doml-modelling
```
