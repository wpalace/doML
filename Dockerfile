# DoML analysis environment — Python 3.13 + R 4.x + DuckDB + ML stack
# Base: Jupyter DataScience Notebook (quay.io — Docker Hub frozen since 2023-10-20)
FROM quay.io/jupyter/datascience-notebook:2026-03-30

LABEL maintainer="DoML framework"
LABEL description="Reproducible ML analysis environment with Python, R, and DuckDB"

# --- R packages (single RUN layer to minimize Docker layers) ---
# Runs as root to install into system R library, then reverts to jovyan.
USER root
RUN Rscript -e 'install.packages(c( \
      "duckdb", \
      "arrow", \
      "tidymodels", \
      "renv", \
      "prophet", \
      "forecast", \
      "umap" \
    ), repos="https://cloud.r-project.org", dependencies=c("Depends","Imports","LinkingTo"), Ncpus=parallel::detectCores())' && \
    fix-permissions "${R_LIBS_USER}" && \
    fix-permissions "/opt/conda/lib/R/library"

# --- Python packages (pinned via requirements.txt) ---
USER ${NB_UID}
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# --- DoML working directory ---
ENV PROJECT_ROOT=/home/jovyan/work
WORKDIR ${PROJECT_ROOT}
