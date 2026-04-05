# Phase 1 Research: Infrastructure & Docker

**Researched:** 2026-04-04
**Domain:** Docker infrastructure for reproducible ML analysis (JupyterLab + Python + R + DuckDB)
**Confidence:** HIGH

## Summary

Phase 1 generates a **template** Dockerfile + docker-compose.yml pair that DoML writes into user projects. The template is built on the official `jupyter/datascience-notebook` image (now hosted on Quay.io, not Docker Hub) and layers on DuckDB, the DoML Python analysis stack, and a fixed set of R packages. The image ships Python 3.13 and R 4.x on Ubuntu 24.04 [CITED: jupyter-docker-stacks docs], with `mamba` as the recommended package manager [CITED: jupyter-docker-stacks recipes]. The docker-compose.yml mounts four volumes (`/data`, `/notebooks`, `/reports`, `/models`) matching INFR-04.

**Primary recommendation:** Pin to a dated tag (e.g. `quay.io/jupyter/datascience-notebook:2026-03-30` — verify at template-generation time against the latest weekly build) rather than `:latest`; install Python packages via `pip --no-cache-dir` using a pinned `requirements.txt`; install R packages via a single `Rscript -e 'install.packages(...)'` layer; configure `nbstripout 0.9.1` via `.pre-commit-config.yaml` with `pre-commit 4.x`.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFR-01 | Framework installs via skills/workflows/agents directory structure | Not Phase 1 scope — generation mechanism deferred. Phase 1 produces the Docker template files that INFR-01 tooling will later emit. |
| INFR-02 | `docker-compose.yml` + `requirements.txt` generated, `jupyter/datascience-notebook` base | Image details + compose structure sections below |
| INFR-03 | DuckDB installed for Python AND R | DuckDB installation section |
| INFR-04 | Directory scaffold: `/data/{raw,processed,external}/`, `/notebooks/`, `/reports/`, `/models/` | docker-compose volumes section |
| INFR-05 | Raw data immutable — no in-place modification | Enforcement via README convention + processed/ workflow; Docker can mount `/data/raw` read-only |
| INFR-06 | `CLAUDE.md` generated at project creation | Template section |
| REPR-01 | Random seeds in all notebooks | Notebook template convention — documented in CLAUDE.md |
| REPR-02 | File paths from env var, no hardcoded absolute paths | `PROJECT_ROOT=/home/jovyan/work` env var in compose |
| REPR-03 | `nbstripout` via pre-commit hook | nbstripout section |
| REPR-04 | `requirements.txt` pins Python versions; `renv.lock` pins R if used | pip-tools output + `renv::snapshot()` |

## Key Findings

### jupyter/datascience-notebook

**Registry:** `quay.io/jupyter/datascience-notebook` — Docker Hub images have been frozen since 2023-10-20 and are no longer updated [CITED: github.com/jupyter/docker-stacks README].

**Recommended tag strategy:** Use a dated tag for reproducibility (e.g. `2026-03-30`), NOT `:latest`. Weekly builds run every Monday; dated tags are immutable [CITED: jupyter-docker-stacks docs].

**Contents (as of early 2026 builds):**
- Base OS: Ubuntu 24.04 [CITED: docker-stacks docs]
- Python: 3.13 (on `latest` tag) [CITED: docker-stacks docs]
- R: 4.x with IRKernel and tidyverse [CITED: docker-stacks selecting.md]
- Julia: included (unused by DoML, can't easily be stripped)
- Package managers: `mamba` (preferred), `conda`, `pip` all available
- JupyterLab 4.x
- Pre-installed Python: pandas, NumPy, SciPy, scikit-learn, matplotlib, seaborn, etc. (inherits scipy-notebook)
- Pre-installed R: tidyverse packages (inherits r-notebook)
- `rpy2` for Python-R bridge
- Default user: `jovyan`, home: `/home/jovyan`
- `fix-permissions` script available for ownership repair after installs

Confidence: HIGH — confirmed via official GitHub and docs.

### DuckDB Installation

**Python (DuckDB 1.5.1, released 2026-03-23):** [CITED: pypi.org/project/duckdb]
```dockerfile
RUN pip install --no-cache-dir 'duckdb==1.5.1'
```
- Requires Python >=3.10 — compatible with image's Python 3.13
- Zero external dependencies (no native deps to worry about)
- Pre-built wheels for linux-x86_64 and linux-aarch64

**R (duckdb R package):** [VERIFIED: CRAN + docker-stacks pattern]
```dockerfile
RUN Rscript -e 'install.packages("duckdb", repos="https://cloud.r-project.org")'
```
- The R `duckdb` package is available on CRAN
- Install via standard `install.packages()` — no special source builds required
- Pairs naturally with `arrow` R package for Parquet I/O

**Combined R package install (single layer, efficient):**
```dockerfile
RUN Rscript -e 'install.packages(c("duckdb","arrow","tidymodels","renv","prophet","forecast","umap"), repos="https://cloud.r-project.org", Ncpus=parallel::detectCores())'
```

### Python Package Installation Pattern

**pip vs mamba decision for DoML:** Use `pip` for all additional packages. [CITED: docker-stacks recipes.md]

Rationale:
- Most ML packages (SHAP, Optuna, ydata-profiling, Prophet) are distributed primarily via PyPI
- `pip --no-cache-dir` is the documented standard pattern in the jupyter docker-stacks recipes
- Mixing conda and pip in the same environment can cause dependency solver conflicts — pip-only is simpler for a user-facing template
- Image's underlying environment is conda-managed, but pip installs into it cleanly when using `--no-cache-dir`

**Dockerfile pattern:** [CITED: docker-stacks recipes]
```dockerfile
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

**requirements.txt pinning strategy:** Pin exact versions (`==`) for reproducibility. Sample:
```
duckdb==1.5.1
papermill==2.6.0
nbconvert==7.16.4
nbstripout==0.9.1
pre-commit==4.5.1
shap==0.44.1
optuna==3.6.1
umap-learn==0.5.6
ydata-profiling==4.12.0
plotly==5.24.1
xgboost==2.1.3
lightgbm==4.5.0
statsmodels==0.14.4
prophet==1.1.6
jinja2==3.1.4
nbformat==5.10.4
```
Note: these version pins are [ASSUMED] based on the STACK.md minimums. The planner must verify each via `pip index versions <pkg>` at template-generation time since the template is generated into user projects and should use current-at-generation versions.

### R Package Installation Pattern

**Approach:** Single `Rscript -e 'install.packages(...)'` layer with CRAN cloud mirror. [CITED: docker-stacks + community patterns]

```dockerfile
USER root
RUN Rscript -e 'install.packages(c( \
      "duckdb", \
      "arrow", \
      "tidymodels", \
      "renv", \
      "prophet", \
      "forecast", \
      "umap", \
      "DataExplorer" \
    ), repos="https://cloud.r-project.org", dependencies=TRUE, Ncpus=parallel::detectCores())' && \
    fix-permissions "${R_LIBS_USER}" && \
    fix-permissions "/opt/conda/lib/R/library"
USER ${NB_UID}
```

**Notes:**
- `tidyverse` is already pre-installed in the base image — don't reinstall
- `Ncpus=parallel::detectCores()` speeds up compilation significantly (R packages with C++ sources like `prophet`, `arrow` benefit most)
- Must `USER root` for install into system R library, then revert to `${NB_UID}` (jovyan)
- `dependencies=TRUE` pulls in Suggests as well — may bloat image; consider `dependencies=c("Depends","Imports","LinkingTo")` for leaner image
- `renv` package is optional at image level — it's for user's own project lockfile workflow (REPR-04)

**Alternative (if image size matters):** Split into two layers — CRAN-only packages first, then Bioconductor/GitHub if any.

### nbstripout + pre-commit Setup

**Versions:** [CITED: pypi.org/project/nbstripout]
- `nbstripout==0.9.1` (released 2026-02-21)
- `pre-commit==4.5.1` (current)

**`.pre-commit-config.yaml`:** [CITED: nbstripout docs]
```yaml
repos:
  - repo: https://github.com/kynan/nbstripout
    rev: 0.9.1
    hooks:
      - id: nbstripout
```

**With extra-keys (strips more metadata, recommended for cleaner diffs):**
```yaml
repos:
  - repo: https://github.com/kynan/nbstripout
    rev: 0.9.1
    hooks:
      - id: nbstripout
        args: ['--extra-keys=metadata.celltoolbar metadata.kernelspec cell.metadata.heading_collapsed cell.metadata.collapsed']
```

**Activation (one-time, documented in CLAUDE.md):**
```bash
pip install pre-commit
pre-commit install
```

**Caveat:** pre-commit hook modifies the working copy on commit, not just the staged snapshot. Document this in CLAUDE.md so users aren't surprised when their local `.ipynb` outputs disappear after commit.

### docker-compose.yml Structure

**Recommended structure:**
```yaml
services:
  jupyter:
    image: quay.io/jupyter/datascience-notebook:2026-03-30
    # OR: build: .  (if using custom Dockerfile)
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ${PROJECT_NAME:-doml}-jupyter
    ports:
      - "8888:8888"
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-}
      - PROJECT_ROOT=/home/jovyan/work
      - CHOWN_HOME=yes
      - CHOWN_HOME_OPTS=-R
    volumes:
      - ./data/raw:/home/jovyan/work/data/raw:ro         # INFR-05: read-only
      - ./data/processed:/home/jovyan/work/data/processed
      - ./data/external:/home/jovyan/work/data/external:ro
      - ./notebooks:/home/jovyan/work/notebooks
      - ./reports:/home/jovyan/work/reports
      - ./models:/home/jovyan/work/models
    working_dir: /home/jovyan/work
    user: root                    # needed for CHOWN_HOME; image drops to jovyan after init
    command: start-notebook.py --NotebookApp.token='${JUPYTER_TOKEN:-}'
```

**Key decisions:**
- **Port 8888:** standard, matches INFR-02 goal of `localhost:8888`
- **`/data/raw` and `/data/external` mounted read-only** (INFR-05 immutability enforcement at the OS level — stronger than convention alone)
- **`work/` prefix:** jupyter image expects user files under `/home/jovyan/work` by convention; mapping matches that
- **`JUPYTER_TOKEN` env var:** empty by default for local dev; can be overridden for shared environments
- **`CHOWN_HOME=yes`:** ensures volume-mounted dirs get owned by jovyan — otherwise bind mounts from host have host UID and jovyan can't write

### Version Compatibility Notes

| Combination | Status | Notes |
|-------------|--------|-------|
| DuckDB 1.x + pandas 2.x | Compatible | Mature integration as of 2026 [CITED: motherduck docs] |
| DuckDB 1.x + pyarrow 14+ | Compatible | DuckDB 1.3+ works cleanly with pyarrow 18/19 [CITED: duckdb GH issues]; pyarrow 14 occasional legacy issues |
| Python 3.13 (image default) + DuckDB 1.5.1 | Compatible | DuckDB 1.5.1 ships 3.14 wheels so 3.13 is covered |
| Prophet 1.1 + pandas 2.x | Compatible [CITED: STACK.md] | Use `pip install prophet`, NOT `fbprophet` |
| scikit-learn 1.4+ + Python 3.13 | Compatible | sklearn 1.5+ officially supports 3.13 |
| XGBoost 2.x + sklearn 1.x | Compatible [CITED: STACK.md] | `tree_method='hist'` is new default |

**Known gotcha:** Pandas 2.1.2 had a pyarrow 14.0 incompatibility [CITED: pandas-dev/pandas#55799]. Use pandas ≥ 2.2 to avoid. Pre-installed pandas in 2026 image will be 2.2+.

## Recommended Approach

### Plan 01-01: Docker environment

**Files to generate (template-level, will be emitted by DoML into user projects later):**

1. **Dockerfile** — customizes `quay.io/jupyter/datascience-notebook:<dated-tag>`:
   - `USER root` → install R packages via `Rscript -e` with `fix-permissions`
   - `USER ${NB_UID}` → `pip install -r requirements.txt --no-cache-dir`
   - No system apt packages needed (base image has build-essential already)

2. **requirements.txt** — pinned Python packages (planner verifies versions at generation time via `pip index versions`)

3. **docker-compose.yml** — structure as shown above, with 6 volume mounts (raw RO, external RO, processed RW, notebooks RW, reports RW, models RW)

4. **.dockerignore** — exclude `data/*`, `notebooks/*.ipynb`, `.git`, `__pycache__`, `*.pyc`, `renv/library`

**Tasks:**
- Task A: Write Dockerfile with pinned base image + R install layer + pip install layer
- Task B: Write requirements.txt with pinned versions (verify each against PyPI at generation)
- Task C: Write docker-compose.yml with volume mounts and RO data enforcement
- Task D: Write .dockerignore
- Task E: Smoke test — `docker-compose build && docker-compose up`, open http://localhost:8888, verify `import duckdb` in Python kernel and `library(duckdb)` in R kernel both succeed

### Plan 01-02: Project directory scaffold and data immutability

**Directory tree to scaffold:**
```
project-root/
├── data/
│   ├── raw/              # immutable, RO mount
│   │   └── .gitkeep
│   ├── processed/        # RW, outputs from EDA
│   │   └── .gitkeep
│   └── external/         # immutable reference data, RO mount
│       └── .gitkeep
├── notebooks/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── .gitignore            # ignores data contents but keeps .gitkeep
├── CLAUDE.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .pre-commit-config.yaml
```

**Immutability enforcement (INFR-05) — three layers of defense:**
1. **Docker mount level:** `./data/raw:/home/jovyan/work/data/raw:ro` (OS enforces)
2. **Convention level:** README + CLAUDE.md state raw is append-only
3. **.gitignore level:** `data/raw/*` in .gitignore with `!data/raw/.gitkeep` exception so raw files aren't committed

**Tasks:**
- Task A: Write directory scaffold script (creates tree with `.gitkeep` files)
- Task B: Write .gitignore template
- Task C: Verify RO mount works — container attempts to write to `/data/raw` should fail

### Plan 01-03: Reproducibility setup (nbstripout, pre-commit, CLAUDE.md template)

**Files:**

1. **.pre-commit-config.yaml** — nbstripout 0.9.1 hook with extra-keys

2. **CLAUDE.md template** — DoML-specific instructions covering:
   - Project structure contract (directory roles)
   - Data immutability rules (INFR-05)
   - Notebook conventions: seeds at top (REPR-01), path resolution via `PROJECT_ROOT` env var (REPR-02)
   - Pre-commit hook warning (modifies working copy)
   - `requirements.txt` / `renv.lock` pinning expectation (REPR-04)
   - How to rebuild image after dependency changes
   - Running commands: `docker-compose up`, `docker-compose exec jupyter bash`

3. **Notebook preamble template** (`notebooks/_template.ipynb`) — first cell sets seeds:
   ```python
   import os, random, numpy as np
   PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/jovyan/work')
   SEED = 42
   random.seed(SEED); np.random.seed(SEED)
   ```

**Tasks:**
- Task A: Write .pre-commit-config.yaml with nbstripout 0.9.1
- Task B: Write CLAUDE.md template with DoML instructions
- Task C: Write notebook preamble template (Python and R variants)
- Task D: Verify pre-commit hook: create dummy notebook with output, commit, confirm output stripped

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Current recommended image tag is `2026-03-30` or similar dated weekly tag | Image section | Planner must verify actual tag at generation time; easy to fix |
| A2 | Specific pinned versions in requirements.txt | Python install section | Versions may be stale; planner must re-verify via PyPI at generation |
| A3 | Prophet installs cleanly as pip package in jupyter image | Version compat | Prophet sometimes has C++ build issues; may need `mamba install -c conda-forge prophet` fallback |
| A4 | ydata-profiling pip-installs cleanly with pandas 2.2+ | Version compat | ydata-profiling has tight pandas version bounds; verify at generation |
| A5 | `fix-permissions` is available in 2026 image builds | Dockerfile pattern | Script has been stable for years; very low risk |
| A6 | Image's default `/home/jovyan/work` is the right working dir | docker-compose | Standard convention; verify in image docs |

## Open Questions

1. **Should DoML pin to `:latest` or a dated tag in the template?**
   - Dated tag: full reproducibility, but goes stale
   - `:latest`: always current, but rebuilds are non-deterministic
   - Recommendation: dated tag, updated at each DoML framework release
   - Decision needed at planning time.

2. **Does the template need a separate R-only path or is the combined Python+R image always used?**
   - INFR-03 says DuckDB "always present regardless of whether EDA uses it directly"
   - INTV-05 says Python default, R opt-in
   - Recommendation: single image with both — simpler to maintain, `jupyter/datascience-notebook` is already combined
   - No decision needed — combined image resolves this.

3. **Should Prophet be pip or conda-forge?**
   - pip often hits C++ compile issues for prophet
   - conda-forge prophet is pre-built
   - Recommendation: try pip first in template; if build fails during smoke test, switch to `mamba install -c conda-forge prophet`
   - Planner should include a fallback note.

4. **Image size concern:** `jupyter/datascience-notebook` is ~5GB baseline; adding ML stack pushes to ~7-8GB. Is this acceptable?
   - For a user-facing template: document in CLAUDE.md, acceptable tradeoff for reproducibility
   - No smaller path without abandoning base image (out of scope per STACK.md)

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | Building/running image | Must be checked on user machine | — | None — hard requirement |
| docker-compose / `docker compose` | Orchestration | Must be checked | — | None |
| git | pre-commit hooks | Must be checked | — | Manual notebook output stripping |

**Blocking:** None at DoML-framework level — these are requirements DoML imposes on end users, documented in CLAUDE.md at project kickoff.

## Validation Architecture

No automated test framework exists yet in DoML (greenfield). Phase 1 validation is **smoke test + manual verification**, not pytest.

### Phase Requirements → Validation Map

| Req ID | Behavior | Validation Type | Command |
|--------|----------|-----------------|---------|
| INFR-02 | docker-compose up produces Jupyter at :8888 | smoke | `docker-compose up -d && curl -sf http://localhost:8888/lab` |
| INFR-03 | DuckDB available in Python | smoke | `docker-compose exec jupyter python -c "import duckdb; print(duckdb.__version__)"` |
| INFR-03 | DuckDB available in R | smoke | `docker-compose exec jupyter Rscript -e 'library(duckdb); packageVersion("duckdb")'` |
| INFR-04 | Directory scaffold exists | file check | `test -d data/raw && test -d data/processed && test -d data/external && test -d notebooks && test -d reports && test -d models` |
| INFR-05 | Raw data is read-only in container | smoke | `docker-compose exec jupyter touch /home/jovyan/work/data/raw/x.txt 2>&1 \| grep -q "Read-only"` |
| INFR-06 | CLAUDE.md exists with DoML content | file check | `test -f CLAUDE.md && grep -q "DoML" CLAUDE.md` |
| REPR-03 | nbstripout pre-commit hook runs | integration | Create notebook with output, commit, verify output stripped |
| REPR-04 | requirements.txt pins versions | file check | `grep -E '^[a-zA-Z].*==' requirements.txt \| wc -l` (count == line count) |

### Wave 0 Gaps

- [ ] No test framework exists yet — Phase 1 validation is bash smoke tests only
- [ ] Create `scripts/smoke-test.sh` that runs all validation commands above with exit codes — recommended

### Sampling Rate

- **Per task:** Run relevant smoke test for that task
- **Per phase gate:** Run full `smoke-test.sh` — all checks green required before Phase 2

## Project Constraints (from CLAUDE.md)

No project-level `CLAUDE.md` exists at repo root yet (verified 2026-04-04). No project-level constraints override this research.

Note: the CLAUDE.md being **generated** in Plan 01-03 is for end-user projects, not for the DoML repo itself.

## Sources

### Primary (HIGH confidence)
- [jupyter/docker-stacks GitHub](https://github.com/jupyter/docker-stacks) — image hosting change to quay.io, tag scheme
- [jupyter-docker-stacks recipes.md](https://github.com/jupyter/docker-stacks/blob/main/docs/using/recipes.md) — Dockerfile patterns, fix-permissions, pip/mamba
- [pypi.org/project/duckdb](https://pypi.org/project/duckdb/) — DuckDB 1.5.1 (2026-03-23), Python ≥3.10
- [pypi.org/project/nbstripout](https://pypi.org/project/nbstripout/) — nbstripout 0.9.1 (2026-02-21) + pre-commit config
- [pre-commit.com](https://pre-commit.com/) — pre-commit 4.5.1, config format
- [DoML STACK.md](/home/bill/source/DoML/.planning/research/STACK.md) — locked stack decisions
- [DoML REQUIREMENTS.md](/home/bill/source/DoML/.planning/REQUIREMENTS.md) — INFR/REPR requirements

### Secondary (MEDIUM confidence)
- [docker-stacks Selecting an Image](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html) — image contents
- [DuckDB compatibility issues](https://github.com/duckdb/duckdb/issues/17656) — pyarrow version notes
- [pandas/pyarrow compat issue](https://github.com/pandas-dev/pandas/issues/55799) — pandas 2.1.2 + pyarrow 14.0 conflict

### Tertiary (LOW confidence — requires verification at plan time)
- Exact pinned versions in requirements.txt — **planner must verify each at generation time**
- Exact latest dated tag for jupyter/datascience-notebook — **planner must verify at generation time** via https://quay.io/repository/jupyter/datascience-notebook?tab=tags

## Metadata

**Confidence breakdown:**
- Docker base image + recipes: HIGH — official docs + GitHub confirmed
- DuckDB installation: HIGH — verified versions + official install commands
- nbstripout/pre-commit config: HIGH — fetched from official sources
- docker-compose structure: HIGH — standard pattern, maps cleanly to INFR-04
- R package install pattern: MEDIUM — standard but `dependencies=TRUE` scope could bloat image
- Specific pinned versions in requirements.txt: LOW — [ASSUMED], planner must re-verify

**Research date:** 2026-04-04
**Valid until:** 2026-05-04 (30 days — Python/R ecosystem moves, jupyter image rebuilds weekly)
