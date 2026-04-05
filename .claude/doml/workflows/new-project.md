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

### Step 2 — Data folder validation *(implemented in Phase 3)*

> Phase 3 implements: check that `data/` exists and contains at least one supported file
> (CSV, Parquet, .xls/.xlsx). Uses DuckDB schema introspection to detect format.
> Produces clear error if empty.

**Phase 2 stub:** Check that `data/raw/` exists. If not, display:

```
data/raw/ not found.

Create the directory and copy your dataset files into data/raw/ before running /doml-new-project.
Supported formats: CSV, Parquet, Excel (.xls, .xlsx)
```

Then stop.

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
