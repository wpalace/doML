# data/raw/ — Immutable Source Data

**Convention: Raw data in this directory is immutable.**

## Rules

1. **Never modify files in this directory in place.** Raw data is the single source of truth for reproducibility.
2. **Never overwrite a raw file.** If source data is updated, add a new dated file (e.g., `sales_2026-03-01.csv` → `sales_2026-04-01.csv`) rather than replacing.
3. **Never commit raw data to git.** Raw data files are excluded via `.gitignore` (only `.gitkeep` is tracked). Use external storage (S3, shared drive, DVC) for distribution.

## Enforcement Layers

DoML enforces immutability at three layers:

| Layer | Mechanism |
|-------|-----------|
| OS / Docker | `data/raw` is mounted read-only (`:ro`) inside the container — writes from notebooks will fail with "Read-only file system" |
| Git | `.gitignore` excludes `data/raw/*` (except `.gitkeep`) so accidental commits are prevented |
| Convention | This README + DoML's CLAUDE.md instructions remind users not to mutate raw data |

## Workflow

1. Drop source files into `data/raw/` on the **host machine** (Docker bind mount reflects them read-only inside container).
2. Analysis notebooks read from `data/raw/` via DuckDB or pandas.
3. Cleaned/transformed datasets are written to `data/processed/` — that directory is mutable.
4. Never edit files here. Ever.

## Why This Matters

Reproducibility. A DoML analysis must be re-runnable from the same raw inputs months later. If raw data is mutated in place, prior analysis results become unverifiable and the audit trail breaks.
