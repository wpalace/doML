# Phase 13: Deployment Workflow Skeleton — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 13-deployment-workflow-skeleton
**Areas discussed:** Target selection UX, Collision handling

---

## Target selection UX

| Option | Description | Selected |
|--------|-------------|----------|
| Interactive menu | No --target flag; AskUserQuestion with 3 options every invocation | ✓ |
| Required --target flag | doml-deploy-model --target cli\|web\|wasm always required | |
| --target optional, default to web | Falls back to web when --target omitted | |

**Follow-up: When --target is supplied, skip menu or confirm?**

| Option | Description | Selected |
|--------|-------------|----------|
| Flag wins, skip menu | --target proceeds directly | (moot) |
| Always confirm | Show menu even with flag | (moot) |
| Remove --target flag entirely | Always interactive | ✓ |

**User's choice:** Remove `--target` flag entirely — always interactive via AskUserQuestion menu.
**Notes:** User explicitly said "get rid of the --target flag and just let it be interactive."

---

## Collision handling

| Option | Description | Selected |
|--------|-------------|----------|
| Stop with message | Print "run /doml-iterate-deployment to create v2" and exit | |
| Auto-increment to next version | Scan src/<modelname>/ for existing vN, write to vN+1 | ✓ |
| Overwrite with warning | Warn and overwrite v1/ | |

**Follow-up: How to communicate the chosen version?**

| Option | Description | Selected |
|--------|-------------|----------|
| Announce and continue | Print "deploying to v2/" then proceed immediately | ✓ |
| Confirm before proceeding | Pause for user confirmation | |
| Silent | No announcement | |

**User's choice:** Auto-increment with announcement — scan filesystem, announce version choice, continue without pause.

---

## Claude's Discretion

- `model_name` sanitization format for directory slug
- Step ordering within workflow (validation sequence)
- DuckDB vs pandas for leaderboard read inside Docker

## Deferred Ideas

- Problem type scope edge cases (clustering/forecasting leaderboard routing) — left to planner
- `--model` override flag implementation details — straightforward, not discussed
