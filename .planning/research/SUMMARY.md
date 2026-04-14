# Research Summary — v1.4 Deployment

**Project:** DoML — Do Machine Learning
**Milestone:** v1.4 Deployment
**Researched:** 2026-04-14

---

## Stack Additions

| Package | Version | Target |
|---------|---------|--------|
| `pyinstaller` | `6.11.1` | CLI binary |
| `pyinstaller-hooks-contrib` | `2024.11` | CLI binary |
| `fastapi` | `0.115.6` | Web service |
| `uvicorn[standard]` | `0.32.1` | Web service |
| `pydantic` | `2.10.3` | Web service |
| `python-multipart` | `0.0.20` | Web service (form POST) |
| `skl2onnx` | `1.17.0` | ONNX/WASM |
| `onnxmltools` | `1.12.2` | ONNX/WASM (XGB/LGBM) |
| `onnxruntime` | `1.20.1` | ONNX parity testing |
| `onnxruntime-web` | `1.20.1` | Browser (CDN, not pip) |

Jinja2 and requests already pinned. No new packages for benchmarking (timeit, subprocess stdlib).

---

## Feature Table Stakes

| Feature | CLI | Web Service | ONNX/WASM |
|---------|-----|-------------|-----------|
| Single prediction | ✅ JSON arg | ✅ POST /predict | ✅ Form submit |
| Batch prediction | ✅ CSV/JSON file | ✅ POST /predict (array) | ❌ Single only |
| Feature schema | ✅ --help output | ✅ GET /schema + auto-form | ✅ Embedded in HTML |
| Health check | ❌ N/A | ✅ GET /health | ❌ N/A |
| OpenAPI docs | ❌ N/A | ✅ /docs (FastAPI auto) | ❌ N/A |
| Regression support | ✅ | ✅ | ✅ |
| Classification support | ✅ | ✅ | ✅ |
| Clustering support | ✅ | ✅ | ✅ (KMeans only) |
| Forecasting support | ✅ | ✅ | ❌ (no ONNX) |

---

## Critical Architecture Decisions

**1. Export full sklearn Pipeline, not just the estimator**
skl2onnx must receive the full Pipeline (ColumnTransformer + estimator) — exporting only the estimator produces wrong predictions on raw features. This is the #1 correctness pitfall.

**2. PyInstaller uses `--onedir` not `--onefile`**
`--onefile` adds 2–4s cold-start penalty for ML payloads. `--onedir` is the production choice. Binaries are Linux-only (built inside Docker).

**3. FastAPI request model built dynamically with `pydantic.create_model()`**
Feature schema is only known at runtime (from model_metadata.json). Standard Pydantic class syntax doesn't work — `create_model()` is the correct pattern.

**4. ONNX model size gate: > 20MB → block WASM, suggest web service**
Large ensemble models produce ONNX files that are impractical for browser delivery. Hard block with clear user message.

**5. model_metadata.json needs two new fields**
`model_name` (for src/ directory naming) and `feature_categories` (for web form dropdowns). Derive `model_name` from estimator class name if absent.

**6. Versioning logic: scan existing vN dirs, take max+1**
Never assume v1 exists. `doml-iterate-deployment` must discover the current max version.

---

## Watch Out For

| Risk | Severity | Mitigation |
|------|----------|-----------|
| sklearn hidden imports missing in PyInstaller binary | HIGH | `--collect-all sklearn --collect-all joblib` + explicit hidden-imports |
| Preprocessing excluded from ONNX export | HIGH | Export full Pipeline, run parity test to catch immediately |
| Input tensor dtype (float32 vs float64) breaking ONNX | HIGH | `dtype=np.float32` at conversion; `Float32Array` in JS |
| Forecasting/DBSCAN silently wrong in deployed endpoint | HIGH | Problem-type gate before target selection |
| Parity test tolerance too strict (float32 rounding) | MEDIUM | Use `atol=1e-4` for regression, exact labels for classification |
| HTTP connection overhead distorting web service benchmarks | MEDIUM | Use `requests.Session()` for all benchmark calls |
| Version directory collision in doml-iterate-deployment | MEDIUM | Scan for max existing vN, don't assume v1 |

---

## Recommended Build Order (Phases 13–18)

| Phase | Scope |
|-------|-------|
| 13 | `deploy-model.md` workflow skeleton + SKILL.md + `deployment_metadata.json` schema + model resolution logic + target selection |
| 14 | CLI target: `predict.py` generation + PyInstaller build step inside Docker |
| 15 | Web service target: `app.py` + `Dockerfile.serve` + `docker-compose.serve.yml` + auto-generated prediction form |
| 16 | ONNX/WASM target: skl2onnx conversion + size gate + self-contained `index.html` generation |
| 17 | Performance report: `deployment_report.ipynb` template + nbconvert + parity test cells |
| 18 | `doml-iterate-deployment`: SKILL.md + `iterate-deployment.md` workflow + version scan logic |
