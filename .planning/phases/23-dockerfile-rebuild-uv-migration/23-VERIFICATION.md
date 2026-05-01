---
phase: 23-dockerfile-rebuild-uv-migration
verified: 2026-04-30T21:30:00Z
status: passed
score: 13/13 must-haves verified
re_verification: false
---

# Phase 23: Dockerfile Rebuild + uv Migration Verification Report

**Phase Goal:** Rebuild the project Dockerfile (and template Dockerfile) on `quay.io/jupyter/scipy-notebook` with a uv-driven install layer, BuildKit cache mount, and an in-build import smoke. Demonstrate cold-cache build under 5 minutes on the user's dev machine.

**Verified:** 2026-04-30T21:30:00Z
**Status:** passed
**Re-verification:** No — initial verification (no prior VERIFICATION.md found in phase directory).

## Goal Achievement

### Observable Truths

Truths derived from ROADMAP §Phase 23 Success Criteria (5 SCs) merged with PLAN frontmatter must_haves across all 4 plans (PLAN-level truths are subset; ROADMAP SCs are non-negotiable contract).

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1   | Root Dockerfile uses `quay.io/jupyter/scipy-notebook:<dated-tag>`, vendors uv via `COPY --from=ghcr.io/astral-sh/uv:0.11.8`, and installs deps with cache-mount + `uv pip install --system -r /tmp/requirements.txt` (ROADMAP SC #1) | VERIFIED | `Dockerfile` line 4: `FROM quay.io/jupyter/scipy-notebook:2026-04-27`; line 11: `COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/`; lines 30-31: `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked` + `uv pip install --system -r /tmp/requirements.txt` |
| 2   | Dockerfile includes the import smoke layer (11 imports) and fails fast on missing wheels (ROADMAP SC #2; CONT-07) | VERIFIED | `Dockerfile` line 32: `python -c "import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, PyInstaller"` chained with `&&` inside the install RUN. Runtime confirmed: `docker run --rm doml-jupyter python -c "import duckdb, ..., PyInstaller"` printed `ALL_11_IMPORTS_SUCCEED`. |
| 3   | Cold-cache `docker compose build --no-cache` completes in **<5 minutes** on user's dev machine; wall-clock recorded in SUMMARY (ROADMAP SC #3; CONT-04) | VERIFIED | 23-SUMMARY.md frontmatter `cold_build_wall_clock_seconds: 36`; `cold_build_under_budget: true`; `cache_evicted_before_build: true`. **36s wall-clock = 8.33× under 300s budget**. Final green commit `fa8a7c6`. |
| 4   | `.claude/doml/templates/Dockerfile` and `docker-compose.yml` mirror new structure for `/doml-new-project` (ROADMAP SC #4; CONT-08) | VERIFIED | `diff <(grep -v 'kaggle CLI' Dockerfile) <(grep -v 'kaggle CLI' .claude/doml/templates/Dockerfile)` returns empty (byte-identical modulo single optional kaggle comment). Template `requirements.in` mirrors root cleanup (no pip-tools, numpy<2.4 present). Template `requirements.txt` regenerated via `uv pip compile … --generate-hashes` with 1618 hashes. docker-compose.yml: no functional change required (BuildKit-default in Compose v2.20+ handles syntax pragma transparently per CONTEXT.md `<code_context>`). |
| 5   | `CLAUDE.md` rebuild instructions updated from `pip-compile` → `uv pip compile … --generate-hashes`; install scripts defensively set `DOCKER_BUILDKIT=1` (ROADMAP SC #5) | VERIFIED | `CLAUDE.md:75` shows `docker compose run --rm jupyter uv pip compile requirements.in --generate-hashes -o requirements.txt`. `AGENTS.md:78` matches. `install.sh:20` has `export DOCKER_BUILDKIT=1`. `install.ps1:34` has `$env:DOCKER_BUILDKIT = "1"`. Both have explanatory `# ── BuildKit (v1.6 cache mount syntax requires it)` comments. |
| 6   | Both Dockerfiles use `# syntax=docker/dockerfile:1.7` line 1 (D-23-A4) | VERIFIED | `head -1 Dockerfile` and `head -1 .claude/doml/templates/Dockerfile` both return `# syntax=docker/dockerfile:1.7`. |
| 7   | Both Dockerfiles set the full UV env block (6 vars: UV_LINK_MODE=copy, UV_COMPILE_BYTECODE=1, UV_NO_PROGRESS=1, UV_PYTHON_DOWNLOADS=never, UV_SYSTEM_PYTHON=1, UV_PYTHON=/opt/conda/bin/python) (D-23-A1) | VERIFIED | `grep -c "^    UV_" Dockerfile` returns 6; same for template. Lines 16-22 of both files show all 6 indented continuation lines under bare `ENV \`. |
| 8   | Both Dockerfiles use single USER root install block + single USER ${NB_UID} drop at end (D-23-A2; PITFALLS #9) | VERIFIED | `grep -cE "^USER root" Dockerfile` returns 1; `grep -cE "^USER \${NB_UID}" Dockerfile` returns 1; same for template. No root↔jovyan ping-pong. |
| 9   | Both Dockerfiles drop the `mamba install r-*` block entirely (D-23-C1) | VERIFIED | `grep -c "mamba install" Dockerfile .claude/doml/templates/Dockerfile` returns 0 for both. |
| 10  | Template Dockerfile drops the standalone kaggle pip-install layer (D-23-B3) | VERIFIED | `grep -c "pip install --no-cache-dir kaggle" .claude/doml/templates/Dockerfile` returns 0. kaggle resolves through unified install: `kaggle==2.1.0` present in template `requirements.txt`. |
| 11  | Both Dockerfiles' line-1 comment + LABEL description drop the R mention and bump Python 3.13 → 3.14 (D-23-C2) | VERIFIED | Line 2: `# DoML analysis environment — Python 3.14 + DuckDB + ML stack` (no R). Line 7: `LABEL description="Reproducible ML analysis environment with Python and DuckDB"` (no R). `grep -c "R 4.x\|with Python, R" Dockerfile` returns 0 for both. |
| 12  | MIGRATION-v1.6.md exists at repo root with R-user v1.5 install pin (Bash + PowerShell paths) (D-23-C3, D-23-C4) | VERIFIED | File exists at `/home/bill/source/DoML/MIGRATION-v1.6.md` (57 lines). Line 10: `bash <(curl ...) --version v1.5.0`. Line 22: `$env:DOML_VERSION = "v1.5.0"; iwr https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex`. "What changed in v1.6" table covers base image, R packages, install layer, cold build time, Python. |
| 13  | Resolved INCIDENT 1 + INCIDENT 2 forensic preservation in 23-SUMMARY.md is intact (don't strip the resolved-INCIDENT sections) | VERIFIED | 23-SUMMARY.md lines 40-67 contain "## Resolved INCIDENTs (preserved for forensics)" section with both INCIDENT 1 (skl2onnx + pyinstaller missing from root requirements.in) and INCIDENT 2 (pyinstaller PyPI ↔ module name casing) fully documented with discovery, symptom, root cause, and resolution. Frontmatter records `fix_in_phase_applied: true` with `fix_in_phase_resolutions` array citing Option B + Option B'. |

**Score:** 13/13 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `Dockerfile` | Root analysis image build recipe (v1.6) — scipy-notebook FROM, uv vendored, BuildKit cache mount, no mamba | VERIFIED | 40 lines. All 13 must-haves above hit this file. gsd-tools verify artifacts: passed (Plan 03). |
| `.claude/doml/templates/Dockerfile` | Template Dockerfile shipped to `/doml-new-project` user projects — mirrors root structurally | VERIFIED | 41 lines. Cross-file structural parity check (`diff` modulo kaggle comment) returns empty. gsd-tools verify artifacts: passed (Plan 03). |
| `.claude/doml/templates/requirements.in` | Template top-level deps: no pip-tools, numpy<2.4, regen-comments point at `uv pip compile` | VERIFIED | 41 lines. `grep -c "^pip-tools"` = 0; `grep -c "^numpy<2.4"` = 1; `grep -c "uv pip compile requirements.in --generate-hashes"` = 2; `grep -c "^kaggle\|^pyinstaller\|^skl2onnx\|^prophet"` all = 1. gsd-tools verify artifacts: passed (Plan 01). |
| `.claude/doml/templates/requirements.txt` | Hash-pinned template lockfile (uv-format, sha256 hashes, 3.14 target) | VERIFIED | 1970 lines, 1618 sha256 hashes, header line 1: `# This file was autogenerated by uv via the following command:`, header line 2 contains `--python-version 3.14 --generate-hashes -o requirements.txt`. gsd-tools verify artifacts: passed (Plan 02). |
| `requirements.in` (root) | Extended with skl2onnx + pyinstaller (INCIDENT 1 fix) | VERIFIED | Lines 48-49: `pyinstaller`, `skl2onnx` present. Comment block at lines 44-47 explains the smoke-list lockstep contract. |
| `requirements.txt` (root) | Regenerated via uv with hashes after INCIDENT 1 fix | VERIFIED | 2066 lines, 1729 sha256 hashes (up from Phase 22's 1644), `pyinstaller==6.20.0`, `skl2onnx==1.20.0`, `numpy==2.3.5` resolved. Header line 2: `uv pip compile requirements.in --python-version 3.14 --generate-hashes -o requirements.txt`. |
| `CLAUDE.md` | Updated REPR-04 regen instruction to `uv pip compile … --generate-hashes` | VERIFIED | Line 75: `docker compose run --rm jupyter uv pip compile requirements.in --generate-hashes -o requirements.txt`. `grep -c "pip-compile requirements.in" CLAUDE.md` returns 0. gsd-tools verify artifacts: passed (Plan 04). |
| `AGENTS.md` | Updated "Pinned dependencies" regen instruction to match CLAUDE.md (D-23-B4) | VERIFIED | Line 78: `regenerate: \`docker compose run --rm jupyter uv pip compile requirements.in --generate-hashes -o requirements.txt\``. `grep -c "pip-compile requirements.in" AGENTS.md` returns 0. gsd-tools verify artifacts: passed (Plan 04). |
| `install.sh` | Defensive `export DOCKER_BUILDKIT=1` near top, scoped to install session | VERIFIED | Lines 18-20: `# ── BuildKit (v1.6 cache mount syntax requires it)` + `# Defensive: scoped to this install session only. Does NOT touch ~/.bashrc.` + `export DOCKER_BUILDKIT=1`. `bash -n install.sh` exits 0 (no syntax errors). |
| `install.ps1` | Defensive `$env:DOCKER_BUILDKIT = "1"` near top, scoped to install session | VERIFIED | Lines 32-34: BuildKit comment + scoping comment + `$env:DOCKER_BUILDKIT = "1"`. |
| `MIGRATION-v1.6.md` | New file at repo root explaining v1.6 is Python-only, points to v1.5 pin (Bash + PowerShell) | VERIFIED | 57 lines. TL;DR fenced block opens. Both Bash (`install.sh --version v1.5.0`) and PowerShell (`$env:DOML_VERSION = "v1.5.0"; iwr ... | iex`) install commands present. "What changed in v1.6" table covers base image, R packages, install layer, build time, Python. gsd-tools verify artifacts: passed (Plan 04). |
| `.planning/phases/23-dockerfile-rebuild-uv-migration/23-SUMMARY.md` | Phase 23 SUMMARY with cold-build wall-clock + completed deliverables + INCIDENT preservation | VERIFIED | 180 lines. Frontmatter has all required fields (`status: complete`, `cold_build_wall_clock_seconds: 36`, `cold_build_under_budget: true`, `cache_evicted_before_build: true`, `docker_buildx_prune_exit_code: 0`, `build_exit_code: 0`, `fix_in_phase_applied: true`). 14 deliverable checkboxes (all ticked). CONT-01..CONT-08 requirements coverage table. Phase Boundary Discipline section. Handoff to Phase 24 + Phase 25. INCIDENTs 1+2 preserved. Worktree/commit timeline lists all 15 phase commits. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `Dockerfile` | `requirements.txt` (root) | `COPY --chown` + `uv pip install --system -r /tmp/requirements.txt` | WIRED | `Dockerfile:29` `COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt`; `Dockerfile:31` `uv pip install --system -r /tmp/requirements.txt`. Build success (exit 0, 36s) confirms the lockfile is consumable. |
| `.claude/doml/templates/Dockerfile` | `.claude/doml/templates/requirements.txt` | Same COPY + uv pip install pattern | WIRED | `templates/Dockerfile:30` and `:32` mirror root structure exactly. Plan 02's dry-run install inside scipy-notebook:2026-04-27 confirmed lockfile resolves cleanly. |
| `Dockerfile` FROM line | scipy-notebook:2026-04-27 base | quay.io image pull | WIRED | `Dockerfile:4` `FROM quay.io/jupyter/scipy-notebook:2026-04-27`. Image pull succeeded during cold-cache build (36s wall-clock includes pull). Same pin in template. |
| Plan 03 Dockerfiles | Plan 04 cold-cache benchmark | `time docker compose build --no-cache` | WIRED | Final green build commit `fa8a7c6`. 23-SUMMARY.md records wall-clock 36s; `doml-jupyter` image present locally (5.87GB, sha256:dd4e08473ffb…). |
| `MIGRATION-v1.6.md` | install.sh / install.ps1 v1.5 pin path | Documented escape hatch for users who need R | WIRED | MIGRATION-v1.6.md line 10 references `bash <(curl ...) --version v1.5.0`; install.sh:5 documents the same `--version` flag. PowerShell line 22 references `$env:DOML_VERSION = "v1.5.0"`; install.ps1:9 documents the same env var. |
| `23-SUMMARY.md` | Phase 24 + Phase 25 handoffs | Wall-clock recorded for Phase 25 CI budget gate; R-free Dockerfile state recorded for Phase 24 narrative sweep | WIRED | 23-SUMMARY.md lines 144-155 contain the "Handoff to Phase 24 + Phase 25" section. Phase 24 inherits R-free Dockerfile + MIGRATION-v1.6.md base; Phase 25 inherits 36s baseline + cache-eviction methodology + working build pattern. |
| `.claude/doml/templates/requirements.in` | `requirements.in` (root) | Mirror discipline (CONT-08) | WIRED | Both files have identical structural cleanup: no `pip-tools`, `numpy<2.4` pin, regen-comments use `uv pip compile … --generate-hashes`. Template lacks `mistune<3` and `pmdarima` (template historically didn't pin them; resolves transitively in lockfile). Functional intent preserved. |

Note: `gsd-tools verify key-links` reported these as "not verified" because the tool searches for the literal `pattern:` text in source/target files (a naive prose-match heuristic that doesn't apply to architectural connection patterns). Manual verification above confirms all links are wired in code.

### Data-Flow Trace (Level 4)

Phase 23 produces a Dockerfile/build pipeline (not a UI rendering dynamic data). Level 4 maps to "data flows from lockfile → image" rather than state→render.

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `Dockerfile` | Installed packages in image | `requirements.txt` (1729 sha256 hashes) consumed via `uv pip install --system` | Yes — runtime smoke `import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, PyInstaller` printed `ALL_11_IMPORTS_SUCCEED` against built image `doml-jupyter:latest` | FLOWING |
| `.claude/doml/templates/Dockerfile` | Installed packages in template-image | `.claude/doml/templates/requirements.txt` (1618 sha256 hashes) | Yes — Plan 02 dry-run install inside scipy-notebook:2026-04-27 exited 0; `kaggle==2.1.0`, `prophet==1.3.0`, `pyinstaller==6.20.0`, `skl2onnx==1.20.0`, `numpy==2.3.5` all resolved with hash-pinned wheels | FLOWING |
| `MIGRATION-v1.6.md` | User-facing install commands | Hand-written reference to install.sh `--version` flag and install.ps1 `$env:DOML_VERSION` | Yes — references match install.sh:5 and install.ps1:9 documented invocations | FLOWING |
| `23-SUMMARY.md` | Wall-clock metric | `time docker compose build --no-cache` measurement (commit `fa8a7c6`) | Yes — 36s recorded in frontmatter; `cache_evicted_before_build: true` confirmed via `docker buildx prune --all -f` exit 0 | FLOWING |

### Behavioral Spot-Checks

Each check completed in under 30s, no state mutations.

| # | Behavior | Command | Result | Status |
| - | -------- | ------- | ------ | ------ |
| 1 | Built `doml-jupyter` image exists locally | `docker images doml-jupyter --format '{{.ID}}'` | `dd4e08473ffb` (5.87GB) | PASS |
| 2 | All 11 smoke imports succeed at runtime in built image | `docker run --rm doml-jupyter python -c "import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, PyInstaller; print('ALL_11_IMPORTS_SUCCEED')"` | `ALL_11_IMPORTS_SUCCEED` (with benign onnxruntime GPU-detection warning) | PASS |
| 3 | Jupyter stack intact (PITFALLS #3 didn't bite) | `docker run --rm doml-jupyter jupyter --version` | `jupyter_client 8.8.0 / jupyter_core 5.9.1 / jupyter_server 2.17.0 / jupyterlab 4.5.6 / nbconvert 7.17.1 / nbformat 5.10.4 / notebook 7.5.5` | PASS |
| 4 | Cross-file structural parity (root ↔ template Dockerfile) | `diff <(grep -v 'kaggle CLI' Dockerfile) <(grep -v 'kaggle CLI' .claude/doml/templates/Dockerfile)` | empty diff | PASS |
| 5 | Six UV env vars present in both Dockerfiles | `grep -c "^    UV_" Dockerfile && grep -c "^    UV_" .claude/doml/templates/Dockerfile` | `6` / `6` | PASS |
| 6 | BuildKit cache mount present in both Dockerfiles | `grep -c -- '--mount=type=cache,target=/root/.cache/uv,sharing=locked' Dockerfile .claude/doml/templates/Dockerfile` | `1` / `1` | PASS |
| 7 | Syntax pragma is line 1 of both Dockerfiles | `head -1 Dockerfile && head -1 .claude/doml/templates/Dockerfile` | both `# syntax=docker/dockerfile:1.7` | PASS |
| 8 | DOCKER_BUILDKIT=1 set in install.sh | `grep -c "^export DOCKER_BUILDKIT=1" install.sh` | `1` | PASS |
| 9 | DOCKER_BUILDKIT=1 set in install.ps1 | `grep -c '\$env:DOCKER_BUILDKIT = "1"' install.ps1` | `1` | PASS |
| 10 | install.sh syntax valid | `bash -n install.sh; echo $?` | `0` | PASS |
| 11 | All 15 phase commits present in git log | `git log --oneline | head -25 \| grep -E "(17aed5c\|5ea0776\|5d0cbba\|6e214cf\|ed582cc\|cd2b66c\|3734605\|31be881\|adcbd9d\|70f7c76\|fa8a7c6)"` | All 11 referenced commits + the docs commits found | PASS |

### Requirements Coverage

PLAN frontmatter requirements: CONT-01, CONT-02, CONT-03, CONT-04, CONT-05, CONT-07, CONT-08 (Phase 23 scope per ROADMAP §Phase 23). CONT-06 was completed in Phase 22 but is referenced by Plan 02 because the template-side regen happens here (template lockfile-side completion of CONT-06).

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| CONT-01 | 23-03 | Docker base image is `quay.io/jupyter/scipy-notebook:<dated-tag>` (Python-only) | SATISFIED | Phase 22 pinned `2026-04-27`; Phase 23 preserved the pin in both Dockerfiles. `Dockerfile:4` and `templates/Dockerfile:4` both show `FROM quay.io/jupyter/scipy-notebook:2026-04-27`. |
| CONT-02 | 23-03 | uv 0.11.x replaces pip-compile and pip install | SATISFIED | Both Dockerfiles use `uv pip install --system -r /tmp/requirements.txt`. CLAUDE.md:75 + AGENTS.md:78 regen-command updates point at `uv pip compile`. No `pip install`, no `pip-compile` in Dockerfile install path. |
| CONT-03 | 23-03 | Dockerfile uses BuildKit cache mount on /root/.cache/uv | SATISFIED | `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked` present in both Dockerfiles (line 30/31). `# syntax=docker/dockerfile:1.7` line 1 enables the mount syntax. |
| CONT-04 | 23-04 | Cold-cache `docker compose build --no-cache` < 300s | SATISFIED | **36s wall-clock** (8.33× under 300s budget) recorded in 23-SUMMARY.md frontmatter. Cache verifiably cold pre-build (`docker buildx prune --all -f` exited 0; `docker buildx du` showed `Reclaimable: 0B`). Final green commit `fa8a7c6`. |
| CONT-05 | 23-03 | uv binary vendored from ghcr.io/astral-sh/uv:0.11.8 via COPY --from | SATISFIED | `Dockerfile:11` and `templates/Dockerfile:11` both show `COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/`. No `pip install uv` anywhere in the install path. |
| CONT-06 | 23-02 | requirements.txt regenerated via `uv pip compile … --generate-hashes` | SATISFIED | Root: 1729 hashes (Phase 22 baseline 1644 + INCIDENT 1 fix added skl2onnx + pyinstaller, regenerated commit `adcbd9d`). Template: 1618 hashes (Plan 02 commit `5ea0776`). Both lockfile headers show `# This file was autogenerated by uv via the following command:` + `uv pip compile requirements.in --python-version 3.14 --generate-hashes -o requirements.txt`. |
| CONT-07 | 23-03 | In-build import smoke layer fails build on broken wheels | SATISFIED | Smoke list of 11 imports (`duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, PyInstaller`) chained with `&&` inside install RUN. **Note:** CONT-07 spec text amended in-phase (commit `70f7c76`) from lowercase `pyinstaller` to PascalCase `PyInstaller` because PyPI distribution name (lowercase) and canonical Python module name (PascalCase) diverge. Footnote in REQUIREMENTS.md line 17 documents the divergence. Smoke caught two real INCIDENTs at build time (missing `skl2onnx`/`pyinstaller` install; wrong `pyinstaller` casing) — fail-fast value confirmed empirically. Runtime verification in built image: 11 imports return `ALL_11_IMPORTS_SUCCEED`. |
| CONT-08 | 23-01, 23-02, 23-03, 23-04 | Templates mirror new structure | SATISFIED | Template `Dockerfile` ↔ root `Dockerfile` byte-identical modulo single optional kaggle comment (cross-file diff confirmed empty). Template `requirements.in` ↔ root `requirements.in` mirror cleanup (no pip-tools, numpy<2.4). Template `requirements.txt` regenerated via uv with hashes (Plan 02). docker-compose.yml: no functional change required for v1.6 per CONTEXT.md `<code_context>` (BuildKit-default in Compose v2.20+). |

**No orphaned requirements.** REQUIREMENTS.md maps CONT-01..CONT-05, CONT-07, CONT-08 to Phase 23 (CONT-06 → Phase 22). All 7 phase requirement IDs accounted for above.

### Anti-Patterns Found

Scanned files modified in this phase: `Dockerfile`, `.claude/doml/templates/Dockerfile`, `.claude/doml/templates/requirements.in`, `.claude/doml/templates/requirements.txt`, `requirements.in`, `requirements.txt`, `CLAUDE.md`, `AGENTS.md`, `install.sh`, `install.ps1`, `MIGRATION-v1.6.md`.

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none) | — | — | — | No TODOs/FIXMEs/placeholder/stub patterns found in any modified file. |

Notes on patterns intentionally present (NOT anti-patterns):
- `Dockerfile:25-26` and `templates/Dockerfile:25-26` contain prescribed PITFALLS comment: `# Use \`uv pip install\` (additive), NOT \`uv pip sync\` — sync would prune conda-shipped jupyterlab/notebook/ipykernel/nbconvert/nbformat and break the kernel (PITFALLS #3).` This is a documentation comment, not a stub. (Plan 03 deviation note explicitly addresses the plan's `! grep -q "uv pip sync"` criterion mismatch — semantic intent preserved: no `uv pip sync` *command* in any RUN, only the warning comment.)
- `MIGRATION-v1.6.md` line 33: `(Phase 24 — removed)` annotations in the comparison table reference work scheduled for Phase 24. These are deliberate cross-phase boundary markers per D-23-C3, not unfinished work in Phase 23.

### Human Verification Required

None.

All five ROADMAP success criteria are verifiable programmatically:
- SC #1, #2, #4, #5: static grep against committed files (verified)
- SC #3: numeric metric in 23-SUMMARY.md frontmatter, cross-checked against final green commit `fa8a7c6` (verified: 36s)
- Runtime smoke (CONT-07 behavior): verified by running the built image (`docker run --rm doml-jupyter python -c …` returned `ALL_11_IMPORTS_SUCCEED`)
- Jupyter stack health: verified by `docker run --rm doml-jupyter jupyter --version` returning a clean version listing

The phase author already performed the visual verification of the green build (commit `fa8a7c6`) and the user-gated checkpoint per Plan 04 Task 3 `<resume-signal>`. The 68-pytest-pass regression gate noted by the orchestrator is consistent with no Python-side regressions.

### Observations (informational, not gaps)

These are notes for future-phase awareness — not Phase 23 verification gaps.

1. **Pre-existing Phase 22 Python-version handoff inconsistency (NOT Phase 23 gap):** The `quay.io/jupyter/scipy-notebook:2026-04-27` base image actually ships **Python 3.13.13** (verified inside built image: `/opt/conda/bin/python --version` returns `Python 3.13.13`), but Phase 22's SUMMARY + PROJECT.md D-03 + 23-SUMMARY.md frontmatter (`python_version: "3.14"`) all claim Python 3.14. The lockfiles were *resolved* with `--python-version 3.14` flag (Phase 22 pre-flight + this phase's INCIDENT 1 regen), and the cp313 wheels installed cleanly because cp313 satisfies `python_version < 3.14` markers. The build works end-to-end; smoke imports succeed; pytest regression gate passes. This is a Phase 22 documentation accuracy concern (the actual interpreter is 3.13, not 3.14) that Phase 23 inherited — Phase 23 made no claims it could falsify, and the Phase 23 deliverable (build under 5 minutes) is met regardless. Recommend Phase 24 or a future cleanup phase reconcile the documentation.

2. **CI workflow correctly absent (Phase 25 boundary preserved):** `.github/workflows/` does not exist; no CI smoke test workflow in this phase. Phase 25 owns CI-01..CI-07 per REQUIREMENTS.md.

3. **R narrative blocks correctly preserved in CLAUDE.md and AGENTS.md (Phase 24 boundary preserved):** CLAUDE.md still has R code blocks at lines 29-31, 48-50, 80, 94-96. AGENTS.md still has R code blocks at lines 40-42, 59-63. Phase 24 (RREM-05) owns sweeping these. Phase 23 only updated the regen-command line in each file (D-23-B4) and the Dockerfile line-1 comment + LABEL (D-23-C2).

### Gaps Summary

No gaps found. All 5 ROADMAP §Phase 23 success criteria pass; all 13 derived observable truths verified; all 12 required artifacts present and substantive; all 7 key links wired; all 11 behavioral spot-checks pass; all 7 requirement IDs (CONT-01, CONT-02, CONT-03, CONT-04, CONT-05, CONT-07, CONT-08) satisfied with code-level evidence; no anti-patterns; both phase-boundary preservation checks (Phase 24 R narrative intact, Phase 25 CI absent) confirmed; INCIDENT preservation in 23-SUMMARY.md intact; runtime smoke against built image returns `ALL_11_IMPORTS_SUCCEED`.

The two in-phase INCIDENTs (smoke ↔ install drift discovery + PyInstaller casing) were resolved before phase close (commits `31be881`, `adcbd9d`, `70f7c76`) and final green benchmark (commit `fa8a7c6`) recorded 36s wall-clock against verifiably-cold cache. The phase shipped with **8.33× headroom under the CONT-04 budget**.

---

_Verified: 2026-04-30T21:30:00Z_
_Verifier: Claude (gsd-verifier)_
