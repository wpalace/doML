# Phase 23: Dockerfile Rebuild + uv Migration — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `23-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-30
**Phase:** 23-dockerfile-rebuild-uv-migration
**Areas discussed:** UV env + USER/layer strategy, Template sweep scope, R mamba block disposition, Build budget proof method

---

## Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| UV env + USER/layer strategy | Adopt full research-vetted UV_* env block and collapse install + smoke + permissions into a single USER root layer? | ✓ |
| Template sweep scope | Mirror Phase 22 root cleanups into template `requirements.in` + drop redundant kaggle Dockerfile layer? | ✓ |
| R mamba block disposition | Phase 23 vs Phase 24 boundary on R cleanup; Dockerfile narrative + migration note location | ✓ |
| Build budget proof method | How to capture and record cold-build wall-clock for `<5 min` SUMMARY proof | ✓ |

**User's choice:** All four areas selected (multi-select).

---

## UV env + USER/layer strategy

User initially asked for clarification before answering — wanted plain-English explanations of UV env vars, USER/layer strategy, and import smoke placement. After clarification, user replied "Lets go with the safest option" — interpreted as picking the research-recommended/recommended-default for each sub-question.

### Q1: UV environment variable block scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full research set | All 6 UV_* vars (UV_LINK_MODE=copy, UV_COMPILE_BYTECODE=1, UV_NO_PROGRESS=1, UV_PYTHON_DOWNLOADS=never, UV_SYSTEM_PYTHON=1, UV_PYTHON=/opt/conda/bin/python). Astral's official Docker guide. | ✓ |
| Middle (3 vars) | UV_LINK_MODE=copy + UV_COMPILE_BYTECODE=1 + UV_SYSTEM_PYTHON=1 only. | |
| Minimal (1 var) | UV_LINK_MODE=copy only. | |

**User's choice:** Full research set (interpreted from "safest option").
**Notes:** No functional risk; aligns with research/ARCHITECTURE.md reference Dockerfile.

### Q2: USER ordering + fix-permissions strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Single root block | USER root for entire install chain (COPY + uv pip install + smoke + fix-permissions), USER ${NB_UID} once at end. | ✓ |
| Multi-stage user switching | Match v1.5 alternating root↔jovyan rhythm. | |

**User's choice:** Single root block (interpreted from "safest option").
**Notes:** Saves ~20-40s per PITFALLS #9. Final container still drops to non-root via the trailing USER ${NB_UID}.

### Q3: Import smoke placement (CONT-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Inline in install RUN | Chain `python -c "import …"` inside the install RUN with `&&`. Failed smoke invalidates install layer cleanly. | ✓ |
| Separate RUN line | Smoke as own RUN. Cleaner build-output diagnostics, easier to comment-out for debugging. | |

**User's choice:** Inline (interpreted from "safest option").
**Notes:** Smoke list per CONT-07: duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller.

---

## Template sweep scope

### Q1: Mirror Phase 22's root requirements.in cleanup into template?

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror fully | Drop pip-tools and add numpy<2.4 to template requirements.in. | ✓ |
| Hold the line | Phase 23 only touches Dockerfile + docker-compose.yml + CLAUDE.md per literal CONT-08 wording. | |

**User's choice:** Mirror fully.

### Q2: Regenerate template requirements.txt with `uv pip compile --generate-hashes`?

| Option | Description | Selected |
|--------|-------------|----------|
| Full regenerate | Full `uv pip compile … --generate-hashes` mirror of root format; isolated commit per PITFALLS #6. | ✓ |
| Surgical edits only | Just remove the pip-tools pin; defer full uv regen to a later phase. | |

**User's choice:** Full regenerate.

### Q3: Drop the kaggle pip-install layer in template Dockerfile?

| Option | Description | Selected |
|--------|-------------|----------|
| Drop the layer | Remove lines 27-34. kaggle is in template requirements.in, so the standalone layer is redundant. Per ARCHITECTURE.md migration step #10. | ✓ |
| Keep it defensive | Preserve in case downstream user removes kaggle from requirements.in. | |

**User's choice:** Drop the layer.

### Q4: Sweep AGENTS.md regen instructions alongside CLAUDE.md?

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep both | Update root CLAUDE.md AND root AGENTS.md `pip-compile` → `uv pip compile`. | ✓ |
| CLAUDE.md only | Roadmap success criterion #5 names CLAUDE.md only; defer AGENTS.md to Phase 24. | |

**User's choice:** Sweep both.
**Notes:** Limited to the regen-command line near AGENTS.md line 78, not broader R narrative content (Phase 24).

---

## R mamba block disposition

### Q1: Confirm Phase 23 deletes the `mamba install r-*` block?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete in Phase 23 | Drop the entire R-mamba block. Phase 22 SUMMARY explicit handoff + ARCHITECTURE.md migration step #1. | ✓ |
| Preserve for Phase 24 | Boundary discipline — let Phase 24 do all R deletions. | |

**User's choice:** Delete in Phase 23.

### Q2: Update Dockerfile line-1 comment + LABEL description in Phase 23 or Phase 24?

| Option | Description | Selected |
|--------|-------------|----------|
| Update in Phase 23 | Rewrite line-1 comment (Python 3.14 + DuckDB, drop R) + LABEL description. We're touching every other line of the Dockerfile anyway. | ✓ |
| Leave for Phase 24 | Strict scope — only functional lines in Phase 23. | |

**User's choice:** Update in Phase 23.

### Q3: Where does the v1.6 R-user migration note live?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 24 R sweep | MIGRATION-v1.6.md ships in Phase 24 alongside the rest of R cleanup. | |
| Phase 23 (when R first disappears) | Couples user comms with the breaking change. Adds doc work to Phase 23. | ✓ |
| Defer to dedicated v1.6 release-notes phase | Treat release notes as own phase post-Phase 25. | |

**User's choice:** Phase 23.
**Notes:** Diverged from recommended option — user prioritized coupling user comms with the breaking change.

### Q4: Migration note shape

| Option | Description | Selected |
|--------|-------------|----------|
| README.md section | Short subsection in root README.md, no new files, highest visibility. | |
| Dedicated MIGRATION-v1.6.md | New file at repo root concentrating breaking-change docs. | ✓ |
| Both | README pointer + MIGRATION-v1.6.md detail. | |

**User's choice:** Dedicated MIGRATION-v1.6.md.

---

## Build budget proof method

### Q1: How should the cold-cache build benchmark be captured?

| Option | Description | Selected |
|--------|-------------|----------|
| Single timed run + record | One `time docker compose build --no-cache` run; record wall-clock + dev-box context. Borderline (>270s) escalates to median-of-3. | ✓ |
| Median of 3 runs | Three back-to-back cold builds; report median + min/max. | |
| Commit a benchmark script + record one run | `scripts/bench-build.sh` for repeatable measurement. | |

**User's choice:** Single timed run + record (with borderline escalation).

### Q2: What gets recorded alongside the wall-clock number?

| Option | Description | Selected |
|--------|-------------|----------|
| Wall-clock + dev-box context | Wall-clock seconds + CPU/cores/RAM/disk/Docker version. | |
| Wall-clock only | Just the seconds. Matches Phase 22 SUMMARY format. | ✓ |
| Wall-clock + dev-box + per-stage breakdown | Most thorough; uses BUILDKIT_PROGRESS=plain. | |

**User's choice:** Wall-clock only.
**Notes:** Diverged from recommended option — user prefers minimal SUMMARY format consistent with Phase 22.

### Q3: What if the first cold build exceeds the 5-minute budget?

| Option | Description | Selected |
|--------|-------------|----------|
| Block phase + diagnose | Phase verification fails; INCIDENT section with per-stage breakdown + long-pole identification + one of three resolutions. | ✓ |
| Document but proceed | Record over-budget number with mitigation suggestions; let Phase 25 CI gate catch it. | |

**User's choice:** Block phase + diagnose.

---

## Claude's Discretion

Listed in `23-CONTEXT.md` `<decisions>` § "Claude's Discretion" — exact RUN-chain ordering, LABEL maintainer preservation, MIGRATION-v1.6.md prose vs TL;DR, DOCKER_BUILDKIT export placement in install scripts, docker-compose.yml `cache_from`/`cache_to` skipped, commit granularity tilt (3 commits with planner-discretion to split commit 3).

## Deferred Ideas

Listed in `23-CONTEXT.md` `<deferred>` — docker-compose BuildKit cache config, multi-stage Dockerfile, uv.lock format, ghcr.io scipy-notebook mirror, pyinstaller-out-of-image, median-of-3 default benchmark, dev-box spec capture, per-stage breakdown by default.

---
*Discussion log generated: 2026-04-30*
