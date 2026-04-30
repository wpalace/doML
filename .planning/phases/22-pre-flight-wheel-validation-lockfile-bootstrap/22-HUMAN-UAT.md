---
status: partial
phase: 22-pre-flight-wheel-validation-lockfile-bootstrap
source: [22-VERIFICATION.md]
started: 2026-04-30T00:00:00Z
updated: 2026-04-30T00:00:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Verify cold-cache `docker compose build` against new lockfile + scipy-notebook:2026-04-27 base
expected: `docker compose build --no-cache` produces a working JupyterLab image (Phase 23 contract — Phase 22 already changed the FROM line on the live root Dockerfile, so any build run today consumes the new base before Phase 23's install-layer rewrite lands)
result: [pending]

### 2. Open template `data_understanding_python.ipynb` in JupyterLab and run the new SUMMARIZE cell against fixture data
expected: DuckDB SUMMARIZE returns the column_name / column_type / min / max / approx_unique / avg / std / q25 / q50 / q75 / count / null_percentage table per file; no kernel errors
result: [pending]

### 3. Confirm `scipy-notebook:2026-04-27` dated tag still resolves on quay.io
expected: `docker pull quay.io/jupyter/scipy-notebook:2026-04-27` succeeds without error
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
