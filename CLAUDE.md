# CLAUDE.md — DoML Analysis Project Instructions

This project was scaffolded by **DoML** (Do Machine Learning). Claude Code should follow these conventions when working in this repository.

## Project Structure

```
data/raw/          # IMMUTABLE source data — read-only mount, never modify
data/processed/    # cleaned datasets (EDA output) — safe to write
data/external/     # reference data (lookups) — read-only mount
notebooks/         # marimo notebooks (plain .py files), one per DoML phase
notebooks/narratives/  # Markdown sidecars (summary, interpretation, ...) the notebooks render
reports/           # stakeholder HTML reports (marimo export, code hidden)
models/            # serialized model artifacts + metadata JSON + leaderboards
src/               # deployment artifacts (CLI, web, WASM)
```

## Notebooks are marimo apps

Every DoML notebook is a [marimo](https://marimo.io) notebook: a pure-Python file with one
function per cell. marimo runs cells in dependency order (a reactive graph), so there is no
hidden state and no "run all cells from the top" ritual.

- **One definition per name.** A variable may be defined in one cell only. To change a value,
  edit the cell that defines it. Names that start with `_` are private to their cell.
- **Outputs are never stored in the notebook.** They live in the exported HTML report only.
  There is nothing to strip before a commit, and diffs are clean Python diffs.
- **Narratives are sidecar files.** Executive summaries and interpretations are Markdown files
  in `notebooks/narratives/<notebook stem>/<section>.md`. The notebook renders them. Never
  paste narrative text into code.
- **Run and export headlessly** with the DoML helper (inside the container):

```bash
docker compose exec doml python .claude/doml/bin/doml_nb.py run notebooks/02_data_understanding.py --report reports/eda_report.html
python3 .claude/doml/bin/doml_nb.py verify-report reports/eda_report.html   # code hidden, no cell errors
python3 .claude/doml/bin/doml_nb.py outputs reports/eda_report.html         # read the outputs as text
docker compose exec doml marimo check --strict notebooks/                   # lint the notebooks
```

- **Edit interactively** at http://localhost:2718 (`marimo edit`, started by `docker compose up`).

## Reproducibility Rules (Non-Negotiable)

### 1. Random seeds at the top of every notebook (REPR-01)

```python
import os, random
import numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
```

Set before any sampling, train/test split, or model fit.

### 2. Relative paths via PROJECT_ROOT (REPR-02)

Never hardcode absolute paths. Resolve from the env var (the container sets `PROJECT_ROOT=/project`;
outside the container the notebook falls back to its own parent directory):

```python
import os
from pathlib import Path
PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', str(mo.notebook_dir().parent)))
raw_data = PROJECT_ROOT / 'data' / 'raw' / 'sales.csv'
```

### 3. Raw data is immutable (INFR-05)

`data/raw/` is mounted **read-only** in the container. Any attempt to write there will fail. If source data changes, add a new dated file (`sales_2026-04-01.csv`), do not overwrite. See `data/raw/README.md`.

### 4. No outputs in git (REPR-03)

marimo notebooks are plain Python and never contain outputs, so nothing needs stripping.
Reports in `reports/*.html` hold the outputs for stakeholders (they are git-ignored).
Re-running a notebook replaces its own leaderboard rows; it never duplicates them.

### 5. Pinned dependencies (REPR-04)

`pyproject.toml` lists the direct dependencies; `uv.lock` pins the full graph; `requirements.txt`
is the hash-pinned export the image installs. Never edit `requirements.txt` by hand. After
changing `pyproject.toml`:

```bash
uv lock && uv export --frozen --no-emit-project --no-dev -o requirements.txt
docker compose build
```

## DoML Analysis Conventions

### DuckDB first

For any tabular profiling, aggregation, or join, prefer DuckDB over pandas when the input is on disk. DuckDB scans CSV/Parquet zero-copy — no need to load into memory first.

```python
import duckdb
df = duckdb.sql("SELECT * FROM 'data/raw/sales.csv' WHERE region = 'EU'").df()
```

DuckDB is **always installed** in this environment, regardless of whether you prefer pandas for downstream work.

### Tidy data before feature engineering

Validate that data conforms to tidy principles (one observation per row, one variable per column, one value per cell) **before** any feature engineering. Flag violations in the EDA notebook — do not silently reshape raw data.

### Correlation is not causation

Every stakeholder HTML report must include a caveats section stating this explicitly (OUT-03).

## Running the Environment

```bash
# Start the marimo editor at http://localhost:2718 (set MARIMO_TOKEN in .env to require a password)
docker compose up -d

# Open a shell inside the container
docker compose exec doml bash

# Rebuild after changing pyproject.toml/requirements.txt or Dockerfile
docker compose build

# Stop
docker compose down
```

## What NOT To Do

- Never modify files in `data/raw/`
- Never commit raw data files, model pickles, or HTML reports to git
- Never use `pip install` inside the container without updating `pyproject.toml` and the lock
- Never hardcode absolute paths like `/project/data/...`
- Never define the same variable in two marimo cells — edit the defining cell instead
- Never skip random seeds
- Never use AutoML tools that hide the decision trail — DoML's purpose is traceable analysis

## DoML Framework

This project uses DoML. Framework commands available in Claude Code:
- `/doml-new-project` — guided project kickoff: interview → Docker generation → scaffold → planning artifacts
- `/doml-business-understanding` — run the Business Understanding phase (notebook + HTML report)
- `/doml-data-understanding` — run the Data Understanding / EDA phase (notebook + HTML report)
- `/doml-modelling` — run Modelling for any problem type (preprocessing + modelling + report where applicable)
- `/doml-iterate` — run a new modelling iteration for any problem type; reads `problem_type` from `config.json` and routes automatically (regression, classification, clustering, dimensionality_reduction)
- `/doml-progress` — show current project status, completed phases, and next recommended action
