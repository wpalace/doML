---
phase: 18-doml-iterate-deployment
plan: 18-01
subsystem: doml-iterate-deployment
tags: [doml, deployment, workflow, skill, iterate]
dependency_graph:
  requires:
    - .claude/doml/workflows/deploy-model.md
    - .claude/doml/workflows/deploy-cli.md
    - .claude/doml/workflows/deploy-web.md
    - .claude/doml/workflows/deploy-wasm.md
    - .claude/doml/templates/notebooks/deployment_report.ipynb
  provides:
    - .claude/skills/doml-iterate-deployment/SKILL.md
    - .claude/doml/workflows/iterate-deployment.md
  affects:
    - models/model_metadata.json (reads model_file for leaderboard guard)
    - src/*/v*/deployment_metadata.json (reads and writes versioned deployment metadata)
tech_stack:
  added: []
  patterns:
    - SKILL.md entry point pattern (mirrors doml-deploy-model)
    - 13-step prose workflow matching deploy-model.md structure
    - model_file path comparison for leaderboard guard (not display names)
    - flag-based target resolution (--target cli|web|wasm)
    - Python heredoc GUIDANCE parsing (T-18-01 safe)
    - verbatim Step 12 performance report (12a-12j) from deploy-model.md
key_files:
  created:
    - .claude/skills/doml-iterate-deployment/SKILL.md
    - .claude/doml/workflows/iterate-deployment.md
  modified: []
decisions:
  - "D-01: Leaderboard-match guard compares model_file paths (not display names) to avoid mismatch between leaderboard model column and deployment_metadata model_name"
  - "D-02: Version scan uses glob src/MODEL_SLUG/v* + max(N)+1; new model slug always starts at v1/"
  - "D-03: --target flag resolves target or falls back to prior deployment_metadata.json; no AskUserQuestion"
  - "D-04: --guidance parsed via Python heredoc (T-18-01 safe); never shell-interpolated; passed to Step 12f narrative"
  - "D-05: iterate-deployment.md is standalone; does NOT modify deploy-model.md; delegates to deploy-cli/web/wasm"
  - "D-06: Three valid no-new-model scenarios: config/guidance change, target change, baseline refresh"
metrics:
  duration: "~7 minutes"
  completed: "2026-04-17"
  tasks_completed: 2
  files_created: 2
  files_modified: 0
---

# Phase 18 Plan 01: doml-iterate-deployment — Summary

**One-liner:** New `/doml-iterate-deployment` command with 13-step iterate-deployment.md workflow: leaderboard-match guard (model_file path comparison), version scan, flag-based target resolution, GUIDANCE parsing via Python heredoc, and verbatim Step 12 performance report.

## What Was Built

Two new files creating the `/doml-iterate-deployment` Claude Code command:

1. **`.claude/skills/doml-iterate-deployment/SKILL.md`** — Entry point. YAML frontmatter registers the command with `name: doml-iterate-deployment`, documents `--model`, `--target`, and `--guidance` flags in `argument-hint`, lists 13 numbered steps in `<objective>`, and references `iterate-deployment.md` via `<execution_context>`.

2. **`.claude/doml/workflows/iterate-deployment.md`** — 13-step orchestration workflow. Structured to match `deploy-model.md` format.

## Workflow Steps Summary

| Step | Name | Treatment |
|------|------|-----------|
| 1 | Validate project state | Verbatim from deploy-model.md |
| 2 | Read config.json + parse flags | Adapted — adds --target and --guidance alongside --model |
| 3 | Leaderboard-match guard | New — compares model_file paths; stops if changed without --model |
| 4 | Ensure model_name in model_metadata.json | Verbatim from deploy-model.md |
| 5 | Derive MODEL_SLUG | Verbatim from deploy-model.md |
| 6 | Resolve deployment target | Adapted — --target flag or prior metadata; no AskUserQuestion |
| 7 | Scan versions + set VERSION | Verbatim from deploy-model.md |
| 8 | Read feature_schema | Verbatim from deploy-model.md |
| 9 | Apply --guidance | New — Claude commentary before delegating |
| 10 | Create dir + write deployment_metadata.json | Adapted — adds optional guidance field |
| 11 | Delegate to target skill | New — explicit @.claude/doml/workflows/deploy-cli/web/wasm.md with --deploy-dir |
| 12 | Generate performance report | Verbatim Steps 12a-12j from deploy-model.md |
| 13 | Update STATE.md + confirm | Adapted — phase 18 reference, version confirmation message |

## Requirements Satisfied

| Requirement | Description | How Satisfied |
|-------------|-------------|---------------|
| ITER-01 | Iterate without re-running /doml-deploy-model | Standalone command with full 13-step workflow |
| ITER-02 | Same model → vN+1 (scanned, not assumed) | Step 7: glob src/MODEL_SLUG/v* + max(N)+1 |
| ITER-03 | Different model → new src/newmodelname/v1/ | Step 2 --model override → Step 5 new slug → Step 7 scans empty dir → v1 |
| ITER-04 | --guidance parameter accepted + applied | Step 2 Python heredoc parsing; Step 9 application; Step 12f narrative |
| ITER-05 | Works without new model | D-06: config change, target change, baseline refresh all produce vN+1 |

## Threat Mitigations Applied

| Threat | Mitigation |
|--------|-----------|
| T-18-01 (GUIDANCE shell injection) | GUIDANCE parsed via Python heredoc `'''${ARGUMENTS}'''`; never shell-interpolated |
| T-18-02 (--model path injection) | MODEL_OVERRIDE validated via `os.path.exists()` inside Python only |
| T-18-04 (--target value injection) | TARGET_OVERRIDE validated through case statement; exit 1 on unknown value |

## Verification Results

All automated checks passed:

```
ls .claude/skills/doml-iterate-deployment/SKILL.md          ✓
ls .claude/doml/workflows/iterate-deployment.md             ✓
grep 'name: doml-iterate-deployment' SKILL.md               ✓
grep 'iterate-deployment.md' SKILL.md                       ✓
grep '--guidance' SKILL.md                                  ✓
grep '--target' SKILL.md                                    ✓
grep 'LATEST_META' iterate-deployment.md                    ✓
grep 'v${VERSION' iterate-deployment.md                     ✓
grep 'MODEL_OVERRIDE' iterate-deployment.md                 ✓
grep '--guidance' iterate-deployment.md                     ✓
grep '--target' iterate-deployment.md                       ✓
grep 'deployment_report' iterate-deployment.md              ✓
grep 'deploy-cli|deploy-web|deploy-wasm' iterate-deployment.md ✓
No AskUserQuestion in iterate-deployment.md                 ✓
Step 13 present                                             ✓
Anti-Patterns section present                               ✓
```

## Deviations from Plan

None — plan executed exactly as written.

The pre-condition note was handled: Phase 17 plans were read to obtain Step 12 (12a-12j) content since Phase 17 SUMMARYs did not yet exist. Step 12 content was taken verbatim from 17-02-PLAN.md task action block.

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1: SKILL.md entry point | 81db146 | .claude/skills/doml-iterate-deployment/SKILL.md |
| Task 2: iterate-deployment.md workflow | a619f91 | .claude/doml/workflows/iterate-deployment.md |

## Self-Check: PASSED

- FOUND: .claude/skills/doml-iterate-deployment/SKILL.md
- FOUND: .claude/doml/workflows/iterate-deployment.md
- FOUND commit 81db146 (Task 1: SKILL.md)
- FOUND commit a619f91 (Task 2: iterate-deployment.md)
