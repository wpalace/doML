# DoML Plan Phase Workflow

## Purpose
Create a detailed plan (PLAN.md) for a DoML analysis phase, specifying which notebooks to generate,
what DuckDB queries to run, what statistical tests to include, and what outputs to produce.

## Invoked by: /doml-plan-phase [phase-number]

## Implementation Status

| Step | Implemented | Phase |
|------|-------------|-------|
| Read project context (STATE.md, config.json) | Phase 2 skeleton | — |
| Business Understanding plan | Phase 4 | BU-01–05 |
| Data Understanding plan | Phase 5 | EDA-01–10 |
| Generic phase planning | Phase 2 skeleton | — |

---

## Workflow

### Step 1 — Validate project state

Read `.planning/STATE.md`. If it does not exist, display:

```
No DoML project found. Run /doml-new-project first.
```

Then stop.

### Step 2 — Determine target phase

If a phase number was passed as an argument, use it.
Otherwise, read STATE.md `current_focus` and ROADMAP.md to find the next unplanned phase.

Display: `Planning Phase [N]: [phase name]`

### Step 3 — Read project config

Read `.planning/config.json`:
- `language`: Python (default) or R
- `problem_type`: regression / classification / clustering / time_series / dimensionality_reduction / unknown
- `time_factor`: true / false (determines whether time series EDA applies in Phase 2)

### Step 4 — Route to phase-specific planner *(Phase 4–5 implement these)*

| Phase | Analysis Phase | Planner |
|-------|---------------|---------|
| 1 | Business Understanding | BU planner (DoML Phase 4) |
| 2 | Data Understanding | EDA planner (DoML Phase 5) |

**Phase 2 stub:** For unimplemented phases, display:

```
Phase [N] planner not yet implemented.

The plan for this phase will be added in:
  - Business Understanding: DoML Phase 4
  - Data Understanding: DoML Phase 5

You can create .planning/phases/[N]-[name]/[N]-01-PLAN.md manually using the
PLAN.md template at .claude/doml/templates/plan-template.md.
```

### Step 5 — Write PLAN.md

When a phase-specific planner is available, write the PLAN.md to:
`.planning/phases/[N]-[name]/[N]-01-PLAN.md`

Update STATE.md `current_focus` to reflect the new plan.

### Step 6 — Confirm

Display the path of the created PLAN.md and next action:

```
Created: .planning/phases/[N]-[name]/[N]-01-PLAN.md

Run /doml-execute-phase [N] to execute this plan.
```
