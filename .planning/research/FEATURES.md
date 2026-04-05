# Feature Research

**Domain:** Meta-prompting ML analysis framework (DoML)
**Researched:** 2026-04-04
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features DS teams assume exist. Missing these = framework feels incomplete or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Guided business context interview | All good analysis starts with understanding the question | MEDIUM | Must extract: problem type, target variable, success metric, stakeholder |
| Problem type detection | Determines which tests, metrics, and models are appropriate | MEDIUM | Regression / Classification / Clustering / Time Series / Dim. Reduction |
| Automated data inventory | Know what's in /data/ before touching it | LOW | File list, shapes, dtypes, nulls, sample rows via DuckDB |
| Distribution analysis | Understand data before modelling | MEDIUM | Histograms, Q-Q plots, Shapiro-Wilk, skewness/kurtosis |
| Correlation analysis | Identify feature relationships | LOW | Pearson for continuous, Cramér's V for categorical, point-biserial for mixed |
| Missing value analysis | Data quality gating | LOW | Missingness patterns, MCAR/MAR/MNAR classification |
| Model leaderboard | Compare models objectively | MEDIUM | Ranked by validation metric; includes baseline model |
| Reproducible notebooks | Peer review and replication | HIGH | Docker + pinned deps + random seeds + no hardcoded paths |
| HTML stakeholder report | Non-technical audience delivery | MEDIUM | nbconvert export + Claude-generated executive summary |
| Train/validation split | Correct evaluation protocol | LOW | Problem-type aware: stratified for classification, temporal for time series |
| Hyperparameter tuning | Squeeze performance from best model | HIGH | Optuna Bayesian optimization |
| Feature importance | Explain what drives the model | MEDIUM | SHAP values for all leaderboard models |
| Docker environment | Reproducibility across machines | MEDIUM | `docker-compose up` → JupyterLab at :8888 |
| DuckDB EDA | Handle large flat files without loading to memory | MEDIUM | SQL queries on CSV/Parquet in notebooks |

### Differentiators (Competitive Advantage)

Features that make DoML stand out from "just do analysis manually."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| LLM-guided questioning workflow | Extracts business context that humans often skip; surfaces assumptions early | HIGH | Like GSD's questioning phase — the analyst is a thinking partner, not a checklist |
| Problem-type-aware pipeline branching | Wrong metric for problem type is the most common ML mistake; DoML prevents it by design | HIGH | Each problem type loads specific tests, metrics, plots, and model families |
| Contextual narrative generation | Charts without words lose stakeholders; LLM writes interpretive text from actual notebook outputs | HIGH | Narrates findings, not code — tied to verified cell outputs, not hallucinated |
| Assumption enforcement | Statistical tests required before models — not optional | MEDIUM | Phase prompts include mandatory assumption check cells |
| Tidy data gate | Inconsistent data structure breaks R/Python interoperability | MEDIUM | Validation step before EDA begins |
| Stationarity check for time series | Skipping this is the most common time series error | MEDIUM | ADF + KPSS required before any ARIMA/Prophet |
| Leaderboard with baseline | Forces comparison against naive predictor — prevents celebrating mediocre models | LOW | DummyClassifier/DummyRegressor always included |
| Prediction intervals in forecasts | Point forecasts alone are dangerous for decision-making | MEDIUM | 80% and 95% PI bands required in forecasting phase |
| Peer-review-ready structure | Team collaboration is first-class; notebooks designed to be read, not just run | MEDIUM | Markdown narrative cells, section headers, documented assumptions |
| Dual-audience outputs | One analysis → two outputs; no duplication of work | MEDIUM | Technical notebook + stakeholder HTML in every phase |
| Reproducibility by default | Docker + pinned deps + seeds = reproducible on day 1, not as an afterthought | HIGH | Scaffold generates all reproducibility infrastructure at project creation |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Fully automated "press button" analysis | Saves time | Black-box output; no human decision trail; hallucination risk is high without checkpoints | Guided workflow where humans validate key decisions |
| AutoML (PyCaret, H2O) | Easy model comparison | Hides preprocessing choices; leaks target info silently; non-reproducible | Explicit scikit-learn Pipelines with documented steps |
| Real-time dashboard | Interactive exploration | Not the DoML output format; adds server dependency | Plotly charts in HTML report (static but interactive) |
| Auto-fix data quality issues | Less manual work | Silently corrupts analysis; assumptions must be documented | Flag issues, recommend fixes, require human approval before proceeding |
| Single mega-notebook | "Everything in one place" | Impossible to peer-review or reproduce one phase at a time | Strict one-notebook-per-phase |
| Natural language querying of data | Accessible to non-technical users | LLM SQL generation errors on complex schemas; hallucinated stats | DuckDB queries written by Claude with human review |
| Automatic model deployment | End-to-end pipeline | Out of scope for analysis framework; different risk profile | Produce serialized model + metadata; deployment is user's responsibility |
| Skip Business Understanding | "I know what I want" | Unanchored analysis; wrong metric selection; stakeholder rejection | Minimum viable: 5-minute structured template even if user "knows the problem" |

## Feature Dependencies

```
Business Understanding Interview (root — everything depends on this)
    ├──determines──> Problem Type
    │                   ├──selects──> Statistical Tests (Phase 2)
    │                   ├──selects──> Evaluation Metrics (Phase 3)
    │                   ├──selects──> Model Family (Phase 3)
    │                   └──enables──> Forecasting Phase (Phase 4, time series only)
    └──defines──> Target Variable
                    └──enables──> Train/Val Split Strategy
                                    └──enables──> Leaderboard

Data Understanding (Phase 2)
    ├──requires──> /data/raw/ populated
    ├──produces──> /data/processed/ (cleaned dataset)
    └──gates──> Data Modelling (Phase 3)

Data Modelling (Phase 3)
    ├──requires──> /data/processed/ from Phase 2
    ├──requires──> Problem Type from Phase 1
    └──produces──> /models/leaderboard.csv + best_model.pkl

Forecasting (Phase 4)
    ├──requires──> Time series problem type confirmed in Phase 1
    ├──requires──> Stationarity analysis from Phase 2
    └──requires──> best_model.pkl from Phase 3

HTML Reports
    ├──requires──> Notebook execution complete
    └──requires──> LLM narrative generation (reads cell outputs)
```

## MVP Definition

### Launch With (Milestone 1 — Traditional ML)

Minimum viable framework to validate the concept.

- [ ] Guided project kickoff interview (problem type, target, business question)
- [ ] Data inventory and validation (/data/ folder check, format detection)
- [ ] Phase 2 EDA notebook template (distributions, correlations, missing values, DuckDB integration)
- [ ] Phase 3 modelling notebook template for each problem type (regression, classification, clustering, time series, dimensionality reduction)
- [ ] Model leaderboard with baseline model always included
- [ ] Phase 4 forecasting notebook template (time series only, with prediction intervals)
- [ ] Docker environment generation (docker-compose + requirements.txt)
- [ ] HTML report generation (nbconvert + executive summary template)
- [ ] Planning artifacts (PROJECT.md, ROADMAP.md, STATE.md)
- [ ] Reproducibility scaffold (random seeds, relative paths, nbstripout)

### Add After Validation (Milestone 1.x)

- [ ] Great Expectations data quality gates (assert schema/distribution before modelling)
- [ ] Forecast tracking (compare predictions to actuals as new data arrives)
- [ ] Automated tidy data validation
- [ ] Model registry (multiple model versions, not just best)

### Future Consideration (Milestone 2+)

- [ ] Deep learning notebook templates (PyTorch/TensorFlow) — Milestone 2
- [ ] NLP/text analysis workflows — Milestone 3
- [ ] Multi-language (R-first) notebook templates
- [ ] Cross-milestone comparison (how did the analysis evolve?)
- [ ] Integration with external data sources (REST APIs, databases)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Guided interview + problem type detection | HIGH | MEDIUM | P0 |
| Docker environment generation | HIGH | LOW | P0 |
| EDA notebook template with DuckDB | HIGH | MEDIUM | P0 |
| Model leaderboard with baseline | HIGH | MEDIUM | P0 |
| HTML stakeholder report | HIGH | MEDIUM | P0 |
| Reproducibility scaffold | HIGH | LOW | P0 |
| Problem-type-aware phase branching | HIGH | HIGH | P1 |
| SHAP explainability in all models | MEDIUM | LOW | P1 |
| Optuna hyperparameter tuning | MEDIUM | MEDIUM | P1 |
| Forecasting phase (time series) | MEDIUM | HIGH | P1 |
| Stationarity tests (time series) | HIGH (when needed) | LOW | P1 |
| Contextual narrative generation | HIGH | HIGH | P1 |
| Great Expectations data gates | MEDIUM | HIGH | P2 |
| Forecast tracking (actuals vs predictions) | MEDIUM | MEDIUM | P2 |

**Priority key:**
- P0: Must have for Milestone 1 launch
- P1: Should have, core quality bar
- P2: Nice to have, add after P0/P1 validated

## Sources

- GSD framework source code — skills/agents/workflows architecture pattern
- CRISP-DM standard — phase structure and mandatory deliverables
- ydata-profiling, PyCaret, scikit-learn, SHAP, Optuna documentation
- Cookiecutter Data Science — standard project structure
- "Python for Data Analysis" (McKinney) — tidy data patterns
- Kaggle ML survey 2024 — most common DS workflow pain points

---
*Feature research for: Meta-prompting ML analysis framework (DoML)*
*Researched: 2026-04-04*
