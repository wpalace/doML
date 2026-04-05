# Architecture Research

**Domain:** Meta-prompting ML analysis framework (DoML)
**Researched:** 2026-04-04
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DoML Framework (installed)                    │
├──────────────────┬──────────────────┬───────────────────────────┤
│    Skills/       │    Workflows/    │    Agents/                │
│    Commands      │    Orchestration │    Subprocesses           │
│  /doml-new-*     │  new-project.md  │  doml-interviewer         │
│  /doml-plan-*    │  plan-phase.md   │  doml-eda-analyst         │
│  /doml-execute-* │  execute-phase.md│  doml-model-advisor       │
│  /doml-*         │  ...             │  doml-report-generator    │
├──────────────────┴──────────────────┴───────────────────────────┤
│                    Planning Artifacts                            │
│  .planning/PROJECT.md  .planning/ROADMAP.md  .planning/STATE.md │
│  .planning/config.json  .planning/phases/    .planning/research/ │
└─────────────────────────────────────────────────────────────────┘
          │ generates / orchestrates
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Analysis Project                              │
├─────────────────────────────────────────────────────────────────┤
│  data/           notebooks/         reports/       models/      │
│  ├── raw/        ├── 01_business_   ├── business_  ├── leaderbd │
│  ├── processed/  │   understanding  │   summary    ├── *.pkl    │
│  └── external/   ├── 02_eda         ├── eda_report └── *.joblib │
│                  ├── 03_modelling   ├── model_rpt               │
│                  └── 04_forecast    └── forecast_rpt            │
└─────────────────────────────────────────────────────────────────┘
          │ executes inside
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Docker Container                                    │
│         (jupyter/datascience-notebook)                          │
│   Python 3.11 | R 4.3 | JupyterLab 4 | DuckDB | pandas        │
│   scikit-learn | tidyverse | statsmodels | Prophet | SHAP       │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Skills | Entry points — map user commands to workflows | Markdown files with YAML frontmatter (like GSD) |
| Workflows | Step-by-step orchestration logic | Markdown files executed by Claude |
| Agents | Specialized subprocesses for research/analysis | Spawned via Agent tool with focused prompts |
| Planning artifacts | Persistent state across sessions | `.planning/` directory tree |
| Notebooks | Analysis outputs — reproducible, peer-reviewable | One `.ipynb` per phase per milestone |
| HTML reports | Stakeholder outputs — insight-focused | nbconvert export + Claude-generated summary |
| Docker environment | Reproducible compute environment | `docker-compose.yml` + `jupyter/datascience-notebook` |
| DuckDB | Large-dataset EDA and wrangling | In-notebook SQL queries on `/data/` files |

## Recommended Project Structure

### Framework Structure (DoML installation)

```
~/.claude/get-shit-done/ (or .doml/ per project)
├── skills/
│   ├── doml-new-project/SKILL.md
│   ├── doml-plan-phase/SKILL.md
│   ├── doml-execute-phase/SKILL.md
│   └── doml-*/SKILL.md
├── workflows/
│   ├── new-project.md
│   ├── plan-phase.md
│   ├── execute-phase.md
│   ├── business-understanding.md
│   ├── data-understanding.md
│   ├── data-modelling.md
│   └── forecasting.md
├── agents/
│   ├── doml-interviewer.md
│   ├── doml-eda-analyst.md
│   ├── doml-model-advisor.md
│   └── doml-report-generator.md
├── templates/
│   ├── notebooks/
│   │   ├── 01_business_understanding.ipynb
│   │   ├── 02_data_understanding.ipynb
│   │   ├── 03_data_modelling.ipynb
│   │   └── 04_forecasting.ipynb
│   ├── reports/
│   │   ├── executive_summary.html.j2
│   │   └── technical_report.html.j2
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   └── requirements.txt
│   ├── project.md
│   ├── state.md
│   └── roadmap.md
└── references/
    ├── ml-best-practices.md
    ├── statistical-tests.md
    ├── tidy-data.md
    └── problem-type-guide.md
```

### Analysis Project Structure (Cookiecutter Data Science convention)

```
my-analysis/
├── .planning/                  # DoML artifacts (like GSD)
│   ├── PROJECT.md
│   ├── ROADMAP.md
│   ├── STATE.md
│   ├── config.json
│   └── phases/
│       ├── phase-1/
│       └── phase-2/
├── data/
│   ├── raw/                    # IMMUTABLE — never modified after deposit
│   ├── processed/              # Derived from raw — notebook outputs
│   └── external/               # Third-party reference data
├── notebooks/
│   ├── 01_business_understanding.ipynb
│   ├── 02_data_understanding.ipynb
│   ├── 03_data_modelling.ipynb
│   └── 04_forecasting.ipynb    # Optional — time series only
├── reports/
│   ├── business_summary.html
│   ├── eda_report.html
│   ├── model_report.html
│   └── figures/
├── models/
│   ├── leaderboard.csv
│   ├── best_model.pkl          # or .joblib
│   └── model_metadata.json
├── docker-compose.yml
├── requirements.txt            # Pinned Python deps
└── CLAUDE.md                   # DoML project instructions
```

## Architectural Patterns

### Pattern 1: Phase-per-Notebook

**What:** Each analysis phase produces exactly one primary Jupyter notebook. Notebooks are named sequentially and contain all code, narrative, and outputs for that phase.

**When to use:** Always — this is the core DoML output contract.

**Trade-offs:**
- Pro: Easy to navigate, peer-review, and reproduce one phase at a time
- Con: Long notebooks can become unwieldy; mitigation is clear section headers and collapsible cells

### Pattern 2: Data Immutability (Kedro-inspired)

**What:** Raw data in `/data/raw/` is never modified. All transformations produce new files in `/data/processed/`. DuckDB queries raw files directly without copying.

**When to use:** Always — prevents accidental data corruption and enables reproducibility.

**Trade-offs:**
- Pro: Full audit trail; raw data always recoverable; DuckDB queries are zero-copy
- Con: Storage duplication — mitigated by DuckDB's lazy evaluation on Parquet

### Pattern 3: Dual-Output Pipeline

**What:** Every phase produces two outputs — a technical Jupyter notebook and a stakeholder HTML report. The notebook is the source of truth; the report is derived from it.

**When to use:** Always — separates audiences at the output layer, not at the analysis layer.

**Trade-offs:**
- Pro: One analysis, two audiences; no duplication of analytical work
- Con: Report generation adds time; mitigated by LLM-assisted summary generation

### Pattern 4: Problem-Type-Aware Workflow Branching

**What:** Business Understanding phase determines the ML problem type (regression, classification, clustering, time series, dimensionality reduction). Subsequent phases load problem-type-specific templates, metrics, and tests.

**When to use:** Always — prevents mismatched evaluation metrics and inappropriate statistical tests.

## Data Flow

```
User deposits data
    ↓
/data/raw/ (immutable)
    ↓
Phase 1: Business Understanding
    → Guided interview → problem_type confirmed
    → business_understanding.ipynb (narrative + data inventory)
    → business_summary.html
    ↓
Phase 2: Data Understanding
    → DuckDB queries /data/raw/ directly (zero-copy EDA)
    → Statistical tests (normality, stationarity, distributions)
    → /data/processed/ (cleaned, feature-engineered datasets)
    → data_understanding.ipynb + eda_report.html
    ↓
Phase 3: Data Modelling
    → Reads /data/processed/
    → Fits multiple models (problem-type specific)
    → Leaderboard → /models/leaderboard.csv
    → Best model → /models/best_model.pkl
    → data_modelling.ipynb + model_report.html
    ↓
Phase 4: Forecasting (time series only)
    → Reads /data/processed/ + best_model.pkl
    → Generates forecasts with prediction intervals
    → Tracks actuals as new data arrives
    → forecasting.ipynb + forecast_report.html
```

## Anti-Patterns

### Anti-Pattern 1: Modifying Raw Data

**What people do:** Transform raw files in-place to "clean" the data directory.

**Why it's wrong:** Destroys the audit trail. Impossible to know what the original data looked like if a transformation is later found to be wrong.

**Do this instead:** All transformations write to `/data/processed/`. Document each transformation step in the EDA notebook.

### Anti-Pattern 2: One Giant Notebook

**What people do:** Put all analysis in a single `analysis.ipynb`.

**Why it's wrong:** Non-reviewable, non-reproducible at phase level, impossible to hand off.

**Do this instead:** Strict one-notebook-per-phase convention. Notebooks can import from each other but each phase is independently runnable.

### Anti-Pattern 3: Skipping Business Understanding

**What people do:** Jump straight to EDA because "the data is already there."

**Why it's wrong:** Without documented problem type and business question, all downstream analysis is unanchored. Model selection and evaluation metrics become arbitrary.

**Do this instead:** Business Understanding phase is mandatory and produces a written decision framing document before any data is touched.

### Anti-Pattern 4: Hardcoded Paths

**What people do:** `pd.read_csv("/Users/john/projects/analysis/data/raw/file.csv")`

**Why it's wrong:** Breaks reproducibility for any other team member.

**Do this instead:** Use environment variable `PROJECT_ROOT` resolved from Docker working directory. All paths relative to project root.

## Open Questions (to verify before implementation)

- Exact `jupyter/datascience-notebook` image tag and pre-installed package versions — verify against current Jupyter Docker Stacks docs
- DuckDB Python API surface for notebook integration — verify `duckdb.connect()` patterns against current docs
- `nbconvert --no-input` flag for hiding code cells in HTML export — verify behavior
- Whether DoML needs its own `doml-tools.cjs` binary (like GSD's `gsd-tools.cjs`) or can reuse/adapt GSD's tooling

## Sources

- GSD (Get Shit Done) source code in `/home/bill/source/DoML/.claude/get-shit-done/` — directly inspected
- Cookiecutter Data Science — standard DS project structure
- CRISP-DM methodology — phase pipeline mapping
- Kedro data catalog pattern — data immutability principle
- Jupyter Docker Stacks — `jupyter/datascience-notebook` base image

---
*Architecture research for: Meta-prompting ML analysis framework (DoML)*
*Researched: 2026-04-04*
