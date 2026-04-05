# DoML New Project Workflow

## Purpose
Guided kickoff for a new DoML analysis project: interview → Docker environment → scaffold → planning artifacts.

## Invoked by: /doml-new-project

## Implementation Status

| Step | Implemented | Phase |
|------|-------------|-------|
| Data folder validation | Phase 3 | INTV-03 |
| Business interview | Phase 3 | INTV-01, INTV-02, INTV-04, INTV-05 |
| ML problem type detection | Phase 3 | INTV-02 |
| Planning artifact generation | Phase 2 | PLAN-01–04 |
| Docker template output | Phase 1 (templates exist) | INFR-02 |
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

### Step 2 — Data folder validation and scan

Run a DuckDB scan of `data/raw/` to detect file formats and display schema context before the interview begins.

**Implementation:**

Use the Bash tool to run the following Python snippet. This calls the `doml.data_scan` module built in Phase 3 Plan 02.

```python
import os
from pathlib import Path
from doml.data_scan import scan_data_folder, format_scan_report

PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', '.'))
data_dir = PROJECT_ROOT / 'data' / 'raw'

try:
    scan_results = scan_data_folder(data_dir)
    report = format_scan_report(scan_results)
    print(report)
except ValueError as e:
    print(f"\nError: {e}\n")
    raise SystemExit(1)
```

If the scan raises ValueError (missing directory, empty directory, or .xls file), print the error message and STOP. Do not write any planning artifacts. Do not proceed to Step 3.

If the scan succeeds, display the `format_scan_report` output to the user. Store `scan_results` in memory — it will be used to auto-populate dataset fields in Step 3.

**No partial writes.** If Step 2 fails, Steps 3–5 do not run.

### Step 3 — Kickoff interview *(implemented in Phase 3)*

> Phase 3 implements: guided interview extracting business question, stakeholder, dataset
> description, expected outcome, time-factor flag, and language preference.
> Saves responses to CONTEXT.md.

**Phase 2 stub:** Display:

```
Kickoff interview not yet implemented (Phase 3).

To proceed manually, edit .planning/PROJECT.md with your project context.
```

### Step 4 — Generate planning artifacts

Read templates from `.claude/doml/templates/`:
- `PROJECT.md` → `.planning/PROJECT.md`
- `ROADMAP.md` → `.planning/ROADMAP.md`
- `STATE.md` → `.planning/STATE.md`
- `config.json` → `.planning/config.json`

Create `.planning/` directory if it does not exist.
Write each template file. Do not overwrite existing files — skip with a warning if already present.

### Step 5 — Display summary

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
