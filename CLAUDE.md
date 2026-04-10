# CLAUDE.md — DoML Analysis Project Instructions

This project was scaffolded by **DoML** (Do Machine Learning). Claude Code should follow these conventions when working in this repository.

## Project Structure

```
data/raw/          # IMMUTABLE source data — read-only mount, never modify
data/processed/    # cleaned datasets (EDA output) — safe to write
data/external/     # reference data (lookups) — read-only mount
notebooks/         # Jupyter notebooks, one per DoML phase
reports/           # stakeholder HTML reports (nbconvert output, code hidden)
models/            # serialized model artifacts + metadata JSON
```

## Reproducibility Rules (Non-Negotiable)

### 1. Random seeds at the top of every notebook (REPR-01)

Python:
```python
import os, random
import numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
```

R:
```r
set.seed(42)
```

Set before any sampling, train/test split, or model fit.

### 2. Relative paths via PROJECT_ROOT (REPR-02)

Never hardcode absolute paths. Resolve from the env var:

Python:
```python
import os
from pathlib import Path
PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', '/home/jovyan/work'))
raw_data = PROJECT_ROOT / 'data' / 'raw' / 'sales.csv'
```

R:
```r
PROJECT_ROOT <- Sys.getenv("PROJECT_ROOT", unset = "/home/jovyan/work")
raw_data <- file.path(PROJECT_ROOT, "data", "raw", "sales.csv")
```

### 3. Raw data is immutable (INFR-05)

`data/raw/` is mounted **read-only** in the container. Any attempt to write there will fail. If source data changes, add a new dated file (`sales_2026-04-01.csv`), do not overwrite. See `data/raw/README.md`.

### 4. Notebook outputs stripped on commit (REPR-03)

`nbstripout` runs as a pre-commit hook. It strips cell outputs, execution counts, and selected metadata from `.ipynb` files before they're committed.

**Heads-up:** The hook modifies your working copy, not just the staged snapshot. After `git commit`, your local `.ipynb` will no longer show outputs. This is expected — re-run the notebook to see outputs again. Reports in `reports/*.html` preserve outputs for stakeholders.

One-time setup (already done if this project came from DoML):
```bash
pip install pre-commit
pre-commit install
```

### 5. Pinned dependencies (REPR-04)

`requirements.txt` pins every Python package with `==`. Never edit it by hand — edit `requirements.in` (unpinned top-level deps) and regenerate:

```bash
docker compose run --rm jupyter pip-compile requirements.in
```

After changing `requirements.txt`, rebuild: `docker compose build`.

R packages: use `renv::snapshot()` to write `renv.lock` if you opt into R.

## DoML Analysis Conventions

### DuckDB first

For any tabular profiling, aggregation, or join, prefer DuckDB over pandas when the input is on disk. DuckDB scans CSV/Parquet zero-copy — no need to load into memory first.

Python:
```python
import duckdb
df = duckdb.sql("SELECT * FROM 'data/raw/sales.csv' WHERE region = 'EU'").df()
```

R:
```r
library(duckdb)
con <- dbConnect(duckdb())
df <- dbGetQuery(con, "SELECT * FROM 'data/raw/sales.csv' WHERE region = 'EU'")
```

DuckDB is **always installed** in this environment, regardless of whether you prefer pandas/dplyr for downstream work.

### Tidy data before feature engineering

Validate that data conforms to tidy principles (one observation per row, one variable per column, one value per cell) **before** any feature engineering. Flag violations in the EDA notebook — do not silently reshape raw data.

### Correlation is not causation

Every stakeholder HTML report must include a caveats section stating this explicitly (OUT-03).

## Running the Environment

```bash
# Start JupyterLab at http://localhost:8888
docker compose up

# Open a shell inside the container
docker compose exec jupyter bash

# Rebuild after changing requirements.txt or Dockerfile
docker compose build

# Stop
docker compose down
```

## What NOT To Do

- Never modify files in `data/raw/`
- Never commit raw data files, model pickles, or HTML reports to git
- Never use `pip install` inside the container without updating `requirements.in`
- Never hardcode absolute paths like `/home/jovyan/work/data/...`
- Never skip random seeds
- Never use AutoML tools that hide the decision trail — DoML's purpose is traceable analysis

## DoML Framework

This project uses DoML. Framework commands available in Claude Code:
- `/doml-new-project` — guided project kickoff: interview → Docker generation → scaffold → planning artifacts
- `/doml-business-understanding` — run the Business Understanding phase (notebook + HTML report)
- `/doml-data-understanding` — run the Data Understanding / EDA phase (notebook + HTML report)
- `/doml-modelling` — run Modelling for any problem type (preprocessing + modelling + report where applicable)
- `/doml-iterate-model` — run a new supervised modelling iteration with analyst direction
- `/doml-iterate-unsupervised` — run a new unsupervised modelling iteration with analyst direction
- `/doml-progress` — show current project status, completed phases, and next recommended action
