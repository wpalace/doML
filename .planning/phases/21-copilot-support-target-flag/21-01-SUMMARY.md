---
phase: 21-copilot-support-target-flag
plan: 01
subsystem: docs
tags: [copilot, agents-md, cross-agent, markdown, doml-framework]

# Dependency graph
requires:
  - phase: 20-install-scripts-claude
    provides: install.sh and install.ps1 as the install scripts that will copy AGENTS.md
provides:
  - AGENTS.md static cross-agent instruction template at repo root

affects:
  - 21-02  # install.sh/install.ps1 copilot branch copies AGENTS.md from $SRC/AGENTS.md

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AGENTS.md as static repo-root template installed verbatim to user project root"
    - "Tool-neutral Markdown (no /command syntax, no @-mentions, no frontmatter)"

key-files:
  created:
    - AGENTS.md
  modified: []

key-decisions:
  - "AGENTS.md uses plain Markdown with no frontmatter — per spec in 21-CONTEXT.md D-05"
  - "Content mirrors CLAUDE.md but with tool-neutral language and an added src/ row in Project Structure"
  - "Commands table includes invocation syntax note for Copilot/Claude/Cursor rather than Claude-only /command references"

patterns-established:
  - "Static template pattern: pre-authored file in repo root, installed verbatim by install scripts"

requirements-completed:
  - COP-01

# Metrics
duration: 5min
completed: 2026-04-22
---

# Phase 21 Plan 01: AGENTS.md Static Template Summary

**Tool-neutral AGENTS.md at repo root covering project structure, reproducibility rules, all 14 DoML commands, DuckDB guidance, and prohibited actions — ready for verbatim install under `--target copilot`**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-22T14:26:00Z
- **Completed:** 2026-04-22T14:31:43Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `AGENTS.md` at the DoML repo root with all required sections
- File is tool-neutral plain Markdown (no Claude-specific `/command` syntax or `@`-mentions)
- 5173 bytes, 16 occurrences of `doml-` commands — meets all acceptance criteria
- Verified: no `@/` references, no frontmatter, file size > 2000 bytes

## Task Commits

Each task was committed atomically:

1. **Task 1: Author AGENTS.md static template** - `592fcfb` (feat)

**Plan metadata:** (docs commit to follow)

## Files Created/Modified

- `AGENTS.md` — Cross-agent instruction template for DoML projects; tool-neutral Markdown covering project structure, reproducibility rules, DoML commands table, DuckDB guidance, and prohibited actions

## Decisions Made

- AGENTS.md uses plain Markdown with no frontmatter (per D-05 in 21-CONTEXT.md — static template, no YAML header required)
- Content mirrors CLAUDE.md but with tool-neutral language; added `src/` row to Project Structure table since deploy targets need it
- Commands table includes a brief invocation syntax note covering Copilot/Claude/Cursor so the file is genuinely cross-tool

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Worktree branch was based on an older commit (`85c9b11`) rather than the specified base (`4bc2aff`). Applied `git reset --soft` to fix the branch base before execution. The index had staged deletions from the previous branch state which were unstaged before committing AGENTS.md.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `AGENTS.md` exists at repo root and will be present in the release archive
- Plan 02 can now implement the `--target copilot` branch in `install.sh`/`install.ps1` and verify the `cp "$SRC/AGENTS.md" "AGENTS.md"` step end-to-end

---
*Phase: 21-copilot-support-target-flag*
*Completed: 2026-04-22*
