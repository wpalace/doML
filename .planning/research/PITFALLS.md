# Pitfalls Research

**Domain:** Common failure modes when rebuilding the DoML Docker container with uv + scipy-notebook + Python 3.13/3.14 + R hard-removal
**Researched:** 2026-04-30
**Milestone:** v1.6 Container Optimization & Python Modernization

## Critical Pitfalls (likely to bite, must address proactively)

### 1. Prophet on Python 3.14 — wheel may not exist; falls back to source build with cmdstan

**What:** prophet 1.3.0 needs a cmdstan toolchain. Even if a cp314 wheel ships, cmdstan may be downloaded/compiled at install time on first use (~150 MB toolchain). PyPI cp314 wheels typically lag Python release by 2–4 months. A source build of prophet+cmdstan is 3–5 min by itself, blowing the 5-min budget.

**Detect:** `uv pip compile requirements.in --python-version 3.14 --dry-run` surfaces unresolvables. `docker run --rm python:3.14-slim pip download prophet --no-deps --only-binary=:all:` confirms wheel availability.

**Prevent:** Pin Python 3.13 for v1.6 (already locked due to ydata-profiling — see #2). Documented fallback path remains.

**Roadmap slot:** Pre-flight wheel-availability check, before Dockerfile rewrite phase.

### 2. ydata-profiling pins `python<3.14` — hard block on Python 3.14

**What:** `ydata-profiling`'s `pyproject.toml` constrains `python = "<3.14,>=3.7"`. Open issue #1811. This single dep forces 3.13.

**Detect:** Already detected in research.

**Prevent:** Lock D-03 to **Python 3.13** for v1.6. Schedule a follow-up phase or future milestone to revisit when ydata-profiling lifts the cap.

**Alternative:** Drop ydata-profiling and replace EDA profiling cell with hand-rolled DuckDB queries — only do this if user wants 3.14 badly enough.

### 3. `uv pip sync` removes conda-shipped packages → kernel breaks

**What:** scipy-notebook's `/opt/conda/bin/python` ships jupyterlab, notebook, ipykernel, nbconvert, nbformat as conda packages. `uv pip sync requirements.txt --system` is destructive — it removes anything not in the lockfile, pruning these and breaking the Jupyter kernel.

**Detect:** After build, `jupyter --version`, `python -c "import notebook; print(notebook.__file__)"`, smoke-papermill a 3-cell notebook.

**Prevent:** Use `uv pip install --system -r requirements.txt` (additive), not `uv pip sync`. Document the distinction in CLAUDE.md and Dockerfile comments.

### 4. mistune 3.x silently breaks conda nbconvert HTML reports

**What:** scipy-notebook ships conda nbconvert which still requires `mistune<3`. uv's resolver may pick mistune 3.x if not constrained, causing HTML reports to render with stack traces or lose styling silently.

**Detect:** After build: `jupyter nbconvert --to html notebooks/business_understanding.ipynb` — must succeed without mistune-related stack trace.

**Prevent:** Keep `mistune<3` pin in `requirements.in`. Add nbconvert smoke step to CI.

### 5. R removal misses references → `/doml-new-project` breaks when user picks "r"

**What:** `data-understanding.md` workflow has explicit `if [ "$LANG" = "r" ]` branch (line 121); `new-project.md` prompts for language preference; PROJECT.md template has `language: python` field with "(default) / R (opt-in)" annotation; `data_understanding_r.ipynb` template referenced in workflows. Removing R partially breaks the new-project flow if the user can still answer "r".

**Detect:** After R removal, run `/doml-new-project` end-to-end and confirm interview never offers R. `grep -rn "language" .claude/doml/` returns only descriptive references.

**Prevent:** Sweep checklist (see end of doc). Add a config-validation gate: if existing `config.json.language` exists and != `python`, print clear error and bail (with migration guidance).

## Medium Pitfalls (probable, plan for)

### 6. uv lockfile format ≠ pip-compile format → noisy diff on regenerate

**What:** `uv pip compile` outputs are similar-but-not-identical to pip-tools (ordering, comment headers, trailing markers). First regeneration shows a 100+ line diff with no semantic change.

**Prevent:** Regenerate as a single isolated commit titled "chore: switch lockfile to uv format" with no other content; document the semantic delta in commit body.

### 7. GitHub Actions cold-cache pull from quay.io — slow + rate limits

**What:** Pulling `quay.io/jupyter/scipy-notebook` (~1.5 GB) on cold cache is 30–90s; quay has stricter anonymous rate limits than ghcr.io.

**Prevent:** Use `actions/cache@v4` for buildx layers, restoring across runs. Pin quay tag (never `:latest`). Optionally mirror base to ghcr.io if rate limits become a problem.

### 8. ubuntu-latest 7 GB RAM ceiling — Optuna×LightGBM may OOM in CI smoke

**What:** Modelling notebooks with 30 Optuna trials × LightGBM with high `num_leaves` can exceed 7 GB RAM.

**Prevent:** CI smoke uses `n_trials=2`, fixture rows ≤500, and `MAX_DATASET_ROWS` env var honored by notebooks. Set `--shm-size=2g` on `docker run`.

### 9. `fix-permissions` over conda dir slows rebuild

**What:** `fix-permissions ${CONDA_DIR}` recurses over freshly populated env, adding 20–40s per layer.

**Prevent:** Collapse all `USER root` operations into a single layer with one `fix-permissions` call at the end. uv installs with appropriate perms already.

### 10. kaggle CLI requires `~/.kaggle/kaggle.json` — CI must skip auth

**What:** Notebooks calling `kaggle datasets download` will hard-fail in CI without credentials.

**Prevent:** Notebooks check `(Path.home() / '.kaggle/kaggle.json').exists()` before invoking; CI papermill runs use parameterized fixture data path that bypasses kaggle entirely.

### 11. ipykernel default name change between docker-stacks images

**What:** scipy-notebook may register kernel as `python3` (likely same as datascience-notebook) but display name has changed in past releases. Papermill called with kernel name lookups by display name could break.

**Prevent:** Pin papermill calls to `--kernel python3` (logical name), not display name. Verify with `jupyter kernelspec list` after build.

### 12. NumPy 2.x ABI breakage if uv resolver picks numpy 2.4

**What:** Pinning numpy via uv resolver may pick 2.4 (if released), breaking C-extension binaries compiled against 2.3.

**Prevent:** Pin numpy explicitly in `requirements.in` (e.g., `numpy<2.4`).

## Low Pitfalls (worth noting)

### 13. `onnxruntime` is heavy (~250 MB)

Used only for WASM target benchmarking (Phase 17). Already cp313. Not worth removing for the size; keep.

### 14. ydata-profiling dependency tree (visions, multimethod, phik, imagehash, wordcloud)

Each is a wheel on cp313. Validate during initial uv compile.

### 15. `PROJECT_ROOT` env in scipy-notebook

Default working dir still `/home/jovyan/work`; env var convention works the same. No-op.

### 16. Existing v1.5 user projects with `language: r` in `config.json`

Will silently misroute to a missing template post-upgrade. Migration note required in MIGRATION.md / README.

## Pre-Flight Checks (before bulk Dockerfile work)

1. **Wheel availability matrix.** Run `uv pip compile requirements.in --python-version 3.13 --dry-run | tee /tmp/wheels-313.txt`. Must succeed with no fallback to sdist.
2. **Build time benchmark on 3.13.** Build the new Dockerfile against scipy-notebook + uv + py3.13 cold cache (`docker buildx build --no-cache`). Confirm <300s.
3. **nbconvert smoke test.** Inside new image: `jupyter nbconvert --to html .claude/doml/templates/notebooks/business_understanding.ipynb`. Must succeed without mistune stack trace.
4. **Kernel + papermill smoke test.** `papermill .../data_understanding_python.ipynb /tmp/out.ipynb -p data_dir tests/fixtures/`.
5. **Audit base image package list.** `docker run --rm quay.io/jupyter/scipy-notebook:<tag> mamba list > /tmp/baseimg.txt`; cross-check `requirements.in` for duplicates that would shadow conda packages.
6. **Verify v1.5 install.sh fallback.** `./install.sh --version v1.5.0 /tmp/test-project` and confirm R-enabled Dockerfile is fetched (since `--version` flag pulls from git tag) — preserves backward compatibility for existing R users who pin to v1.5.

## R Removal Checklist (for execution phase)

**Files to delete:**
- `.claude/doml/templates/notebooks/data_understanding_r.ipynb`
- Any `notebooks/test_r_tidyverse.ipynb` or similar root-level R artifacts

**Files to modify (R blocks/branches removed):**
- `Dockerfile` (root) — delete `mamba install r-*` block
- `.claude/doml/templates/Dockerfile` — same
- `.claude/doml/workflows/data-understanding.md` — remove `if [ "$LANG" = "r" ]` gate (line ~121), remove R-specific 3d/3e/3f/5e/5f/5g/5h subroutines
- `.claude/doml/workflows/new-project.md` — remove "language preference" prompt; hardcode `language: python` in generated config.json; drop "Python, R, and DuckDB" mentions
- `.claude/doml/skills/doml-new-project/SKILL.md` — remove "sets language preference" mention
- `.claude/doml/templates/PROJECT.md` — remove `language` field and "(default) / R (opt-in)" annotation
- `CLAUDE.md` (root) — delete R code blocks (lines 29-31, 48-50, 80, 94-96)
- `.claude/doml/templates/CLAUDE.md` — same
- `AGENTS.md` (root) — delete R blocks (lines 40-44, 59-63)
- `README.md` — drop "language preference" mention (line ~15); verify Mermaid `R` node is iterate-step (keep), not R-language
- All `doml-iterate/SKILL.md`, `doml-data-understanding/SKILL.md`, `doml-modelling/SKILL.md` — grep for "language" or "R"; trim
- All other workflow files (`deploy-*.md`, `iterate-*.md`, `progress.md`, `get-data.md`) — grep for `\bR\b`; verify each match (most are likely `R` mermaid node or unrelated)

**Files to validate:**
- All modelling notebook templates and `forecasting.ipynb`, `anomaly_detection.ipynb`, `business_understanding.ipynb`, `deployment_report.ipynb`: grep for `language == 'r'` or IRkernel — most are false positives but verify
- `install.sh`, `install.ps1` — confirm clean of R refs
- `requirements.in` (template + root) — drop `pip-tools`

**Migration documentation:**
- New: `MIGRATION-v1.6.md` or section in MILESTONES.md/README — explains Python-only direction and v1.5 pin path

---
*Pitfalls research for: v1.6 Container Optimization & Python Modernization*
*Researched: 2026-04-30*
