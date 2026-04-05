---
phase: "01"
plan: "03"
subsystem: infrastructure-docker
tags: [reproducibility, pre-commit, nbstripout, gitignore, claude-md, requirements]
dependency_graph:
  requires: [01-01, 01-02]
  provides: [nbstripout-hook, gitignore, claude-md, requirements-in]
  affects: [all-future-phases]
tech_stack:
  added: [nbstripout==0.9.1, pre-commit, pip-tools]
  patterns: [pre-commit hooks, pip-compile workflow, immutable raw data, DuckDB-first]
key_files:
  created:
    - .pre-commit-config.yaml
    - .gitignore
    - CLAUDE.md
    - requirements.in
  modified: []
decisions:
  - "nbstripout 0.9.1 chosen as pinned revision to ensure reproducible hook behavior"
  - "requirements.in introduced as unpinned source-of-truth; requirements.txt remains the pip-compile output"
  - "CLAUDE.md encodes all reproducibility rules as hard constraints for Claude Code sessions"
metrics:
  duration: "5 minutes"
  completed: "2026-04-05"
  tasks: 3
  files: 4
---

# Phase 01 Plan 03: Reproducibility Setup Summary

**One-liner:** Pre-commit nbstripout hook, comprehensive .gitignore, DoML CLAUDE.md conventions file, and requirements.in unpinned dependency source added to enforce reproducibility guardrails.

## What Was Built

### Task 1: Pre-commit hook and .gitignore

`.pre-commit-config.yaml` configures `nbstripout` at revision `0.9.1` to strip notebook outputs, execution counts, and selected metadata keys before commit. The extra-keys argument covers `metadata.celltoolbar`, `metadata.kernelspec`, `cell.metadata.heading_collapsed`, and `cell.metadata.collapsed`.

`.gitignore` excludes:
- All files under `data/raw/`, `data/processed/`, `data/external/` (raw data never committed; INFR-05)
- `data/raw/.gitkeep` and `data/raw/README.md` are explicitly allowed via negation patterns
- Generated artifacts: `reports/*.html`, `models/*.pkl`, `models/*.joblib`, `models/*.json`
- `.ipynb_checkpoints/` and `*/.ipynb_checkpoints/`
- Standard Python artifacts: `__pycache__/`, `.pyc`, `.egg-info/`, `.pytest_cache/`, `.venv/`
- R artifacts: `.Rhistory`, `.RData`, `renv/library/`, `renv/staging/`
- Editor/OS: `.DS_Store`, `.vscode/`, `.idea/`, `*.swp`

### Task 2: CLAUDE.md

CLAUDE.md encodes all DoML conventions as hard constraints for Claude Code. Sections written:

| Section | Requirement |
|---------|-------------|
| Random seeds at notebook top (Python + R) | REPR-01 |
| Relative paths via PROJECT_ROOT env var | REPR-02 |
| Raw data immutability (data/raw/ = read-only mount) | INFR-05 |
| Notebook outputs stripped on commit (nbstripout) | REPR-03 |
| Pinned deps via pip-compile from requirements.in | REPR-04 |
| DuckDB-first for tabular profiling/aggregation | analysis convention |
| Tidy data validation before feature engineering | analysis convention |
| Correlation is not causation in every HTML report | OUT-03 |
| Running environment (docker compose commands) | operations |
| What NOT to do (prohibited patterns) | guardrails |
| DoML framework commands | developer UX |

### Task 3: requirements.in

`requirements.in` is the unpinned source file for `pip-compile`. Contains 20 top-level dependencies:

- Core tooling: `duckdb`, `papermill`, `nbconvert`, `nbformat`, `jinja2`
- Reproducibility: `nbstripout`, `pre-commit`, `pip-tools`
- ML stack: `shap`, `optuna`, `umap-learn`, `xgboost`, `lightgbm`, `statsmodels`, `prophet`
- Visualization/profiling: `plotly`, `ydata-profiling`

## Reproducibility Guardrails Now Active

| Guardrail | Mechanism | Requirement |
|-----------|-----------|-------------|
| Notebook outputs excluded from git history | nbstripout 0.9.1 pre-commit hook | REPR-03 |
| Raw data excluded from git | .gitignore data/raw/* with !.gitkeep negation | INFR-05 |
| Generated artifacts excluded | .gitignore reports/*.html, models/*.pkl/.joblib/.json | — |
| Dependency pinning workflow | requirements.in -> pip-compile -> requirements.txt | REPR-04 |
| Seed enforcement in notebooks | CLAUDE.md Rule 1 (hard constraint for Claude Code) | REPR-01 |
| Relative path enforcement | CLAUDE.md Rule 2 PROJECT_ROOT pattern | REPR-02 |

## Decisions Made

1. nbstripout revision `0.9.1` pinned in `.pre-commit-config.yaml` rather than using `latest` or a branch name — ensures deterministic hook behavior across team setups.
2. `requirements.in` introduced alongside the existing `requirements.txt` — `requirements.in` is the human-editable file; `requirements.txt` is always pip-compile output, never hand-edited.
3. CLAUDE.md rules declared "Non-Negotiable" for Reproducibility Rules section — these override any Claude default behavior.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- .pre-commit-config.yaml: FOUND
- .gitignore: FOUND
- CLAUDE.md: FOUND
- requirements.in: FOUND
- Task commit d3c3597: FOUND
