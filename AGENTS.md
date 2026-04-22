# AGENTS.md — DoML Analysis Project

Cross-agent instructions for AI coding assistants (GitHub Copilot, Cursor, Gemini CLI, Claude Code,
and others) working in this DoML project.

## What Is DoML

DoML (Do Machine Learning) is a meta-prompting ML analysis framework. A data scientist drops a
dataset into `/data`, answers guided questions, and gets a fully reproducible, peer-reviewable
ML analysis with stakeholder-ready summaries — without reinventing the process each time.

This project was scaffolded by DoML. All analysis follows CRISP-DM phases implemented as
Jupyter notebooks with Docker-based execution.

## Project Structure

| Path | Description | Access |
|------|-------------|--------|
| `data/raw/` | IMMUTABLE source data — never modify | Read-only mount |
| `data/processed/` | Cleaned datasets (EDA output) | Writable |
| `data/external/` | Reference data / lookups | Read-only mount |
| `notebooks/` | Jupyter notebooks, one per DoML phase | Writable |
| `reports/` | Stakeholder HTML reports (code hidden) | Writable |
| `models/` | Serialized model artifacts + metadata JSON | Writable |
| `src/` | Deployment artifacts (CLI, web, WASM) | Writable |

## Reproducibility Rules (Non-Negotiable)

### 1. Random seeds at the top of every notebook

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

### 2. Relative paths via PROJECT_ROOT

Never hardcode absolute paths. Resolve from the environment variable:

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

### 3. Raw data is immutable

`data/raw/` is mounted read-only in the container. Never write to it. If source data changes,
add a new dated file (e.g., `sales_2026-04-01.csv`) — do not overwrite.

### 4. Notebook outputs stripped on commit

`nbstripout` runs as a pre-commit hook. Outputs, execution counts, and selected metadata are
stripped before commit. Re-run the notebook to see outputs again.

### 5. Pinned dependencies

`requirements.txt` pins every package with `==`. Edit `requirements.in` (unpinned) and
regenerate: `docker compose run --rm jupyter pip-compile requirements.in`

## Running the Environment

```bash
docker compose up         # Start JupyterLab at http://localhost:8888
docker compose exec jupyter bash  # Shell inside container
docker compose build      # Rebuild after changing requirements.txt or Dockerfile
docker compose down       # Stop
```

## DoML Commands

Run these commands in your AI coding assistant to execute DoML analysis phases:

| Command | Description |
|---------|-------------|
| `doml-new-project` | Guided project kickoff: interview, Docker generation, scaffold, planning artifacts |
| `doml-business-understanding` | Run the Business Understanding phase (notebook + HTML report) |
| `doml-data-understanding` | Run the Data Understanding / EDA phase (notebook + HTML report) |
| `doml-modelling` | Run Modelling for any problem type (preprocessing + modelling + report) |
| `doml-iterate` | Run a new modelling iteration; auto-detects problem_type from config.json |
| `doml-anomaly-detection` | Run anomaly detection phase (Isolation Forest, LOF, DBSCAN) |
| `doml-forecasting` | Run time series forecasting (only when time_factor=true in config.json) |
| `doml-get-data` | Download datasets from Kaggle or direct URL into data/raw/ |
| `doml-deploy-model` | Package the best model into a deployment target (CLI, web service, or WASM) |
| `doml-deploy-cli` | Build a portable CLI binary from the best model using PyInstaller |
| `doml-deploy-web` | Generate a FastAPI web service for the best model |
| `doml-deploy-wasm` | Convert model to ONNX and generate a self-contained browser inference page |
| `doml-iterate-deployment` | Iterate a deployed model (version bump or new model) |
| `doml-progress` | Show current project status, completed phases, and next recommended action |

Invocation syntax varies by tool:
- GitHub Copilot Chat: `/doml-new-project`
- Claude Code: `/doml-new-project`
- Cursor / other tools: follow your tool's skill invocation syntax

## DuckDB First

For any tabular profiling, aggregation, or join, prefer DuckDB over pandas when input is on disk.
DuckDB scans CSV/Parquet zero-copy — no need to load into memory first.

```python
import duckdb
df = duckdb.sql("SELECT * FROM 'data/raw/sales.csv' WHERE region = 'EU'").df()
```

## What NOT To Do

- Never modify files in `data/raw/`
- Never commit raw data files, model pickles, or HTML reports to git
- Never use `pip install` inside the container without updating `requirements.in`
- Never hardcode absolute paths
- Never skip random seeds
- Never use AutoML tools that hide the decision trail — DoML's purpose is traceable analysis
- Never use time-based train/test splits for time series (use `TimeSeriesSplit` only)
