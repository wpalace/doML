# Architecture Research

**Domain:** Single-stage Dockerfile + uv overlay + BuildKit cache mounts
**Researched:** 2026-04-30
**Milestone:** v1.6 Container Optimization & Python Modernization

## Recommended Dockerfile Structure (v1.6)

Single-stage. Multi-stage adds complexity without size win because runtime needs the wheels anyway. Use the official `astral-sh/uv` image to vendor the `uv` binary via `COPY --from`. Install into the **system** Python that scipy-notebook ships (no `uv venv` — Jupyter kernel discovery, papermill, and `start-notebook.py` already point at `/opt/conda/bin/python`; a venv adds a kernel-registration headache).

```dockerfile
# syntax=docker/dockerfile:1.7
FROM quay.io/jupyter/scipy-notebook:2026-04-21

# Vendor the uv binary from the official Astral image (pinned)
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/

# uv environment knobs (Astral's "Using uv in Docker" guide)
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_SYSTEM_PYTHON=1 \
    UV_PYTHON=/opt/conda/bin/python

USER root
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv pip install --system -r /tmp/requirements.txt \
 && python -c "import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller" \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

USER ${NB_UID}
ENV PROJECT_ROOT=/home/jovyan/work
WORKDIR ${PROJECT_ROOT}
```

Key points:
- **`scipy-notebook` (not `datascience-notebook`)** — drops base from ~3.5–4.5 GB to ~1.3–1.5 GB compressed.
- **`uv pip install` (not `uv pip sync`)** — sync removes packages not in lockfile, which would prune conda-shipped jupyterlab/notebook/ipykernel and break the kernel. Install is additive.
- **`--system`** — writes into `/opt/conda/lib/python3.13/site-packages`, same place pip wrote in v1.5, so kernels and `start-notebook.py` find packages without changes.
- **BuildKit cache mount** on `/root/.cache/uv` keeps wheels across rebuilds; warm rebuilds become near-instant.
- **`UV_LINK_MODE=copy`** required because cache mount and target site-packages are on different layers/filesystems — hardlinks fail with cross-device errors. Astral explicitly recommends `copy` in Docker.
- **`UV_COMPILE_BYTECODE=1`** precompiles `.pyc` at install time so first notebook launch isn't slowed by import-time compilation.
- **In-Dockerfile import smoke layer** (`python -c "import …"`) fails the build immediately if a wheel is broken instead of at first notebook run. Adds ~3s, becomes the canary.

## docker-compose.yml Changes

Minimal. Compose v2.20+ uses BuildKit by default; only need to add a build-arg surface and (optionally) explicit cache config:

```yaml
services:
  jupyter:
    build:
      context: .
      dockerfile: Dockerfile
      # Optional: persist BuildKit layer cache for CI / shared dev machines
      cache_from:
        - type=local,src=/tmp/.buildx-cache
      cache_to:
        - type=local,dest=/tmp/.buildx-cache,mode=max
    # Mounts (./data/raw:ro etc.) stay identical
```

For local dev, the inline cache mount in the Dockerfile alone is enough. Keep `DOCKER_BUILDKIT=1` in the install scripts as belt-and-suspenders for users on older Docker Desktop.

## Cache Strategy

| Concern | Choice | Rationale |
|---------|--------|-----------|
| BuildKit cache mounts | Yes | `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked` |
| Dockerfile syntax pragma | `# syntax=docker/dockerfile:1.7` | Required for cache mount syntax |
| uv link mode | `copy` | Hardlink fails cross-filesystem |
| Layer ordering | `FROM` → `COPY --from uv` → `ENV` → `COPY requirements.txt` → `RUN uv pip install` → `WORKDIR` | Deepest cacheable layer; only invalidated by requirements.txt change |
| App code in image | No | DoML mounts everything via compose volumes — no `COPY . .` |

## Lockfile Workflow

| Concern | Choice |
|---------|--------|
| Source of truth | `requirements.in` (unchanged from v1.5) |
| Lock command | `uv pip compile requirements.in -o requirements.txt --generate-hashes` |
| Lock format | Standard `requirements.txt` (pip-compile-style header). Stay with this for v1.6 — universally readable, doesn't lock framework to uv forever. PEP 751 `pylock.toml` still draft as of Apr 2026. |
| Rebuild flow | Edit `requirements.in` → `docker compose run --rm jupyter uv pip compile requirements.in -o requirements.txt --generate-hashes` → `docker compose build` → commit both files together |

## CI Smoke Test Workflow Structure

```yaml
name: docker-smoke
on: [push, pull_request]
jobs:
  build-and-smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Restore BuildKit cache
        uses: actions/cache@v4
        with:
          path: /tmp/.buildx-cache
          key: buildx-${{ hashFiles('Dockerfile','requirements.txt') }}
          restore-keys: buildx-
      - name: Cold-cache build (timed)
        run: |
          START=$(date +%s)
          docker buildx build --no-cache \
            --cache-to=type=local,dest=/tmp/.buildx-cache-new,mode=max \
            --load -t doml:ci .
          echo "COLD_BUILD_SEC=$(( $(date +%s) - START ))" >> $GITHUB_ENV
      - name: Assert <300s budget
        run: test "${COLD_BUILD_SEC}" -lt 300
      - name: Papermill smoke test
        run: |
          docker run --rm --shm-size=2g \
            -v ${{ github.workspace }}:/home/jovyan/work doml:ci \
            bash tests/smoke/run_all_notebooks.sh
      - name: Promote cache
        run: rm -rf /tmp/.buildx-cache && mv /tmp/.buildx-cache-new /tmp/.buildx-cache
```

## Build Time Budget Breakdown (estimated)

Targeting an 8-core / 32GB / NVMe dev box on a 100Mbps+ connection.

| Stage | Estimated time | Notes |
|-------|----------------|-------|
| Pull `scipy-notebook:2026-04-21` | 45–75s | ~1.3–1.5 GB compressed (vs ~3.5–4.5 GB datascience) |
| `COPY --from=astral-sh/uv` | 1–2s | uv binary ~30 MB single static blob |
| `uv pip install` cold cache (no wheel cache) | 90–150s | ~22 wheels; uv parallel resolver 8–10× faster than pip-tools. Prophet + pmdarima slowest at ~15–20s each. |
| Bytecode compile (`UV_COMPILE_BYTECODE`) | 10–15s | Folded into install step |
| Import smoke + `fix-permissions` | 8–12s | Recursive chown over `${CONDA_DIR}` |
| **Total cold cache** | **~155–250s** | Comfortably under 300s budget |
| Total warm cache (no requirements.txt change) | 5–15s | Layer cache hits |
| Warm with requirements.txt edit, wheel cache hit | 20–40s | Only changed wheels resolve |

Where time goes: ~40% base pull, ~50% wheel install, ~10% permissions/smoke. Biggest single accelerator is `scipy-notebook` over `datascience-notebook` (~120s saved on pull alone).

## Migration Steps from Current Dockerfile

1. **Delete** the entire `mamba install … r-duckdb r-tidymodels r-renv r-umap` block (D-04: R hard removal).
2. **Change base** from `quay.io/jupyter/datascience-notebook:2026-04-02` → `quay.io/jupyter/scipy-notebook:2026-04-21` (or latest stable dated tag).
3. **Add** `# syntax=docker/dockerfile:1.7` as line 1.
4. **Add** `COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/` after `FROM`.
5. **Add** the `ENV UV_*` block.
6. **Replace** `RUN pip install --no-cache-dir --requirement /tmp/requirements.txt` with `RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked uv pip install --system -r /tmp/requirements.txt && python -c "import …"`.
7. **Keep** the two `fix-permissions` calls — scipy-notebook still uses `${NB_UID}=1000` and ships `fix-permissions` at `/usr/local/bin/fix-permissions`.
8. **Keep** `USER ${NB_UID}` switch and `WORKDIR ${PROJECT_ROOT}` at the bottom.
9. **Remove** `pip-tools` from `requirements.in` (D-02 — replaced by uv).
10. **Remove** the kaggle Dockerfile layer (lines 30-34 in current; redundant after uv-driven single resolve).
11. **Update** `CLAUDE.md` rebuild instruction: `pip-compile` → `uv pip compile … --generate-hashes`.
12. **Update** install scripts (`install.sh`, `install.ps1`) to set `DOCKER_BUILDKIT=1` defensively.
13. **Mirror** all changes into `.claude/doml/templates/Dockerfile`, `.claude/doml/templates/docker-compose.yml`, and `.claude/doml/templates/requirements.in`.

## Build Order Considerations

**Dependencies (must precede):**
- `COPY --from=astral-sh/uv` must come before any `RUN uv …`.
- `ENV UV_LINK_MODE=copy` must be set before `RUN uv pip install` (else hardlink errors on cache mount).
- `requirements.txt` must be `COPY`ed before `uv pip install`.
- `fix-permissions` must run after the last root-owned write to `${CONDA_DIR}`.

**Fail-fast points:**
- `uv pip install` exits non-zero on hash mismatch or unresolvable spec — surfaces dependency drift loudly. `--generate-hashes` in the lock makes this strict.
- In-Dockerfile import smoke (`python -c "import …"`) fails build immediately on broken wheels.
- In CI, `test "${COLD_BUILD_SEC}" -lt 300` gates milestone success.

## New Files / Components Introduced

| Component | Path | Purpose |
|-----------|------|---------|
| Smoke runner | `tests/smoke/run_all_notebooks.sh` | papermill orchestrator over all 10 templates |
| Fixture data | `tests/fixtures/regression.csv`, `tests/fixtures/timeseries.csv` | Tiny inputs for smoke runs |
| CI workflow | `.github/workflows/smoke-test.yml` | Cold-build budget + smoke gate on every push |
| Updated docs | `CLAUDE.md`, `AGENTS.md`, `README.md` | Reflect Python-only + uv flow |
| Removed | `r-*` from Dockerfile, `data_understanding_r.ipynb`, R blocks in workflows | D-04 |

---
*Architecture research for: v1.6 Container Optimization & Python Modernization*
*Researched: 2026-04-30*
