# Architecture Research — v1.4 Deployment

**Domain:** Integrating deployment into existing DoML framework
**Researched:** 2026-04-14
**Confidence:** HIGH

---

## Existing Architecture (relevant parts)

```
.claude/skills/           # DoML commands (SKILL.md entry points)
  doml-business-understanding/
  doml-data-understanding/
  doml-modelling/
  doml-iterate/
  doml-forecasting/
  doml-anomaly-detection/
  doml-get-data/
.claude/doml/
  workflows/              # Step-by-step orchestration files
  templates/              # nbformat notebooks stamped into projects
models/
  best_model.pkl          # joblib-serialized sklearn Pipeline
  model_metadata.json     # feature schema, problem_type, metrics, leaderboard rank
  leaderboard.csv         # all trained models with CV metrics
data/processed/
  preprocessed_*.csv      # output of preprocessing phase
notebooks/                # analysis notebooks per phase
reports/                  # HTML stakeholder reports
src/                      # NEW — deployment artifacts (v1.4)
```

---

## New Components

### Skills (entry points)
```
.claude/skills/
  doml-deploy-model/
    SKILL.md              # routes to deploy-model.md workflow
  doml-iterate-deployment/
    SKILL.md              # routes to iterate-deployment.md workflow
```

### Workflows
```
.claude/doml/workflows/
  deploy-model.md         # main deployment orchestration
  iterate-deployment.md   # deployment iteration orchestration
```

### Notebook Template
```
.claude/doml/templates/notebooks/
  deployment_report.ipynb  # static nbformat template; cells parameterized by target type
```

### Project Output Layout
```
src/
  <modelname>/
    v1/
      deployment_metadata.json  # model_file, target, build_date, doml_version, feature_schema
      # CLI target:
      predict.py               # Python source (for inspection)
      predict.spec             # PyInstaller spec file (for rebuilds)
      dist/predict             # compiled binary
      requirements_serve.txt   # pinned inference deps (subset of full requirements.txt)
      # Web service target:
      app.py                   # FastAPI application
      templates/index.html     # Jinja2 prediction form
      Dockerfile.serve         # inference-only Docker image
      docker-compose.serve.yml
      requirements_serve.txt
      # ONNX/WASM target:
      model.onnx               # converted ONNX model
      index.html               # self-contained prediction page
      deployment_metadata.json
```

---

## Data Flow

### deploy-model.md workflow steps

```
1. Read model_metadata.json → resolve model file, feature schema, problem type
2. If --model override: resolve specified model from leaderboard.csv
3. Ask user: target (CLI / Web service / ONNX-WASM)
4. Ask user: model name (default from model_metadata.json or leaderboard top model name)
5. Create src/<modelname>/v1/ directory
6. Write deployment_metadata.json
7. Branch on target:
   A. CLI → generate predict.py + predict.spec → PyInstaller build inside Docker
   B. Web service → generate app.py + templates/index.html + Dockerfile.serve + docker-compose.serve.yml
   C. ONNX/WASM → skl2onnx convert → base64 embed → generate index.html
8. Execute deployment_report.ipynb (benchmarks + parity test)
9. nbconvert → deployment_report.html
10. Commit src/<modelname>/v1/ + notebooks/deployment_report.ipynb + reports/deployment_report.html
```

### iterate-deployment.md workflow steps

```
1. Read deployment_metadata.json from most recent deployment version
2. If --guidance: parse direction (new model / same model retuned / inference optimization)
3. Determine if model changed:
   - Same model file → bump version within same model folder (v1 → v2)
   - Different model → resolve new model name → new src/<newmodelname>/v1/
4. Re-run relevant deployment step (same target as prior version by default; allow override)
5. Re-execute deployment_report.ipynb with new version params
6. Commit
```

---

## Integration Points

### model_metadata.json schema extension (needed for deployment)
Current fields (from Phase 6): `problem_type`, `target_column`, `feature_names`, `feature_dtypes`, `cv_metric`, `cv_score`, `model_file`

**New fields needed for deployment:**
```json
{
  "model_name": "random_forest_regressor",   // sanitized name for src/ directory
  "feature_categories": {                    // unique values per categorical feature (for form dropdowns)
    "region": ["EU", "US", "APAC"]
  },
  "test_predictions_file": "data/processed/test_predictions.csv"  // parity test reference
}
```

If `model_metadata.json` doesn't have `model_name`, derive from class name: `RandomForestRegressor` → `random_forest_regressor`.

If `test_predictions_file` absent, the parity test section of the report is skipped with a note.

### Forecasting deployment constraint
- Prophet and ARIMA/SARIMAX models are not serializable as standard sklearn Pipelines
- They serialize via `model.pkl` (Prophet) or joblib (pmdarima)
- CLI and web service targets work (load pickle, call `.predict()`)
- ONNX/WASM target NOT available for forecasting — enforce check at step 3

### Clustering deployment
- `model.predict(X)` returns cluster label integer
- No probability output (KMeans has `transform()` for distances — expose as optional)
- ONNX export supported for KMeans — WASM target available

---

## Build Order Recommendation

| Phase | Deliverable | Depends on |
|-------|-------------|------------|
| 13 | deploy-model.md workflow + SKILL.md + model_metadata.json schema ext | Phase 12 |
| 14 | CLI target (predict.py generation + PyInstaller build step) | Phase 13 |
| 15 | Web service target (FastAPI app + Dockerfile.serve + form template) | Phase 13 |
| 16 | ONNX/WASM target (skl2onnx convert + HTML page generation) | Phase 13 |
| 17 | Performance report notebook template + nbconvert pipeline | Phase 13 |
| 18 | doml-iterate-deployment + iterate-deployment.md workflow | Phase 13–17 |
