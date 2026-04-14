# DoML analysis environment — Python 3.13 + R 4.x + DuckDB + ML stack
# Base: Jupyter DataScience Notebook (quay.io — Docker Hub frozen since 2023-10-20)
FROM quay.io/jupyter/datascience-notebook:2026-04-02

LABEL maintainer="DoML framework"
LABEL description="Reproducible ML analysis environment with Python, R, and DuckDB"

# --- R packages via mamba (conda-forge binaries — compatible with conda R) ---
# arrow/prophet/forecast deferred: arrow incompatible; prophet/forecast need rstan (Milestone 2).
USER root
RUN mamba install --yes \
      r-duckdb \
      r-tidymodels \
      r-renv \
      r-umap \
    && mamba clean --all -f -y \
    && fix-permissions "${CONDA_DIR}" \
    && fix-permissions "/home/${NB_USER}"

# --- Python packages (pinned via requirements.txt) ---
USER ${NB_UID}
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# --- Data acquisition (kaggle CLI) ---
# Installed as a separate layer so it is always present even before requirements.txt is regenerated.
# Once pip-compile adds kaggle to requirements.txt this layer becomes a no-op upgrade.
USER root
RUN pip install --no-cache-dir kaggle && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
USER ${NB_UID}

# --- DoML working directory ---
ENV PROJECT_ROOT=/home/jovyan/work
WORKDIR ${PROJECT_ROOT}
