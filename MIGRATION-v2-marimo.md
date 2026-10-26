# Migrating a DoML project from Jupyter to marimo (v2)

DoML v2 replaces Jupyter notebooks with marimo notebooks and removes the R workflow.

## What changed

| Before (v1) | After (v2) |
|---|---|
| `notebooks/*.ipynb`, outputs stripped by nbstripout | `notebooks/*.py` marimo apps; no outputs are ever stored |
| `jupyter nbconvert --execute --to html` | `python .claude/doml/bin/doml_nb.py run NB --report reports/X.html` |
| Narrative cells edited inside the notebook JSON | Markdown sidecars in `notebooks/narratives/<notebook>/<section>.md` |
| `quay.io/jupyter/datascience-notebook` image (5.9 GB, conda + pip) | `python:3.14-slim` + uv lock (2.1 GB, pip only) |
| `requirements.in` + `pip-compile` | `pyproject.toml` + `uv.lock` + hash-pinned `requirements.txt` |
| `docker-compose.yml`, service `jupyter`, port 8888 | `compose.yaml`, service `doml`, port 2718 (`marimo edit`) |
| Container path `/home/jovyan/work` | `/project` |
| R data-understanding notebook (`language: r`) | Removed. Data understanding is Python only |
| Kaggle: `KAGGLE_USERNAME` + `KAGGLE_KEY` | Also `KAGGLE_API_TOKEN` (recommended) |

## Steps for an existing project

1. Re-run the installer (`install.sh` or `install.ps1`) in the project root.
2. Copy the new environment files over the old ones, then delete the old ones:

   ```bash
   cp .claude/doml/templates/{Dockerfile,compose.yaml,pyproject.toml,uv.lock,requirements.txt} .
   rm -f docker-compose.yml requirements.in
   docker compose down && docker compose build && docker compose up -d
   ```

3. Re-run the DoML commands to make new marimo notebooks. Old `.ipynb` files are not
   converted (no Jupyter back-compatibility); delete them.
4. Remove `language` from `.planning/config.json`. Add `target_column` if it is missing.
5. Replace the nbstripout hook in `.pre-commit-config.yaml` with the `marimo check` hook from
   the DoML repository.
