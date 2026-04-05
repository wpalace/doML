---
plan: 01-04
phase: 01-infrastructure-docker
status: complete
completed: 2026-04-05
requirements_satisfied: [INFR-07]
---

# Plan 01-04 Summary: Environment Smoke Tests

## Result: PASS — all three notebooks executed inside the container

## Docker Build

- **Base image corrected:** `2026-03-30` tag did not exist on quay.io; updated to `2026-04-02`
- **R packages switched to mamba:** `Rscript install.packages()` failed due to C++ source compilation in the conda R environment; switched to `mamba install r-duckdb r-tidymodels r-renv r-umap` which installs pre-built conda-forge binaries successfully
- **Packages deferred to Milestone 2:** `arrow` (R) — incompatible with conda R; `prophet`/`forecast` (R) — require rstan Stan C++ compilation

## Python Requirements Corrections

| Package | Old Pin | New Pin | Reason |
|---------|---------|---------|--------|
| shap | 0.44.1 | 0.47.2 | np.obj2sctype removed in NumPy 2.0 |
| umap-learn | 0.5.6 | 0.5.11 | Updated for NumPy 2.x compat |
| prophet | 1.1.6 | 1.3.0 | Python 3.13 support |
| jinja2 | 3.1.4 | 3.1.6 | ydata-profiling requires >=3.1.6 |
| ydata-profiling | 4.12.0 | (removed) | pkg_resources missing in conda Python 3.13; deferred to EDA phase |

## Notebook Execution Results

### test_python_stack.ipynb — PASS

```
numpy: 2.4.3
pandas: 3.0.2
scikit-learn: 1.8.0
statsmodels: 0.14.4
xgboost: 2.1.3
lightgbm: 4.5.0
shap: 0.47.2
optuna: 3.6.1
umap-learn: 0.5.11
plotly: 5.24.1
PASS: visualization stack operational
papermill: 2.6.0  |  nbconvert: 7.16.4  |  nbformat: 5.10.4  |  jinja2: 3.1.6
XGBoost smoke test — accuracy on synthetic data: 0.750
PASS: Python ML stack operational
```

### test_duckdb.ipynb — PASS

```
DuckDB version: 1.5.1
region  rows  total_sales  avg_sales  total_units
    US     2       7900.0     3950.0         79.0
  APAC     2       3850.0     1925.0         38.0
    EU     2       2180.0     1090.0         22.0
PASS: DuckDB CSV scan operational
PROJECT_ROOT = /home/jovyan/work
PASS: PROJECT_ROOT env var present
```

### test_r_tidyverse.ipynb — PASS

```
tidyverse core libraries loaded
dplyr version: 1.2.0  |  ggplot2 version: 4.0.2
tidymodels version: 1.4.1
PASS: R/tidyverse stack operational
tidymodels linear_reg fit: 20 predictions generated
PASS: tidymodels operational
```

## Deferred Items (Milestone 2)

- R `arrow` package: incompatible with conda R environment — DuckDB covers Parquet reads natively
- R `prophet` / `forecast`: require rstan/Stan C++ compilation — add back when forecasting phase is implemented
- Python `ydata-profiling`: uses `pkg_resources` which is absent in conda Python 3.13 — revisit when implementing EDA phase (Phase 5)
