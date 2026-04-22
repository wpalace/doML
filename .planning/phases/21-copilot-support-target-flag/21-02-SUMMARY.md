---
phase: 21-copilot-support-target-flag
plan: 02
subsystem: infra
tags: [bash, powershell, install-script, copilot, github-copilot, target-flag]

# Dependency graph
requires:
  - phase: 21-copilot-support-target-flag
    provides: AGENTS.md static template at repo root (from plan 01)
  - phase: 20-install-scripts-claude
    provides: install.sh and install.ps1 Phase 20 baseline

provides:
  - install.sh with --target claude|copilot flag and D-06 CLAUDE.md always-overwrite
  - install.ps1 with -Target claude|copilot parameter, $env:DOML_TARGET env var fallback, and D-06 always-overwrite

affects:
  - users running install scripts to choose AI coding assistant target

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bash long-option parsing via while/case loop (not getopts — getopts only handles single-char flags)"
    - "PowerShell param + env-var fallback pattern for pipe-to-iex mode ($env:DOML_TARGET mirrors $env:DOML_VERSION)"
    - "Two-branch conditional install: if TARGET==copilot → .github/ tree; else → .claude/ tree"
    - "D-06: always-overwrite pattern — no skip-if-present conditional for CLAUDE.md"

key-files:
  created: []
  modified:
    - install.sh
    - install.ps1

key-decisions:
  - "Default target is claude — backward-compatible with all Phase 20 users (D-02)"
  - "No --target both option — mutually exclusive per D-01"
  - "SKILL.md files copied verbatim to .github/skills/ — no transformation needed (D-03)"
  - "CLAUDE.md installed as .github/copilot-instructions.md for copilot target (D-04)"
  - "AGENTS.md guard: fast-fail with packaging error message if $SRC/AGENTS.md missing (D-08)"
  - "D-06 applied to both scripts: CLAUDE.md always overwritten, skip-if-present conditional removed"

patterns-established:
  - "Target flag pattern: --target cli arg with env-var fallback ($env:DOML_TARGET) for pipe-to-iex"
  - "Allowlist validation before use (T-21-02-01, T-21-02-02): exits 1 with clear error on invalid target"
  - "Archive guard pattern: explicit test-before-copy for AGENTS.md with packaging error message (T-21-02-04)"

requirements-completed:
  - INST-07
  - INST-08
  - COP-02
  - COP-03
  - COP-04

# Metrics
duration: 8min
completed: 2026-04-22
---

# Phase 21 Plan 02: --target Flag in install.sh and install.ps1 Summary

**Bash and PowerShell install scripts extended with `--target claude|copilot` flag: copilot branch installs SKILL.md files to `.github/skills/`, `CLAUDE.md` as `.github/copilot-instructions.md`, and `AGENTS.md` at project root; D-06 always-overwrite applied to both scripts**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-22T14:27:00Z
- **Completed:** 2026-04-22T14:35:43Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Extended `install.sh` with `--target claude|copilot` flag (while/case long-option parsing), default `claude` (D-02), invalid value exits 1
- Extended `install.ps1` with `[string]$Target` parameter and `$env:DOML_TARGET` env var fallback for pipe-to-iex mode
- Both scripts apply D-06: CLAUDE.md always overwritten (skip-if-present conditional removed)
- Both scripts include explicit AGENTS.md guard — fast-fail with packaging error if missing from archive (T-21-02-04)
- All 10 acceptance criteria passed for install.sh; all 11 acceptance criteria passed for install.ps1

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend install.sh with --target flag** - `cc2c8f6` (feat)
2. **Task 2: Extend install.ps1 with -Target parameter** - `85230f7` (feat)

## Files Created/Modified

- `install.sh` — Bash installer with `--target claude|copilot` flag; 116 net insertions; copilot branch installs to `.github/`; claude branch unchanged file set with D-06 always-overwrite
- `install.ps1` — PowerShell installer with `-Target` parameter and `$env:DOML_TARGET` fallback; 135 net insertions; same target branches as Bash script; `finally` cleanup block preserved

## Decisions Made

- Used `while`/`case` loop (not `getopts`) for `--target` — `getopts` handles only single-character flags; long options require manual parsing
- PowerShell `$env:DOML_TARGET` env var fallback added for parity with `$env:DOML_VERSION` — users running via `irm ... | iex` cannot pass named parameters directly
- AGENTS.md guard (`test -f "$SRC/AGENTS.md"` / `Test-Path $agentsSrc`) makes archive packaging failures visible rather than silently succeeding with a missing file

## Deviations from Plan

None - plan executed exactly as written. All code blocks from the plan's action sections were implemented verbatim with no structural changes required.

## Issues Encountered

- Worktree branch was based on an older commit (`85c9b11`) rather than the specified base (`68cb231`). Applied `git reset --soft 68cb2316e35c816b7fdac457a2f4dd20b0bf90a9` to fix before execution.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `install.sh --target copilot` and `install.ps1 -Target copilot` are fully implemented
- Both scripts pass syntax validation (`bash -n install.sh` exits 0)
- Full end-to-end smoke test requires a live GitHub release tag or manual local archive simulation
- Phase 21 core deliverables complete: AGENTS.md (plan 01) + --target flag (plan 02)

---
*Phase: 21-copilot-support-target-flag*
*Completed: 2026-04-22*

## Self-Check: PASSED
