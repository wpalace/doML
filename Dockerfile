# syntax=docker/dockerfile:1.7
# DoML analysis environment — Python 3.14 + DuckDB + ML stack
# Base: Jupyter SciPy Notebook (quay.io — Docker Hub frozen since 2023-10-20)
FROM quay.io/jupyter/scipy-notebook:2026-04-27

LABEL maintainer="DoML framework"
LABEL description="Reproducible ML analysis environment with Python and DuckDB"

# --- Vendor uv binary from the official Astral image (pinned) ---
# Per research/STACK.md + ARCHITECTURE.md: do NOT `pip install uv` — supply chain + non-determinism.
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/

# --- uv environment knobs (Astral "Using uv in Docker" guide) ---
# UV_LINK_MODE=copy is mandatory — cache mount + target site-packages cross filesystems,
# hardlink mode would error out. UV_COMPILE_BYTECODE precompiles .pyc at install for fast first launch.
ENV \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_SYSTEM_PYTHON=1 \
    UV_PYTHON=/opt/conda/bin/python

# --- Python packages (pinned via requirements.txt) ---
# Use `uv pip install` (additive), NOT `uv pip sync` — sync would prune conda-shipped
# jupyterlab/notebook/ipykernel/nbconvert/nbformat and break the kernel (PITFALLS #3).
# In-build import smoke fails the build immediately on any broken wheel (CONT-07).
USER root
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip install --system -r /tmp/requirements.txt \
 && python -c "import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller" \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

USER ${NB_UID}

# --- DoML working directory ---
ENV PROJECT_ROOT=/home/jovyan/work
WORKDIR ${PROJECT_ROOT}
