# Research Summary — v1.6 Container Optimization & Python Modernization

**Project:** DoML — Do Machine Learning
**Domain:** Reproducible ML analysis container (Jupyter + Python + DuckDB)
**Researched:** 2026-04-30
**Confidence:** HIGH

## Executive Summary

DoML v1.6 will rebuild the Docker container from a Python-only, uv-driven foundation. The current `quay.io/jupyter/datascience-notebook` base ships ~3.5–4.5 GB compressed because it includes R + Julia toolchains. Switching to `quay.io/jupyter/scipy-notebook` (~1.3–1.5 GB) plus `uv` for dependency install drops cold-cache build time from the current ~10–12 min to an estimated **155–250s** — well under the 5-minute milestone budget.

Python 3.14 is the user's aspirational target, but **`ydata-profiling` pins `python<3.14`** (open issue #1811). Because ydata-profiling is the EDA profiling backbone, we pin v1.6 to **Python 3.13**, which has universal cp313 wheel coverage for every dep in `requirements.in`. Python 3.14 is documented as a follow-up once ydata-profiling lifts the cap.

R is hard-removed (D-04). The cleanup surface spans 16+ files: `Dockerfile`, workflows (`data-understanding.md`, `new-project.md`), `PROJECT.md` template, `CLAUDE.md`, `AGENTS.md`, `README.md`, several SKILL.md files, and the `data_understanding_r.ipynb` template. Backward compatibility for existing v1.5 R users is preserved via `install.sh --version v1.5.0` (git-tag pin).

The two highest risks are: (1) `uv pip sync` would prune conda-shipped Jupyter packages — must use additive `uv pip install --system` instead; (2) `mistune<3` pin must be retained or HTML reports break silently. Both mitigated by explicit pins + a CI smoke test that runs all 10 notebook templates against fixture data on every push.

## Key Findings

### Recommended Stack

Build a single-stage Dockerfile on `quay.io/jupyter/scipy-notebook:2026-04-21`, vendor uv 0.11.8 via `COPY --from=ghcr.io/astral-sh/uv:0.11.8`, install pinned deps with `uv pip install --system` under a BuildKit cache mount.

**Core technologies:**
- **Python 3.13** — universal wheel coverage; 3.14 blocked by ydata-profiling
- **scipy-notebook (Jupyter)** — base image, drops R/Julia, saves ~2.5 GB
- **uv 0.11.8** — replaces `pip-compile` and `pip install`, 8–10× faster, BuildKit cache friendly
- **DuckDB 1.4.3 LTS** — analytical SQL backbone (CLAUDE.md mandate)

### Expected Features

**Must have (table stakes):** All 10 existing notebook templates must execute end-to-end (BU, EDA Python, anomaly, preprocessing, modelling regression/classification/clustering/dim-reduction, forecasting, deployment report). All 14+ `/doml-*` commands must keep working. pyinstaller, skl2onnx, prophet, lightgbm, xgboost, optuna, shap, ydata-profiling, kaggle CLI, papermill, nbstripout, pre-commit, pytest must all install via uv.

**Should have (competitive):** GitHub Actions smoke workflow that runs every notebook template against bundled fixture data; cold-build time gate (<300s) asserted on every push.

**Defer:** Python 3.14 (until ydata-profiling lifts its cap), GPU/CUDA support, deep learning frameworks (PyTorch/TF), `uv.lock` migration (stay with `requirements.txt`).

### Architecture Approach

Single-stage Dockerfile; uv overlay on conda-managed system Python. BuildKit cache mount (`--mount=type=cache,target=/root/.cache/uv`) makes warm rebuilds ~5–15s. Compose v2.20+ uses BuildKit by default — minimal `docker-compose.yml` changes.

**Major components:**
1. **Dockerfile (root + template)** — base image switch, R block deleted, uv install layer, in-Dockerfile import smoke
2. **CI smoke workflow** (`.github/workflows/smoke-test.yml`) — cold-build timing gate + papermill over all templates
3. **Test fixtures** (`tests/fixtures/`, `tests/smoke/run_all_notebooks.sh`) — small CSV inputs and orchestrator
4. **Lockfile workflow** — `uv pip compile requirements.in -o requirements.txt --generate-hashes` replaces `pip-compile`

### Critical Pitfalls

1. **`uv pip sync` removes conda packages** — use `uv pip install --system` (additive) instead. Verify with kernel + papermill smoke after build.
2. **mistune 3.x silently breaks conda nbconvert** — keep `mistune<3` pin; add nbconvert HTML smoke step.
3. **R removal misses references** — sweep checklist in PITFALLS.md covers 16+ files; add config-validation gate.
4. **Python 3.14 wheels lag** — confirmed Python 3.13 instead due to ydata-profiling.
5. **CI OOM risk** — Optuna trials capped at 2 in CI; fixtures ≤500 rows; `--shm-size=2g`.

## Implications for Roadmap

Suggested phase structure (continues numbering from v1.5; **starts at Phase 22**):

### Phase 22: Pre-flight Wheel + Build Validation
**Rationale:** Verify Python 3.13 path + uv resolver + scipy-notebook before any production code is touched. Surfaces cp313 gaps, unexpected resolver picks, conda/pip conflicts.
**Delivers:** `requirements.txt` regenerated via `uv pip compile`, audit log of base image vs requirements.in overlap, "go/no-go" decision recorded
**Avoids:** Pitfall #2 (ydata-profiling 3.14 block), wheel surprises, conda shadowing

### Phase 23: Dockerfile Rebuild + uv Migration
**Rationale:** Core technical work. With pre-flight green, swap base, add uv layer, add BuildKit cache mount. Touches root Dockerfile, root docker-compose.yml, and template equivalents.
**Delivers:** New Dockerfile (root + template), updated docker-compose.yml, updated CLAUDE.md/AGENTS.md rebuild instructions, regenerated `requirements.txt` (with hashes), `pip-tools` removed from `requirements.in`
**Uses:** scipy-notebook 2026-04-21, uv 0.11.8, BuildKit 1.7
**Avoids:** Pitfall #3 (uv pip sync) and #4 (mistune)

### Phase 24: R Removal Sweep
**Rationale:** Independent of Dockerfile rewrite (the new Dockerfile already drops R packages, but the workflow/notebook/doc surface is its own scoped cleanup). Best done after #23 so smoke tests can validate Python-only paths.
**Delivers:** Deleted `data_understanding_r.ipynb`; cleaned `data-understanding.md`/`new-project.md`/SKILL.md files; cleaned CLAUDE.md/AGENTS.md/README.md; config-validation gate for `language` field; MIGRATION-v1.6 note
**Avoids:** Pitfall #5 (R refs missed)

### Phase 25: CI Smoke Test + Build Budget Gate
**Rationale:** Closing the milestone success criterion. Without this, "<5 min build" and "all templates work" are claims, not facts.
**Delivers:** `tests/fixtures/` (3 small CSVs), `tests/smoke/run_all_notebooks.sh`, `.github/workflows/smoke-test.yml`, papermill calls parameterized to fixture paths, `MAX_DATASET_ROWS` + `n_trials=2` env-var support added to notebooks where heavy
**Avoids:** Pitfalls #7, #8, #10 (CI gotchas)

### Phase Ordering Rationale

- **22 first:** Pre-flight gates the milestone — if Python 3.13 + uv don't resolve cleanly, we change scope before doing damage. Cheap to run, expensive to skip.
- **23 next:** Dockerfile work depends on validated `requirements.txt` from #22. Once Dockerfile is rebuilt, smoke testing the new image becomes possible.
- **24 then:** R removal can happen in parallel with #23 in principle, but the Phase 23 Dockerfile already drops R packages — sweeping the workflow/notebook surface afterwards lets us validate the cleaned `/doml-new-project` against the rebuilt container.
- **25 last:** Smoke test + CI validate that #23 + #24 actually achieve the milestone goal end-to-end. Acts as the milestone gate.

### Research Flags

- **Phase 22 — wheel availability:** Standard pattern, just `uv pip compile --dry-run` checks. No deeper research needed.
- **Phase 23 — Dockerfile authoring:** Standard pattern, ARCHITECTURE.md sketch is implementation-ready.
- **Phase 24 — R removal:** Sweep checklist already concrete in PITFALLS.md. May surface unexpected R refs during execution; budget time for that.
- **Phase 25 — CI workflow:** Standard pattern (papermill + GitHub Actions); no extra research. Phase plan should account for actual notebook fixture data shape.

All four phases are well-mapped — none should require a separate `/gsd-research-phase` invocation.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All version pins verified via PyPI; only cp314 path is MEDIUM and we're not on it |
| Features | HIGH | Capability surface enumerated from existing PROJECT.md + CLAUDE.md + workflow files |
| Architecture | HIGH | Astral docs explicit on uv-in-Docker pattern; cache mount syntax stable since BuildKit 1.4 |
| Pitfalls | HIGH | 5 critical pitfalls have concrete detection + prevention; R sweep checklist is concrete |

**Overall confidence:** HIGH

### Gaps to Address

- **Exact scipy-notebook dated tag** (2026-04-21 assumed; user/Phase 22 should pin to whatever resolves at build time, never `:latest`)
- **ydata-profiling actually working under uv 3.13** — high probability yes (uv-managed setuptools provides `pkg_resources`), but Phase 22 should validate explicitly
- **`pyinstaller` wheel size impact on cold build** — small risk it pushes >300s; budget breakdown shows comfortable margin but worth a measurement

## Sources

### Primary (HIGH confidence)
- [PEP 745 — Python 3.14 Release Schedule](https://peps.python.org/pep-0745/)
- [Astral docs — Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/)
- [Jupyter Docker Stacks docs](https://jupyter-docker-stacks.readthedocs.io/)
- [ydata-profiling issue #1811](https://github.com/ydataai/ydata-profiling/issues) — `python<3.14` cap

### Secondary (MEDIUM confidence)
- [Python 3.14 Wheels Readiness Tracker](https://status.fedoralovespython.org/wheels_py314/)
- [hynek.me — Production Python Docker Containers with uv](https://hynek.me/articles/docker-uv/)
- PyPI lookups: pmdarima 2.1.1, lightgbm 4.6.0, prophet 1.3.0, shap 0.51.0, statsmodels 0.14.6, onnxruntime 1.25.1, pyinstaller 6.20.0, duckdb 1.4.3

### Tertiary (validate during execution)
- exact scipy-notebook dated tag latest — pin during Phase 22
- ydata-profiling under uv-managed Python 3.13 — validate during Phase 22 pre-flight

---
*Research completed: 2026-04-30*
*Ready for roadmap: yes*
