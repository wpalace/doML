# Phase 3: Kickoff Interview — Research

**Researched:** 2026-04-05
**Domain:** Conversational workflow design, DuckDB file introspection, ML problem type classification
**Confidence:** HIGH

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Decision 1: Problem Type Detection**
Claude infers + user confirms. Interview asks for business question in free text. Claude infers ML problem type (regression, classification, clustering, time series, or dimensionality reduction), explains its reasoning, and asks the user to confirm or correct. If domain is recognizable, Claude offers a domain research step (user can accept or skip). Domain research summary is included in PROJECT.md Problem Framing section.

**Decision 2: Interview Output Artifact**
PROJECT.md — fill in template placeholders + add a "Problem Framing" section. Fills: business question, stakeholder, dataset description, expected outcome. Adds a dedicated Problem Framing section containing: INTV-04 framing sentence, ML problem type (confirmed), time-factor flag (yes/no + explanation), language preference (Python/R), and domain research summary (if accepted). Language preference is also written to `.planning/config.json` as `analysis_language` (INTV-05). No separate FRAMING.md. PROJECT.md is the single source of truth.

**Decision 3: Data Scan Depth and Timing**
Shape + schema only. DuckDB scans each file in `data/raw/` and surfaces file list with format, row × column count per file, and column names with inferred dtypes. No sample rows, no null counts. Scan runs before any interview questions. Output is shown at the top of the interview session.

**Decision 4: Empty /data/ Behavior**
Hard stop with a clear, actionable error message. No partial state is written. When `data/raw/` is missing, empty, or contains no supported files, workflow stops immediately with an error listing what was expected, where to put files, and supported formats. No `--skip-validation` flag. Data always required.

### Claude's Discretion

None specified — all major decisions are locked.

### Deferred Ideas (OUT OF SCOPE)

- **Synthetic data generation**: Run the kickoff interview against a generated/sample dataset before real data is available. Deferred to a future milestone.

</user_constraints>

---

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INTV-01 | Guided interview extracts: dataset description, business question, stakeholder context, and expected outcome | AskUserQuestion pattern in SKILL.md; question sequence design in Interview Workflow section |
| INTV-02 | Interview always asks whether time is a factor in the dataset (determines if forecasting phase applies) | Time-factor signal detection in ML Classification Heuristics section; must set `time_factor` in config.json |
| INTV-03 | Interview validates that `/data/` folder is populated and detects file formats (CSV, Parquet, Excel) before proceeding | DuckDB format detection section — confirmed APIs for all three formats; empty/unsupported handling documented |
| INTV-04 | Interview produces written decision framing: "We are trying to [decision] using [metric] as a proxy" | PROJECT.md template section — placeholder exists; framing sentence patterns in Code Examples |
| INTV-05 | Python is the default analysis language; interview allows user to opt into R | config.json template already has `"language": "python"`; `analysis_language` write pattern documented |

</phase_requirements>

---

## Summary

Phase 3 implements the guided kickoff interview inside the existing `/doml-new-project` command. The workflow already exists as a skeleton (`new-project.md`) with Phase 2 stubs at Steps 2 and 3. This phase replaces those stubs with real implementations: DuckDB file scanning (Step 2) and the full conversational interview (Step 3). Everything runs inside the Claude Code agent — no separate subprocess, no external API calls.

The interview pattern is well-established in the GSD codebase: `AskUserQuestion` is already declared in the `doml-new-project` SKILL.md allowed-tools list. The workflow reads user responses, Claude reasons over them, then writes two output files: a filled-in `PROJECT.md` and an updated `config.json`. No new file formats or templates are needed.

DuckDB format detection is the most technically involved part. CSV and Parquet work natively with `DESCRIBE SELECT * FROM 'file'`. Excel requires the `excel` extension (autoloads in DuckDB 1.2+), which is confirmed available in the project's pinned duckdb==1.5.1. Critical gotcha: `.xls` (legacy Excel format) is not supported by the DuckDB excel extension — only `.xlsx`. This must be documented in the error message.

**Primary recommendation:** Implement the two plans sequentially — Plan 03-02 (data scan) first, then Plan 03-01 (interview) — because the scan output is displayed at the top of the interview session and informs interview questions.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| duckdb | 1.5.1 (pinned) | File format detection + schema introspection | Already in requirements.txt; zero-copy scanning of CSV/Parquet/Excel; project convention (INFR-03) |
| AskUserQuestion (Claude Code tool) | built-in | Interactive interview questions | Already in doml-new-project SKILL.md allowed-tools; the correct mechanism for interactive workflows in Claude Code |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| duckdb excel extension | autoloaded | Read .xlsx files | INSTALL/LOAD not needed — autoloads on first `read_xlsx()` call in DuckDB 1.2+ |
| pathlib (stdlib) | — | Path resolution, file existence checks | Resolving PROJECT_ROOT and data/raw/ per REPR-02 convention |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| DuckDB schema introspection | pandas DataFrame.dtypes | pandas loads entire file into memory; DuckDB scans zero-copy — use DuckDB per project convention |
| DuckDB excel extension | openpyxl + pandas | openpyxl is not in requirements.txt; DuckDB excel autoloads without extra pip packages |
| AskUserQuestion | Plain-text numbered lists | AskUserQuestion renders a richer TUI; text_mode fallback already supported by the project's workflow config |

**Installation:** No new packages. duckdb==1.5.1 is already in `requirements.txt`. The excel extension autoloads on first use.

---

## Architecture Patterns

### Where Phase 3 Fits in the Existing Workflow

The `new-project.md` workflow file controls execution order. Phase 3 replaces exactly two stubs:

```
Step 2 — Data folder validation   ← 03-02 implements this
Step 3 — Kickoff interview         ← 03-01 implements this
Step 4 — Generate planning artifacts  (already implemented in Phase 2)
Step 5 — Display summary              (already implemented in Phase 2)
```

### Pattern 1: DuckDB File Scan (before interview)

**What:** Run DuckDB against every file in `data/raw/`. Produce a scan report showing format, row count, column names, and dtypes. Display this at the top of the interview session.

**When to use:** Always, as the first action of `/doml-new-project` (after the existing project check).

```python
# Source: duckdb official docs + DuckDB 1.5.1 behavior
import duckdb
from pathlib import Path

def scan_file(path: Path) -> dict:
    """Returns {format, row_count, columns: [{name, dtype}]} or raises."""
    con = duckdb.connect()
    suffix = path.suffix.lower()

    if suffix == ".csv":
        schema = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{path}')").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{path}')").fetchone()[0]
    elif suffix == ".parquet":
        schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{path}')").fetchone()[0]
    elif suffix == ".xlsx":
        # excel extension autoloads on first read_xlsx call (DuckDB 1.2+)
        schema = con.execute(f"DESCRIBE SELECT * FROM read_xlsx('{path}')").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM read_xlsx('{path}')").fetchone()[0]
    else:
        raise ValueError(f"Unsupported format: {suffix}")

    # DESCRIBE returns: column_name, column_type, null, key, default, extra
    columns = [{"name": row[0], "dtype": row[1]} for row in schema]
    return {"format": suffix[1:].upper(), "row_count": row_count, "columns": columns}
```

**DESCRIBE output columns** (DuckDB): `column_name`, `column_type`, `null`, `key`, `default`, `extra`
[CITED: duckdb.org/docs/stable/sql/statements/describe]

### Pattern 2: Empty /data/ Hard Stop

**What:** Check `data/raw/` before any scan. If missing, empty, or no supported files found, stop with a clear message. [VERIFIED: CONTEXT.md Decision 4]

```
Error: No data files found in data/raw/

Expected at least one file in supported formats:
  - CSV (.csv)
  - Parquet (.parquet)
  - Excel (.xlsx)

Note: Legacy .xls format is not supported. Save as .xlsx first.

Add your dataset files to data/raw/ and run /doml-new-project again.
```

### Pattern 3: AskUserQuestion Interview Flow

**What:** Use `AskUserQuestion` for each interview question. Claude reasons over the answer before asking the next one. This produces a natural conversation, not a static form.

**When to use:** For all user-facing questions in the interview workflow.

```
# Pattern from gsd-discuss-phase (verified in .claude/skills/gsd-discuss-phase/SKILL.md)
# AskUserQuestion is declared in allowed-tools — Claude Code renders a TUI prompt.
# text_mode fallback: if workflow.text_mode is true, present as numbered list instead.
```

The `doml-new-project` SKILL.md already has `AskUserQuestion` in `allowed-tools`. No change needed to the skill file. [VERIFIED: .claude/skills/doml-new-project/SKILL.md]

### Pattern 4: Interview Question Sequence

Questions are asked in this order. The DuckDB scan output is shown FIRST (before any question), so users can reference column names when answering.

| # | Question | Purpose | Maps to |
|---|----------|---------|---------|
| 0 | *(DuckDB scan display — not a question)* | Ground the user with schema context | INTV-03 |
| 1 | What business decision or action will this analysis inform? | Core problem framing | INTV-01, INTV-04 |
| 2 | Who is the stakeholder — who will act on the findings? | Audience + communication style | INTV-01 |
| 3 | What does success look like for them? | Expected outcome | INTV-01 |
| 4 | Describe the dataset — what does each row represent? | Dataset context | INTV-01 |
| 5 | Is time a relevant factor? (Does order/sequence matter? Do you need forecasts?) | Time-factor flag | INTV-02 |
| 6 | *(Claude infers ML type, explains reasoning, asks to confirm or correct)* | Problem type | INTV-04 |
| 7 | *(Claude offers domain research — user accepts or skips)* | Domain grounding | Decision 1 |
| 8 | Python (default) or R for notebooks? | Language preference | INTV-05 |

### Pattern 5: Writing Interview Output

After the interview, two files are updated:

**`.planning/config.json`** — update `analysis_language` field:
```json
{
  "language": "python",        // existing field (set at init)
  "analysis_language": "python",  // INTV-05: set by interview
  "problem_type": "classification",
  "time_factor": false,
  "dataset": {
    "path": "data/raw/",
    "format": "csv",
    "target_column": null
  }
}
```

**`.planning/PROJECT.md`** — fill template placeholders AND add Problem Framing section. The template (Phase 2) already has the right structure. Use `Edit` tool to fill each `[placeholder]` in place.

### Anti-Patterns to Avoid

- **Don't run the interview before the scan.** The schema display grounds the user — skipping it makes business questions harder to answer (e.g., user doesn't know if there's a date column).
- **Don't write partial state.** If the interview is interrupted or fails, do not write a partially-filled PROJECT.md. Write only when the full interview is complete.
- **Don't hardcode paths.** All path references must use the PROJECT_ROOT convention (REPR-02). Prefer `Path(os.environ.get('PROJECT_ROOT', '.')) / 'data' / 'raw'`.
- **Don't ask for sample rows.** Sample rows belong in the EDA phase, not the kickoff scan (Decision 3).
- **Don't use pandas for the file scan.** DuckDB is the project convention for all file introspection.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV type detection | Custom delimiter/dtype sniffer | `read_csv_auto()` | DuckDB handles delimiter, quoting, encoding, and type inference automatically |
| Parquet schema reading | pyarrow schema parsing | `DESCRIBE SELECT * FROM read_parquet(...)` | Zero-copy; consistent API across all three formats |
| Excel file reading | openpyxl sheet iteration | `read_xlsx()` via DuckDB excel extension | Autoloads; no extra pip install; consistent with project DuckDB-first convention |
| Interactive question prompts | Custom stdin input loop | `AskUserQuestion` tool | Already in SKILL.md allowed-tools; renders TUI; handles text_mode fallback |
| Problem type routing | Giant if/else string match | Claude inference + user confirm | More robust than keyword matching; educational for user; covers edge cases |

**Key insight:** All three file formats (CSV, Parquet, Excel) can be inspected with the same `DESCRIBE SELECT * FROM <reader_fn>(path)` pattern. Write one inspection loop, branch only on file extension to choose the reader function.

---

## DuckDB Format Detection Details

### CSV

```python
# Source: DuckDB 1.5.1 — read_csv_auto is an alias for read_csv with auto_detect=True
con.execute("DESCRIBE SELECT * FROM read_csv_auto('/path/to/file.csv')")
# Returns: [(column_name, column_type, null, key, default, extra), ...]
```

`read_csv_auto` detects: delimiter, quote character, header row, and column types. Types default to: NULL > BOOLEAN > TIME > DATE > TIMESTAMP > BIGINT > DOUBLE > VARCHAR (fallback). [CITED: duckdb.org/docs/current/data/csv/auto_detection]

### Parquet

```python
# Source: DuckDB 1.5.1 native support — no extension needed
con.execute("DESCRIBE SELECT * FROM read_parquet('/path/to/file.parquet')")
```

Parquet is a first-class format in DuckDB. No extension required. Schema is read from Parquet metadata directly. [ASSUMED — no official doc page fetched but supported by web search evidence]

### Excel (.xlsx only)

```python
# Source: DuckDB excel extension — autoloads on first use (DuckDB 1.2+)
# DuckDB 1.5.1 includes excel extension in core extensions repository
con.execute("DESCRIBE SELECT * FROM read_xlsx('/path/to/file.xlsx')")
```

**Critical: `.xls` is NOT supported.** Only `.xlsx` works. [CITED: duckdb.org/docs/1.3/core_extensions/excel]

The excel extension autoloads on first `read_xlsx()` call — no explicit `INSTALL excel; LOAD excel;` needed in DuckDB 1.2+. [CITED: motherduck.com/blog/duckdb-excel-extension/]

Type inference for Excel: most values become DOUBLE or VARCHAR; TIMESTAMP, TIME, DATE, BOOLEAN inferred from cell format when possible. [CITED: duckdb.org/docs/1.3/core_extensions/excel]

### Error Handling for Unreadable Files

DuckDB raises a Python exception when a file cannot be read (wrong format, corrupted file, permission error). The scan loop should catch these and report clearly:

```python
try:
    result = scan_file(path)
except Exception as e:
    result = {"format": "ERROR", "error": str(e), "path": path}
```

---

## ML Problem Type Classification Heuristics

### Signal Words by Problem Type

This is training knowledge, not verifiable in code. The planner should treat these as ASSUMED patterns that Claude will apply during the interview. [ASSUMED]

| Problem Type | Signals in Business Question | Example Phrases |
|---|---|---|
| **Regression** | Predict a continuous quantity; "how much", "estimate", "forecast a value" | "predict next month's revenue", "estimate house price", "how many units will sell" |
| **Classification** | Assign to a category; "which", "will they", "yes/no", "risk" | "will this customer churn", "is this transaction fraud", "classify patient risk" |
| **Clustering** | Discover natural groups; "segment", "group", "find patterns", no known labels | "segment customers by behavior", "find similar products", "group regions by performance" |
| **Time Series** | Ordered observations over time; forecasting, trend, seasonality | "forecast demand for next quarter", "predict time to failure", "detect anomalies over time" — time-factor flag will also be set |
| **Dimensionality Reduction** | Reduce features for visualization or preprocessing; "visualize", "compress", "find structure in high-dimensional data" | "visualize how customers cluster in feature space", "identify principal factors driving variation" |

### Time Factor Signals

The time-factor question (INTV-02) should directly ask: "Is time an important dimension in this data? For example: does the order of rows matter, are there timestamps you want to use as a sequence, or do you need to forecast future values?"

A "yes" answer triggers:
- `time_factor: true` in `config.json`
- May upgrade problem type to `time_series` if not already classified that way

### Confirm-or-Correct Phrasing

After Claude infers the type, present it like this:

```
Based on your description, this looks like a **classification** problem — you want to predict
whether each customer will churn (a yes/no outcome with a known label).

Does that match your understanding, or should I reconsider?
  → Yes, that's right
  → Actually, it's [other type] — [brief reason]
  → I'm not sure — let's discuss
```

### Decision Framing Sentence (INTV-04)

The framing sentence has the form: "We are trying to [decision] using [metric/column] as a proxy."

Good examples:
- "We are trying to **predict which customers will cancel their subscription** using **churn_flag** as a proxy."
- "We are trying to **forecast monthly energy demand** using **kwh_consumption** as a proxy."
- "We are trying to **understand which customers belong to the same behavioral segment** — unsupervised, no proxy variable."

Claude should draft this sentence from the user's answers and show it to the user for confirmation before writing it to PROJECT.md.

---

## PROJECT.md Template Analysis

The template at `.claude/doml/templates/PROJECT.md` has these placeholder slots that the interview must fill: [VERIFIED: .claude/doml/templates/PROJECT.md]

| Placeholder | Source | Interview Question |
|---|---|---|
| `PROJECT_NAME` | Derived from directory name or asked | Step 4 in workflow (planning artifacts) |
| `YYYY-MM-DD` (created/updated) | Auto-populated from system date | Not asked |
| `DATASET_FILE_OR_FOLDER` | DuckDB scan results | Auto-populated |
| `problem_type: unknown` (frontmatter) | Interview + type detection | Auto-set after confirmation |
| `language: python` (frontmatter) | Language preference question | Question 8 |
| `[What decision or action will this analysis inform?]` | Business question | Question 1 |
| `[Who will act on the findings from this analysis?]` | Stakeholder | Question 2 |
| `[What does success look like?]` | Expected outcome | Question 3 |
| `[Brief description of what the data represents]` | Dataset description | Question 4 |
| `[Collection period / known biases]` | Optional — can be left with defaults | Questions 4 follow-up |
| `[regression / classification / ...]` | Problem type detection | Question 6 |
| `[Yes / No — Is time a relevant dimension?]` | Time factor | Question 5 |
| `We are trying to [decision] using [metric] as a proxy.` | Claude-drafted framing sentence | After Question 6 |
| `Python (default) / R (opt-in)` | Language preference | Question 8 |

The **Problem Framing** section already exists in the template. The interview fills it in. A domain research summary subsection can be appended conditionally if the user accepted the domain research offer.

---

## Common Pitfalls

### Pitfall 1: `.xls` Files Silently Fail or Confuse Users

**What goes wrong:** User puts a `.xls` (legacy Excel) file in `data/raw/`. The DuckDB excel extension throws an error. User sees an opaque Python exception, not a clear message.

**Why it happens:** DuckDB's excel extension only supports `.xlsx`. The `.xls` binary format (BIFF) requires a separate parser (libxls/GDAL). This is a known open issue in the duckdb-excel project.

**How to avoid:** In the supported extensions check, explicitly list `.xls` as "legacy format, not supported." The error message must say: "Save your .xls file as .xlsx (Excel 97-2003 → Excel Workbook in File → Save As) and try again."

**Warning signs:** File extension check before DuckDB call. If `suffix == '.xls'`, fail fast with the helpful message before attempting DuckDB.

### Pitfall 2: Excel Extension Not Available in Offline/Air-Gapped Environments

**What goes wrong:** `read_xlsx()` triggers autoload, which tries to fetch the extension from the DuckDB extension repository. In Docker without internet access, this fails silently or with a confusing network error.

**Why it happens:** DuckDB extension autoloading requires internet access on first use. The docker environment may not have outbound internet access.

**How to avoid:** The docker-compose.yml does not restrict network. However, if this becomes an issue, the fallback is: `INSTALL excel FROM 'community';` or pre-installing via `pip install duckdb[all]` (if available). For Milestone 1, document this as a known constraint; the Docker environment has internet access during setup.

**Warning signs:** Test `LOAD excel` explicitly at the start of the scan step and catch `ExtensionLoadException`.

### Pitfall 3: Empty CONFIG Entries After Partial Interview

**What goes wrong:** User abandons the interview partway. The workflow writes a partially-filled `PROJECT.md` with some placeholders replaced and others still `[blank]`. Downstream phases (Business Understanding) read PROJECT.md and encounter unfilled template tokens.

**Why it happens:** Writing PROJECT.md incrementally after each question.

**How to avoid:** Collect all interview answers in memory first. Write PROJECT.md as a single atomic operation after all questions are answered and the user confirms the framing sentence. If the workflow is interrupted before write, PROJECT.md stays in its template state (which is safe for downstream).

### Pitfall 4: Problem Type Misclassification With Time-Factor

**What goes wrong:** User describes a time-series problem ("forecast monthly sales") but Claude classifies it as regression. The `time_factor` flag is set to true, but `problem_type` is "regression". Downstream phases route incorrectly.

**Why it happens:** Forecasting and regression both predict continuous values; the distinction is whether time order matters.

**How to avoid:** After the user confirms the time-factor (INTV-02), if `time_factor = true` AND `problem_type = regression`, offer: "Since time is a factor and you're predicting a continuous value over time, this is typically treated as a **time series** problem rather than cross-sectional regression. Does that apply here?" Give the user the option to switch. Document this branching logic explicitly in the workflow.

### Pitfall 5: AskUserQuestion Empty Response

**What goes wrong:** `AskUserQuestion` returns an empty or whitespace-only string. The workflow proceeds with a blank answer, producing a PROJECT.md with empty fields.

**Why it happens:** Tool invocation edge cases, or user dismisses the prompt.

**How to avoid:** After every `AskUserQuestion` call, check if the response is empty or whitespace-only. If so, retry once. If still empty, fall back to plain-text prompt asking the user to type their answer. This pattern is documented in the GSD discuss-phase workflow. [VERIFIED: .claude/get-shit-done/workflows/discuss-phase.md lines 109-125]

---

## Code Examples

### Complete Scan Loop

```python
# Source: DuckDB 1.5.1 + official DuckDB docs pattern
import duckdb
import os
from pathlib import Path

SUPPORTED = {'.csv', '.parquet', '.xlsx'}
UNSUPPORTED_LEGACY = {'.xls'}

def scan_data_folder(data_dir: Path) -> list[dict]:
    """
    Scans data/raw/ and returns a list of file scan results.
    Raises ValueError if data_dir is missing, empty, or has no supported files.
    """
    if not data_dir.exists():
        raise ValueError(f"data/raw/ directory not found at {data_dir}")

    all_files = list(data_dir.iterdir())
    if not all_files:
        raise ValueError("data/raw/ is empty")

    legacy = [f for f in all_files if f.suffix.lower() in UNSUPPORTED_LEGACY]
    supported = [f for f in all_files if f.suffix.lower() in SUPPORTED]

    if not supported:
        msg = "No supported files found in data/raw/\n"
        if legacy:
            msg += f"Found legacy .xls files: {[f.name for f in legacy]}\n"
            msg += "Save .xls files as .xlsx (File > Save As > Excel Workbook) and try again.\n"
        msg += "Supported formats: CSV (.csv), Parquet (.parquet), Excel (.xlsx)"
        raise ValueError(msg)

    con = duckdb.connect()
    results = []
    for path in sorted(supported):
        try:
            results.append(_scan_one_file(con, path))
        except Exception as e:
            results.append({"file": path.name, "format": "ERROR", "error": str(e)})
    return results

def _scan_one_file(con, path: Path) -> dict:
    suffix = path.suffix.lower()
    reader = {
        '.csv': f"read_csv_auto('{path}')",
        '.parquet': f"read_parquet('{path}')",
        '.xlsx': f"read_xlsx('{path}')",
    }[suffix]

    schema = con.execute(f"DESCRIBE SELECT * FROM {reader}").fetchall()
    row_count = con.execute(f"SELECT COUNT(*) FROM {reader}").fetchone()[0]
    # DESCRIBE columns: column_name, column_type, null, key, default, extra
    columns = [{"name": row[0], "dtype": row[1]} for row in schema]

    return {
        "file": path.name,
        "format": suffix[1:].upper(),
        "rows": row_count,
        "cols": len(columns),
        "columns": columns,
    }
```

### Scan Display Format

```
Data files found in data/raw/

  sales_data.csv        CSV      45,231 rows × 12 cols
    columns: order_id (INTEGER), order_date (DATE), customer_id (VARCHAR),
             product_id (VARCHAR), quantity (INTEGER), revenue (DOUBLE), ...

  customers.parquet     Parquet   8,402 rows × 7 cols
    columns: customer_id (VARCHAR), region (VARCHAR), signup_date (DATE), ...
```

### config.json Write Pattern

```python
import json
from pathlib import Path

def update_config(planning_dir: Path, updates: dict):
    config_path = planning_dir / "config.json"
    config = json.loads(config_path.read_text())
    config.update(updates)
    config["last_updated"] = "2026-04-05"  # use actual date
    config_path.write_text(json.dumps(config, indent=2))

# After interview:
update_config(Path(".planning"), {
    "analysis_language": "python",  # or "r"
    "language": "python",           # keep in sync — progress.md reads "language"
    "problem_type": "classification",
    "time_factor": False,
    "dataset": {
        "path": "data/raw/",
        "format": "csv",
        "target_column": None
    }
})
```

---

## Workflow File Implementation Guide

The workflow lives at `.claude/doml/workflows/new-project.md`. Phase 3 replaces the Step 2 and Step 3 stubs. The replacement content should follow this structure:

### Step 2 Replacement (Data Folder Validation)

```markdown
### Step 2 — Data folder validation

Run DuckDB schema introspection on all files in data/raw/.

1. Check if data/raw/ directory exists — hard stop with error if missing.
2. List files in data/raw/. Hard stop with error if empty.
3. Check for .xls files — mention conversion requirement in error if any found.
4. For each supported file (.csv, .parquet, .xlsx):
   - DESCRIBE SELECT * FROM <reader>(path) — get column names and types
   - SELECT COUNT(*) FROM <reader>(path) — get row count
   - Catch errors per file; report which files failed to scan
5. Hard stop if zero files scanned successfully.
6. Display scan results at the top of the session (format shown in Code Examples).
```

### Step 3 Replacement (Interview)

```markdown
### Step 3 — Kickoff interview

Use AskUserQuestion for each question. Collect all answers before writing any files.

[Question sequence as documented in Architecture Patterns → Pattern 4]

After all answers collected and user confirms the decision framing sentence:
- Write filled-in PROJECT.md (single atomic write using Edit or Write tool)
- Update config.json with language, problem_type, time_factor, dataset info
- Display confirmation: "Interview complete. PROJECT.md updated."
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| `read_excel` via openpyxl/pandas | DuckDB `read_xlsx()` via excel extension | DuckDB 1.2 (2025) | No extra pip packages needed |
| `read_csv_auto` (older alias) | `read_csv` with `auto_detect=True` (or alias still works) | DuckDB 1.0+ | `read_csv_auto` still works in 1.5.1 as alias |
| Manual `INSTALL excel; LOAD excel;` | Autoloads on first `read_xlsx()` call | DuckDB 1.2+ | Simpler setup — no explicit install step |
| Separate FRAMING.md | Problem Framing section in PROJECT.md | Decision 2 | Single source of truth; fewer files |

**Deprecated/outdated:**
- `read_csv_auto` as distinct function: still works as an alias in DuckDB 1.5.1, but canonical name is now `read_csv` with `auto_detect=True`. Using either is fine.
- Spatial extension for Excel: some older DuckDB guides suggest using the spatial extension for `st_read()` to read Excel. This is incorrect for modern DuckDB — the excel extension is the correct path.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Parquet is a first-class DuckDB format requiring no extension | DuckDB Format Detection Details | Low — Parquet support is core to DuckDB's value proposition; extremely unlikely to change |
| A2 | DuckDB excel extension autoloads without internet issues inside the project's Docker environment | Pitfall 2 | Medium — if Docker has no outbound internet, first `read_xlsx()` call will fail; easy to detect in testing |
| A3 | ML problem type signal words (regression, classification, etc.) are reliable heuristics | ML Problem Type Classification Heuristics | Low — Claude inference with user confirmation provides a human check on any misclassification |

---

## Open Questions

1. **Does the Docker environment have internet access for excel extension autoload?**
   - What we know: docker-compose.yml does not restrict networking; extension autoloads in DuckDB 1.2+
   - What's unclear: Whether the JupyterLab container can reach the DuckDB extension repository
   - Recommendation: Add a test in the workflow that catches extension load failure and surfaces a clear error; not a blocker for plan writing

2. **Should the interview ask about the target column name explicitly?**
   - What we know: `config.json` template has `"target_column": null`; INTV-01 requires "dataset description"
   - What's unclear: Whether asking for target column during kickoff is premature (user may not know column names yet before seeing the scan output)
   - Recommendation: Show scan output (column names visible) and then optionally ask "which column are you trying to predict?" — soft question, user can answer "not sure yet"

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | DuckDB scan script | Yes (host: 3.12, Docker: 3.13) | 3.12/3.13 | — |
| duckdb Python package | File format detection | Yes (in requirements.txt) | 1.5.1 | — |
| DuckDB excel extension | .xlsx reading | Yes (autoloads from DuckDB 1.2+; included in 1.5.1 distribution) | bundled | Pre-install: `INSTALL excel;` if autoload fails |
| pathlib | Path resolution | Yes (stdlib) | 3.4+ | — |
| AskUserQuestion tool | Interview questions | Yes (declared in SKILL.md allowed-tools) | built-in | text_mode fallback (numbered lists) |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:**
- DuckDB excel extension: if autoload fails in offline Docker, run `INSTALL excel FROM 'community';` once during container setup or add to Dockerfile.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (via requirements.txt — not yet pinned; needs Wave 0) |
| Config file | none — see Wave 0 |
| Quick run command | `pytest tests/test_data_scan.py -x` |
| Full suite command | `pytest tests/ -x` |

Note: pytest is not in the current `requirements.txt` or `requirements.in`. Wave 0 must add it.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INTV-03 | CSV file detected + schema returned | unit | `pytest tests/test_data_scan.py::test_csv_scan -x` | Wave 0 |
| INTV-03 | Parquet file detected + schema returned | unit | `pytest tests/test_data_scan.py::test_parquet_scan -x` | Wave 0 |
| INTV-03 | XLSX file detected + schema returned | unit | `pytest tests/test_data_scan.py::test_xlsx_scan -x` | Wave 0 |
| INTV-03 | Empty data/raw/ → hard stop error | unit | `pytest tests/test_data_scan.py::test_empty_dir_raises -x` | Wave 0 |
| INTV-03 | Missing data/raw/ → hard stop error | unit | `pytest tests/test_data_scan.py::test_missing_dir_raises -x` | Wave 0 |
| INTV-03 | Legacy .xls file → clear error message | unit | `pytest tests/test_data_scan.py::test_xls_not_supported -x` | Wave 0 |
| INTV-04 | Framing sentence written to PROJECT.md | unit | `pytest tests/test_project_output.py::test_framing_written -x` | Wave 0 |
| INTV-05 | config.json `analysis_language` set after interview | unit | `pytest tests/test_project_output.py::test_language_written -x` | Wave 0 |
| INTV-01, INTV-02 | Full interview → PROJECT.md contains all required sections | integration | `pytest tests/test_interview_workflow.py -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_data_scan.py -x` (scan unit tests only, fast)
- **Per wave merge:** `pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_data_scan.py` — covers INTV-03 (scan, empty, missing, xls, xlsx, parquet, csv)
- [ ] `tests/test_project_output.py` — covers INTV-04, INTV-05 (output file content verification)
- [ ] `tests/test_interview_workflow.py` — covers INTV-01, INTV-02 (end-to-end interview mock)
- [ ] `tests/fixtures/` — sample CSV, Parquet, and XLSX files for test scans
- [ ] Framework install: `pip install pytest` + add `pytest` to `requirements.in` then `pip-compile`

---

## Project Constraints (from CLAUDE.md)

| Constraint | Directive | Impact on Phase 3 |
|---|---|---|
| REPR-02 | All file paths resolved from PROJECT_ROOT env var — no hardcoded absolute paths | Scan loop must use `Path(os.environ.get('PROJECT_ROOT', '.'))` as base |
| INFR-05 | data/raw/ is read-only mounted in Docker | Scan code must never write to data/raw/ |
| DuckDB first | For any tabular profiling or aggregation, prefer DuckDB over pandas when input is on disk | Use DuckDB for all file scanning — not pandas, not pyarrow |
| REPR-04 | requirements.txt pins every package with == | pytest and any test fixtures must go through requirements.in → pip-compile pipeline |
| REPR-03 | nbstripout pre-commit hook active | Not relevant to Phase 3 (no notebooks) |
| No AutoML | Never use AutoML tools that hide decision trail | ML problem type classification uses Claude inference + user confirmation, not AutoML |

---

## Sources

### Primary (HIGH confidence)
- `.claude/doml/workflows/new-project.md` — existing stub structure showing exactly what Phase 3 replaces
- `.claude/skills/doml-new-project/SKILL.md` — confirmed AskUserQuestion in allowed-tools
- `.claude/doml/templates/PROJECT.md` — confirmed template structure and all placeholder slots
- `.claude/doml/templates/config.json` — confirmed `analysis_language` field and surrounding structure
- `.planning/phases/03-kickoff-interview/03-CONTEXT.md` — locked decisions (all four)
- `requirements.txt` — confirmed duckdb==1.5.1 is pinned
- [duckdb.org/docs/1.3/core_extensions/excel](https://duckdb.org/docs/1.3/core_extensions/excel) — confirmed .xls not supported; confirmed autoload; confirmed read_xlsx parameters
- [motherduck.com/blog/duckdb-excel-extension/](https://motherduck.com/blog/duckdb-excel-extension/) — confirmed INSTALL/LOAD pattern; autoload behavior; all_varchar gotcha

### Secondary (MEDIUM confidence)
- [duckdb.org/docs/current/data/csv/auto_detection](https://duckdb.org/docs/current/data/csv/auto_detection) — CSV type detection priority order
- GSD discuss-phase workflow (lines 109-125) — AskUserQuestion empty response handling pattern

### Tertiary (LOW confidence)
- ML problem type signal words (regression/classification/clustering/time series/dimensionality reduction heuristics) — training knowledge; marked [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — duckdb version verified from requirements.txt; AskUserQuestion verified in SKILL.md
- Architecture patterns: HIGH — workflow stub structure verified from new-project.md; template slots verified
- DuckDB format detection: HIGH — official DuckDB docs fetched; .xls limitation confirmed
- ML classification heuristics: LOW — training knowledge only; user confirmation step mitigates risk
- Pitfalls: MEDIUM — most verified through official docs or source inspection; Pitfall 2 (offline Docker) is ASSUMED

**Research date:** 2026-04-05
**Valid until:** 2026-07-05 (DuckDB API is stable; excel extension autoload behavior locked since 1.2)
