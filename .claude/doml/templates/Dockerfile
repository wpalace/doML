# syntax=docker/dockerfile:1
# DoML analysis environment: Python 3.14 + marimo + DuckDB + ML stack.
# One slim image; every Python package comes from the hash-pinned requirements.txt.
# No Jupyter server, kernel, nbconvert, papermill or conda: marimo notebooks are plain
# Python files that run with `marimo edit` (interactive) or `marimo export html` (headless).
FROM ghcr.io/astral-sh/uv:0.11.8@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 AS uv

FROM python:3.14-slim-trixie@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8 AS runtime

LABEL org.opencontainers.image.title="doml" \
      org.opencontainers.image.description="Reproducible ML analysis environment (marimo, DuckDB, scikit-learn)"

COPY --from=uv /uv /uvx /usr/local/bin/

# libgomp1: OpenMP runtime for LightGBM/XGBoost wheels.
# binutils: objdump, which PyInstaller needs for the CLI deploy target.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      binutils \
      libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# UV_LINK_MODE=copy: the cache mount and site-packages are on different filesystems.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_PROGRESS=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_SYSTEM_PYTHON=1

COPY requirements.txt /tmp/requirements.txt
# `uv pip sync` installs exactly the lock (nothing more), checking every hash.
# The import smoke test fails the build at once on a broken wheel.
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip sync --system --require-hashes /tmp/requirements.txt \
 && python -c "import marimo, duckdb, shap, prophet, pmdarima, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, PyInstaller, seaborn, plotly"

# Fixed non-root user. Compose can override the UID with `user:` so files written to
# bind mounts belong to the host user; HOME is world-writable for that case.
RUN useradd --uid 1000 --create-home doml \
 && chmod 0777 /home/doml

ENV HOME=/home/doml \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    PROJECT_ROOT=/project \
    PYTHONUNBUFFERED=1

USER 1000
# Bake the DuckDB excel extension (read_xlsx) into the image over HTTPS, so data
# profiling works offline and never waits on an extension download at run time.
RUN python - <<'PY'
import duckdb, gzip, pathlib, urllib.request
ver = duckdb.execute("PRAGMA version").fetchone()[0]
plat = duckdb.execute("PRAGMA platform").fetchone()[0]
dest = pathlib.Path.home() / ".duckdb" / "extensions" / ver / plat / "excel.duckdb_extension"
dest.parent.mkdir(parents=True, exist_ok=True)
url = f"https://extensions.duckdb.org/{ver}/{plat}/excel.duckdb_extension.gz"
req = urllib.request.Request(url, headers={"User-Agent": "duckdb"})
with urllib.request.urlopen(req, timeout=120) as r:
    dest.write_bytes(gzip.decompress(r.read()))
duckdb.execute("LOAD excel")
PY
WORKDIR /project
EXPOSE 2718

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:2718/health', timeout=4)" || exit 1

# Interactive editor for every notebook in notebooks/. Set MARIMO_TOKEN to require a password.
CMD ["sh", "-c", "exec marimo edit notebooks --host 0.0.0.0 --port 2718 --headless ${MARIMO_TOKEN:+--token-password \"$MARIMO_TOKEN\"} ${MARIMO_TOKEN:---no-token}"]
