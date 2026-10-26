# AGENTS.md — DoML Analysis Project

Cross-agent instructions for AI coding assistants (GitHub Copilot, Cursor, Gemini CLI, Claude Code,
and others) working in this DoML project.

## What Is DoML

DoML (Do Machine Learning) is a meta-prompting ML analysis framework. A data scientist drops a
dataset into `/data`, answers guided questions, and gets a fully reproducible, peer-reviewable
ML analysis with stakeholder-ready summaries — without reinventing the process each time.

This project was scaffolded by DoML. All analysis follows CRISP-DM phases implemented as
marimo notebooks with Docker-based execution.

## Project Structure

| Path | Description | Access |
|------|-------------|--------|
| `data/raw/` | IMMUTABLE source data — never modify | Read-only mount |
| `data/processed/` | Cleaned datasets (EDA output) | Writable |
| `data/external/` | Reference data / lookups | Read-only mount |
| `notebooks/` | marimo notebooks (`.py`), one per DoML phase; `narratives/` sidecars | Writable |
| `reports/` | Stakeholder HTML reports (code hidden) | Writable |
| `models/` | Serialized model artifacts + metadata JSON | Writable |
| `src/` | Deployment artifacts (CLI, web, WASM) | Writable |

## marimo Notebooks

Every notebook is a marimo app: a plain-Python `.py` file, one function per cell, run in
dependency order. A variable may be defined in one cell only (edit the defining cell to change
it; `_name` is cell-private). Outputs are never stored in the file. Narratives (executive
summary, interpretation, iteration direction) are Markdown sidecars in
`notebooks/narratives/<notebook stem>/<section>.md` that the notebook renders.

```bash
docker compose exec doml python .claude/doml/bin/doml_nb.py run notebooks/<nb>.py --report reports/<name>.html
python3 .claude/doml/bin/doml_nb.py verify-report reports/<name>.html
docker compose exec doml marimo check --strict notebooks/
```

## Reproducibility Rules (Non-Negotiable)

### 1. Random seeds at the top of every notebook

```python
import os, random
import numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
```

Set before any sampling, train/test split, or model fit.

### 2. Relative paths via PROJECT_ROOT

Never hardcode absolute paths. Resolve from the environment variable (`/project` in the container):

```python
import os
from pathlib import Path
PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', str(mo.notebook_dir().parent)))
raw_data = PROJECT_ROOT / 'data' / 'raw' / 'sales.csv'
```

### 3. Raw data is immutable

`data/raw/` is mounted read-only in the container. Never write to it. If source data changes,
add a new dated file (e.g., `sales_2026-04-01.csv`) — do not overwrite.

### 4. No outputs in git

marimo notebooks hold code only, so there is nothing to strip. Outputs live in `reports/*.html`.

### 5. Pinned dependencies

`pyproject.toml` (direct deps) → `uv.lock` (full pin) → `requirements.txt` (hash-pinned export
installed by the image). Regenerate: `uv lock && uv export --frozen --no-emit-project --no-dev -o requirements.txt`

## Running the Environment

```bash
docker compose up -d              # Start the marimo editor at http://localhost:2718
docker compose exec doml bash     # Shell inside container
docker compose build              # Rebuild after changing pyproject.toml/requirements.txt or Dockerfile
docker compose down               # Stop
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
- Never use `pip install` inside the container without updating `pyproject.toml` and the lock
- Never hardcode absolute paths
- Never skip random seeds
- Never use AutoML tools that hide the decision trail — DoML's purpose is traceable analysis
- Never use time-based train/test splits for time series (use `TimeSeriesSplit` only)
