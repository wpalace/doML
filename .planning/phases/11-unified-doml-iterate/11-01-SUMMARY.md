---
phase: 11-unified-doml-iterate
plan: "01"
subsystem: doml-iterate
tags: [skill, workflow, iteration, supervised, unsupervised, unified]
one-liner: "Unified /doml-iterate skill + 11-step iterate.md workflow covering all four problem types with regex-first direction parsing, versioned HTML reports, and append-only leaderboard"
dependency-graph:
  requires:
    - iterate-unsupervised.md (unsupervised pipeline reference — copied verbatim)
    - modelling.md (HTML report nbconvert pattern — Steps 6b-6e)
    - .planning/config.json (problem_type routing)
  provides:
    - .claude/skills/doml-iterate/SKILL.md (unified command entry point)
    - .claude/doml/workflows/iterate.md (full 11-step workflow)
  affects:
    - All four problem types: regression, classification, clustering, dimensionality_reduction
    - reports/ (versioned HTML reports for every iteration of every type)
    - models/leaderboard.csv + models/unsupervised_leaderboard.csv (append-only)
tech-stack:
  added: []
  patterns:
    - regex-first direction parsing with Claude natural language fallback (D-03)
    - sys.argv[1] for direction string injection prevention (T-11-01)
    - nbformat API for all cell modifications (no shell interpolation)
    - versioned notebook + HTML report naming (vN suffix)
    - problem_type routing from config.json (D-04)
key-files:
  created:
    - .claude/skills/doml-iterate/SKILL.md
    - .claude/doml/workflows/iterate.md
  modified: []
decisions:
  - "D-01: Direction is positional bare string — /doml-iterate \"direction\" — not --direction flag"
  - "D-02: All four problem types produce versioned HTML reports (model_report_vN, clustering_report_vN, dimreduction_report_vN)"
  - "D-03: Supervised direction parsing is regex-first (model focus, Optuna trials, hyperparameter overrides, feature engineering) with Claude fallback for unrecognised patterns"
  - "D-04: Unified routing — regression/classification to supervised pipeline; clustering/dimensionality_reduction to unsupervised pipeline; unknown type → clear error"
  - "D-05: Unsupervised modify script copied verbatim from iterate-unsupervised.md Step 6"
key-decisions:
  - "Unified /doml-iterate replaces both /doml-iterate-model (stub) and /doml-iterate-unsupervised"
  - "Direction string only reaches notebook via sys.argv[1] — never shell-interpolated (injection prevention)"
  - "Supervised timeout 1200s vs unsupervised 900s (no Optuna in unsupervised)"
  - "All four problem types produce versioned HTML reports via nbconvert --no-input"
metrics:
  duration: "~15 minutes"
  completed: "2026-04-11"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 11 Plan 01: Unified doml-iterate Skill + Workflow Summary

Unified `/doml-iterate` skill entry point and complete 11-step `iterate.md` workflow covering all four problem types (regression, classification, clustering, dimensionality_reduction) with full supervised iteration path implemented to match the unsupervised reference.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create .claude/skills/doml-iterate/SKILL.md | 7cc8cef | .claude/skills/doml-iterate/SKILL.md |
| 2 | Create .claude/doml/workflows/iterate.md — unified 10-step workflow | 246f405 | .claude/doml/workflows/iterate.md |

## What Was Built

### Task 1 — SKILL.md

`.claude/skills/doml-iterate/SKILL.md` — the Claude Code slash command entry point for `/doml-iterate`. Follows the established DoML skill pattern (anomaly-detection, iterate-unsupervised):

- Frontmatter `name: doml-iterate` with `allowed-tools` (Read, Write, Edit, Bash, Glob, Grep)
- `<objective>` covering all four problem types and the three invariants (versioned notebook, versioned HTML report, append-only leaderboard)
- `<arguments>` block documenting direction as a positional bare string with five examples spanning all problem types
- `<execution_context>` referencing `@.claude/doml/workflows/iterate.md`
- `<context>` passing `{{args}}` through

### Task 2 — iterate.md Unified Workflow

`.claude/doml/workflows/iterate.md` — 671-line unified workflow with 11 numbered steps:

**Step 1:** Config read + problem_type routing. `regression`/`classification` → `IS_SUPERVISED=true`; `clustering`/`dimensionality_reduction` → `IS_SUPERVISED=false`; unknown type → clear error listing valid values.

**Steps 2-5:** Versioned notebook discovery (glob + max version sort), prior interpretation read via nbformat API, next version increment, template copy from the appropriate template (four templates, one per problem type).

**Step 6:** Direction-based cell modification — two separate Python scripts:
- `doml_modify_unsupervised_notebook.py`: copied verbatim from iterate-unsupervised.md Step 6; handles k=N, eps=N, n_neighbors=N, n_components=N overrides
- `doml_modify_supervised_notebook.py`: regex-first parsing for model focus (XGBoost/LightGBM/RandomForest/Ridge/Lasso/LogisticRegression), Optuna trial count (`trials=N`), hyperparameter overrides (max_depth/n_estimators/learning_rate/C/alpha), feature directives (drop, polynomial); Claude fallback cell when no regex matches

Both scripts receive direction via `sys.argv[1]` — never shell-interpolated (T-11-01 mitigation).

**Step 7:** Docker nbconvert execution — 1200s supervised (Optuna), 900s unsupervised. Container-not-running error with recovery instructions. Post-execution cell output count assertion.

**Step 8:** Leaderboard append verification — `models/leaderboard.csv` (supervised) or `models/unsupervised_leaderboard.csv` (unsupervised). Shows max iteration row.

**Step 9:** Versioned HTML report generation — `model_report_vN.html`, `clustering_report_vN.html`, `dimreduction_report_vN.html`. Executive narrative cell inserted first. nbconvert `--no-input`. Three verification checks (file exists, caveats present, code hidden).

**Step 10:** Interpretation Markdown cell appended via nbformat API — direction applied, metric delta table, assessment, next steps.

**Step 11:** Structured analyst report with metric delta table (format varies by problem type), files updated, next actions.

**Anti-patterns section** explicitly prohibits shell interpolation of direction string, leaderboard overwrite, hardcoded versions, wrong metrics for problem type, and non-versioned report names.

## Deviations from Plan

None — plan executed exactly as written. The workflow file structure and step content match the plan's task action specifications. Unsupervised modify script was copied verbatim from iterate-unsupervised.md Step 6 as specified. Step numbering goes to 11 (plan showed 10 but listed Step 11 — Report to analyst — the plan itself used 11).

## Known Stubs

None. The workflow is fully implemented. Direction parsing scripts are complete and self-contained. The only conditional path (Claude fallback) is intentional by design (D-03) — it engages when no structured regex matches, which is correct behavior.

## Threat Surface Scan

No new network endpoints, auth paths, or infrastructure introduced. Files created are workflow documentation only — executed by Claude Code in analyst sessions. The direction string injection threat (T-11-01) is mitigated: both modification scripts receive direction via `sys.argv[1]` not shell string interpolation.

## Self-Check

- [x] `.claude/skills/doml-iterate/SKILL.md` exists — verified
- [x] `.claude/doml/workflows/iterate.md` exists — verified
- [x] Commit 7cc8cef exists (Task 1)
- [x] Commit 246f405 exists (Task 2)
- [x] All 14 automated checks from plan verification passed: ALL_CHECKS_OK
- [x] Five plan verification checks passed: SKILL_OK, 30 problem_type matches, sys.argv[1] present, 3 versioned report names, both leaderboard paths
