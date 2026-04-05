# Stack Research

**Domain:** Meta-prompting ML analysis framework (DoML)
**Researched:** 2026-04-04
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| jupyter/datascience-notebook | latest-ubuntu (pinned) | Base Docker image | Official Jupyter team image; ships Python 3.11+, R 4.3+, conda, JupyterLab 4.x — reduces Docker setup to near-zero |
| DuckDB | 1.x | Large-dataset EDA and wrangling | In-process SQL on CSV/Parquet/Excel without a server; zero-copy reads; available in both Python and R |
| papermill | 2.x | Parameterized notebook execution | Execute notebooks programmatically with injected parameters; standard for notebook-as-pipeline pattern |
| nbconvert | 7.x | HTML report generation from notebooks | Ships with Jupyter; `--no-input` flag hides code cells for stakeholder output |
| pandas | 2.x | Tabular data manipulation (Python) | De facto standard; tidy data in Python; native Parquet/CSV/Excel support |
| tidyverse | 2.x | Tabular data manipulation (R) | dplyr + tidyr + ggplot2 + readr — canonical tidy data stack in R |
| scikit-learn | 1.4+ | Traditional ML models and preprocessing | Unified API across all traditional ML problem types; Pipeline enforces leak-free preprocessing |
| statsmodels | 0.14+ | Statistical tests and time series | EDA-level statistical tests (normality, stationarity, regression diagnostics) |
| Prophet | 1.1+ | Time series forecasting | Robust to missing data, seasonality, holiday effects; Python and R |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| XGBoost | 2.x | Gradient boosted trees | Regression and classification leaderboard — often best performer on tabular data |
| LightGBM | 4.x | Fast gradient boosting | Large datasets where XGBoost is too slow; same API |
| SHAP | 0.44+ | Model explainability | Every model in leaderboard — feature importance and individual prediction explanations |
| Optuna | 3.x | Hyperparameter tuning | Bayesian optimization; integrates with scikit-learn, XGBoost, LightGBM |
| umap-learn | 0.5+ | Dimensionality reduction | UMAP for visualization and feature reduction; faster than t-SNE on large datasets |
| scipy | 1.12+ | Statistical tests | Normality tests (Shapiro-Wilk), hypothesis tests, distribution fitting |
| plotly | 5.x | Interactive visualizations | EDA and report charts — renders in notebooks and HTML exports |
| seaborn | 0.13+ | Statistical visualization | Distribution plots, correlation matrices, pair plots |
| ydata-profiling | 4.x | Automated EDA report | One-line `ProfileReport` for initial data overview — use to supplement, not replace, EDA |
| great-expectations | 0.x | Data quality validation | Assert data schema and distribution assumptions before modelling |
| nbformat | 5.x | Programmatic notebook creation | Build notebook cells from templates in DoML skill execution |
| Jinja2 | 3.x | HTML report templating | Render executive summary HTML from structured findings |
| tidymodels | 1.x | Tidy ML in R | Unified R API for model fitting/evaluation; R equivalent of scikit-learn |
| forecast (R) | 8.x | Time series in R | Hyndman's package; ARIMA, ETS, auto.arima |
| duckdb (R) | 1.x | DuckDB R bindings | Same DuckDB engine in R notebooks |
| arrow (R/Python) | 14+ | Parquet I/O | Read/write Parquet files efficiently in both languages |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| docker-compose | Container orchestration | Single `docker-compose up` starts JupyterLab at localhost:8888 |
| nbstripout | Strip notebook outputs before git commit | Prevents large binary diffs in version control |
| pre-commit | Git hook management | Runs nbstripout automatically on `git add` |
| renv (R) | R dependency lockfile | `renv.lock` pins R package versions for reproducibility |
| pip-tools | Python dependency management | `requirements.in` → `requirements.txt` with pinned versions |

## Installation

```bash
# Docker (recommended — installs everything)
docker-compose up

# Python extras (add to requirements.txt in Docker image)
pip install duckdb papermill nbconvert shap optuna umap-learn \
            ydata-profiling great-expectations plotly xgboost \
            lightgbm statsmodels prophet jinja2 nbformat nbstripout

# R extras (add to Dockerfile as R install commands)
# install.packages(c("tidyverse", "tidymodels", "duckdb", "arrow",
#                    "forecast", "prophet", "umap", "DataExplorer"))
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|------------------------|
| jupyter/datascience-notebook | rocker/tidyverse (R-only) | Pure R projects with no Python requirement |
| jupyter/datascience-notebook | Custom Dockerfile from python:3.11-slim | Fine-grained control over image size — more setup work |
| DuckDB | Spark / PySpark | Dataset > 100GB that doesn't fit on a single machine |
| DuckDB | SQLite | When persistent writes are needed, not just analytical queries |
| papermill | Ploomber | More complex DAG pipelines; overkill for DoML's linear phase structure |
| Optuna | scikit-learn GridSearchCV | Simple hyperparameter grids with few parameters — less overhead |
| Optuna | Ray Tune | Distributed hyperparameter search across multiple machines |
| Prophet | statsmodels ARIMA/SARIMAX | When interpretability of ARIMA parameters matters; Prophet is less transparent |
| SHAP | LIME | When global (not just local) explanations are needed — SHAP is preferred |
| plotly | matplotlib | Static figures only — plotly preferred for interactive HTML reports |
| ydata-profiling | sweetviz | Both good; ydata-profiling more comprehensive and actively maintained |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| TensorFlow / PyTorch | Deep learning — deferred to Milestone 2; adds complexity, large Docker image | Milestone 2 |
| MLflow / DVC | Full MLOps stack — overkill for analysis framework; adds server dependencies | models/ directory + leaderboard.csv |
| Streamlit / Dash | Interactive dashboards — not the output format for DoML | nbconvert HTML reports |
| PyCaret | AutoML black box — hides the process DoML is trying to make explicit and teachable | scikit-learn Pipelines with explicit steps |
| Spark | Overkill for single-machine analysis; DuckDB handles GB-scale files natively | DuckDB |
| Conda environments outside Docker | Conflicts with Docker; creates "works on my machine" situations | Docker only |
| Jupyter Classic (non-Lab) | Outdated; JupyterLab 4 ships with datascience image | JupyterLab 4 |
| sklearn's `train_test_split` for time series | Random split contaminates temporal data | `sklearn.model_selection.TimeSeriesSplit` |

## Stack Patterns by Problem Type

**Regression:**
- Models: LinearRegression, Ridge, Lasso, RandomForestRegressor, XGBRegressor, LGBMRegressor
- Metrics: RMSE, MAE, R², MAPE
- Validation: KFold(n_splits=5, shuffle=True)
- Explainability: SHAP waterfall + summary plots

**Classification (Binary/Multi-class):**
- Models: LogisticRegression, RandomForestClassifier, XGBClassifier, LGBMClassifier
- Metrics: ROC-AUC, precision, recall, F1, confusion matrix; accuracy only for balanced classes
- Validation: StratifiedKFold(n_splits=5)
- Calibration: CalibratedClassifierCV for probability outputs
- Explainability: SHAP beeswarm + force plots

**Clustering:**
- Models: KMeans (elbow + silhouette), DBSCAN, AgglomerativeClustering, GaussianMixture
- Metrics: Silhouette score, Davies-Bouldin, Calinski-Harabasz
- Validation: No labels — use internal metrics across k range
- Visualization: UMAP + PCA for cluster visualization

**Time Series:**
- Models: auto_arima (statsmodels), Prophet, ExponentialSmoothing (statsmodels)
- Validation: TimeSeriesSplit — strictly chronological
- Preprocessing: ADF + KPSS stationarity tests; differencing if needed
- Metrics: RMSE, MAE, MAPE, coverage of prediction intervals
- Forecasting output: point forecast + 80% + 95% prediction intervals

**Dimensionality Reduction:**
- Methods: PCA (variance explained curve), t-SNE (perplexity tuning), UMAP (n_neighbors tuning)
- Use cases: Visualization (t-SNE/UMAP for 2D), Feature reduction (PCA), Anomaly detection preprocessing
- Always retain explained variance metrics

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| scikit-learn 1.4+ | Python 3.9-3.12 | Avoid 1.x with Python 3.8 (deprecated) |
| XGBoost 2.x | scikit-learn 1.x | Use `XGBRegressor(device='cpu')` — `tree_method='hist'` default changed in v2 |
| Prophet 1.1 | pandas 2.x | Install via `pip install prophet` — not `fbprophet` (old name) |
| DuckDB 1.x | pandas 2.x, Arrow 14+ | DuckDB can query pandas DataFrames directly via `duckdb.query()` |
| tidymodels 1.x | R 4.2+ | Full tidyverse compatibility |

## Sources

- Jupyter Docker Stacks documentation — image contents and Python/R versions
- DuckDB documentation — SQL API for Python and R
- Scikit-learn documentation — Pipeline, CV patterns
- "Forecasting: Principles and Practice" — Hyndman — Prophet, ARIMA patterns
- ydata-profiling GitHub — EDA automation capabilities
- SHAP documentation — model explainability patterns

---
*Stack research for: Meta-prompting ML analysis framework (DoML)*
*Researched: 2026-04-04*
