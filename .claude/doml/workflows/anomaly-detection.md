# DoML Anomaly Detection Workflow

## Purpose
Run the optional anomaly detection phase end-to-end: tidy validation, Isolation Forest, LOF, DBSCAN,
consensus flag, HTML report, and flag CSV output.

## Invoked by: /doml-anomaly-detection [--file path/to/file] [--guidance "..."]

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

### Step 2 — Read project config and parse arguments

Read `.planning/config.json`. If missing:

```
config.json not found. Run /doml-new-project first.
```

Stop.

Parse `$ARGUMENTS`:

- `--file <path>` — override the default input file. Set `INPUT_FILE` to the provided path.
  If not present, resolve `INPUT_FILE` from `config.json`:
  ```bash
  INPUT_FILE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c['dataset']['path'])")
  ```
- `--guidance "..."` — analyst direction text. If present, save to `GUIDANCE` variable.
  If absent, set `GUIDANCE=""`.

Verify `INPUT_FILE` exists on disk:
```bash
test -f "$INPUT_FILE" || { echo "Error: Input file not found: $INPUT_FILE"; exit 1; }
```

### Step 3 — Check for existing notebook

If `notebooks/anomaly_detection.ipynb` already exists, ask before overwriting:

```
notebooks/anomaly_detection.ipynb already exists. Overwrite? (yes / no)
```

Use AskUserQuestion. If the user says no, stop without overwriting.

### Step 4 — Copy notebook template

```bash
mkdir -p notebooks
cp .claude/doml/templates/notebooks/anomaly_detection.ipynb notebooks/anomaly_detection.ipynb
```

If the template does not exist:

```
Notebook template not found: .claude/doml/templates/notebooks/anomaly_detection.ipynb
Run /doml-anomaly-detection after Phase 10 plan 02 has been executed.
```

Stop.

### Step 5 — Execute the notebook inside Docker

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/anomaly_detection.ipynb \
  --ExecutePreprocessor.timeout=600
```

If the container is not running, display:

```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-anomaly-detection again.
```

Stop.

On execution failure (non-zero exit code), display the nbconvert error output and stop.
Do not proceed to HTML generation.

### Step 6 — Verify notebook output

```bash
python3 -c "
import nbformat
with open('notebooks/anomaly_detection.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
code_cells_with_output = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f'Executed notebook: {code_cells_with_output} code cells with output')
assert code_cells_with_output > 0, 'No cell outputs found — execution may have failed'
"
```

If verification fails, report the error and stop. Do not generate the HTML report on an
unexecuted notebook.

### Step 7 — Write anomaly detection narrative

Generate a 2–3 paragraph executive summary interpreting the anomaly findings for non-technical
stakeholders. The narrative MUST go beyond describing what was found — it must suggest how to
handle each anomaly cluster (see D-03 in CONTEXT.md).

Read the following to inform the narrative:
- `.planning/PROJECT.md` — business question, stakeholder, decision framing
- `.planning/config.json` — problem_type, dataset.path
- The executed notebook `notebooks/anomaly_detection.ipynb` — cell outputs showing Isolation
  Forest scores, LOF scores, DBSCAN labels, consensus flag counts, and the summary table

The narrative must:
- Avoid technical jargon (no "LOF", "DBSCAN", "sklearn", "nbformat")
- State how many anomalies were flagged in plain language (e.g., "The analysis identified
  27 records — about 2.3% of the dataset — that behaved differently from the rest")
- For each identifiable anomaly cluster, suggest a treatment action:
  - "These N rows have extreme values across multiple features — likely data entry errors.
    Consider dropping before modelling."
  - "These N rows are valid edge-case observations — keep in training data but flag for
    sensitivity analysis."
  - "These N rows cluster together and may represent a legitimate minority subgroup."
- Flag any limitations (e.g., only numeric features were used; categoricals were excluded)
- End with a note about the flag CSV available for downstream use
- Be 2–3 short paragraphs

If `GUIDANCE` is non-empty, incorporate it as additional context shaping the narrative.

Write the narrative to a temporary Python script to avoid special-character quoting issues,
then run it:

```python
# /tmp/doml_insert_anomaly_summary.py
import nbformat, uuid

NARRATIVE = """[WRITE YOUR 2-3 PARAGRAPH ANOMALY EXECUTIVE SUMMARY HERE]"""

with open('notebooks/anomaly_detection.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

summary_cell = nbformat.v4.new_markdown_cell(source='## Executive Summary\n\n' + NARRATIVE)
summary_cell['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(0, summary_cell)

with open('notebooks/anomaly_detection.ipynb', 'w') as f:
    nbformat.write(nb, f)

print('Anomaly detection executive narrative inserted as cell 0')
```

Write the actual narrative into `NARRATIVE`, then run:
```bash
python3 /tmp/doml_insert_anomaly_summary.py
```

### Step 8 — Generate HTML report

**Step 8a — Create reports/ directory**

```bash
mkdir -p reports
```

**Step 8b — Convert notebook to HTML (code cells hidden)**

```bash
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/anomaly_detection.ipynb \
  --output-dir reports \
  --output anomaly_report
```

This produces `reports/anomaly_report.html`. The `--no-input` flag hides all code cells (OUT-02).

If the container is not running, display:
```
Docker container is not running. Start it with:
  docker compose up -d
Then run /doml-anomaly-detection again.
```

Stop.

**Step 8c — Verify HTML report**

```bash
# Check 1: File exists
test -f reports/anomaly_report.html && echo "REPORT_EXISTS" || echo "REPORT_MISSING"

# Check 2: Code cells are hidden (OUT-02) — expected: 0 matches
grep -c 'class="input"' reports/anomaly_report.html && echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"

# Check 3: Caveats section present (OUT-03) — expected: >= 1 match
grep -ci "correlation is not causation" reports/anomaly_report.html && echo "CAVEATS_OK" || echo "CAVEATS_MISSING"

# Check 4: Executive summary present — expected: >= 1 match
grep -c "Executive Summary" reports/anomaly_report.html && echo "EXEC_SUMMARY_OK" || echo "EXEC_SUMMARY_MISSING"
```

If any check fails, report which check failed. Do not suppress failures.

### Step 9 — Verify flag CSV was written

```bash
# Determine expected filename from INPUT_FILE basename
FLAG_CSV="data/processed/anomaly_flags_$(basename "$INPUT_FILE")"

if [ -f "$FLAG_CSV" ]; then
  ROW_COUNT=$(python3 -c "import csv; print(sum(1 for _ in open('$FLAG_CSV')) - 1)")
  echo "ANOM-04 OK: $FLAG_CSV exists ($ROW_COUNT data rows)"
else
  echo "ANOM-04 FAIL: $FLAG_CSV not found — notebook may not have completed the Save Flags section"
fi
```

### Step 10 — Update STATE.md

Write to `.planning/STATE.md`:
- Update `current_focus` to "Anomaly detection complete — review reports/anomaly_report.html"
- Append to Decisions section:
  `[Phase 10]: doml-anomaly-detection completed — notebooks/anomaly_detection.ipynb + reports/anomaly_report.html + data/processed/anomaly_flags_*.csv`
- Update `last_activity` with today's date

### Step 11 — Confirm

Display:

```
Anomaly Detection complete.

  Notebook:  notebooks/anomaly_detection.ipynb
  Report:    reports/anomaly_report.html
  Flags CSV: data/processed/anomaly_flags_{filename}.csv

Review the report for treatment recommendations per anomaly cluster.
The flag CSV is ready for use in downstream preprocessing or modelling.
```
