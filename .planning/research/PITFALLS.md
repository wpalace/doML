# Pitfalls Research

**Domain:** Meta-prompting ML analysis framework (DoML)
**Researched:** 2026-04-04
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Data Leakage — Target Information in Features

**What goes wrong:**
The model appears to perform exceptionally well during validation but fails completely on new data. Features derived from the target variable (or future information) leak into the training set.

**Why it happens:**
Leakage is subtle — scaling fitted on the full dataset before splitting, target-encoding computed before splitting, features that embed future knowledge (e.g., "customer churned within 30 days" used as a feature for churn prediction).

**How to avoid:**
All preprocessing (scaling, encoding, imputation) must be fit on training data only and applied to validation/test. Use sklearn Pipelines or R `recipes` to enforce this. Feature review: ask "could this feature exist at prediction time?"

**Warning signs:**
Validation accuracy far exceeds realistic expectations for the problem. Model performance degrades sharply on holdout/production data. Features with suspiciously high importance.

**Phase to address:**
Phase 3 — Data Modelling (preprocessing pipeline design); flagged in Phase 2 — Data Understanding (feature construction review)

---

### Pitfall 2: Improper Train/Test Split — Temporal Contamination

**What goes wrong:**
For time series data, random splitting mixes future data into the training set, making the model appear to predict the past (trivial) rather than the future (hard).

**Why it happens:**
Default `train_test_split(random_state=42)` is applied without considering temporal ordering. Analysts treat time series as i.i.d. tabular data.

**How to avoid:**
Always use chronological splitting for time series. Use `TimeSeriesSplit` (sklearn) or `rsample::sliding_period` (R). Validate that training data is strictly before validation data by timestamp.

**Warning signs:**
Perfect or near-perfect forecasts on validation set. Model cannot generalize to next week's data despite high reported accuracy.

**Phase to address:**
Phase 1 — Business Understanding (clarify if time is a factor); Phase 3 — Data Modelling (enforce temporal CV)

---

### Pitfall 3: Poor Business Question Framing

**What goes wrong:**
The analysis answers a technically correct but business-irrelevant question. Stakeholders reject findings because they don't connect to the decision they need to make.

**Why it happens:**
Data scientists start with the data they have rather than the question that matters. The business context is treated as boilerplate rather than a constraint on the analysis.

**How to avoid:**
Business Understanding phase must produce a written decision framing: "We are trying to [decision]. We will use [metric] as a proxy. The analysis is valid if [condition]." Get stakeholder sign-off before data work begins.

**Warning signs:**
Stakeholders ask "so what?" after seeing results. Analysis answers "what happened" when the business needed "what should we do."

**Phase to address:**
Phase 1 — Business Understanding (mandatory)

---

### Pitfall 4: Confusing Correlation with Causation in Reports

**What goes wrong:**
HTML stakeholder reports present correlation findings as causal recommendations. Non-technical stakeholders act on them as if they are actionable levers.

**Why it happens:**
Analysts know the distinction but communicate loosely. LLMs generating narrative summaries default to causal language ("X causes Y") when the evidence only supports correlation.

**How to avoid:**
Use explicit language templates: "X is associated with Y" not "X causes Y." HTML reports must include a disclaimer section. LLM prompts for report generation must enforce correlation-only language unless causal analysis was explicitly performed.

**Warning signs:**
Report uses words like "drives," "causes," "leads to" without causal methodology (e.g., DoWhy, A/B test, difference-in-differences).

**Phase to address:**
Phase 2 — Data Understanding (language in EDA); Phase 3 — Data Modelling (report generation prompts)

---

### Pitfall 5: Overfitting Mistaken for Model Quality

**What goes wrong:**
A model with 99% training accuracy is selected as the best model. It fails on new data. The leaderboard only shows in-sample or improperly validated metrics.

**Why it happens:**
Cross-validation is skipped for speed. k-fold is used without stratification for imbalanced classes. Leaderboard shows train score rather than validation score.

**How to avoid:**
Leaderboard must show only held-out validation scores (never training scores). Use stratified k-fold for classification. Report mean ± std across folds. Flag models where train/val gap exceeds a threshold.

**Warning signs:**
Training metric >> validation metric. Top leaderboard model is the most complex (deepest tree, most estimators). Model selection changes dramatically with different random seeds.

**Phase to address:**
Phase 3 — Data Modelling (leaderboard design, CV protocol)

---

### Pitfall 6: Distribution Assumption Violations

**What goes wrong:**
Statistical tests are applied to data that violates their assumptions (e.g., t-test on heavily skewed data, Pearson correlation on non-linear relationships, ARIMA on non-stationary series without differencing).

**Why it happens:**
Default test selection without checking assumptions. LLM-generated analysis code uses the most familiar test without verifying applicability.

**How to avoid:**
Data Understanding phase must include normality tests (Shapiro-Wilk, Q-Q plots), stationarity tests (ADF, KPSS for time series), and variance homogeneity tests (Levene's). Test selection should be conditional on these checks.

**Warning signs:**
EDA shows heavy skew or outliers but parametric tests are still used. Time series analysis proceeds without stationarity testing. Residual plots show non-random patterns.

**Phase to address:**
Phase 2 — Data Understanding

---

### Pitfall 7: Reproducibility Failures

**What goes wrong:**
A teammate cannot reproduce the analysis. The notebook runs on the original analyst's machine but fails elsewhere. Results differ between runs.

**Why it happens:**
Random seeds not set. Dependencies not pinned. Data preprocessing done outside the notebook (in Excel, manually). Docker not used consistently. Relative paths break between machines.

**How to avoid:**
All random seeds set at the top of every notebook (`np.random.seed(42)`, `set.seed(42)` in R). Docker environment with pinned `requirements.txt` / `renv.lock`. All data transformations inside the notebook. Absolute paths resolved from project root via environment variable.

**Warning signs:**
Notebook uses `pd.read_csv("../my local path/data.csv")`. No random seed at top. `pip install` inside notebook without version pins.

**Phase to address:**
Phase 0 — Infrastructure setup (Docker, project structure)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip cross-validation, use single train/test split | Faster iteration | Unreliable model selection, overfitting risk | Never in final analysis; OK for rapid prototyping only |
| Hardcode file paths | Quick to write | Breaks on teammate's machine, CI/CD | Never |
| Drop all rows with any missing value | Clean data fast | Loss of valuable data, biased results | Only if <1% missing and MCAR confirmed |
| Use accuracy for imbalanced classification | Simple metric | Misleading — 95% accuracy on 95/5 split means "always predict majority" | Never as primary metric for imbalanced data |
| Skip EDA, go straight to modelling | Time savings | Miss data quality issues, wrong model assumptions | Never |

## Statistical Pitfalls

| Pitfall | Symptoms | Prevention | Phase |
|---------|----------|------------|-------|
| Multiple testing without correction | Many significant p-values, most are noise | Apply Bonferroni or FDR (Benjamini-Hochberg) correction | Phase 2 |
| p-hacking — testing until significant | "Cherry-picked" findings | Pre-register hypotheses in Business Understanding | Phase 1 + 2 |
| Ignoring effect size — only reporting p-value | "Statistically significant but practically irrelevant" | Always report Cohen's d / eta-squared alongside p-value | Phase 2 |
| Stationarity ignored in time series | Spurious regressions (r²=0.99 between unrelated series) | ADF + KPSS tests mandatory before any time series model | Phase 2 |

## ML Modeling Pitfalls

| Pitfall | Symptoms | Prevention | Phase |
|---------|----------|------------|-------|
| No baseline model | Complex model looks good but simple model is just as good | Always start with DummyClassifier/DummyRegressor or mean prediction baseline | Phase 3 |
| Feature selection on full dataset | Optimistic feature importances | Feature selection inside CV loop only | Phase 3 |
| Wrong evaluation metric for business problem | High AUC but wrong operating point | Map business objective to metric in Phase 1 (precision vs recall tradeoff) | Phase 1 + 3 |
| Hyperparameter tuning on test set | Overly optimistic final performance | Never touch test set until final model selected | Phase 3 |
| Ignoring class imbalance | Model predicts majority class only | Report confusion matrix; use SMOTE, class weights, or stratified sampling | Phase 3 |

## LLM-Guided Analysis Pitfalls

| Pitfall | Risk | Prevention |
|---------|------|------------|
| LLM invents statistics | Fabricated p-values or effect sizes in narrative | All statistical claims must be code-generated in notebook; LLM only narrates verified outputs |
| LLM uses causal language for correlational findings | Stakeholders make wrong decisions | Report generation prompts must enforce associative language; human review gate |
| LLM selects inappropriate model without domain check | Wrong model family for problem type | Business Understanding phase explicitly determines problem type before any modelling prompt |
| LLM skips assumption checks | Invisible violations, wrong conclusions | Phase prompts must explicitly require assumption tests before model fitting |
| Context window compression loses earlier decisions | Contradictory recommendations across phases | STATE.md and PROJECT.md maintained to persist decisions across sessions |

## "Looks Done But Isn't" Checklist

- [ ] **EDA:** Often missing distribution tests — verify Shapiro-Wilk and outlier analysis are in notebook
- [ ] **Time series:** Often missing stationarity tests — verify ADF/KPSS before any ARIMA/Prophet
- [ ] **Classification:** Often missing confusion matrix + class balance report — verify both are present
- [ ] **Model comparison:** Often missing baseline — verify DummyClassifier/mean baseline is in leaderboard
- [ ] **HTML report:** Often missing caveats section — verify assumptions and limitations are stated
- [ ] **Reproducibility:** Often missing random seeds — verify `np.random.seed` / `set.seed` at notebook top
- [ ] **DuckDB queries:** Often missing query explanation — verify each SQL block has a markdown explanation cell
- [ ] **Forecasting:** Often missing prediction intervals — verify CI/PI bands are included with point forecasts

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Data leakage | Phase 3 — Modelling | Code review: preprocessing inside Pipeline |
| Temporal contamination | Phase 1 — Business Understanding | Confirm TimeSeriesSplit used if time factor |
| Poor business framing | Phase 1 — Business Understanding | Decision framing doc reviewed by stakeholder |
| Causal language | Phase 2 + 3 — EDA + Reporting | Report language audit checklist |
| Overfitting | Phase 3 — Modelling | Train vs val gap threshold check |
| Distribution violations | Phase 2 — Data Understanding | Assumption test notebook cells required |
| Reproducibility | Phase 0 — Infrastructure | Docker build + fresh run on teammate machine |
| LLM hallucination | All phases | All numeric claims traceable to notebook cell output |

## Sources

- CRISP-DM methodology — data mining process standard
- Scikit-learn documentation — preprocessing pipelines, CV best practices
- "Python for Data Analysis" (Wes McKinney) — pandas tidy data patterns
- "Statistical Rethinking" (Richard McElreath) — causal vs correlational reasoning
- "Forecasting: Principles and Practice" (Hyndman & Athanasopoulos) — time series CV, stationarity
- MLflow / DVC community pitfall documentation
- Kaggle post-mortems — common leakage patterns in competitions

---
*Pitfalls research for: Meta-prompting ML analysis framework (DoML)*
*Researched: 2026-04-04*
