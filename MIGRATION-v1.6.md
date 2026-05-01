# Migrating to DoML v1.6

DoML v1.6 is **Python-only**. R support has been removed from the Dockerfile, the `/doml-new-project` interview, and the analysis workflows. If you depend on R inside the DoML container, **pin to v1.5** until DoML re-introduces an R path (no current ETA).

## TL;DR — install v1.5 instead of latest

**Bash / Linux / macOS:**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh) --version v1.5.0
```

Or with the env-var form:

```bash
VERSION=v1.5.0 bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)
```

**PowerShell / Windows:**

```powershell
$env:DOML_VERSION = "v1.5.0"; iwr https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
```

Both forms pull the v1.5.0 git tag — the last release that ships an R-enabled Dockerfile (`mamba install r-duckdb r-tidymodels r-renv r-umap` block + `data_understanding_r.ipynb` template + R branches in the data-understanding workflow).

## What changed in v1.6

| Surface | v1.5 | v1.6 |
|---|---|---|
| Base image | `quay.io/jupyter/datascience-notebook` (Python + R + Julia) | `quay.io/jupyter/scipy-notebook` (Python only) |
| R packages | `r-duckdb`, `r-tidymodels`, `r-renv`, `r-umap` via mamba | none (block deleted) |
| R notebook template | `data_understanding_r.ipynb` | (Phase 24 — removed) |
| Language preference prompt | "Python (default) / R (opt-in)" in `/doml-new-project` | (Phase 24 — Python only) |
| Install layer | `pip install -r requirements.txt` | `uv pip install --system -r requirements.txt` (BuildKit cache mount) |
| Cold build time | ~5–9 min | <5 min (CONT-04) |
| Python | 3.13 | 3.14 |

Phase 23 of the v1.6 milestone made the Dockerfile change. Phase 24 sweeps the remaining R narrative from workflows, CLAUDE.md, AGENTS.md, README.md, and the `/doml-new-project` interview.

## Why v1.5 is the migration target

- The `--version v1.5.0` flag (Bash) / `$env:DOML_VERSION = "v1.5.0"` (PowerShell) pulls a tagged git release — content-addressable, won't drift if `main` moves.
- v1.5 was the last public DoML release with the full R toolchain installed in the container (Phase 21 was the v1.5 cap; v1.5.0 tag = R-enabled).
- You can run v1.5 indefinitely — no automatic upgrade. v1.5 receives no further updates from the DoML team, but the framework is self-contained inside your project directory after install.

The base-image swap is the load-bearing reason R is gone: v1.5's `quay.io/jupyter/datascience-notebook` ships a conda R toolchain out of the box, while v1.6's `quay.io/jupyter/scipy-notebook` does not. Adding R back to v1.6 would require either swapping back to `datascience-notebook` (regression on image size) or adding a `mamba install r-*` block on top of `scipy-notebook` (the v1.5 install pattern, with extra layer cost).

## When R returns

There is no committed roadmap for an R re-introduction. The `language: r` config branch was hard-removed (D-04 of v1.6) rather than soft-deprecated because (a) the conda R toolchain was the largest single contributor to image bloat (~2–2.5 GB), and (b) keeping R paths alongside Python paths doubled the maintenance surface for every analysis workflow.

If you need R for a specific analysis: pin to v1.5 for that project. Mixing v1.5 and v1.6 projects on the same machine works fine — each project ships its own Docker image and `.claude/` tree.

## Questions

Open an issue at https://github.com/wpalace/doML/issues if you hit a v1.5 install path that no longer works. v1.5 install scripts pull from `archive/refs/tags/v1.5.0.tar.gz` on GitHub; as long as the tag exists in the repo, the install path is stable.
