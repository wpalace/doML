# Phase 23: Dockerfile Rebuild + uv Migration — Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Rebuild the install layer of the root `Dockerfile` and `.claude/doml/templates/Dockerfile` on `quay.io/jupyter/scipy-notebook:2026-04-27` (already pinned by Phase 22) using uv 0.11.8 vendored via `COPY --from=ghcr.io/astral-sh/uv:0.11.8`, a BuildKit cache mount on `/root/.cache/uv`, and an in-build import smoke. Mirror template cleanups Phase 22 made to root (drop `pip-tools`, add `numpy<2.4`). Update CLAUDE.md and AGENTS.md regen instructions from `pip-compile` → `uv pip compile … --generate-hashes`. Defensively set `DOCKER_BUILDKIT=1` in `install.sh` and `install.ps1`. Write `MIGRATION-v1.6.md` at repo root for users who need to pin to v1.5 for R support. Demonstrate cold-cache `docker compose build --no-cache` under 5 minutes on the user's dev machine and record wall-clock in `23-SUMMARY.md`.

**In scope:**
- Root `Dockerfile` install-layer rewrite (delete `mamba install r-*` block; uv install with cache mount; inline import smoke; single root install block; consolidated fix-permissions)
- Template `Dockerfile` mirror (same install-layer rewrite + drop redundant kaggle layer)
- `# syntax=docker/dockerfile:1.7` pragma added to both Dockerfiles
- Full UV env block (6 vars) in both Dockerfiles
- Update line-1 comment + LABEL description (drop R, bump Python 3.13 → 3.14) in both Dockerfiles
- Template `requirements.in` cleanup: drop `pip-tools`, add `numpy<2.4` (mirror Phase 22 root)
- Template `requirements.txt` full regeneration with `uv pip compile … --generate-hashes` (isolated commit per PITFALLS #6)
- `CLAUDE.md` regen instruction sweep: `pip-compile` → `uv pip compile`
- `AGENTS.md` regen instruction sweep (same one-line change)
- `install.sh` + `install.ps1` defensively `export DOCKER_BUILDKIT=1` (or `$env:DOCKER_BUILDKIT="1"` on PowerShell)
- New file: `MIGRATION-v1.6.md` at repo root (R-user migration / v1.5 pin path)
- Phase verification: cold-cache `docker compose build --no-cache` wall-clock recorded in `23-SUMMARY.md`; if >300s, phase blocks with INCIDENT diagnosis

**Out of scope (other phases):**
- R sweep across workflows / notebooks / language-prompt removal / config-validation gate / R blocks in CLAUDE.md and AGENTS.md narrative content (Phase 24 — RREM-01..RREM-07)
- CI smoke test workflow + bundled fixture data + 300s automated gate (Phase 25 — CI-01..CI-07)
- Future-Requirement items: SLIM-FUT-01 (move pyinstaller out), SLIM-FUT-02 (mirror scipy-notebook to ghcr.io), LOCK-FUT-01 (PEP 751 / `uv.lock` migration)

</domain>

<decisions>
## Implementation Decisions

### UV environment block + container user/layer strategy

- **D-23-A1:** Adopt the full research-recommended UV env block in both Dockerfiles — `UV_LINK_MODE=copy`, `UV_COMPILE_BYTECODE=1`, `UV_NO_PROGRESS=1`, `UV_PYTHON_DOWNLOADS=never`, `UV_SYSTEM_PYTHON=1`, `UV_PYTHON=/opt/conda/bin/python`. Aligned with Astral's "Using uv in Docker" guide (`research/ARCHITECTURE.md`).
- **D-23-A2:** Single `USER root` install block. `COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt`, then a single `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked` chain that runs `uv pip install --system -r /tmp/requirements.txt && python -c "import …" && fix-permissions ${CONDA_DIR} && fix-permissions /home/${NB_USER}`. Then `USER ${NB_UID}` once at the end. Eliminates the v1.5 root↔jovyan ping-pong; saves ~20-40s per PITFALLS #9.
- **D-23-A3:** Import smoke is **inline** in the install RUN (chained with `&&`), not a separate RUN line. Failed smoke invalidates the install layer cleanly. Smoke list per CONT-07: `duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller`.
- **D-23-A4:** `# syntax=docker/dockerfile:1.7` pragma is line 1 of both Dockerfiles (required for the cache mount syntax to be portable across Docker versions).

### Template sweep scope

- **D-23-B1:** Mirror Phase 22's root `requirements.in` cleanup into `.claude/doml/templates/requirements.in` — drop `pip-tools`, add `numpy<2.4`. Keeps `/doml-new-project` scaffolds in lockstep with the v1.6 root.
- **D-23-B2:** Fully regenerate `.claude/doml/templates/requirements.txt` via `uv pip compile .claude/doml/templates/requirements.in -o .claude/doml/templates/requirements.txt --generate-hashes`. Land as an **isolated commit** (PITFALLS #6: format-only diff is noisy).
- **D-23-B3:** Drop the standalone kaggle pip-install layer (lines 27-34 of `.claude/doml/templates/Dockerfile`) — `kaggle` is in template `requirements.in` and resolves through the unified uv install. Per ARCHITECTURE.md migration step #10.
- **D-23-B4:** Update both root `CLAUDE.md` (REPR-04 section) and root `AGENTS.md` "Pinned dependencies" section: `pip-compile requirements.in` → `uv pip compile requirements.in --generate-hashes -o requirements.txt`. Keeps Copilot-target installs consistent with Claude-target.

### R mamba block disposition (Phase 23 vs Phase 24 boundary)

- **D-23-C1:** Phase 23 deletes the entire `USER root / mamba install r-duckdb r-tidymodels r-renv r-umap / mamba clean / fix-permissions` block from both Dockerfiles. Confirms Phase 22 SUMMARY handoff and ARCHITECTURE.md migration step #1. scipy-notebook ships no conda R toolchain, so preserving this block would just fail the build.
- **D-23-C2:** Phase 23 updates the line-1 comment in both Dockerfiles (`# DoML analysis environment — Python 3.13 + R 4.x + DuckDB + ML stack` → `# DoML analysis environment — Python 3.14 + DuckDB + ML stack`) and the LABEL description (drop "R" mention). The Dockerfile is the file under heaviest edit in this phase — leaving stale narrative text would mislead the next reader.
- **D-23-C3:** v1.6 R-user migration note is **authored in Phase 23**, not Phase 24. Couples user-facing comms with the breaking change (R disappears from the build in Phase 23). Phase 24 still owns the rest of the R sweep (workflows, notebooks, CLAUDE.md R code blocks, AGENTS.md R blocks, language-prompt removal, config-validation gate).
- **D-23-C4:** Migration note shape: dedicated `MIGRATION-v1.6.md` at repo root. Content: explains v1.6 is Python-only, points R users to `bash install.sh --version v1.5.0` (Bash) or `$env:DOML_VERSION = "v1.5"; iwr ... | iex` (PowerShell) to pin the last R-supporting release. Phase 24 may extend this file with the broader R-removal rationale; Phase 23 ships the install-pin escape hatch.

### Build budget proof method

- **D-23-D1:** Cold-cache benchmark = a **single** `time docker compose build --no-cache` run on user's dev machine. If wall-clock lands in the borderline range (>270s, <300s), escalate to median-of-3 to filter network noise. Research estimate is 155-250s, so a single run leaves headroom in expected case.
- **D-23-D2:** `23-SUMMARY.md` records **wall-clock only** (matches Phase 22 SUMMARY format). No dev-box specs, no per-stage breakdown unless triggered by D-23-D3.
- **D-23-D3:** **Budget-bust protocol:** if wall-clock ≥300s, the phase **blocks** and writes an `INCIDENT` section in `23-SUMMARY.md` with: (a) per-stage breakdown captured via `BUILDKIT_PROGRESS=plain docker buildx build --no-cache`, (b) identified long-pole stage, (c) one of three resolutions: in-phase fix (e.g., remove an unexpected source build), tightened constraint (network/base-image guidance documented), or re-open Phase 22 (if a wheel that resolved cleanly in pre-flight is now source-building). Auto-advance chain stops; user gates the resolution.

### Claude's Discretion

- Exact Dockerfile line ordering within the install RUN's `&&` chain (uv install → smoke → fix-permissions is research-recommended, but argument order in fix-permissions calls is flexible).
- LABEL `maintainer` content unchanged ("DoML framework" preserved); only LABEL `description` is rewritten (drop "R").
- Whether the new `MIGRATION-v1.6.md` opens with prose or a TL;DR fenced block.
- Whether `DOCKER_BUILDKIT=1` is set as an `export` line near the top of `install.sh` and a single `$env:DOCKER_BUILDKIT="1"` line in `install.ps1`, or inline-prepended only to the `docker compose build`-related guidance (tilt: top-of-file export — defensive, no-op if already set).
- docker-compose.yml `cache_from` / `cache_to` BuildKit-cache-persistence config is **not** added in v1.6 (research §"docker-compose.yml Changes" calls it optional; users who want it can add locally; Phase 25 CI workflow handles its own cache).
- Commit granularity: tilt is three commits — (1) `chore(23): mirror template requirements + drop pip-tools, add numpy<2.4`, (2) `chore(23): regenerate template lockfile via uv (isolated format diff)`, (3) `feat(23): rebuild Dockerfile install layer on uv + scipy-notebook` (covers both Dockerfiles + CLAUDE.md + AGENTS.md + install.sh + install.ps1 + MIGRATION-v1.6.md + 23-CONTEXT.md + 23-SUMMARY.md). Planner may split commit 3 if the plan benefits from it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone research (read first)
- `.planning/research/ARCHITECTURE.md` — recommended single-stage Dockerfile structure; UV env block; cache mount; layer ordering; build-time budget breakdown; migration steps from current Dockerfile (steps 1–13)
- `.planning/research/STACK.md` — pinned versions for every dep; "What NOT to Use" table (UV_LINK_MODE=hardlink, uv pip sync, pip install uv, etc.)
- `.planning/research/PITFALLS.md` — §3 (uv pip sync breaks kernel — must use `uv pip install --system`), §4 (mistune<3 retained), §6 (lockfile-format noisy diff → isolated commit), §9 (single fix-permissions sweep), §11 (papermill kernel name)
- `.planning/research/SUMMARY.md` — phase-ordering rationale; confidence assessment

### Project + roadmap
- `.planning/PROJECT.md` — D-01..D-04 v1.6 locked decisions (scipy-notebook base, uv replaces pip-compile, Python 3.14, R hard-removal); milestone build budget (<5 min)
- `.planning/REQUIREMENTS.md` — CONT-01..CONT-08 (acceptance criteria for this phase); RREM-01..RREM-07 (Phase 24 — out of scope here); CI-01..CI-07 (Phase 25 — out of scope here); SLIM-FUT-01, SLIM-FUT-02, LOCK-FUT-01 (deferred)
- `.planning/ROADMAP.md` §Phase 23 — 5 success criteria; depends on Phase 22

### Phase 22 handoff (consumed by Phase 23)
- `.planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-CONTEXT.md` — pre-flight rig decisions; D-22-13/14/15 (scipy-notebook tag pin)
- `.planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-SUMMARY.md` — Python 3.14 confirmed; tag `2026-04-27` pinned in both Dockerfiles' FROM lines; root `requirements.txt` regenerated with 1644 hashes; explicit Phase 23 handoff list (delete mamba block, replace pip install, add cache mount + smoke, update CLAUDE.md, update install scripts, mirror to template)
- `.planning/phases/22-pre-flight-wheel-validation-lockfile-bootstrap/22-AUDIT.md` — conda↔uv shadow-risk surface (4 packages flagged); reference for build-failure forensics

### Code touched in this phase
- `Dockerfile` (root) — install-layer rewrite + line-1 comment + LABEL
- `.claude/doml/templates/Dockerfile` — mirror + drop kaggle layer
- `.claude/doml/templates/requirements.in` — drop `pip-tools`, add `numpy<2.4`
- `.claude/doml/templates/requirements.txt` — full regenerate via `uv pip compile … --generate-hashes`
- `CLAUDE.md` (root) — REPR-04 regen command update
- `AGENTS.md` (root) — "Pinned dependencies" section regen command update
- `install.sh` — set `DOCKER_BUILDKIT=1` defensively
- `install.ps1` — set `$env:DOCKER_BUILDKIT="1"` defensively
- `MIGRATION-v1.6.md` (new) — R-user v1.5 pin path

### Cross-phase hand-offs
- **From Phase 22:** scipy-notebook tag `2026-04-27` pinned; Python 3.14 validated; root lockfile with hashes; PROJECT.md D-03 reflects 3.14
- **To Phase 24:** Dockerfiles are R-free; CLAUDE.md / AGENTS.md still have R *narrative* / code blocks (out of Phase 23 scope per D-23-C1..C4 boundary)
- **To Phase 25:** `<5 min cold build` benchmark is documented in 23-SUMMARY.md; CI workflow asserts the same budget on every push (Phase 25 CI-04)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **Existing Dockerfile skeleton** (`USER root` / `RUN ...` / `USER ${NB_UID}` / `WORKDIR ${PROJECT_ROOT}`) — structural shape preserved; only the install-layer body changes. `LABEL maintainer="DoML framework"` preserved verbatim.
- **scipy-notebook tag `2026-04-27`** already pinned in both Dockerfile FROM lines by Phase 22 — no further pin work needed.
- **Root `requirements.txt`** with 1644 hashes / 100 packages (Phase 22) — the new install layer's `uv pip install --system -r /tmp/requirements.txt` consumes this directly.
- **`fix-permissions` script** ships at `/usr/local/bin/fix-permissions` in scipy-notebook (same as datascience-notebook) — same calling convention.
- **`UV_*` env block** lifts directly from `research/ARCHITECTURE.md` reference Dockerfile — no novel design.
- **Existing `install.sh` / `install.ps1` argument-parsing scaffolding** — adding `export DOCKER_BUILDKIT=1` is a one-line addition near the top.

### Established patterns
- **Dated quay.io tags for reproducibility** (v1.5 + v1.6 pattern: `<image>:YYYY-MM-DD`). Pin format unchanged.
- **`requirements.in` is source of truth, `requirements.txt` is generated** — REPR-04. The regen command changes from `pip-compile` to `uv pip compile`; the contract is identical.
- **Templates mirror root** — `.claude/doml/templates/` is what `/doml-new-project` ships to user projects. CONT-08's spirit is "templates always match root".
- **`docker compose run --rm jupyter <cmd>`** is the established containerized-tool invocation (used in CLAUDE.md REPR-04 example) — same shape applies to `uv pip compile`.

### Integration points
- **`/doml-new-project` workflow** writes `Dockerfile` and `requirements.txt` from `.claude/doml/templates/` into new user projects. Template Dockerfile changes propagate automatically once shipped.
- **`install.sh` / `install.ps1`** copy root `CLAUDE.md` (and `AGENTS.md` for copilot target) verbatim — root edits propagate to new installs.
- **`docker-compose.yml`** (root + template) — no functional changes required for v1.6 (BuildKit cache mount in Dockerfile is sufficient); BuildKit-default behavior of Compose v2.20+ handles syntax pragma transparently.

</code_context>

<specifics>
## Specific Ideas

- **Phase boundary discipline (mirror of Phase 22's `<specifics>`):** Phase 23 owns the Dockerfile install-layer rewrite + the migration-note escape hatch. Phase 24 owns the workflow/notebook/CLAUDE.md/AGENTS.md R *narrative* sweep + config-validation gate. Resist the temptation to land Phase 24 R-text deletions in Phase 23 — but the line-1 Dockerfile comment + LABEL description ARE in scope (D-23-C2) because we're rewriting those files.
- **Isolated lockfile commit (D-23-B2)** for the template `requirements.txt` regen is non-negotiable per PITFALLS #6 — same reasoning as Phase 22 commit 2.
- **`UV_LINK_MODE=copy` is mandatory**, not optional. Without it the BuildKit cache mount + target site-packages cross-filesystem boundary causes hardlink errors. Documented in research; preserve as a comment in the Dockerfile next to the ENV line.
- **`uv pip install`, never `uv pip sync`** (PITFALLS #3). `sync` would prune scipy-notebook's conda-shipped jupyterlab/notebook/ipykernel/nbconvert/nbformat → kernel breaks. Document the distinction inline near the install RUN.
- **Verification deliverable order:** (1) build succeeds, (2) wall-clock recorded, (3) container starts (`docker compose up -d`), (4) `jupyter --version` works inside container, (5) `python -c "<the smoke list>"` passes outside the build context too. Step 4-5 catch any subtle conda-shipped-package shadowing that the in-build smoke might paper over.
- **AGENTS.md sweep (D-23-B4)** is only the regen-command line on/around line 78 — NOT the broader R narrative blocks elsewhere in AGENTS.md (those are Phase 24).

</specifics>

<deferred>
## Deferred Ideas

- **docker-compose.yml `cache_from` / `cache_to`** — research suggests it as optional for shared-machine BuildKit cache persistence. Skipped in v1.6; users can add locally; Phase 25 CI manages its own cache. Future-track if a "shared dev box / CI cache" pattern emerges.
- **Multi-stage Dockerfile** — research explicitly rejects (no size win because runtime needs the wheels anyway). Re-evaluate only if a build-time-only tool needs isolation.
- **`uv.lock` (PEP 751) format** — covered by `LOCK-FUT-01` in REQUIREMENTS.md Future. Stay on `requirements.txt` format for v1.6.
- **Mirror scipy-notebook to ghcr.io** — `SLIM-FUT-02`. Stays deferred.
- **Move `pyinstaller` out of main image** — `SLIM-FUT-01`. Stays deferred.
- **Median-of-3 / automated benchmark script** — D-23-D1 will trigger only if first run is borderline (>270s). If we end up doing it, the throwaway script is not committed unless useful for Phase 25 CI.
- **Dev-box spec capture in SUMMARY** (D-23-D2 alternative) — not in v1.6; CI infra will be the canonical reproduction surface (Phase 25). If a regression report needs context, capture then.
- **Per-stage build breakdown in SUMMARY** — only triggered by the budget-bust INCIDENT protocol (D-23-D3); not the default.

</deferred>

---

*Phase: 23-dockerfile-rebuild-uv-migration*
*Context gathered: 2026-04-30*
