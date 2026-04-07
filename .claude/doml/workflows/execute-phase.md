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

**Note for Phase 2 (Data Understanding):** Executor will be implemented in DoML Phase 5.

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

**Note for Phase 2 (Data Understanding):** Step 5 for EDA will use `eda_report.html` as output. Implemented in DoML Phase 5.

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
