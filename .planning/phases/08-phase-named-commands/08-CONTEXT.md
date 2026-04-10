# Phase 8 Context: Phase-Named Commands

**Phase:** 8 — Phase-Named Commands
**Milestone:** 3 — Refinement
**Requirements:** CMD-10, CMD-11, CMD-12
**Date:** 2026-04-10

---

## Decisions

### Architecture — Standalone workflow files

Each new skill gets its own self-contained workflow file. The executor logic currently in
`execute-phase.md` (Steps 3a–3t) will be extracted and split into three dedicated files:

- `.claude/doml/workflows/business-understanding.md`
- `.claude/doml/workflows/data-understanding.md`
- `.claude/doml/workflows/modelling.md`

`execute-phase.md` is retired alongside the old skill files.

### Retirement — Delete old skill files

Both `.claude/skills/doml-execute-phase/` and `.claude/skills/doml-plan-phase/` skill directories
are deleted entirely. Clean break — the new phase-named commands fully replace them.

### Modelling scope — All four problem types

`doml-modelling` routes all four problem types by reading `config.json` `problem_type`:
- `regression` → preprocessing + modelling_regression.ipynb
- `classification` → preprocessing + modelling_classification.ipynb
- `clustering` → modelling_clustering.ipynb (no preprocessing step)
- `dim_reduction` → modelling_dimreduction.ipynb (no preprocessing step)

Preprocessing is included for supervised types only (regression, classification).

### Planning — Execute directly, optional --guidance

No planning step required. All three commands execute end-to-end without needing a prior
`doml-plan-phase` run.

Users can pass `--guidance "..."` to provide analyst direction that shapes how the workflow
runs (e.g., "focus on feature importance", "try polynomial features"). This mirrors the
`--direction` flag in `doml-iterate-unsupervised`. The guidance string is passed through
to the Claude interpretation cell in the notebook.

---

## New Skills to Create

| Skill | Replaces | Workflow |
|-------|----------|----------|
| `doml-business-understanding` | `doml-execute-phase 1` | `business-understanding.md` |
| `doml-data-understanding` | `doml-execute-phase 2` | `data-understanding.md` |
| `doml-modelling` | `doml-execute-phase 3` (and Phase 7 executor) | `modelling.md` |

---

## Files to Create

- `.claude/skills/doml-business-understanding/SKILL.md`
- `.claude/skills/doml-data-understanding/SKILL.md`
- `.claude/skills/doml-modelling/SKILL.md`
- `.claude/doml/workflows/business-understanding.md` (extracted from execute-phase.md Steps 3a–3f)
- `.claude/doml/workflows/data-understanding.md` (extracted from execute-phase.md Steps 3g–3m)
- `.claude/doml/workflows/modelling.md` (extracted from execute-phase.md Steps 3g–3t, Phase 7 executor)

## Files to Delete

- `.claude/skills/doml-execute-phase/SKILL.md` (and directory)
- `.claude/skills/doml-plan-phase/SKILL.md` (and directory)
- `.claude/doml/workflows/execute-phase.md`
- `.claude/doml/workflows/plan-phase.md`

## Files to Update

- `CLAUDE.md` — update command names in the DoML Framework section
- `.claude/doml/templates/CLAUDE.md` (if it exists) — same
- `.claude/doml/workflows/progress.md` — update references to new command names
- `.planning/STATE.md` — update `current_focus` and decisions list

---

## Out of Scope for Phase 8

- `doml-iterate-model` and `doml-iterate-unsupervised` — retired in Phase 11
- `doml-forecasting`, `doml-get-data`, `doml-anomaly-detection` — later phases
- New notebook templates — all templates already exist; Phase 8 is command restructure only
