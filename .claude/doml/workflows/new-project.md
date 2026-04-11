# DoML New Project Workflow

## Purpose
Guided kickoff for a new DoML analysis project: interview → Docker environment → scaffold → planning artifacts.

## Invoked by: /doml-new-project

## Implementation Status

| Step | Implemented | Phase |
|------|-------------|-------|
| Existing project detection | Phase 2 | PLAN-01 |
| Docker environment setup | Phase 3 | INFR-02 |
| Data folder validation and scan | Phase 3 | INTV-03 |
| Business interview | Phase 3 | INTV-01, INTV-02, INTV-04, INTV-05 |
| ML problem type detection | Phase 3 | INTV-02 |
| Planning artifact generation | Phase 2 | PLAN-01–04 |
| Business Understanding notebook | Phase 4 | BU-01–05 |
| Data Understanding notebook | Phase 5 | EDA-01–10 |

---

## Workflow

### Step 1 — Detect existing project

Check if `.planning/STATE.md` already exists. If it does, display:

```
A DoML project already exists in this directory.

Current status: [status from STATE.md]

To continue where you left off, run /doml-progress.
To re-run the kickoff interview, delete .planning/ and try again.
```

Then stop.

### Step 2 — Docker environment setup

Check whether a JupyterLab Docker environment is already configured and running. All Python analysis runs inside the container — no local Python is assumed on the host machine.

**Detection check:**

Use the Bash tool to check whether `docker-compose.yml` exists in the project root AND references a `jupyter` service with the DoML volume layout:

```bash
test -f docker-compose.yml && grep -q "jupyter" docker-compose.yml && grep -q "/home/jovyan/work" docker-compose.yml
```

**If the check passes (matching setup found):**

Display:
```
Docker environment detected — using existing docker-compose.yml
```

Verify the container is running:
```bash
docker compose ps --services --filter status=running 2>/dev/null | grep -q jupyter
```

If not running, start it:
```bash
docker compose up -d
```

Wait up to 15 seconds for the container to be ready, then proceed to Step 3.

**If the check fails (no matching setup):**

Ask using AskUserQuestion:
"No Docker environment found. Set up JupyterLab with Python, R, and DuckDB? [yes/no]"

If yes:
1. Copy the three DoML Docker templates into the project root (read each source first, then write to destination). Do not overwrite files that already exist:
   - `.claude/doml/templates/docker-compose.yml` → `./docker-compose.yml`
   - `.claude/doml/templates/Dockerfile` → `./Dockerfile`
   - `.claude/doml/templates/requirements.txt` → `./requirements.txt`
   - `.claude/doml/templates/requirements.in` → `./requirements.in`
2. Start the environment:
   ```bash
   docker compose up -d
   ```
3. Wait up to 15 seconds for the container to be ready, then proceed to Step 3.

If no:
Display:
```
Warning: Analysis phases require the Docker environment (JupyterLab with Python, R, and DuckDB).
Steps 3–5 will be skipped. You can set up the environment later by running:
  docker compose up -d
```
Then stop — do not proceed to Step 3.

### Step 3 — Data folder validation and scan

Run a DuckDB scan of `data/raw/` to detect file formats and display schema context before the interview begins. The scan runs **inside the container** — no local Python required on the host.

**Implementation:**

Use the Bash tool to run the following inline Python via `docker compose exec`:

```bash
docker compose exec jupyter python -c "
import duckdb, json, os
from pathlib import Path

data_dir = Path('/home/jovyan/work/data/raw')

# Validate directory
if not data_dir.exists():
    print('\nError: data/raw/ directory not found. Create it and add at least one CSV, Parquet, or XLSX file.\n')
    raise SystemExit(1)

# Find supported files
extensions = {'.csv', '.parquet', '.xlsx', '.xls'}
files = [f for f in data_dir.iterdir() if f.suffix.lower() in extensions and not f.name.startswith('.')]

if not files:
    print('\nEMPTY_DATA_DIR\n')
    raise SystemExit(2)

# Check for unsupported .xls files
xls_files = [f for f in files if f.suffix.lower() == '.xls']
if xls_files:
    names = ', '.join(f.name for f in xls_files)
    print(f'\nError: Legacy .xls files are not supported ({names}). Convert to .xlsx or .csv first.\n')
    raise SystemExit(1)

# Scan each file with DuckDB
results = []
for f in sorted(files):
    ext = f.suffix.lower()
    fmt = ext.lstrip('.')
    if fmt == 'parquet':
        rel = f'read_parquet(\"{f}\")'
    elif fmt == 'xlsx':
        rel = f'read_xlsx(\"{f}\")'  # requires duckdb spatial or xlsx extension
    else:
        rel = f'\"{f}\"'
    try:
        con = duckdb.connect()
        row_count = con.execute(f'SELECT COUNT(*) FROM {rel}').fetchone()[0]
        cols = con.execute(f'DESCRIBE SELECT * FROM {rel}').fetchall()
        col_info = [{'name': c[0], 'dtype': c[1]} for c in cols]
        results.append({'path': str(f), 'format': fmt.upper(), 'row_count': row_count, 'col_count': len(col_info), 'columns': col_info})
        con.close()
    except Exception as e:
        print(f'Warning: Could not scan {f.name}: {e}')

# Print formatted report
print()
print('=== Data Scan: data/raw/ ===')
print()
for r in results:
    fname = Path(r['path']).name
    print(f'  {fname}  [{r[\"format\"]}]  {r[\"row_count\"]:,} rows x {r[\"col_count\"]} columns')
    for c in r['columns']:
        print(f'    {c[\"name\"]:30s}  {c[\"dtype\"]}')
    print()

# Output JSON for agent memory
print('__SCAN_JSON__')
print(json.dumps(results))
"
```

Parse the output:
- Everything before `__SCAN_JSON__` is the human-readable report — display it to the user.
- The line after `__SCAN_JSON__` is the JSON array — parse it and store as `scan_results` in memory for Step 4.

Parse the exit code:
- If exit code is **0** → scan succeeded, continue to Step 4.
- If exit code is **2** AND output contains `EMPTY_DATA_DIR` → do NOT stop. Proceed to Step 3b (acquisition loop).
- If exit code is **1** → display the error message printed by the script and STOP. Do not write any planning artifacts. Do not proceed to Step 3b or Step 4.

This applies for container not running, data/raw missing, or .xls file errors (all exit 1).

**No partial writes.** If Step 3 fails (exit code 1), Steps 3b and 4–6 do not run.

### Step 3b — Data acquisition fallback (when data/raw/ is empty)

If the Step 3 scan exits with code 2 AND output contains `EMPTY_DATA_DIR`, do NOT stop. Instead, enter the acquisition loop:

**Present AskUserQuestion:**
```
data/raw/ is empty. No datasets found.

How would you like to get your data?
  → Get data now (Kaggle or URL)
  → Add files manually
```

**If user chooses "Get data now":**

Run the full doml-get-data acquisition flow inline:
1. Ask using AskUserQuestion: "Enter your data source:"
   - For Kaggle: `kaggle owner/dataset-name` (e.g. `kaggle titanic/titanic-dataset`)
   - For URL: `url https://example.com/data.csv`
2. Parse the response as `SOURCE_TYPE` (first word) and `SOURCE_VALUE` (remainder).
3. Execute the get-data workflow steps (Steps 1–8 of @.claude/doml/workflows/get-data.md) inline.
4. After get-data completes, re-run the Step 3 DuckDB scan.
5. If scan now finds files → display the scan report and continue to Step 4.
6. If scan still finds no files → loop back to the AskUserQuestion above.

**If user chooses "Add files manually":**

Display:
```
Add your dataset files to the ./data/raw/ directory on your host machine.

Supported formats: CSV (.csv), TSV (.tsv), Parquet (.parquet), Excel (.xlsx)
Note: Legacy .xls files are not supported — convert to .xlsx or .csv first.

Docker mounts data/raw/ automatically — no container restart needed after adding files.
```

Then ask using AskUserQuestion:
```
I've added my files to data/raw/ — continue
```

After the user confirms, re-run the Step 3 DuckDB scan.
- If scan finds files → display the scan report and continue to Step 4.
- If scan still finds no files → loop back to the top AskUserQuestion ("Get data now" / "Add files manually").

**What still stops with an error (unchanged):**
- `data/raw/` directory does not exist → stop with error (exit code 1)
- `.xls` files found → stop with format error (exit code 1)
- Container not running → stop with error (exit code 1)

### Step 4 — Kickoff interview

Conduct the guided business context interview. Collect all answers before writing any files. Write PROJECT.md and config.json atomically after the user confirms the decision framing sentence.

**Before asking questions**, confirm the scan report from Step 2 is visible to the user (it was printed above). The column names and file shapes help the user answer questions accurately.

**Question sequence (INTV-01, INTV-02, INTV-04, INTV-05):**

Pose each question using AskUserQuestion. After each response, check: if the response is empty or whitespace-only, retry once with the same question. If still empty, ask the user to type their answer in plain text.

**Q1 — Business question (INTV-01)**
"What business decision or action will this analysis inform? (Describe what you want to know or do.)"

Store as `q1_business_question`.

**Q2 — Stakeholder (INTV-01)**
"Who is the stakeholder — who will act on the findings? (A person, team, or role.)"

Store as `q2_stakeholder`.

**Q3 — Expected outcome (INTV-01)**
"What does success look like for them? What will they do differently after seeing the results?"

Store as `q3_expected_outcome`.

**Q4 — Dataset description (INTV-01)**
"Describe the dataset: what does each row represent? (Reference the column names shown above if helpful.)"

Store as `q4_dataset_description`.

**Q5 — Time factor (INTV-02)**
"Is time a relevant dimension in this data? For example: does the order of rows matter, are there timestamps you want to use as a sequence, or do you need to forecast future values? (yes / no)"

Set `time_factor = True` if the user answers yes or describes temporal ordering. Store the user's explanation as `q5_time_explanation`.

**Problem type inference (INTV-04)**

After Q1–Q5, infer the ML problem type from the answers collected. Use this heuristic:
- Predict a continuous value → `regression`
- Predict a category or yes/no outcome → `classification`
- Discover natural groups, no known labels → `clustering`
- Ordered time observations + forecasting → `time_series` (especially if time_factor=True)
- Reduce features or visualize high-dimensional data → `dimensionality_reduction`

Explain your reasoning to the user, then ask using AskUserQuestion:
"Based on your description, this looks like a **[inferred_type]** problem — [one-sentence reasoning].
Does that match your understanding, or should I reconsider?
  → Yes, that's right
  → Actually, it's [other type] — [brief reason]
  → I'm not sure — let's discuss"

Accept the user's correction if they provide one. Store the confirmed type as `problem_type`.

**Time-factor upgrade check (Pitfall 4):**
If `time_factor=True` AND `problem_type="regression"`, ask using AskUserQuestion:
"Since time is a factor and you're predicting a continuous value over time, this is typically treated as a **time series** problem rather than cross-sectional regression. Does that apply here? (yes / no)"
If yes, change `problem_type` to `"time_series"`.

**Q6 — Domain research offer (Decision 1)**
Ask using AskUserQuestion:
"I can look up common success metrics, known data pitfalls, and standard ML approaches for your domain. Would you like me to do a brief domain research step? (yes / no)"

If yes: Research the domain described in Q1–Q4 using your training knowledge. Summarize: (a) 2–3 typical success metrics for this problem type in this domain, (b) 2–3 known data pitfalls in this domain, (c) the standard ML approach. Store this summary as `domain_research_summary`.

If no: Set `domain_research_summary = None`.

**Q7 — Language preference (INTV-05)**
Ask using AskUserQuestion:
"Python (default) or R for this project's notebooks? Press Enter for Python."

Default to `"python"` if the user presses Enter or responds with anything other than "r" or "R".
Set `analysis_language = "python"` or `"r"`.

**Decision framing sentence (INTV-04)**

Draft the framing sentence from the collected answers:

For supervised problems:
  "We are trying to [decision: what the stakeholder will do] using [metric/target column] as a proxy."

For unsupervised problems (clustering, dimensionality_reduction):
  "We are trying to [decision] — unsupervised, no proxy variable."

The target column should be inferred from `scan_results` column names based on the business question context. If ambiguous, use "the target variable" as a placeholder.

Show the drafted sentence to the user via AskUserQuestion:
"Here is the decision framing for this project:

  > [drafted framing sentence]

Does this capture the goal accurately? (confirm / revise)"

If the user asks to revise, incorporate their feedback and show the revised sentence. Repeat until confirmed.
Store the confirmed sentence as `framing_sentence`.

**Atomic write — PROJECT.md (Decision 2, Pitfall 3):**

Only after the framing sentence is confirmed, fill in `.planning/PROJECT.md`. Use the Edit tool to replace each placeholder:

| Placeholder in template | Replace with |
|-------------------------|--------------|
| `PROJECT_NAME` (frontmatter and heading) | directory name (basename of working directory) |
| `YYYY-MM-DD` (created) | today's date (ISO 8601) |
| `YYYY-MM-DD` (last_updated) | today's date (ISO 8601) |
| `DATASET_FILE_OR_FOLDER` | filenames from `scan_results` (comma-separated if multiple) |
| `problem_type: unknown` | `problem_type: [confirmed problem_type]` |
| `language: python` | `language: [analysis_language]` |
| `[What decision or action will this analysis inform?]` | `q1_business_question` |
| `[Who will act on the findings from this analysis?]` | `q2_stakeholder` |
| `[What does success look like? What will the stakeholder do differently after seeing results?]` | `q3_expected_outcome` |
| `[Brief description of what the data represents]` | `q4_dataset_description` |
| `[Date range or recency of data]` | leave as-is (unknown at this stage) |
| `[Any known issues with data quality, coverage, or representativeness]` | leave as-is (unknown at this stage) |
| `[regression / classification / clustering / time_series / dimensionality_reduction]` | confirmed `problem_type` |
| `[Column name, or "none" for unsupervised]` | best guess from `scan_results` column names, or `"unknown"` |
| `[List of columns expected to be predictive, if known]` | leave as-is |
| `[Yes / No — Is time a relevant dimension in this dataset?]` | "Yes" or "No" + `q5_time_explanation` |
| `We are trying to [decision] using [metric/outcome column] as a proxy.` | `framing_sentence` |
| `Python (default) / R (opt-in)` | `[analysis_language title-cased]` |
| `[Why this preference was selected, if non-default]` | "User default" for python; user's stated reason for R |

Also replace `DATASET_FILE` in the `**Source:** data/raw/DATASET_FILE` line with the primary filename from `scan_results`.

If `domain_research_summary` is not None, append a new subsection immediately after the Decision Framing line in PROJECT.md:

```
**Domain research summary:**
[domain_research_summary text here]
```

**Atomic write — config.json (INTV-05, Pitfall 3):**

After PROJECT.md is written, update `.planning/config.json` using the Edit tool. Read the full current config.json first, then modify these specific keys and write the complete updated JSON:

- `"analysis_language"`: add this key (or update if present) — set to `"python"` or `"r"`
- `"problem_type"`: set to confirmed problem type string
- `"time_factor"`: set to `true` or `false`
- `"dataset.format"`: set `dataset.format` to primary format from `scan_results` (first file's format, lowercase: `"csv"`, `"parquet"`, or `"xlsx"`)
- `"last_updated"`: set to today's date (ISO 8601)

Do not change any other config.json fields. Do not write a partially-updated config — read the full current config.json, modify the specific keys, then write the complete updated JSON.

**No partial writes (Pitfall 3):** If the interview is interrupted before the framing sentence is confirmed, do not write PROJECT.md or config.json. The templates remain in their initial state, which is safe for downstream phases.

### Step 5 — Generate planning artifacts

Read templates from `.claude/doml/templates/`:
- `PROJECT.md` → `.planning/PROJECT.md`
- `ROADMAP.md` → `.planning/ROADMAP.md`
- `STATE.md` → `.planning/STATE.md`
- `config.json` → `.planning/config.json`

Create `.planning/` directory if it does not exist.
Write each template file. Do not overwrite existing files — skip with a warning if already present.

### Step 6 — Display summary

```
DoML project initialized.

Created:
  .planning/PROJECT.md   — fill in your business context
  .planning/ROADMAP.md   — analysis phase roadmap
  .planning/STATE.md     — session continuity state
  .planning/config.json  — project preferences

Next: Run /doml-new-project after Phase 3 is implemented for the full interview,
      or edit .planning/PROJECT.md manually and run /doml-progress.
```
