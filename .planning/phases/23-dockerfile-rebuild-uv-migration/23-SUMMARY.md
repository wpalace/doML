---
phase: 23-dockerfile-rebuild-uv-migration
status: complete
completed: 2026-05-01
cold_build_wall_clock_seconds: 36
budget_seconds: 300
ratio_under_budget: 8.33
cold_build_under_budget: true
cache_evicted_before_build: true
docker_buildx_prune_exit_code: 0
build_exit_code: 0
fix_in_phase_applied: true
fix_in_phase_resolutions:
  - "Option B — added skl2onnx + pyinstaller to root requirements.in; regenerated root lockfile via uv pip compile --generate-hashes inside scipy-notebook:2026-04-27 / Python 3.14"
  - "Option B' — corrected smoke-list casing pyinstaller → PyInstaller in both Dockerfiles + CONT-07 + 23-CONTEXT.md (PyPI distribution name vs canonical Python module name divergence)"
base_image: quay.io/jupyter/scipy-notebook:2026-04-27
python_version: "3.14"
uv_version: 0.11.8
---

# Phase 23 Summary — Dockerfile Rebuild + uv Migration

**Decision: GREEN** — cold-cache `docker compose build --no-cache` completes in **36 seconds** against a 300-second budget (8.33× under budget). All 11 smoke imports succeed (`duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, PyInstaller`). Image `doml-jupyter` builds cleanly. BuildKit cache verifiably cold pre-build (`docker buildx prune --all -f` exited 0; `docker buildx du` showed `Reclaimable: 0B`). Phase 23 closes; Phases 24 (R sweep) and 25 (CI smoke + automated 300s gate) unblock.

## Cold-cache benchmark (final green run)

| Metric | Value |
|---|---|
| Command | `time docker compose build --no-cache` (with `DOCKER_BUILDKIT=1`) |
| **Wall-clock** | **36 seconds** |
| Budget (CONT-04) | 300 seconds |
| Ratio under budget | 8.33× headroom |
| Cache eviction | `docker buildx prune --all -f` exited 0 (verified cold; post-prune `docker buildx du` = `Reclaimable: 0B`) |
| Build exit code | 0 |
| Image built | `doml-jupyter` (sha256:dd4e08473ffb…) |
| Method | Single timed run (D-23-D1; not borderline so median-of-3 escalation not triggered) |

Per D-23-D2: wall-clock-only format. No per-stage breakdown required for the green path.

## Resolved INCIDENTs (preserved for forensics)

The phase encountered two sibling bugs in the smoke ↔ install contract during the cold-cache benchmark. Both were resolved in-phase per D-23-D3.

### INCIDENT 1 — Phase 22 lockfile carryover (resolved)

**Discovered:** First cold-cache benchmark (commit `3734605`)
**Symptom:** `ModuleNotFoundError: No module named 'skl2onnx'` at smoke layer, build exit 1, wall-clock 32s
**Root cause:** `skl2onnx` and `pyinstaller` were in template `requirements.in` but never made it into root `requirements.in`. Phase 22's pre-flight rig validated wheels in `requirements.in` only and never cross-checked against the smoke list. Plan 03 mirrored the smoke list verbatim from CONT-07 spec, faithfully preserving the drift.
**Resolution (Option B):**
- `chore(23): add skl2onnx + pyinstaller to root requirements.in (Phase 22 mirror gap)` — commit `31be881`
- `chore(23): regenerate root lockfile via uv to add skl2onnx + pyinstaller (isolated format diff)` — commit `adcbd9d` (PITFALLS #6 isolated commit)
- Resulting root lockfile: 1729 hashes (up from Phase 22's 1644), `pyinstaller==6.20.0`, `skl2onnx==1.20.0`, `numpy==2.3.5` held
- Verified: lockfile resolved cleanly inside `quay.io/jupyter/scipy-notebook:2026-04-27` with `--python-version 3.14` (same rig as Plan 23-02 template lockfile regen)

### INCIDENT 2 — pyinstaller PyPI ↔ module name casing (resolved)

**Discovered:** Second cold-cache benchmark (after INCIDENT 1 resolution)
**Symptom:** `ModuleNotFoundError: No module named 'pyinstaller'` at smoke layer, despite `pyinstaller==6.20.0` being installed (visible in build log line `+ pyinstaller==6.20.0`)
**Root cause:** PyPI distribution name is `pyinstaller` (lowercase, what `requirements.in` lists and what `pip install` accepts); canonical Python module name is `PyInstaller` (PascalCase). CONT-07 spec text used the lowercase form, which Plan 03 inherited verbatim. The smoke verifies importability — the lowercase form fails import even though install succeeded.
**Resolution (Option B'):**
- `fix(23): correct PyInstaller smoke import casing (Option B' fix-in-phase)` — commit `70f7c76`
  - `Dockerfile` line 32: `pyinstaller` → `PyInstaller`
  - `.claude/doml/templates/Dockerfile` line 33: same
  - `.planning/REQUIREMENTS.md` CONT-07 line 17: `pyinstaller` → `PyInstaller` + footnote explaining PyPI ↔ module name divergence
  - `.planning/phases/23-dockerfile-rebuild-uv-migration/23-CONTEXT.md` D-23-A3: same correction with forensic note

**Sibling bug pattern.** Both INCIDENTs share the same shape: "smoke list disagrees with install set." INCIDENT 1 was a missing install; INCIDENT 2 was a wrong import name for an installed package. The smoke layer (CONT-07) caught both at build time — exactly the fail-fast value it was designed to provide.

## Deliverables

- [x] Root `Dockerfile` rewritten on single-stage uv + scipy-notebook + cache mount + inline 11-import smoke (Plan 03 Task 1)
- [x] Template `Dockerfile` mirrors root + standalone kaggle layer deleted (Plan 03 Task 2 — D-23-B3)
- [x] Template `requirements.in` mirrors root: `pip-tools` removed, `numpy<2.4` added (Plan 01 — D-23-B1)
- [x] Template `requirements.txt` regenerated via `uv pip compile … --generate-hashes` (Plan 02 — D-23-B2 isolated commit)
- [x] Root `requirements.in` extended with `skl2onnx` + `pyinstaller` (INCIDENT 1 resolution — closes Phase 22 mirror gap)
- [x] Root `requirements.txt` regenerated via `uv pip compile … --generate-hashes` (INCIDENT 1 resolution — 1729 hashes, isolated commit)
- [x] Both Dockerfiles' smoke list use `PyInstaller` (PascalCase) for the canonical Python module name (INCIDENT 2 resolution)
- [x] `CLAUDE.md` REPR-04 regen instruction updated (`pip-compile` → `uv pip compile … --generate-hashes -o requirements.txt`)
- [x] `AGENTS.md` "Pinned dependencies" regen instruction matches CLAUDE.md (D-23-B4)
- [x] `install.sh` defensively sets `export DOCKER_BUILDKIT=1` (scoped to install session)
- [x] `install.ps1` defensively sets `$env:DOCKER_BUILDKIT = "1"` (scoped to install session)
- [x] `MIGRATION-v1.6.md` ships at repo root with R-user v1.5 install pin (Bash + PowerShell paths) — D-23-C3, D-23-C4
- [x] **Cold-cache `docker compose build --no-cache` succeeds end-to-end** (build exit 0, wall-clock 36s)
- [x] **Wall-clock under 300s recorded for green-path build** (36s = 8.33× under budget)

## Requirements coverage (CONT-01..CONT-08)

| Requirement | Disposition |
|-------------|-------------|
| CONT-01 (scipy-notebook base) | Satisfied — Phase 22 pinned tag `2026-04-27`; Phase 23 preserved the pin in both Dockerfiles |
| CONT-02 (uv replaces pip-compile + pip install) | Satisfied — both Dockerfiles use `uv pip install --system`; CLAUDE.md / AGENTS.md regen-command updates point at `uv pip compile` |
| CONT-03 (BuildKit cache mount on /root/.cache/uv) | Satisfied — `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked` in both Dockerfiles |
| CONT-04 (cold-cache build < 300s) | **Satisfied — 36s wall-clock, 8.33× under budget** (recorded above; cache-eviction verified cold pre-build) |
| CONT-05 (uv vendored from ghcr.io/astral-sh/uv:0.11.8) | Satisfied — `COPY --from=ghcr.io/astral-sh/uv:0.11.8` in both Dockerfiles |
| CONT-06 (requirements.txt regen via uv with hashes) | Satisfied — root by Phase 22 + extended via INCIDENT 1 fix (1729 hashes); template by Plan 02 (1618 hashes) |
| CONT-07 (in-build import smoke) | Satisfied — 11-package smoke (duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, **PyInstaller**) succeeds at build time; CONT-07 spec text corrected for canonical Python module casing |
| CONT-08 (templates mirror root) | Satisfied — both Dockerfiles structurally byte-identical (modulo optional kaggle comment); both requirements.in / requirements.txt files mirror root structure |

## Decisions Made (D-23-A1..D3 outcomes)

- **D-23-A1** (full UV env block 6 vars) — All 6 vars present indented continuation in both Dockerfiles (UV_LINK_MODE=copy, UV_COMPILE_BYTECODE=1, UV_NO_PROGRESS=1, UV_PYTHON_DOWNLOADS=never, UV_SYSTEM_PYTHON=1, UV_PYTHON=/opt/conda/bin/python).
- **D-23-A2** (single root install block) — Single `USER root` for entire install + smoke + fix-permissions chain; single `USER ${NB_UID}` drop at end.
- **D-23-A3** (inline import smoke) — Smoke chained with `&&` inside the install RUN; fails install layer cleanly on broken wheels (caught both INCIDENTs as designed).
- **D-23-A4** (syntax pragma) — `# syntax=docker/dockerfile:1.7` at line 1 of both Dockerfiles.
- **D-23-B1** (template requirements.in mirror) — Plan 01 dropped `pip-tools`, added `numpy<2.4`.
- **D-23-B2** (template lockfile isolated commit) — Plan 02 regenerated via uv pip compile with 1618 hashes; PITFALLS #6 isolated commit honored.
- **D-23-B3** (drop kaggle layer) — Plan 03 Task 2 removed the standalone kaggle pip-install layer from template Dockerfile.
- **D-23-B4** (CLAUDE.md + AGENTS.md regen-cmd update) — Plan 04 Task 1 swept both root-level docs.
- **D-23-C1** (delete mamba R block) — Plan 03 deleted from both Dockerfiles; scipy-notebook ships no R toolchain anyway.
- **D-23-C2** (line-1 comment + LABEL drop R, bump 3.14) — Plan 03 rewrote in both Dockerfiles.
- **D-23-C3** (migration note in Phase 23) — Plan 04 Task 2 created MIGRATION-v1.6.md.
- **D-23-C4** (dedicated MIGRATION-v1.6.md shape) — Standalone file at repo root with Bash + PowerShell pin paths.
- **D-23-D1** (single benchmark run) — One `time docker compose build --no-cache` recorded (36s); not borderline so no median-of-3 escalation.
- **D-23-D2** (wall-clock-only SUMMARY) — Frontmatter records `cold_build_wall_clock_seconds: 36` only; per-stage breakdown only appears in INCIDENT-resolution sections per D-23-D3.
- **D-23-D3** (INCIDENT protocol) — Triggered twice. Both INCIDENTs documented with per-stage breakdown, root cause, and resolution. Phase blocked at each, user gated each fix-in-phase resolution. Final state: GREEN.

## Phase Boundary Discipline

Per CONTEXT.md `<specifics>` and D-23-C boundary:

**In scope (Phase 23) — done:**
- Dockerfile install-layer rewrite (line 1 syntax pragma, FROM preserved, mamba R block deleted, uv vendored, UV env block, cache mount + uv pip install + import smoke + consolidated fix-permissions, single USER drop)
- Template mirror including kaggle-layer drop (D-23-B3)
- Line-1 comment + LABEL description rewrite (D-23-C2)
- CLAUDE.md / AGENTS.md regen-command line updates (D-23-B4)
- install.sh / install.ps1 DOCKER_BUILDKIT=1 defensive flag
- MIGRATION-v1.6.md (R-user v1.5 pin escape hatch — D-23-C3)
- Root requirements.in extended with skl2onnx + pyinstaller (INCIDENT 1 in-phase fix)
- Root requirements.txt regenerated with hashes (INCIDENT 1 in-phase fix)
- Smoke-list casing correction `pyinstaller` → `PyInstaller` (INCIDENT 2 in-phase fix)
- CONT-07 spec text amended to match canonical Python module name (INCIDENT 2 in-phase fix; minor REQUIREMENTS.md edit)

**Out of scope (Phase 24) — preserved:**
- R narrative blocks in CLAUDE.md (lines 29-31, 48-50, 80, 94-96 per PITFALLS R Removal Checklist)
- R narrative blocks in AGENTS.md (lines 40-44, 59-63)
- `data_understanding_r.ipynb` template, R branches in `data-understanding.md` workflow
- `/doml-new-project` language-preference prompt
- Runtime config-validation gate for `language: r`

**Out of scope (Phase 25) — pending:**
- CI smoke test workflow + bundled fixture data + automated 300s gate
- Build-time wall-clock CI assertion (Phase 25 CI-04 reuses the eviction methodology proved here)

## Handoff to Phase 24 + Phase 25

**Phase 24 (R Removal Sweep) inherits:**
- Both Dockerfiles already R-free at the build level (CONT-01 satisfied; mamba R block + R 4.x narrative deleted from Dockerfile line 2 + LABEL)
- MIGRATION-v1.6.md exists at repo root — Phase 24 may extend with broader R-removal rationale (D-23-C3 left room)
- Smoke list is now stable and verified (no further smoke ↔ install drift expected; Phase 24 only deletes R narrative, not Python deps)

**Phase 25 (CI Smoke Test + Build Budget Gate) inherits:**
- Documented cold-cache wall-clock baseline: **36s** (8.33× under 300s budget, ample headroom for CI infra variance)
- Verified cache-eviction methodology (`docker buildx prune --all -f` with non-`|| true` exit-code check) — Phase 25's CI script reuses this pattern
- Working Dockerfile + requirements.txt + template mirror — CI build commands point at the same files
- Forensic precedent: smoke ↔ install drift is detectable at build time; Phase 25 CI smoke catches future regressions automatically

## Worktree / commit timeline

| Commit | Description | Wave |
|--------|-------------|------|
| `17aed5c` | chore(23-01): mirror template requirements + drop pip-tools, add numpy<2.4 | 1 |
| `20e6e65` | docs(23-01): complete plan SUMMARY | 1 |
| `5ea0776` | chore(23): regenerate template lockfile via uv (isolated format diff) | 2 |
| `08633f4` | docs(23-02): complete plan SUMMARY | 2 |
| `5d0cbba` | feat(23): rebuild root Dockerfile install layer on uv + scipy-notebook | 3 |
| `6e214cf` | feat(23): mirror template Dockerfile to root + drop kaggle layer | 3 |
| `a55ad0b` | docs(23-03): complete plan SUMMARY | 3 |
| `ed582cc` | docs(23-04): update regen command + DOCKER_BUILDKIT defensive flag | 4 |
| `cd2b66c` | docs(23-04): add MIGRATION-v1.6.md — R-user v1.5 install pin escape hatch | 4 |
| `3734605` | docs(23-04): record cold-cache benchmark + INCIDENT — smoke ↔ lockfile drift | 4 — INCIDENT 1 detected |
| `cc60a53` | docs(23-04): append self-check to 23-SUMMARY.md | 4 — INCIDENT 1 detected |
| `31be881` | chore(23): add skl2onnx + pyinstaller to root requirements.in (Phase 22 mirror gap) | 4 — INCIDENT 1 fix |
| `adcbd9d` | chore(23): regenerate root lockfile via uv to add skl2onnx + pyinstaller (isolated format diff) | 4 — INCIDENT 1 fix |
| `70f7c76` | fix(23): correct PyInstaller smoke import casing (Option B' fix-in-phase) | 4 — INCIDENT 2 fix |
| (this commit) | feat(23): green-path benchmark — cold build 36s after INCIDENT 1 + INCIDENT 2 fix-in-phase resolutions | 4 — Phase close |

---
*Phase 23 completed: 2026-05-01*
*Build log preserved on host: `/tmp/build-23-fix.log` (final green run)*
