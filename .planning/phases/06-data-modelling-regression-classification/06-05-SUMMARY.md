---
phase: 06-data-modelling-regression-classification
plan: 05
status: complete
completed: 2026-04-07
---

# Plan 06-05 Summary: /doml-iterate-model Command Stub

## Artifacts Produced

1. `.claude/skills/doml-iterate-model/SKILL.md` — command entry point
2. `.claude/doml/workflows/iterate-model.md` — workflow stub

## Implementation

### SKILL.md

Follows `doml-execute-phase/SKILL.md` format exactly:
- frontmatter: name, description, allowed-tools
- `<objective>` section: what the command does
- `⚠️ Stub` warning prominent at top
- `<arguments>` section: optional direction string with 4 usage examples
- `<execution_context>`: references `@.claude/doml/workflows/iterate-model.md`
- `<process>`: routes to iterate-model.md workflow

The skill is registered and Claude Code will discover it (confirmed: appeared in skills list immediately after file creation).

### iterate-model.md

Format mirrors `execute-phase.md` (Purpose, Invoked by, Implementation Status table, then stub workflow).

**Implementation Status table:** All 5 steps marked `Stub / Phase 6b`

**7 planned workflow steps documented:**
1. Identify prior notebook (highest version in `notebooks/`)
2. Resolve next version number (glob + increment)
3. Generate modified notebook (direction → model/feature/hyperparameter focus)
4. Execute new iteration notebook (1200s timeout, same as execute-phase.md Step 3k)
5. Append results to `leaderboard.csv` with cross-iteration display
6. Write Claude interpretation cell (compare v{M+1} vs v{M})
7. Display summary with delta

**Direction argument documented:** Three mapping rules — model names, feature engineering, hyperparameter focus.

**Manual workaround documented:** Step-by-step for analysts until Phase 6b ships (copy notebook, edit in JupyterLab, re-run, leaderboard auto-appends).

**Implementation note:** Identifies 3 technical requirements for Phase 6b — direction parsing, dynamic cell injection, cross-iteration leaderboard display.

## Deferred to Phase 6b

- Direction string parsing (NLP → notebook modification)
- Dynamic cell injection into notebook template
- Cross-iteration leaderboard aggregation display
- Full autonomous execution pipeline

## Verification Passed

All checks from plan verification block:
- SKILL_EXISTS ✓
- `grep -c "doml-iterate-model" SKILL.md` → 5 ✓
- `grep -c "iterate-model.md" SKILL.md` → 2 ✓
- `grep -ci "stub\|deferred" SKILL.md` → 1 ✓
- WORKFLOW_EXISTS ✓
- `grep -c "direction" iterate-model.md` → 10 ✓
- `grep -c "leaderboard" iterate-model.md` → 9 ✓
- `grep -c "Step" iterate-model.md` → 11 ✓
