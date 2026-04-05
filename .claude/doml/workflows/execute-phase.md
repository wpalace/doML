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

### Step 2 — Find PLAN.md

Determine target phase (from argument or STATE.md `current_focus`).
Look for `.planning/phases/[N]-*/[N]-*-PLAN.md`.

If no PLAN.md found:

```
No plan found for Phase [N]. Run /doml-plan-phase [N] first.
```

Stop.

### Step 3 — Route to phase executor *(DoML Phases 4–5 implement these)*

| Phase | Executor | Notebook | Report |
|-------|----------|----------|--------|
| 1 — Business Understanding | DoML Phase 4 | notebooks/01_business_understanding.ipynb | reports/business_summary.html |
| 2 — Data Understanding | DoML Phase 5 | notebooks/02_data_understanding.ipynb | reports/eda_report.html |

**Phase 2 stub:** For unimplemented phases, display:

```
Executor for Phase [N] not yet implemented.

Phase executors are added in:
  - Business Understanding (Phase 1): implemented in DoML Phase 4
  - Data Understanding (Phase 2): implemented in DoML Phase 5

The framework skeleton is ready. Full execution will be available after DoML Phase 4.
```

### Step 4 — Execute PLAN.md tasks

When a phase executor is available:
1. Read all `<task>` blocks from PLAN.md
2. Execute each task in wave order (wave 1 tasks first, then wave 2, etc.)
3. After each task, verify the `<verify><automated>` command passes
4. On verification failure, stop and report which task failed

### Step 5 — Generate HTML report

After all notebook tasks complete:

```bash
jupyter nbconvert --to html --no-input notebooks/[notebook_name].ipynb \
  --output reports/[report_name].html
```

Verify the HTML file was created. Confirm code cells are hidden (no `<div class="input">` blocks in output).

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
