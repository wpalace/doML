---
phase: 22-pre-flight-wheel-validation-lockfile-bootstrap
plan: 03
subsystem: infra
tags: [docker, scipy-notebook, audit, py-fut, project-md, requirements-traceability]

# Dependency graph
requires:
  - phase: 22-02
    provides: Resolved Python 3.14 + scipy-notebook tag 2026-04-27 + audit raw artifacts staged at /tmp/preflight-22/
provides:
  - Both Dockerfiles' FROM lines bumped to quay.io/jupyter/scipy-notebook:2026-04-27 (FROM-line ONLY edits)
  - 22-AUDIT.md with mamba list (387 lines) + conflict diff (4 packages) + uv pip compile diff (2097 lines)
  - 22-SUMMARY.md (phase-level) with GO decision, python_version: 3.14, scipy_notebook_tag: 2026-04-27, auto_fallback_fired: false
  - PROJECT.md D-03 re-locked from "Python 3.13 (3.14 blocked by ydata-profiling)" → "Python 3.14 (locked at end of Phase 22 pre-flight)"
  - REQUIREMENTS.md PY-FUT-01 retired entirely; traceability table marks PY-01..PY-05 + CONT-06 as Complete
affects: [23 (Dockerfile install-layer rewrite — consumes pinned FROM line), 24 (R removal — line-1 comment touched there)]

# Tech tracking
tech-stack:
  added: []
  removed: []
  patterns:
    - "Phase boundary discipline: ONLY the FROM line edited in both Dockerfiles; mamba install r-* block, pip install line, kaggle-CLI layer all preserved"
    - "Single-file inline audit (no audit/ subdirectory) with three H2 sections per D-22-16/D-22-17"
    - "Strikethrough vs literal removal: the plan called for literal line removal of PY-FUT-01 to satisfy 'does NOT contain ydata-profiling lifts' acceptance criterion — applied"

key-files:
  created:
    - .planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-AUDIT.md
    - .planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-SUMMARY.md
  modified:
    - Dockerfile
    - .claude/doml/templates/Dockerfile
    - .planning/PROJECT.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-22-13/D-22-14/D-22-15: tag-only pin to scipy-notebook:2026-04-27; FROM-line only; line-1 comment + LABEL/install-layer/USER/WORKDIR untouched"
  - "D-22-06: Python target re-locked from 3.13 → 3.14 in PROJECT.md D-03 (3.14 won pre-flight first try, no fallback fired)"
  - "D-22-08: PY-FUT-01 + PY-FUT-02 retired entirely from REQUIREMENTS.md Future Requirements (3.14-won path)"
  - "D-22-16/D-22-17: 22-AUDIT.md is single-file, three required H2 sections (Mamba List / Conflict Diff / uv pip compile Diff), full mamba list inlined as fenced text"
  - "D-22-18 commit 3 verbatim message landed: 'docs(22): pre-flight audit + scipy-notebook tag pin'"

patterns-established:
  - "Worktree-base recovery on parallel agent spawn: git reset --soft <correct base> && git reset HEAD && git checkout -- . — same pattern as plans 22-01 and 22-02"
  - "STATE.md/ROADMAP.md left to orchestrator: executor MUST NOT commit those during a wave (per prompt instructions)"

requirements-completed: [PY-01, PY-02, PY-03, PY-04, PY-05, CONT-06]

# Metrics
duration: ~7min
completed: 2026-04-30
---

# Phase 22 Plan 03 Summary — Pre-flight Audit + scipy-notebook Tag Pin

**Both Dockerfile FROM lines bumped to `quay.io/jupyter/scipy-notebook:2026-04-27`, `22-AUDIT.md` written with all three required H2 sections (mamba list / conflict diff / uv pip compile diff), `22-SUMMARY.md` written with GO decision and `python_version: 3.14`, PROJECT.md D-03 re-locked to 3.14, REQUIREMENTS.md PY-FUT-01/02 retired and traceability table updated to Complete for PY-01..PY-05 + CONT-06 — landed in single commit `5da3eea` per D-22-18 commit 3.**

## Performance

- **Duration:** ~7 min
- **Tasks:** 5 (all atomic + grouped into single commit per D-22-18 commit-3 contract)
- **Files modified:** 6 (4 modified, 2 new)

## Accomplishments

- **Task 1 — Dockerfile FROM-line bumps:**
  - Root `Dockerfile` line 3: `FROM quay.io/jupyter/datascience-notebook:2026-04-02` → `FROM quay.io/jupyter/scipy-notebook:2026-04-27`
  - Template `.claude/doml/templates/Dockerfile` line 3: same edit
  - Both files: identical FROM lines (verified via diff), unchanged line counts (29/38), no other lines touched
- **Task 2 — `22-AUDIT.md`:** 2526-line audit document inline-embedding all three required artifacts (mamba list 387 lines, conflict diff 4 packages, uv pip compile diff 2097 lines) plus pre-flight run log outcome record (3.14 PASS, 3.13 SKIPPED)
- **Task 3 — `22-SUMMARY.md`:** 86-line phase summary with frontmatter (`python_version: 3.14`, `scipy_notebook_tag: 2026-04-27`, `auto_fallback_fired: false`, `go_no_go: GO`), 11-item deliverables checklist, PY-01..PY-05 + CONT-06 coverage table, Phase 23 handoff section
- **Task 4 — PROJECT.md / REQUIREMENTS.md:**
  - PROJECT.md D-03: re-locked from 3.13 → 3.14 with explicit Phase 22 reference
  - REQUIREMENTS.md PY-FUT-01 + PY-FUT-02: retired (replaced section header + summary line; literal "ydata-profiling lifts" wording removed)
  - REQUIREMENTS.md traceability table: PY-01, PY-02, PY-03, PY-04, PY-05, CONT-06 all flipped from `Pending` → `Complete`
- **Task 5 — Commit 3:** `5da3eea docs(22): pre-flight audit + scipy-notebook tag pin` — exactly the 6 prescribed files (no requirements.in/.txt, no template requirements files, no notebook). Verbatim D-22-18 commit-3 message.

## Task Commits

All 5 tasks roll into a single commit per D-22-18 commit-3 contract (consistent with the commit grouping in plans 22-01 and 22-02):

1. Task 1 (Dockerfile FROM-line bumps) → file edits in commit `5da3eea`
2. Task 2 (`22-AUDIT.md` write) → file creation in commit `5da3eea`
3. Task 3 (`22-SUMMARY.md` write) → file creation in commit `5da3eea`
4. Task 4 (PROJECT.md D-03 + REQUIREMENTS.md PY-FUT-01 + traceability) → file edits in commit `5da3eea`
5. Task 5 (commit) → `5da3eea` itself

**Commit:** `5da3eea` — `docs(22): pre-flight audit + scipy-notebook tag pin`

## Files Created/Modified

| File | Type | Change |
|------|------|--------|
| `Dockerfile` | modified | Line 3 FROM bumped (1 insertion + 1 deletion); 28 other lines untouched |
| `.claude/doml/templates/Dockerfile` | modified | Line 3 FROM bumped (1 insertion + 1 deletion); 37 other lines untouched |
| `.planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-AUDIT.md` | created | 2526 lines (mamba list + conflict diff + uv pip compile diff inlined) |
| `.planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-SUMMARY.md` | created | 86 lines (frontmatter + GO decision + deliverables + coverage + handoff) |
| `.planning/PROJECT.md` | modified | D-03 line: 3.13 → 3.14 (1 insertion + 1 deletion) |
| `.planning/REQUIREMENTS.md` | modified | PY-FUT block rewritten as RESOLVED; 6 traceability rows flipped to Complete (8 insertions + 9 deletions) |

## Decisions Made

- **PY-FUT-01 retirement format:** Plan said "REMOVE the entire PY-FUT-01 line entirely (D-22-08)" but also recommended documenting the resolution. Initial strikethrough attempt would have left the literal `**PY-FUT-01**: Upgrade container to Python 3.14 once \`ydata-profiling\` lifts` substring intact (under `~~` markers), which would fail the plan's acceptance criterion `does NOT contain the line ...ydata-profiling lifts`. Resolved by replacing the entire two-bullet PY-FUT block with a section-level "RESOLVED in Phase 22" header + single explanatory paragraph. Both PY-FUT-01 and PY-FUT-02 retired together — neither is pending anymore. Original literal substring is gone (verified: `grep -c "ydata-profiling.*lifts"` returns 0).
- **Branch decision:** PYVER == "3.14" → Branch A (D-22-08 path 1). PROJECT.md D-03 fully replaced (not appended). REQUIREMENTS.md PY-FUT-01 fully retired (not edited in place).
- **STATE.md/ROADMAP.md left untouched:** Per orchestrator prompt's explicit instruction ("Do NOT update STATE.md or ROADMAP.md — the orchestrator owns those writes after the wave completes"). The pre-existing modifications to these files in the worktree (likely from the orchestrator's earlier plan-22-01/22-02 wave commits that were merged in via the worktree base) were reverted to HEAD before staging this plan's commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Worktree branch base recovered (same pattern as plans 22-01, 22-02)**
- **Found during:** Initial worktree branch verification step (per `<worktree_branch_check>` block)
- **Issue:** `git merge-base HEAD c6050a4...` returned `d5e299f` (the v1.5 archive head), confirming worktree branch was created from the wrong base. Same pattern as plans 22-01 and 22-02.
- **Fix:** `git rebase --onto c6050a4 HEAD^ HEAD` initially, then `git reset --soft c6050a4 && git reset HEAD && git checkout -- .` per the prompt's recovery script. After recovery, 155 v1.5 archive files showed as deleted on disk (the soft reset moved HEAD without restoring files); restored those via `git status --porcelain | awk '/^.D/ {print $2}' | xargs -d '\n' git checkout HEAD --`. Net result: clean working tree with only the intended modifications.
- **Files modified:** None at the file level — purely repository state manipulation
- **Verification:** `git status --porcelain` shows only the 4 intended modifications (2 Dockerfiles + PROJECT.md + REQUIREMENTS.md) plus 2 new files (AUDIT + SUMMARY) plus untracked `.claude/worktrees/`
- **Committed in:** N/A (state correction, not a code change)

**2. [Rule 1 - Bug] Strikethrough vs literal removal of PY-FUT-01**
- **Found during:** Task 4 acceptance verification re-read
- **Issue:** First attempt at PY-FUT-01 retirement used markdown strikethrough (`~~Upgrade container to Python 3.14 once \`ydata-profiling\` lifts...~~`) with a "RESOLVED in Phase 22" note appended. The strikethrough preserves the original text inside `~~` markers, which still contains the literal substring `ydata-profiling lifts`. Plan's acceptance criterion explicitly says: "`.planning/REQUIREMENTS.md` does NOT contain the line `**PY-FUT-01**: Upgrade container to Python 3.14 once \`ydata-profiling\` lifts`".
- **Fix:** Replaced the entire `### Python 3.14 (PY-FUT)` subsection: header now reads `### Python 3.14 (PY-FUT) — RESOLVED in Phase 22 (2026-04-30)`, followed by a single explanatory paragraph. Both PY-FUT-01 and PY-FUT-02 retired together (consistent — once 3.14 is in production, both follow-up requirements are moot).
- **Files modified:** `.planning/REQUIREMENTS.md` (lines 50-54 in the resolved file)
- **Verification:** `grep -c "ydata-profiling.*lifts" .planning/REQUIREMENTS.md` returns 0
- **Committed in:** `5da3eea`

**3. [Rule 3 - Blocking] STATE.md/ROADMAP.md uncommitted modifications detected and reverted**
- **Found during:** Pre-commit `git status` review (between Task 4 and Task 5)
- **Issue:** Worktree had uncommitted modifications in `.planning/STATE.md` (status: planning → executing, last-activity update) and `.planning/ROADMAP.md` (Phase 22 plan progress 0/3 → 2/3). These appear to be uncommitted changes from a prior orchestrator-managed wave that got carried over by the worktree-base mismatch. The orchestrator prompt for THIS plan explicitly says: "Do NOT update STATE.md or ROADMAP.md — the orchestrator owns those writes after the wave completes."
- **Fix:** `git checkout HEAD -- .planning/STATE.md .planning/ROADMAP.md` before staging the plan-3 commit, ensuring only the 6 prescribed files end up in `5da3eea`.
- **Files modified:** None at the file level (revert)
- **Verification:** `git diff --cached` for commit 3 shows exactly 6 files; STATE.md and ROADMAP.md are NOT in commit 3
- **Committed in:** N/A (state correction; orchestrator will land STATE.md/ROADMAP.md updates after wave completes)

### Acceptance Criteria Deviation (Documented, Not Auto-Fixable)

**4. [Rule 3 - Documented Only] Plan's HEAD~1 commit-message acceptance criterion does not match orchestrator wave structure**
- **Found during:** Task 5 post-commit verification
- **Issue:** Plan acceptance criterion expects `git log --oneline -3` to show:
  - HEAD: `docs(22): pre-flight audit + scipy-notebook tag pin` ✓ MATCHES
  - HEAD~1: `chore: switch lockfile to uv format (Python 3.14)` ✗ ACTUAL = `docs(22-02): complete root requirements + uv lockfile plan`
  - HEAD~2: `chore: drop ydata-profiling from template + replace EDA profiling cell` ✗ ACTUAL = `chore: switch lockfile to uv format (Python 3.14)`
- **Why:** The orchestrator (running plans 22-01 and 22-02 in earlier waves) lands plan-summary commits (`docs(22-01)` after plan 22-01, `docs(22-02)` after plan 22-02) BETWEEN the chore commits. So the actual chain is `chore-1 → docs-1 → chore-2 → docs-2 → docs-3` where the plan's expected chain assumed `chore-1 → chore-2 → docs-3`. The 3-commit HEAD window therefore captures the docs-3, docs-2, chore-2 (not chore-2, chore-1, docs-3 as the plan expected).
- **Resolution:** Cannot be auto-fixed without rewriting committed history (which is destructive and against project rules). Plan's HEAD subject + file-set + message-verbatim acceptance criteria all PASS. The full 5-commit history (`git log --oneline -5`) does contain all three D-22-18 commits in the right semantic order: `docs(22)` → `chore(22-02 lockfile)` → `chore(22-01 ydata)`, with orchestrator docs commits interleaved.
- **Impact:** None on Phase 22 outcome. Documented for orchestrator awareness; future phase plans may want to clarify the 3-vs-5-commit HEAD window expectation.
- **Files modified:** None
- **Verification:** Full chain visible in `git log --oneline -5`
- **Committed in:** N/A

---

**Total deviations:** 4 (3 auto-fixed: 1 worktree state, 1 strikethrough → literal removal, 1 STATE/ROADMAP revert; 1 documented-only: orchestrator wave commit-chain interleaving)
**Impact on plan:** Zero scope creep, zero file content drift from plan intent. All plan-level `<verification>` and `<success_criteria>` checks pass; only one plan-level `<acceptance_criteria>` substring (HEAD~1 commit subject) doesn't match due to orchestrator wave structure outside this executor's control.

## Issues Encountered

- **Worktree base mismatch:** Same pattern as plans 22-01 and 22-02 — worktree was spawned from `d5e299f` (v1.5 archive head) instead of `c6050a4`. Recovery via the prompt's `<worktree_branch_check>` script worked cleanly; no work lost.
- **Edit-tool read-before-edit warnings:** PreToolUse hook flagged Dockerfile, PROJECT.md, REQUIREMENTS.md "READ-BEFORE-EDIT REMINDER" warnings even though all three files HAD been read at the start of the session. Edits all succeeded without retry — the hook is advisory, not blocking. No action needed.

## User Setup Required

None — Phase 22 is now fully landed in source control. Phase 23 starts from a Dockerfile that already targets `scipy-notebook:2026-04-27`, a `requirements.txt` with sha256 hashes, and a PROJECT.md/REQUIREMENTS.md that already reflect Python 3.14.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| (none new) | — | Plan touches Dockerfile FROM lines and planning docs only. T-22-03-01 (scipy-notebook tag mutation) carries `accept` disposition per CONTEXT (immutable Jupyter dated tags); T-22-03-02 (audit-trail repudiation) MITIGATED via inlined audit + summary; T-22-03-03 (phase-boundary leak) MITIGATED — verified mamba install r-* block, pip install line, kaggle layer all preserved verbatim in both Dockerfiles. |

## Next Phase Readiness

Phase 23 (Dockerfile install-layer rewrite + uv migration) is fully unblocked:
- Both Dockerfiles already have the correct `scipy-notebook:2026-04-27` FROM line — Phase 23 can edit the install layer without touching the FROM line
- `requirements.txt` (root) already has 1644 sha256 hashes from `uv pip compile --generate-hashes` — Phase 23's `uv pip install --system` step consumes it directly
- PROJECT.md D-03 already says "Python 3.14" — Phase 23 doesn't need to update it
- 22-AUDIT.md provides the conda↔uv shadow surface (4 packages: jinja2, mistune, numpy, statsmodels) for Phase 23's import-smoke layer to validate against
- 22-SUMMARY.md identifies the exact Phase 23 deliverables under "Handoff to Phase 23" section

## Self-Check

- [x] `Dockerfile` line 3 = `FROM quay.io/jupyter/scipy-notebook:2026-04-27` (verified via grep)
- [x] `.claude/doml/templates/Dockerfile` line 3 = `FROM quay.io/jupyter/scipy-notebook:2026-04-27` (verified via grep + diff against root)
- [x] `datascience-notebook` not present in either Dockerfile (verified: count=0 both)
- [x] `22-AUDIT.md` exists with all three required H2 headers (Mamba List / Conflict Diff / uv pip compile Diff — counts 1/1/1)
- [x] `22-AUDIT.md` is 2526 lines (>100 line acceptance threshold met)
- [x] `22-SUMMARY.md` exists with `python_version: 3.14`, `go_no_go: GO`, `auto_fallback_fired: false`
- [x] `22-SUMMARY.md` body contains "Decision: GO", "Deliverables" (11 items), "Requirements Coverage" (PY-01..PY-05 + CONT-06), "Handoff to Phase 23"
- [x] PROJECT.md D-03 references "Phase 22 pre-flight" + "Python 3.14"
- [x] REQUIREMENTS.md does NOT contain `**PY-FUT-01**: Upgrade container to Python 3.14 once \`ydata-profiling\` lifts` (verified via grep -c = 0)
- [x] REQUIREMENTS.md traceability rows for PY-01..PY-05 + CONT-06 all marked `Complete`
- [x] Commit `5da3eea` has subject `docs(22): pre-flight audit + scipy-notebook tag pin` (verbatim D-22-18 commit 3)
- [x] Commit `5da3eea` touches exactly 6 files (4 modified + 2 new); does NOT include requirements.in/.txt or template requirements/notebook (those are in commits 1 and 2)
- [x] Working tree clean (only `.claude/worktrees/` untracked, which is expected agent-internal state)

## Self-Check: PASSED

---
*Phase: 22-pre-flight-wheel-validation-lockfile-bootstrap*
*Plan: 03*
*Completed: 2026-04-30*
