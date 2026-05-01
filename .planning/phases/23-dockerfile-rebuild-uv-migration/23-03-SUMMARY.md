---
phase: 23-dockerfile-rebuild-uv-migration
plan: 03
subsystem: infra
tags: [docker, dockerfile, uv, buildkit, scipy-notebook, cache-mount, kaggle, mamba-removal]

# Dependency graph
requires:
  - phase: 22-pre-flight-wheel-validation-lockfile-bootstrap
    provides: scipy-notebook:2026-04-27 tag pin in both Dockerfiles' FROM lines, root requirements.txt with hashes, Python 3.14 validation
  - phase: 23-dockerfile-rebuild-uv-migration (Plan 23-01)
    provides: cleaned template requirements.in (pip-tools dropped, numpy<2.4 added)
  - phase: 23-dockerfile-rebuild-uv-migration (Plan 23-02)
    provides: regenerated template requirements.txt via uv pip compile with kaggle in resolved tree
provides:
  - Root Dockerfile rebuilt on single-stage uv pattern with BuildKit cache mount and inline import smoke
  - Template Dockerfile mirrors root structurally (CONT-08 mirror discipline) with standalone kaggle layer deleted
  - Both Dockerfiles R-free at the build level (mamba R block deleted from both)
  - BuildKit `# syntax=docker/dockerfile:1.7` pragma adopted in both files
  - uv 0.11.8 vendored from ghcr.io/astral-sh/uv (CONT-05) — NOT pip-installed
  - Full UV env block (6 vars) in both Dockerfiles
  - Single USER root install layer with cache mount + uv pip install --system + 11-import smoke + consolidated fix-permissions
  - Single USER ${NB_UID} drop at end (PITFALLS #9 — no root↔jovyan ping-pong)
affects: [23-04 (cold-cache build benchmark + docs sweep + install-script flag + MIGRATION-v1.6.md), 24-r-narrative-sweep (Dockerfile R-text already gone — Phase 24 owns workflows/notebooks/CLAUDE.md/AGENTS.md narrative blocks), 25-ci-smoke-test (build pattern Plan 25 will assert in CI)]

# Tech tracking
tech-stack:
  added:
    - uv 0.11.8 (vendored via COPY --from=ghcr.io/astral-sh/uv:0.11.8)
    - BuildKit cache mount (type=cache,target=/root/.cache/uv,sharing=locked)
    - Dockerfile syntax pragma 1.7 (required for cache mount portability)
  patterns:
    - Single-stage uv install layer (per research/ARCHITECTURE.md reference Dockerfile)
    - Inline in-build import smoke chained into the same RUN as the install (D-23-A3)
    - Consolidated fix-permissions sweep (single layer chain, not two separate layers — D-23-A2, PITFALLS #9)
    - Vendored uv from official Astral image (NOT pip install uv) — STACK.md "What NOT to Use"
    - `uv pip install --system` (additive), NEVER `uv pip sync` (PITFALLS #3 would prune conda jupyter stack)

key-files:
  created: []
  modified:
    - Dockerfile (root) — install layer rebuilt end-to-end on uv + cache mount + inline smoke; mamba R block deleted; line-1 comment + LABEL description drop R, bump 3.14
    - .claude/doml/templates/Dockerfile — mirrors root structurally; standalone kaggle pip-install layer deleted (kaggle now flows through unified `uv pip install -r requirements.txt`); same R-removal updates

key-decisions:
  - "Wholesale rewrite rather than surgical patch — install layer restructure spans USER topology, ENV block, RUN structure, mamba block deletion, comment, LABEL. A full rewrite against the reference Dockerfile in research/ARCHITECTURE.md is more verifiable than a series of targeted edits."
  - "UV_LINK_MODE=copy placed on its own indented continuation line (with `ENV \\` on the bare line above) rather than on the bare ENV line — needed for the plan's automated `grep -c '^    UV_' >= 6` check to pass and for individual `^    UV_LINK_MODE=copy` acceptance criteria. The plan's literal target text and acceptance grep were internally inconsistent; chose the version that satisfies the verifiable contracts."
  - "Per-task atomic commits (Task 1: root, Task 2: template) following parent prompt's 'Commit each task atomically' instruction, even though the plan's commit_strategy specified one combined commit. Per-task commits preserve traceability and the plan's `feat(23): ...` semantic intent is preserved in both messages."
  - "Standalone kaggle pip-install layer deleted only AFTER pre-flight check confirmed kaggle==2.1.0 is in the regenerated template lockfile from Plan 23-02. Without that check, deleting the layer would silently remove kaggle from the image."

patterns-established:
  - "Dockerfile install layer template: syntax pragma → FROM → LABEL → COPY uv from ghcr → ENV UV_* (6 vars) → USER root → COPY requirements.txt → RUN --mount=type=cache uv pip install --system + import smoke + fix-permissions chained → USER NB_UID → WORKDIR. Both root and template files follow this exact structure."
  - "Cross-file structural parity check: root and template Dockerfiles diff to zero lines (modulo a single optional kaggle-comment line in the template). CONT-08 mirror discipline enforced via `diff` command in acceptance criteria."

requirements-completed: [CONT-01, CONT-02, CONT-03, CONT-05, CONT-07, CONT-08]

# Metrics
duration: 3min
completed: 2026-05-01
---

# Phase 23 Plan 03: Dockerfile Install-Layer Rebuild on uv + scipy-notebook Summary

**Both root and template Dockerfiles rewritten end-to-end on the single-stage uv pattern: BuildKit cache mount on /root/.cache/uv, vendored uv 0.11.8, full UV env block, inline 11-import smoke, consolidated fix-permissions, mamba R block deleted, template's standalone kaggle layer deleted.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-01T02:10:42Z
- **Completed:** 2026-05-01T02:14:10Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Root `Dockerfile` rewritten on the single-stage uv pattern (29 lines → 40 lines, +11 net). Install layer is now a single `USER root` block with `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked uv pip install --system -r /tmp/requirements.txt && python -c "import …" && fix-permissions ${CONDA_DIR} && fix-permissions /home/${NB_USER}`, single drop to `USER ${NB_UID}` at end.
- Template `.claude/doml/templates/Dockerfile` mirrored to root structurally — same syntax pragma, same FROM, same LABEL block, same uv vendor, same UV env block, same install RUN, same USER topology. Only difference: one extra explanatory comment line above `USER root` clarifying that kaggle is resolved through requirements.txt (replacing the deleted standalone kaggle layer's intent).
- Template's standalone `RUN pip install --no-cache-dir kaggle` layer (lines 27-34 of v1.5 template) deleted — kaggle now flows through the unified `uv pip install` chain because Plan 23-02's regenerated template lockfile contains `kaggle==2.1.0`. Pre-flight grep confirmed kaggle in lockfile before deletion.
- mamba R block (`mamba install r-duckdb r-tidymodels r-renv r-umap`) deleted from BOTH Dockerfiles. scipy-notebook ships no conda R toolchain, so the block would fail the build anyway (D-23-C1).
- Line-1 comment in both files updated: `# DoML analysis environment — Python 3.13 + R 4.x + DuckDB + ML stack` → `# DoML analysis environment — Python 3.14 + DuckDB + ML stack`.
- LABEL description in both files updated: `"…with Python, R, and DuckDB"` → `"Reproducible ML analysis environment with Python and DuckDB"` (D-23-C2).
- LABEL maintainer preserved verbatim (`"DoML framework"`) per Discretion in 23-CONTEXT.md.
- BuildKit `# syntax=docker/dockerfile:1.7` pragma added as line 1 of both files (D-23-A4 — required for cache mount syntax portability across Docker versions).

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite root Dockerfile install layer** — `5d0cbba` (feat)
2. **Task 2: Rewrite template Dockerfile + delete standalone kaggle layer** — `6e214cf` (feat)

_Note: Per-task commits chosen over the plan's combined commit_strategy because the parent orchestrator prompt instructed "Commit each task atomically." Both messages preserve the plan's `feat(23): ...` semantic. The orchestrator owns the metadata commit (STATE.md / ROADMAP.md / REQUIREMENTS.md updates) — this executor does not run those._

## Files Created/Modified

- `Dockerfile` — Root analysis image build recipe (v1.6). Install layer rebuilt on uv + BuildKit cache mount + inline smoke + single fix-permissions sweep. R-free at build level. 29 lines → 40 lines.
- `.claude/doml/templates/Dockerfile` — Template Dockerfile shipped to `/doml-new-project` user projects. Mirrors root structurally. Standalone kaggle layer deleted. R-free at build level. 38 lines → 41 lines.

## Decisions Made

- **UV_LINK_MODE indentation:** placed on an indented continuation line under a bare `ENV \\` line, rather than on the `ENV` line itself. This satisfies both the per-var acceptance criteria (each requiring `^    UV_*` four-space-indented match) and the plan's own `[ "$(grep -c "^    UV_" Dockerfile)" -ge 6 ]` automated verify (which the plan's literal target text — `ENV UV_LINK_MODE=copy \\` on the bare line — would have failed at 5). The semantic D-23-A1 requirement is "all 6 UV vars present in the ENV block", which is preserved.
- **Per-task commits:** parent orchestrator prompt overrides the plan's combined `commit_strategy`. Both commits use `feat(23): ...` prefix per the plan's intent.
- **Wholesale rewrite over surgical edit:** the install layer restructure touches USER topology, ENV block (new), RUN structure, mamba deletion, line-1 comment, and LABEL description — a surgical patch is harder to verify than a full rewrite against the reference Dockerfile.
- **Pre-flight check before deleting kaggle layer:** `grep -E '^kaggle==' .claude/doml/templates/requirements.txt` confirmed `kaggle==2.1.0` in the resolved tree before the standalone layer was deleted (Plan 23-02 output verified).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] UV_LINK_MODE placement to satisfy plan's verification grep**
- **Found during:** Task 1 (root Dockerfile rewrite — verification step)
- **Issue:** The plan's `<action>` section showed `ENV UV_LINK_MODE=copy \\` on the bare ENV line (UV_LINK_MODE NOT 4-space-indented), with the other 5 UV_* vars on indented continuation lines. But the plan's per-var acceptance criteria (lines 5-10) required `grep -c '^    UV_LINK_MODE=copy' == 1` (four-space-indented), and the plan's automated `<verify>` block required `grep -c '^    UV_' >= 6` (i.e., all 6 indented). The literal target text would yield 5 indented UV_ lines (UV_LINK_MODE on the bare ENV line), failing both criterion #5 and the automated verify.
- **Fix:** Restructured the ENV block to put `ENV \\` on its own bare line, with all 6 UV_* vars on 4-space-indented continuation lines. Net Dockerfile +1 line.
- **Files modified:** Dockerfile (root), .claude/doml/templates/Dockerfile (mirrored)
- **Verification:** Plan's automated verify (`grep -c "^    UV_" >= 6`) now passes with `grep -c == 6` on both files. All 6 individual per-var criteria now pass. Semantic D-23-A1 ("full UV env block") preserved.
- **Committed in:** 5d0cbba (Task 1) for root; 6e214cf (Task 2) for template (mirrored)

**Note on `uv pip sync` grep criterion:** The plan's `<action>` text explicitly includes the comment line `# Use \`uv pip install\` (additive), NOT \`uv pip sync\` — sync would prune conda-shipped jupyterlab/notebook/ipykernel/nbconvert/nbformat and break the kernel (PITFALLS #3).` The plan's grep `! grep -q "uv pip sync"` would match that comment text and "fail", but the plan's `<action>` text mandates the comment. The semantic intent (no `uv pip sync` *command* used in any RUN) is preserved — the only string match is in the PITFALLS warning comment, which the plan itself prescribes. This is a plan-internal inconsistency that resolves by treating the `<action>` text as source of truth. Not counted as a deviation since no file content was changed away from the plan's literal target.

---

**Total deviations:** 1 auto-fixed (1 blocking — Rule 3, plan-internal inconsistency between literal target text and verification grep)
**Impact on plan:** No scope creep. The single fix made the plan's own automated verify pass, with semantic D-23-A1 intent preserved (all 6 UV vars present in the ENV block). Mirrored to template Dockerfile to maintain CONT-08 cross-file parity.

## Issues Encountered

- Initial worktree branch was based on `d5e299f` (a more recent commit on main than expected). Reset to `08633f4` (Plan 23-02 completion) per the orchestrator's `<worktree_branch_check>` instruction. After reset, working tree was clean and Plan 23-01 + 23-02 outputs (cleaned template requirements.in, uv-generated template requirements.txt with kaggle==2.1.0) were verified in place before Task 1 began.

## Verification Performed

- All 23 acceptance criteria for Task 1 (root Dockerfile) PASS, including: line-1 syntax pragma, line-2 R-free comment, FROM scipy-notebook:2026-04-27 unchanged, COPY uv:0.11.8, full 6-var UV env block, BuildKit cache mount, `uv pip install --system`, inline 11-import smoke (`duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller`), single USER root, single USER ${NB_UID} drop, mamba install absent, LABEL maintainer preserved, LABEL description R-free, no R 4.x narrative residue, WORKDIR ${PROJECT_ROOT}, line count in 35-42 sanity bound (40 lines), no `uv pip sync` command (only string match is the prescribed PITFALLS comment), trailing newline.
- All 20 acceptance criteria for Task 2 (template Dockerfile) PASS, including all of the above + standalone kaggle layer deleted (`pip install --no-cache-dir kaggle` count == 0), no `pip install --no-cache-dir` anywhere (uv-only install path), line count in 36-43 sanity bound (41 lines).
- **Cross-file structural parity check:** `diff <(grep -v 'kaggle CLI' Dockerfile) <(grep -v 'kaggle CLI' .claude/doml/templates/Dockerfile)` returns zero output. Root and template Dockerfiles are byte-identical except for the single optional kaggle-comment line in the template — confirms CONT-08 mirror discipline.
- Plan's automated `<verify>` block for both tasks PASS.
- `git diff --name-only HEAD~2..HEAD` shows exactly two files changed: `Dockerfile` and `.claude/doml/templates/Dockerfile`. No collateral changes.
- Docker reachable on dev host (`docker info` succeeds) — required preflight per critical_constraints. Note: NO actual `docker compose build` invoked here (Plan 23-04 owns the cold-cache build benchmark + budget gate).

## User Setup Required

None — no external service configuration required for this plan. The Dockerfile install layer is a structural rewrite verified by static grep checks. The actual build proof (cold-cache `docker compose build --no-cache` under 5 minutes, runtime kernel smoke, jupyter --version inside container) is Plan 23-04's deliverable.

## Next Phase Readiness

- Plan 23-04 (final phase plan) can now run: docs sweep (CLAUDE.md REPR-04, AGENTS.md "Pinned dependencies"), install-script defensive `DOCKER_BUILDKIT=1` flag (install.sh + install.ps1), `MIGRATION-v1.6.md` authorship, cold-cache build benchmark, container-startup smoke, phase summary.
- Phase 24 (R narrative sweep) is unblocked at the Dockerfile level — both Dockerfiles are R-free as of this plan. Phase 24 owns the broader R sweep across workflows / notebooks / CLAUDE.md narrative / AGENTS.md narrative / language-prompt removal / config-validation gate.
- Phase 25 (CI smoke test) consumes the build pattern established here — same `docker compose build` invocation, same import smoke list, same scipy-notebook tag pin.
- **No blockers** for Plan 23-04 entry.

## Self-Check: PASSED

- Files exist:
  - `Dockerfile` — FOUND
  - `.claude/doml/templates/Dockerfile` — FOUND
  - `.planning/phases/23-dockerfile-rebuild-uv-migration/23-03-SUMMARY.md` — FOUND
- Commits exist:
  - `5d0cbba` (Task 1: root Dockerfile) — FOUND
  - `6e214cf` (Task 2: template Dockerfile) — FOUND
- Content claims verified:
  - Root Dockerfile: 40 lines (in 35-42 sanity bound) — PASS
  - Template Dockerfile: 41 lines (in 36-43 sanity bound) — PASS
  - Cross-file structural parity (modulo kaggle comment) — PASS
  - Both files have 6 indented UV_ vars — PASS
  - Both files have BuildKit cache mount — PASS
  - Both files mamba-free — PASS
  - Template's standalone kaggle layer deleted — PASS
  - Exactly 2 files changed in this plan (`Dockerfile` and `.claude/doml/templates/Dockerfile`) — PASS

---
*Phase: 23-dockerfile-rebuild-uv-migration*
*Completed: 2026-05-01*
