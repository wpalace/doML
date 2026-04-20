# Phase 15: Web Service Target — Discussion Log

**Date:** 2026-04-16

## Areas Discussed

All four gray areas were selected for discussion.

---

### 1. Categorical Dropdown Source

**Question:** WEB-06 needs `<select>` elements populated from the processed dataset. Where do category values come from?

**Decision:** Embed into `deployment_metadata.json` at deploy time.

- Scan `preprocessed_*.csv` during `doml-deploy-model` execution
- Store `categories: [...]` (or `null` for numerics) per feature in `feature_schema`
- `app.py` reads from metadata at startup — no data directory mount at runtime
- `docker-compose.serve.yml` does NOT mount `./data/`

**Implication:** `deploy-model.md` workflow must be updated to include the category scan step.

---

### 2. Pydantic Model Strategy

**Question:** How should `app.py` define the typed Pydantic request model?

**Decision:** Dynamic `create_model()` at startup.

- `app.py` reads `deployment_metadata.json` at startup and calls `pydantic.create_model()`
- Single self-contained file, same template for all deployments
- Type mapping: `int64`/`float64` → `float`; `object` → `str`; else → `str`

---

### 3. Docker Base Image

**Question:** Which base image for `Dockerfile.serve`?

**Decision:** `python:3.14-slim`

- Generates `requirements.serve.txt` with pinned deps
- Service starts via uvicorn on port 8080

---

### 4. Prediction Result Display

**Question:** What does the user see after form submission?

**Decision:** Formatted card with probability bars.

- `Prediction: <value>` for all problem types
- Classification: also shows probability table with CSS width bars
- Result injected into `<div id="result">` via `innerHTML`
