---
phase: 23-dockerfile-rebuild-uv-migration
plan: 01
subsystem: infra
tags: [uv, requirements, templates, doml-new-project, dependency-management]

# Dependency graph
requires:
  - phase: 22-pre-flight-wheel-validation-lockfile-bootstrap
    provides: "Root requirements.in cleanup (drop pip-tools, add numpy<2.4) + scipy-notebook tag pin + Python 3.14 lock"
provides:
  - "Template requirements.in mirrors v1.6 root surface (no pip-tools, explicit numpy<2.4 pin)"
  - "Both regen-command comments in template now point at `uv pip compile … --generate-hashes`"
  - "`/doml-new-project` scaffolds will inherit the v1.6 dependency surface"
affects:
  - 23-02-template-lockfile-regeneration
  - 23-03-dockerfile-rewrite-root
  - 23-04-dockerfile-rewrite-template
  - any phase consuming `.claude/doml/templates/requirements.in`

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Template mirrors root (CONT-08): templates/requirements.in tracks repo-root requirements.in structurally"
    - "uv as lockfile generator: regen-command comments document `uv pip compile … --generate-hashes` invocation"
    - "Explicit numpy upper bound (numpy<2.4) prevents transitive 2.4 from breaking C-extension wheels"

key-files:
  created: []
  modified:
    - ".claude/doml/templates/requirements.in"

key-decisions:
  - "D-23-B1 applied: drop pip-tools and add numpy<2.4 in template requirements.in to mirror Phase 22 root cleanup"
  - "Isolated commit (1 file, 3 insertions / 3 deletions) — keeps Plan 02's lockfile-format-noisy diff clean"
  - "kaggle preserved (consumed by /doml-get-data); mistune<3 NOT added to template (template historically did not pin it; lockfile resolves transitively)"

patterns-established:
  - "Template-vs-root structural-mirror discipline: when root requirements.in changes shape, the template change lands as its own isolated commit with chore(NN-MM) prefix"

requirements-completed: [CONT-08]

# Metrics
duration: 1min
completed: 2026-05-01
---

# Phase 23 Plan 01: Mirror Template Requirements + Drop pip-tools, Add numpy<2.4 Summary

**Template `requirements.in` mirrors Phase 22's root cleanup — pip-tools removed, numpy<2.4 added under ML stack, both regen-command comments point at `uv pip compile … --generate-hashes`**

## Performance

- **Duration:** ~1 min (single 4-class edit + verification)
- **Started:** 2026-05-01T02:01:58Z
- **Completed:** 2026-05-01T02:02:56Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Template `requirements.in` regen-command header rewritten to use `uv pip compile requirements.in --generate-hashes -o requirements.txt`
- `pip-tools` removed from `--- Reproducibility ---` block (replaced by uv per D-02 / D-23-B1)
- `numpy<2.4` added as the first entry under `--- ML stack ---` (PY-05 / PITFALLS #12 ABI pin)
- kaggle-block regen-command comment also rewritten to use `uv pip compile`
- `/doml-new-project` scaffolds will inherit the v1.6 dependency surface (CONT-08 partial coverage advanced)

## Task Commits

1. **Task 1: Update template requirements.in (4-class edit)** — `17aed5c` (chore)

## Files Created/Modified
- `.claude/doml/templates/requirements.in` — drop pip-tools, add numpy<2.4, switch both regen-command comments to `uv pip compile … --generate-hashes`

## Decisions Made
None - plan executed exactly as written. All four prescribed text changes (top-of-file regen comment, pip-tools deletion, numpy<2.4 insertion, kaggle-block regen comment) applied per D-23-B1.

## Deviations from Plan

None - plan executed exactly as written.

## Acceptance Criteria

All 8 acceptance checks pass:

| # | Check | Expected | Actual |
|---|-------|----------|--------|
| 1 | `grep -c '^pip-tools' …` | 0 | 0 |
| 2 | `grep -c '^numpy<2.4' …` | 1 | 1 |
| 3 | `grep -c 'uv pip compile requirements.in --generate-hashes -o requirements.txt' …` | 2 | 2 |
| 4 | `grep -c 'pip-compile requirements.in' …` | 0 | 0 |
| 5 | `grep -c '^kaggle' …` | 1 | 1 |
| 6 | `grep -c '^prophet' …` | 1 | 1 |
| 7 | `grep -c -E '^pyinstaller\|^skl2onnx' …` | 2 | 2 |
| 8 | trailing newline (`tail -c1 \| xxd`) | `0a` | `0a` |

Plan-level automated verify command: **PASS**.

## Issues Encountered
None.

## User Setup Required
None — structural cleanup of source-of-truth requirements.in only; no external service configuration.

## Next Phase Readiness
- **Plan 02 (template lockfile regen)** ready to consume this updated `requirements.in` via `uv pip compile .claude/doml/templates/requirements.in -o .claude/doml/templates/requirements.txt --generate-hashes`. Per D-23-B2, that regen lands as its own isolated commit (PITFALLS #6: format-only diff is noisy).
- **Plans 03-04 (Dockerfile rewrites)** unaffected by this change — they consume the regenerated `requirements.txt`, not `requirements.in`.
- CONT-08 partial coverage advanced; full coverage completes in Plan 02 (template lockfile) and Plans 03-04 (template Dockerfile).

## Self-Check: PASSED

- File `.claude/doml/templates/requirements.in` exists at expected path: FOUND
- Commit `17aed5c` exists in current branch: FOUND
- All 8 acceptance criteria verified: PASS
- Plan automated-verify command: PASS
- Working tree clean after commit: VERIFIED

---
*Phase: 23-dockerfile-rebuild-uv-migration*
*Plan: 01*
*Completed: 2026-05-01*
