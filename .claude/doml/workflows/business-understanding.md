# DoML Business Understanding Workflow

## Purpose
Run the Business Understanding phase end-to-end: copy notebook template, check for headerless CSVs,
execute in Docker, write executive narrative, generate HTML report.

## Invoked by: /doml-business-understanding [--guidance "..."]

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

### Step 2 — Read project config

Read `.planning/config.json` and `.planning/PROJECT.md`. If either is missing:

```
PROJECT.md or config.json not found. Run /doml-new-project first.
```

Stop.

Extract optional `--guidance` from `$ARGUMENTS`. If present, save to a `GUIDANCE` variable
for use in Step 6. If `$ARGUMENTS` is empty or does not contain `--guidance`, set
`GUIDANCE=""`.

### Step 3 — Copy notebook template

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

**Step 3.1 — Check for headerless CSVs**

Before executing the notebook, scan `data/raw/` for CSVs that have no header row:

```bash
python3 -c "
import duckdb, pathlib, json
raw = pathlib.Path('data/raw')
config_path = pathlib.Path('.planning/config.json')
config = json.loads(config_path.read_text()) if config_path.exists() else {}
known_names = config.get('column_names', {})

for csv in sorted(raw.glob('**/*.csv')):
    con = duckdb.connect()
    try:
        cols = con.execute(f\"DESCRIBE SELECT * FROM read_csv_auto('{csv}')\").df()['column_name'].tolist()
        auto_named = all(__import__('re').match(r'^column\d+\$', c) for c in cols)
        stem = csv.stem
        if auto_named and stem not in known_names and csv.name not in known_names:
            print(f'HEADERLESS:{csv.name}:{len(cols)}')
    finally:
        con.close()
"
```

If any `HEADERLESS:` lines appear, for each affected file ask the user to provide column names
using AskUserQuestion:

```
'{filename}' has no header row — DuckDB detected {N} columns.
data/raw/ is read-only, so you cannot add headers to the source file.
Please provide the column names as a comma-separated list (e.g. sepal_length,sepal_width,petal_length,petal_width,species):
```

After the user responds, write their names to `.planning/config.json` under `column_names`:

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

Replace `{stem}` and `{user_response}` with the actual values before running:
```bash
python3 /tmp/doml_set_column_names.py
```

### Step 4 — Execute the notebook inside Docker

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
Then run /doml-business-understanding again.
```
and stop.

On execution failure (non-zero exit code), display the nbconvert error output and stop.
Do not proceed to HTML generation.

### Step 5 — Verify notebook output

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

If verification fails, report the error and stop. Do not generate the HTML report on an
unexecuted notebook.

### Step 6 — Write executive narrative

Generate a 2–3 paragraph executive summary suitable for non-technical stakeholders.

Read the following to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, expected outcome, decision framing sentence
- `.planning/config.json` — problem type, time factor, language
- The executed notebook's cell outputs (`notebooks/01_business_understanding.ipynb`) for dataset counts

Write the narrative as plain Markdown. It must:
- Avoid technical jargon (no mentions of "DuckDB", "nbformat", "config.json")
- Address the stakeholder's business question in plain language
- Summarize what data was found (number of files, approximate row/column counts)
- State the confirmed ML problem type in plain terms (e.g., "This is a prediction problem"
  instead of "regression")
- Be 2–3 short paragraphs

If `GUIDANCE` is non-empty, incorporate it as additional context shaping the framing of the
narrative (e.g., if guidance says "focus on churn drivers", ensure the narrative emphasises
the churn framing).

Insert the narrative as the FIRST cell in the notebook using this Python script (write to a
temp file to avoid quoting issues):

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

### Step 7 — Generate HTML report

**Step 7a — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 7b — Convert notebook to HTML (code cells hidden)**

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/01_business_understanding.ipynb \
  --output-dir reports \
  --output business_summary
```

This produces `reports/business_summary.html`. The `--no-input` flag hides all code cells
(OUT-02).

If the container is not running, display:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-business-understanding again.
```
and stop.

**Step 7c — Verify HTML report**

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

### Step 8 — Update STATE.md

Write to `.planning/STATE.md`:
- Update `current_focus` to "Data Understanding (next) — run /doml-data-understanding"
- Append to Decisions section:
  `[Phase 08]: doml-business-understanding completed — notebooks/01_business_understanding.ipynb + reports/business_summary.html generated`
- Update `last_activity` with today's date

### Step 9 — Confirm

Display:
```
Business Understanding complete.

  Notebook: notebooks/01_business_understanding.ipynb
  Report:   reports/business_summary.html

Next step: /doml-data-understanding
```
