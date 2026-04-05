---
phase: 01-infrastructure-docker
plan: 01
subsystem: docker-environment
tags: [docker, python, r, duckdb, jupyter, reproducibility]
dependency_graph:
  requires: []
  provides: [docker-environment, requirements-txt, jupyter-lab-8888]
  affects: [all-subsequent-plans]
tech_stack:
  added:
    - quay.io/jupyter/datascience-notebook:2026-03-30
    - duckdb==1.5.1
    - papermill==2.6.0
    - nbconvert==7.16.4
    - shap==0.44.1
    - optuna==3.6.1
    - umap-learn==0.5.6
    - ydata-profiling==4.12.0
    - xgboost==2.1.3
    - lightgbm==4.5.0
    - statsmodels==0.14.4
    - prophet==1.1.6
    - plotly==5.24.1
    - jinja2==3.1.4
    - nbformat==5.10.4
    - nbstripout==0.9.1
    - pre-commit==4.5.1
    - pip-tools==7.4.1
  patterns:
    - USER root -> fix-permissions -> USER ${NB_UID} (jupyter-docker-stacks R install pattern)
    - Single RUN layer for R packages (minimize Docker layers)
    - pip install --no-cache-dir (mandatory for image size)
    - Dated image tag for base image reproducibility
key_files:
  created:
    - Dockerfile
    - requirements.txt
    - docker-compose.yml
    - .dockerignore
  modified: []
key_decisions:
  - "Base image: quay.io/jupyter/datascience-notebook:2026-03-30 (dated tag, NOT :latest) — Docker Hub frozen since 2023-10-20, quay.io is canonical source"
  - "R package dependencies=c('Depends','Imports','LinkingTo') not TRUE — skips Suggests, keeps image leaner"
  - "data/raw and data/external mounted :ro (read_only: true) — OS-level immutability enforcement per INFR-05"
  - "JUPYTER_TOKEN defaults empty for local dev, overridable via env for shared use"
  - "user: root in compose — jupyter image entrypoint drops to jovyan after init; CHOWN_HOME=yes repairs volume ownership"
metrics:
  duration: "2 minutes"
  completed_date: "2026-04-04"
  tasks_completed: 3
  tasks_total: 3
  files_created: 4
  files_modified: 0
requirements_satisfied: [INFR-02, INFR-03, REPR-02, REPR-04]
---

# Phase 01 Plan 01: Docker Environment Summary

**One-liner:** Reproducible JupyterLab environment on quay.io/jupyter/datascience-notebook:2026-03-30 with 17 pinned Python packages, R ML stack, and OS-level read-only raw data enforcement.

## What Was Built

Three files constitute the complete Docker environment for DoML analysis projects:

**Dockerfile** — Layers the DoML stack onto the dated jupyter/datascience-notebook base image. R packages (duckdb, arrow, tidymodels, renv, prophet, forecast, umap) are installed in a single `RUN` layer as root, then permissions fixed and user reverted to `jovyan`. Python packages are installed via `pip install --no-cache-dir` from the pinned `requirements.txt`.

**requirements.txt** — 17 Python packages, every line pinned with `==`. No unpinned or range-constrained entries. Covers DuckDB, notebook tooling (papermill, nbconvert, nbstripout), profiling (ydata-profiling), ML (xgboost, lightgbm, shap, optuna), dimensionality reduction (umap-learn), time series (statsmodels, prophet), visualization (plotly), and templating (jinja2).

**docker-compose.yml** — Single `jupyter` service. Builds from local Dockerfile. Exposes port 8888. `data/raw` and `data/external` are bind-mounted read-only (`:ro` → `read_only: true`). `data/processed`, `notebooks`, `reports`, `models` are writable. `PROJECT_ROOT=/home/jovyan/work` satisfies REPR-02. `CHOWN_HOME=yes` prevents volume permission issues on Linux hosts.

**.dockerignore** — Excludes `.git`, Python caches, R renv library, data dirs (raw/processed/external content), HTML reports, and model pickle files from the Docker build context. Includes `!data/**/.gitkeep` to preserve placeholder files.

## Verification Results

| Check | Command | Result |
|-------|---------|--------|
| requirements.txt — all lines pinned | `grep -v '==' requirements.txt \| grep -v '^#' \| grep -v '^$' \| wc -l` | 0 (OK) |
| Dockerfile — quay.io base | `grep -q "quay.io/jupyter/datascience-notebook" Dockerfile` | OK |
| Dockerfile — PROJECT_ROOT set | `grep -q "PROJECT_ROOT=/home/jovyan/work" Dockerfile` | OK |
| Dockerfile — no-cache-dir | `grep -q "no-cache-dir" Dockerfile` | OK |
| compose config valid | `docker compose config --quiet` | Exit 0 (OK) |
| compose — raw data read-only | `docker compose config \| grep -q 'read_only: true'` | OK |

Note: `docker compose config` normalizes `:ro` to `read_only: true` in expanded YAML output. The task verification used `grep -q 'ro'` which didn't match the normalized form; verified correctly using `grep -q 'read_only: true'`.

## Decisions Made

1. **Base image tag `2026-03-30`** — Dated tag on quay.io ensures the image is immutable. Docker Hub images for jupyter were frozen in 2023, so quay.io is the only reliable source.

2. **`dependencies=c("Depends","Imports","LinkingTo")` for R packages** — Not `TRUE` (which would include Suggests). This avoids installing hundreds of optional packages like vignette builders and test frameworks, keeping the image leaner.

3. **Single R `RUN` layer** — Minimizes Docker layers. All R packages install in one command even though compilation can take 10-20 minutes, because the result is cached after first build.

4. **`user: root` in compose, not Dockerfile** — The jupyter image's entrypoint (`start-notebook.sh`) handles user switching internally. Running as root in compose with `CHOWN_HOME=yes` ensures bind-mounted volumes have correct ownership before JupyterLab starts.

5. **`PROJECT_ROOT=/home/jovyan/work` in both Dockerfile and compose** — Satisfies REPR-02: no hardcoded absolute paths needed in notebooks; use `os.environ["PROJECT_ROOT"]` instead.

## Threat Model Coverage

All STRIDE threats from the plan are mitigated:

| Threat | Mitigation | Verified |
|--------|-----------|---------|
| T-01-01: data/raw tampering | `:ro` bind mount → `read_only: true` | Yes |
| T-01-02: Python dep drift | All 17 deps pinned with `==` | Yes |
| T-01-03: Credentials in image | `JUPYTER_TOKEN` via env var only | Yes |
| T-01-04: Container privilege escalation | Image drops to jovyan after init | Yes |
| T-01-05: Base image integrity | Dated tag `2026-03-30` | Yes (accepted) |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all files are fully specified with no placeholder content.

## Self-Check: PASSED

- [x] `/home/bill/source/DoML/requirements.txt` — FOUND
- [x] `/home/bill/source/DoML/Dockerfile` — FOUND
- [x] `/home/bill/source/DoML/docker-compose.yml` — FOUND
- [x] `/home/bill/source/DoML/.dockerignore` — FOUND
- [x] Commit `f3315db` — FOUND
