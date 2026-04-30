# Feature Research

**Domain:** Python-only ML analysis container — capabilities the rebuilt image must support
**Researched:** 2026-04-30
**Milestone:** v1.6 Container Optimization & Python Modernization

## Table-Stakes Capabilities (must work post-rebuild)

### Jupyter / Notebook execution
- **JupyterLab** — provided by scipy-notebook base; no separate install. Serves at `:8888` via `start-notebook.py`.
- **ipykernel** — provided by base; required by all 10 notebook templates.
- **nbconvert** (conda-managed) — emits HTML stakeholder reports. Pin `mistune<3` retained.
- **nbformat** (conda-managed) — read/write `.ipynb`.
- **papermill** — parameterized notebook execution + drives the new CI smoke test.
- **nbstripout** 0.9.1 — REPR-03 pre-commit hook.
- **jinja2** — `/doml-deploy-web` HTML templates and nbconvert templating.

### Data layer
- **DuckDB** ≥1.4.3 — analytical SQL backbone (CLAUDE.md "DuckDB first" mandate); EDA profiling.
- **pandas, numpy, scipy** — base image provides; `uv pip install` may upgrade to pinned versions.
- **pyarrow** — Parquet/Arrow support; verify base ships it, add explicitly if not.
- **matplotlib, seaborn** — base image provides.

### ML stack
- **scikit-learn** ≥1.8.0 — preprocessing, modelling pipelines.
- **xgboost, lightgbm** — leaderboard contenders for regression/classification.
- **shap** — model explainability.
- **optuna** — hyperparameter tuning (top-3 × 30 trials).
- **umap-learn** — dim-reduction notebook.
- **statsmodels** — EDA tests + ARIMA in forecasting.
- **prophet** 1.3.0 (wheel-only) — forecasting leaderboard.
- **pmdarima** 2.1.1 — auto-ARIMA in forecasting.

### Deployment paths
- **pyinstaller** — `/doml-deploy-cli` step 5 invokes `pyinstaller --version` inside container.
- **skl2onnx** — `/doml-deploy-wasm` requires `import skl2onnx`.
- **onnxruntime** — Phase 17 PERF-01 benchmark + WASM parity test.
- **FastAPI / uvicorn / pydantic** — stay in `requirements.serve.txt`, NOT in main container (separate `Dockerfile.serve` for `/doml-deploy-web`).

### EDA / profiling
- **plotly** — interactive viz in reports.
- **ydata-profiling** — was deferred in v1.0 due to `pkg_resources` under conda 3.13. Likely works on uv-managed pip 3.13. Validate during build.

### Data acquisition
- **kaggle** — `/doml-get-data`.

### Reproducibility
- **pytest** — test runner; new role: drives smoke test orchestration.
- **pre-commit** — REPR-03 hook framework.

## Differentiators (nice-to-have for v1.6)

- **uv as runtime tool inside container** — exposes `uv pip install` for ad-hoc experimentation with same lockfile semantics. Cheap to keep; recommended.
- **GitHub Actions smoke workflow** — beyond "build passes", actually runs every notebook template. Strongest milestone-success signal.
- **Build-time benchmark recorded in CI** — assert <300s on every push; auto-fails the milestone budget if regressed.

## Anti-Features (explicitly NOT in scope for v1.6)

- All R: `r-duckdb`, `r-tidymodels`, `r-renv`, `r-umap`, IRkernel, `language: "r"` config option, `data_understanding_r.ipynb`, R blocks in CLAUDE.md, R blocks in AGENTS.md (D-04).
- **pip-tools / pip-compile** — replaced by uv (D-02).
- **mamba install layer** in Dockerfile — entire R block deleted.
- **Custom kaggle Dockerfile layer** — was workaround for stale `requirements.txt`; with uv-driven single resolve becomes redundant.
- **datascience-notebook base image** — replaced by scipy-notebook (D-01).
- **Multi-stage Dockerfile** — single stage suffices.
- **`uv.lock` (uv-native)** — stay with `requirements.txt` for portability.
- **GPU/CUDA support** — out of scope.
- **Deep learning frameworks** (PyTorch, TensorFlow) — deferred to a future milestone.

## Smoke Test Feature Requirements

### Notebooks to execute end-to-end via papermill (against fixture data)

1. `notebooks/business_understanding.ipynb`
2. `notebooks/data_understanding_python.ipynb`
3. `notebooks/anomaly_detection.ipynb`
4. `notebooks/preprocessing.ipynb`
5. `notebooks/modelling_regression.ipynb`
6. `notebooks/modelling_classification.ipynb`
7. `notebooks/modelling_clustering.ipynb`
8. `notebooks/modelling_dimreduction.ipynb`
9. `notebooks/forecasting.ipynb`
10. `notebooks/deployment_report.ipynb`

**Expected runtime:** <10 min total (each notebook <90s on small fixture).

### Fixture datasets needed

- **Regression/classification fixture** — ~500 rows, mixed numeric + categorical (e.g., synthetic Boston-like or sklearn `load_diabetes`).
- **Time series fixture** — ~365 daily rows, single target.
- **Unsupervised fixture** — same as regression but without target column.

Commit fixtures to `tests/fixtures/` (small enough to include in repo).

### Infrastructure additions

- `tests/smoke/run_all_notebooks.sh` (or `.py`) — orchestrator running papermill against each template with fixture parameters.
- `tests/fixtures/` — committed CSV fixtures.
- `.github/workflows/smoke-test.yml` — GitHub Actions workflow: build image, time the cold build, assert <300s, run smoke runner against all 10 notebooks.

**No new packages required for smoke** — `papermill` + `pytest` already in `requirements.in`. `nbclient` pulled transitively.

### CI environment guardrails

- `MAX_DATASET_ROWS=500` env var honored by notebooks (or hard-coded in fixtures).
- Optuna trials capped at `n_trials=2` for CI runs (env-var-driven).
- Kaggle CLI gracefully skips when `~/.kaggle/kaggle.json` absent.
- `--shm-size=2g` on docker run to avoid OOM in modelling notebooks.

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Keep ydata-profiling? | Yes — try on Python 3.13 + uv. Drop if `pkg_resources` issue persists. |
| pyinstaller in main image vs lazy install? | Keep in main image (matches `/doml-deploy-cli` step 5 expectation). Revisit only if budget blown. |
| FastAPI in main container? | No — stays in `requirements.serve.txt`, separate `Dockerfile.serve`. |
| pmdarima 3.14 compat? | Moot — Python 3.13 chosen due to ydata-profiling. pmdarima 2.1.1 has cp313 wheels. |
| mistune pin? | Keep `<3` defensively until smoke test verifies conda nbconvert tolerates mistune 3.x. |
| uv lockfile format? | `uv pip compile requirements.in -o requirements.txt --generate-hashes` — keep `requirements.txt` as canonical lockfile. |

---
*Feature research for: v1.6 Container Optimization & Python Modernization*
*Researched: 2026-04-30*
