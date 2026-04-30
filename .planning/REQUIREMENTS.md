# Requirements: DoML v1.6 — Container Optimization & Python Modernization

**Defined:** 2026-04-30
**Core Value:** A data scientist can drop a dataset into `/data`, answer a few questions, and get a fully reproducible, peer-reviewable ML analysis with stakeholder-ready summaries — without re-inventing the process each time.
**Milestone Goal:** Cut Docker cold-build time to under 5 minutes by switching to `quay.io/jupyter/scipy-notebook` + `uv`, locking Python 3.13, and removing R support entirely from the framework.

## v1.6 Requirements

### Container Build (CONT)

- [ ] **CONT-01**: Docker base image is `quay.io/jupyter/scipy-notebook:<dated-tag>` (Python-only, drops R + Julia from datascience-notebook)
- [ ] **CONT-02**: `uv` 0.11.x replaces `pip-compile` and `pip install` for dependency resolution and install in the Dockerfile
- [ ] **CONT-03**: Dockerfile uses BuildKit cache mount (`RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked`) so warm rebuilds reuse downloaded wheels
- [ ] **CONT-04**: Cold-cache `docker compose build --no-cache` completes in under 5 minutes (300s) on user's dev machine
- [ ] **CONT-05**: `uv` binary is vendored from `ghcr.io/astral-sh/uv:0.11.8` via `COPY --from` (no `pip install uv`)
- [ ] **CONT-06**: `requirements.txt` is regenerated with `uv pip compile requirements.in -o requirements.txt --generate-hashes`
- [ ] **CONT-07**: Dockerfile includes an in-build import smoke layer (`python -c "import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller"`) that fails the build immediately on broken wheels
- [ ] **CONT-08**: All `.claude/doml/templates/Dockerfile` and `.claude/doml/templates/docker-compose.yml` template files mirror the new structure (so `/doml-new-project` produces v1.6 containers for new analyses)

### Python Modernization (PY)

- [ ] **PY-01**: Container Python is pinned to **Python 3.13.x**
- [ ] **PY-02**: All packages listed in `requirements.in` resolve to cp313 wheels with no source builds during cold-cache install
- [ ] **PY-03**: `mistune<3` constraint is retained in `requirements.in` to preserve compatibility with conda-managed nbconvert
- [ ] **PY-04**: `pip-tools` is removed from `requirements.in` (replaced by uv per D-02)
- [ ] **PY-05**: `numpy<2.4` is pinned explicitly in `requirements.in` to prevent ABI breakage from a future numpy 2.4 release

### R Deprecation (RREM)

- [ ] **RREM-01**: All R packages and the `mamba install` block are deleted from both root `Dockerfile` and `.claude/doml/templates/Dockerfile`
- [ ] **RREM-02**: `data_understanding_r.ipynb` template is deleted from `.claude/doml/templates/notebooks/`
- [ ] **RREM-03**: `data-understanding.md` workflow no longer branches on `language == "r"` — all R-specific steps (3d/3e/3f, 5e/5f/5g/5h per STATE.md) are removed
- [ ] **RREM-04**: `new-project.md` interview no longer prompts for language selection; generated `config.json` hardcodes `language: python`
- [ ] **RREM-05**: All R references are removed from `CLAUDE.md`, `AGENTS.md`, `README.md`, `PROJECT.md` template, and any SKILL.md files that branch on language
- [ ] **RREM-06**: A migration note (in `README.md` and/or a new `MIGRATION-v1.6.md`) directs users needing R to pin `install.sh --version v1.5`
- [ ] **RREM-07**: Runtime config-validation gate: when DoML commands load `config.json` with `language` present and != `python`, command surfaces a clear error with migration guidance and exits non-zero

### CI Smoke Test (CI)

- [ ] **CI-01**: Bundled fixture datasets exist under `tests/fixtures/` covering supervised (regression + classification, ≤500 rows), unsupervised (clustering / dim-reduction reuse), and time-series (≤365 daily rows) cases
- [ ] **CI-02**: A smoke runner script (`tests/smoke/run_all_notebooks.sh` or `.py`) invokes `papermill` against all 10 production notebook templates against the bundled fixtures and reports per-template pass/fail
- [ ] **CI-03**: GitHub Actions workflow `.github/workflows/smoke-test.yml` runs on `push` and `pull_request`, builds the image with cold cache, and runs the smoke runner
- [ ] **CI-04**: CI workflow records the cold-build wall-clock and fails the job when build time exceeds 300 seconds (CONT-04 budget asserted automatically)
- [ ] **CI-05**: Smoke test passes for all 10 templates against bundled fixtures (no notebook execution errors); a notebook failure fails the CI job
- [ ] **CI-06**: Notebooks gracefully skip `kaggle datasets download` when `~/.kaggle/kaggle.json` is absent (so CI runs without Kaggle credentials)
- [ ] **CI-07**: Modelling notebooks honor `OPTUNA_N_TRIALS` and `MAX_DATASET_ROWS` environment variables to cap heavy operations during CI runs

## Future Requirements (deferred — not v1.6 scope)

### Python 3.14 (PY-FUT)

- **PY-FUT-01**: Upgrade container to Python 3.14 once `ydata-profiling` lifts the `python<3.14` cap (issue #1811)
- **PY-FUT-02**: Re-validate cp314 wheel coverage for lightgbm, prophet, pmdarima at upgrade time

### Lockfile Modernization (LOCK-FUT)

- **LOCK-FUT-01**: Migrate from `requirements.txt` (pip-compile format) to `uv.lock` or PEP 751 `pylock.toml` once PEP 751 lands and ecosystem support is universal

### Container Slimming (SLIM-FUT)

- **SLIM-FUT-01**: Move `pyinstaller` out of main image into a lazy install path inside `/doml-deploy-cli` to shrink the analysis image
- **SLIM-FUT-02**: Mirror base image to `ghcr.io` to avoid `quay.io` rate limits in CI if they become a problem

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Multi-stage Dockerfile | Single-stage suffices; runtime needs all wheels. Multi-stage adds complexity without size win. |
| GPU / CUDA support | Deferred — no current DoML notebook template uses GPU. Adds significant image bloat. |
| Deep learning frameworks (PyTorch, TF, Keras) | Deferred to a future milestone; out of v1.6 scope (and ydata-profiling block on 3.14 is unrelated). |
| Python 3.14 in v1.6 | Blocked by `ydata-profiling` `python<3.14` pin (issue #1811). Captured as PY-FUT-01. |
| `uv.lock` / PEP 751 migration | Stay with `requirements.txt` for portability; revisit when PEP 751 lands. |
| FastAPI / uvicorn / pydantic in main image | Stays in `requirements.serve.txt` for `Dockerfile.serve` (web deployment target). Keeps analysis image lean. |
| v1.5 carryover paperwork (Phase 19/20 SUMMARY/VERIFICATION, README typos, COP-04 VS Code manual test) | User-decided out of scope for v1.6. Stays as accepted tech debt; address in a future cleanup milestone. |
| Backward-compatibility shim for `language: r` config | D-04 hard removal; existing R users pin `install.sh --version v1.5` (RREM-06 migration note) |
| Soft-deprecation warning before removing R | D-04 hard removal; v1.5 install path is the soft-deprecation channel |
| Mirroring base image to ghcr.io | Captured as SLIM-FUT-02 — only if rate limits become a real problem |

## Traceability

Which phases cover which requirements. Filled by roadmapper.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONT-01 | TBD | Pending |
| CONT-02 | TBD | Pending |
| CONT-03 | TBD | Pending |
| CONT-04 | TBD | Pending |
| CONT-05 | TBD | Pending |
| CONT-06 | TBD | Pending |
| CONT-07 | TBD | Pending |
| CONT-08 | TBD | Pending |
| PY-01 | TBD | Pending |
| PY-02 | TBD | Pending |
| PY-03 | TBD | Pending |
| PY-04 | TBD | Pending |
| PY-05 | TBD | Pending |
| RREM-01 | TBD | Pending |
| RREM-02 | TBD | Pending |
| RREM-03 | TBD | Pending |
| RREM-04 | TBD | Pending |
| RREM-05 | TBD | Pending |
| RREM-06 | TBD | Pending |
| RREM-07 | TBD | Pending |
| CI-01 | TBD | Pending |
| CI-02 | TBD | Pending |
| CI-03 | TBD | Pending |
| CI-04 | TBD | Pending |
| CI-05 | TBD | Pending |
| CI-06 | TBD | Pending |
| CI-07 | TBD | Pending |

**Coverage:**
- v1.6 requirements: 27 total (8 CONT + 5 PY + 7 RREM + 7 CI)
- Mapped to phases: 0 (filled by roadmapper)
- Unmapped: 27 ⚠️ (resolves after roadmap step)

---
*Requirements defined: 2026-04-30*
*Last updated: 2026-04-30 — initial v1.6 requirements*
