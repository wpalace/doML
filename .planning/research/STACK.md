# Stack Research

**Domain:** Reproducible ML analysis container (Jupyter + Python + DuckDB)
**Researched:** 2026-04-30
**Confidence:** HIGH (Python 3.13 path), MEDIUM (Python 3.14 path)
**Milestone:** v1.6 Container Optimization & Python Modernization

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | **3.13** | Notebook runtime + ML stack | Universal cp313 wheel coverage for all listed deps; 3.14 blocked by `ydata-profiling` pin (`python<3.14`, see issue #1811). Revisit 3.14 when ydata-profiling lifts the cap. |
| `quay.io/jupyter/scipy-notebook:2026-04-21` | dated tag | Base image (Jupyter + scientific Python) | Drops R (~2-2.5 GB savings vs `datascience-notebook`); ships JupyterLab, ipykernel, nbconvert (conda-managed), numpy/scipy/pandas/sklearn/numba/matplotlib/seaborn pre-installed; same `${NB_UID}` / `fix-permissions` model as v1.5 base. |
| `uv` | **0.11.8** | Package resolution + install | 8-10× faster than pip-tools, parallel resolver, BuildKit cache-friendly, deterministic with `--generate-hashes`. Replaces `pip-compile` + `pip install`. |
| DuckDB | **1.4.3 LTS** | Analytical SQL backbone (CLAUDE.md mandate) | Required by EDA notebook profiling and CLAUDE.md "DuckDB first" rule. Cp314 wheels confirmed. |

### Supporting Libraries (must install via uv)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| papermill | latest | Parameterized notebook execution | Used by every `/doml-*` workflow + new CI smoke test |
| nbstripout | 0.9.1 | Strip notebook outputs pre-commit | REPR-03 |
| jinja2 | 3.x | Web template rendering | `/doml-deploy-web` index.html |
| mistune | `<3` | nbconvert markdown parser | Pin retained — conda nbconvert in scipy-notebook still requires `<3`; lifting causes silent HTML report regressions |
| pre-commit | latest | Hook framework | REPR-03 |
| pytest | latest | Test runner | New: CI smoke test driver |
| shap | 0.51.0 | Model explainability | modelling notebooks |
| optuna | latest | Hyperparameter tuning | modelling notebooks (top-3 × 30 trials) |
| umap-learn | 0.5.12 | Dim-reduction | modelling_dimreduction.ipynb |
| xgboost | 3.2.0 | Gradient boosting | modelling regression/classification leaderboard |
| lightgbm | 4.6.0 | Gradient boosting | modelling regression/classification leaderboard |
| statsmodels | 0.14.6 | Statistical models | EDA tests + ARIMA/SARIMA in forecasting |
| prophet | 1.3.0 | Time series forecasting | forecasting leaderboard (wheel-only — no source build / cmdstan compile) |
| pmdarima | 2.1.1 | Auto-ARIMA | forecasting (alternative ARIMA path) |
| onnxruntime | 1.25.1 | ONNX inference | Phase 17 PERF-01 benchmark + WASM target parity test |
| skl2onnx | 1.20.0 | sklearn → ONNX export | `/doml-deploy-wasm` |
| pyinstaller | 6.20.0 | CLI binary build | `/doml-deploy-cli` |
| ydata-profiling | latest | EDA profiling reports | Was deferred in v1.0 (`pkg_resources` issue under conda 3.13). Likely works on uv-managed pip 3.13. **Validate during build.** |
| plotly | 5.x or 6.x | Interactive viz | report templates |
| kaggle | latest | Dataset downloads | `/doml-get-data` |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `uv pip compile` | Generate `requirements.txt` from `requirements.in` | Drop-in replacement for `pip-compile`, add `--generate-hashes` for supply-chain safety |
| BuildKit (`docker buildx`) | Layer caching + cache mounts | Required for `RUN --mount=type=cache` syntax |
| `astral-sh/uv:0.11.8` Docker image | uv binary source | `COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/` — no `pip install uv` |

## Installation (Dockerfile sketch)

```dockerfile
# syntax=docker/dockerfile:1.7
FROM quay.io/jupyter/scipy-notebook:2026-04-21
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_SYSTEM_PYTHON=1
USER root
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip install --system -r /tmp/requirements.txt \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"
USER ${NB_UID}
ENV PROJECT_ROOT=/home/jovyan/work
WORKDIR ${PROJECT_ROOT}
```

`uv pip install` is preferred over `uv pip sync` — sync removes conda-shipped packages and breaks the kernel (see PITFALLS #4).

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `uv` | `pip-tools` | Stay on `pip-compile` only if uv resolver picks unexpected versions during transition. Document switch-back path. |
| scipy-notebook base | `python:3.13-slim` + manual JupyterLab | Use slim only if scipy-notebook can't hit <5 min budget (it should — see ARCHITECTURE estimates 155-250s). Slim gives smallest image but loses Jupyter team's hardening. |
| Python 3.13 | Python 3.14 | When ydata-profiling lifts `<3.14` cap (issue #1811). Will require re-validating lightgbm/prophet/pmdarima cp314 wheels. |
| Single-stage Dockerfile | Multi-stage | Multi-stage adds complexity without size win — runtime needs all wheels. Skip unless build-time-only tools become necessary. |
| `requirements.txt` (pip-compile format) | `uv.lock` (uv-native) | Stay with `requirements.txt` for v1.6 — universally readable, doesn't lock framework to uv forever. Revisit when PEP 751 lands. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `quay.io/jupyter/datascience-notebook` | Includes R + Julia (~2-2.5 GB extra), violates D-04 | `scipy-notebook` |
| `pip install -r requirements.txt` (no cache mount) | Cold rebuild downloads every wheel, blows 5-min budget | `uv pip install` with `--mount=type=cache` |
| `uv pip sync --system` | Removes conda-shipped packages → kernel breaks | `uv pip install --system` (additive) |
| `pip install uv` in Dockerfile | Non-deterministic resolve, requires Python interpreter for installer | `COPY --from=ghcr.io/astral-sh/uv:0.11.8` |
| Python 3.14 (for v1.6) | `ydata-profiling` pins `python<3.14`; lightgbm/prophet/pmdarima cp314 wheels unverified | Python 3.13 — universal coverage |
| Hardlink mode (`UV_LINK_MODE=hardlink`) | Cross-filesystem cache mount → hardlink errors | `UV_LINK_MODE=copy` |
| Building prophet from source | Pulls cmdstan toolchain (~150 MB), 3-5 min compile | Wheel-only pin (`prophet==1.3.0`) |
| `mamba install` block in Dockerfile | R packages — D-04 hard removal | Delete entire `mamba install` layer |
| `pip-tools` in `requirements.in` | Replaced by uv (D-02) | Remove from `requirements.in` |

## Stack Patterns by Variant

**If 5-min budget is missed on first build:**
- Drop `ydata-profiling` (heaviest dep tree); replace EDA profiling cell with hand-rolled DuckDB queries
- Move `pyinstaller` out of main image into `/doml-deploy-cli` lazy-install
- Use `python:3.13-slim` + minimal JupyterLab install (last resort)

**If ydata-profiling fails on 3.13 under uv:**
- Confirm `pkg_resources` issue is actually fixed under uv-managed setuptools (likely yes)
- If still broken, drop ydata-profiling and document as known limitation

**If lightgbm/prophet ship cp314 wheels mid-milestone:**
- Bump Python to 3.14 in a follow-up phase; not v1.6 scope

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3.13 | all listed deps | Confirmed via PyPI lookups |
| ydata-profiling latest | `python<3.14` | Hard pin (issue #1811) — blocks 3.14 |
| numpy 2.3.x | all listed C-extension wheels | Pin numpy explicitly to prevent uv picking 2.4 if released |
| mistune `<3` | conda nbconvert in scipy-notebook | Verify after build with `jupyter nbconvert --to html` smoke test |
| uv 0.11.8 | scipy-notebook conda Python | Use `--system` flag; do not create venv |

## Sources

- [PEP 745 — Python 3.14 Release Schedule](https://peps.python.org/pep-0745/) — release dates
- [Python 3.14 Wheels Readiness Tracker](https://status.fedoralovespython.org/wheels_py314/) — wheel coverage matrix
- [astral-sh/uv Releases](https://github.com/astral-sh/uv/releases) — uv 0.11.8 verified
- [Using uv in Docker (Astral)](https://docs.astral.sh/uv/guides/integration/docker/) — UV_LINK_MODE, cache mount patterns
- [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html) — scipy-notebook contents
- [ydata-profiling issue #1811](https://github.com/ydataai/ydata-profiling/issues) — `python<3.14` cap
- PyPI — pmdarima 2.1.1 (cp314 confirmed), lightgbm 4.6.0 (cp313 confirmed; cp314 unverified), prophet 1.3.0
- DuckDB 1.4.3 LTS announcement — Dec 2025

---
*Stack research for: v1.6 Container Optimization & Python Modernization*
*Researched: 2026-04-30*
