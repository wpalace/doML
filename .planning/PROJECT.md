# DoML — Do Machine Learning

## What This Is

DoML is a meta-prompting framework (inspired by GSD) that guides a data science team through ML analysis using Claude Code or other LLMs. Unlike GSD, whose goal is to *build* software, DoML's goal is to *understand* a dataset — producing reproducible Jupyter notebooks that explain findings to technical peers and clean HTML reports that deliver insights to non-technical stakeholders.

## Core Value

A data scientist can drop a dataset into `/data`, answer a few questions, and get a fully reproducible, peer-reviewable ML analysis with stakeholder-ready summaries — without re-inventing the process each time.

## Current State

**Last shipped:** v1.5 Public Release + Install Scripts (2026-04-30) — DoML is now publicly installable via Bash and PowerShell one-liners with optional GitHub Copilot target. See `.planning/MILESTONES.md`.

**Next milestone:** TBD — run `/gsd-new-milestone` to plan.

## Requirements

### Validated

**Public Release + Install (v1.5)**
- ✓ `install.sh` (Bash) and `install.ps1` (PowerShell) — archive-based framework installers (no `git clone`) with VERSION pinning, fail-fast error handling, and idempotent `data/` preservation — v1.5
- ✓ `README.md` at repo root with Quick Start one-liners, Mermaid new-project flow diagram, command table, AI token investment note — v1.5
- ✓ MIT `LICENSE` (Copyright (c) 2026 William W Palace, III) and `.github/FUNDING.yml` (PayPal + Venmo) for GitHub Sponsor button — v1.5
- ✓ `--target claude|copilot` flag on both installers; copilot branch installs SKILL.md to `.github/skills/`, workflows + templates to `.github/doml/`, `CLAUDE.md` as `.github/copilot-instructions.md`, and `AGENTS.md` at project root — v1.5
- ✓ Tool-neutral `AGENTS.md` template for cross-agent compatibility (Copilot, Cursor, Gemini, Claude) — v1.5
- ✓ D-06: `CLAUDE.md` always overwritten on install so framework upgrades pull in changes — v1.5

**Deployment (v1.4)**
- ✓ `doml-deploy-model` command deploys the #1 leaderboard model (or user-specified override) to a chosen target — v1.4
- ✓ CLI target: PyInstaller-compiled portable binary, no Python required on target machine — v1.4
- ✓ Web service target: FastAPI app in Docker with auto-generated HTML prediction form — v1.4
- ✓ ONNX/WASM target: self-contained HTML page using onnxruntime-web, zero server dependency — v1.4
- ✓ Performance report: Jupyter notebook + HTML with latency benchmarks and parity test — v1.4
- ✓ Output layout: `src/<modelname>/v1/` with version iterations — v1.4
- ✓ `doml-iterate-deployment` re-deploys with same model (version bump) or new model (new folder) — v1.4
- ✓ `doml-iterate-deployment` accepts `--guidance` and runs without requiring a new model — v1.4
- ✓ Supported problem types: Regression, Classification, Clustering, Forecasting — v1.4

### Active

(None — run `/gsd-new-milestone` to plan the next milestone)

### Carryover Tech Debt

- v1.5 phases 19, 20 missing SUMMARY.md and VERIFICATION.md (paperwork; artifacts shipped)
- REQUIREMENTS.md text was stale for INST-06, INST-07, INST-08, COP-03, DOC-05 at archive time (locked decisions D-01..D-06 not back-propagated to spec)
- Phase 21 VERIFICATION.md predates fixes 2fa0413 and 4e90677 (workflows + templates installation in copilot branch)
- VALIDATION.md missing for phases 19, 20; phase 21 VALIDATION.md is draft (`nyquist_compliant: false`)
- COP-04 needs human verification in VS Code Copilot Chat
- README "Future Milestones" section has spelling errors
- Phase 10 carryover: 3 unresolved `human_uat` items in `10-HUMAN-UAT.md`

### Active (continued — original v1.0+ requirements)

**Framework Architecture**
- [ ] DoML-specific skill/agent/workflow structure inspired by GSD (not a GSD plugin — standalone framework)
- [ ] Commands: `/doml-new-project`, `/doml-plan-phase`, `/doml-execute-phase`, and milestone equivalents
- [ ] Guided kickoff interview that validates `/data` folder contents and infers ML problem type
- [ ] Business understanding phase always clarifies whether time is a factor (determines if forecasting applies)

**Analysis Pipeline (per milestone)**
- [ ] Phase 1 — Business Understanding: capture background, stakeholder context, business question, confirm problem type
- [ ] Phase 2 — Data Understanding: EDA, statistical tests, distribution analysis, data provenance, assumptions documentation; DuckDB used for large-dataset wrangling and SQL-based exploratory queries
- [ ] Phase 3 — Data Modelling: model fitting, comparison leaderboard, hyperparameter tuning, model explainability
- [ ] Phase 4 — Forecasting (optional, time-series only): generate forecasts, track actuals as new data arrives

**Traditional ML Problem Types (Milestone 1 scope)**
- [ ] Regression (linear, ridge, lasso, tree-based — XGBoost, RF)
- [ ] Classification (binary and multi-class, calibration, ROC analysis)
- [ ] Clustering (k-means, DBSCAN, hierarchical)
- [ ] Time series (ARIMA, Prophet, statsmodels-based forecasting)
- [ ] Dimensionality reduction (PCA, t-SNE, UMAP)

**Outputs**
- [ ] Jupyter notebooks per phase — reproducible, peer-reviewable, runnable in Docker
- [ ] HTML executive summary (Claude-generated: key findings + recommendations + visualizations)
- [ ] HTML rendered notebook export (code cells hidden — narrative and charts only for stakeholders)
- [ ] Tidy data principles observed in all notebooks regardless of language (Python or R)

**Infrastructure**
- [ ] Docker environment generated by DoML — default base: `jupyter/datascience-notebook` (Python + R)
- [ ] Docker container stands up at project start; all notebooks run inside it
- [ ] DuckDB available in the Docker environment for large-dataset wrangling and exploratory analysis
- [ ] Data formats supported: CSV/TSV, Parquet/Arrow, Excel (.xlsx)
- [ ] `/data` folder present and validated before analysis begins

### Out of Scope

- **Deep learning** — deferred to Milestone 2; adds PyTorch/TensorFlow/Keras and transfer learning workflows
- **NLP / text data** — deferred to a future milestone
- **Real-time / streaming data** — batch analysis only in Milestone 1
- **Custom Docker base images** — users use the Jupyter data science container; custom images are user responsibility
- **SQL database connectors** — DuckDB covers analytical SQL needs; connecting to Postgres/MySQL/etc. deferred
- **GSD plugin architecture** — DoML is standalone, inspired by GSD but not dependent on it

## Context

- **Inspired by GSD**: DoML mirrors GSD's skill/agent/workflow meta-prompting architecture but is purpose-built for ML analysis workflows
- **CRISP-DM influence**: The four-phase pipeline (Business → Data → Modelling → Forecasting) is inspired by CRISP-DM but simplified and adapted for the LLM-assisted workflow
- **Target users**: DS teams (multiple collaborators) — notebooks must be reproducible and peer-reviewable
- **Dual audience**: Data scientists consume notebooks; non-technical stakeholders consume HTML reports
- **DuckDB as analytical backbone**: DuckDB enables fast SQL-based EDA on large flat files (CSV, Parquet) without a database server — natural fit for the `/data`-centric workflow
- **Research-heavy**: Best practices for each ML problem type should be researched before implementing phase workflows — the framework should encode domain knowledge, not just scaffold structure
- **Milestone model**: Milestone 1 = traditional ML. Subsequent milestones extend problem type coverage (deep learning, NLP, etc.)

## Constraints

- **Runtime**: Jupyter notebooks inside Docker — `jupyter/datascience-notebook` as default base image
- **Languages**: Python and R — both supported; tidy data principles required in either
- **Data locality**: All data lives in `/data` at project root — no external database connections in Milestone 1
- **Data formats**: CSV/TSV, Parquet/Arrow, Excel (.xlsx) — no SQL connectors in Milestone 1
- **Analytical SQL**: DuckDB is the preferred tool for large-dataset wrangling and exploratory queries
- **Reproducibility**: All analysis must be fully reproducible by any team member with Docker installed
- **Separation of concerns**: Technical depth in notebooks; insight delivery in HTML reports — never conflate audiences

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Standalone framework (not GSD plugin) | DoML has fundamentally different phase structure and domain concepts; coupling to GSD would add friction | — Pending |
| Jupyter data science container as default | Official Jupyter team image supports both Python and R out of the box; reduces Docker setup complexity | — Pending |
| Forecasting as optional phase | Time is not always a factor; forcing forecasting on classification/clustering problems adds noise | — Pending |
| Both HTML outputs (summary + rendered notebook) | Non-technical stakeholders need narrative summaries; technical reviewers need the full notebook | — Pending |
| Tidy data as universal principle | Consistent data structure across Python (pandas) and R (tidyverse) simplifies cross-language workflows | — Pending |
| DuckDB for large-dataset EDA | Handles CSV/Parquet at scale without a database server; SQL is familiar to most data practitioners | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/doml-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/doml-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-30 — after v1.5 Public Release + Install Scripts milestone*
