# Stack Research — v1.4 Deployment

**Domain:** DoML model deployment (CLI binary, FastAPI web service, ONNX/WASM)
**Researched:** 2026-04-14
**Confidence:** HIGH

---

## Existing Validated Capabilities (DO NOT re-research)
- scikit-learn pipelines (preprocessing + model), joblib serialization → `models/best_model.pkl`
- `model_metadata.json` stores feature names, problem type, target column, CV metrics
- Docker environment (jupyter/datascience-notebook base) already running
- Python 3.11/3.12, numpy 2.x, pandas, jinja2 already pinned

---

## New Stack Additions Required

### CLI Binary — PyInstaller
| Package | Version | Purpose |
|---------|---------|---------|
| `pyinstaller` | `6.11.1` | Compile Python + deps into self-contained executable |
| `pyinstaller-hooks-contrib` | `2024.11` | Community hooks for sklearn, numpy, pandas auto-collection |

**Key build flags:**
- `--onedir` preferred over `--onefile` for ML models — avoids slow extraction on each run; `--onefile` adds ~2s cold-start penalty unpacking to temp dir
- `--hidden-import sklearn.utils._cython_blas` and other sklearn Cython internals must be declared explicitly
- `--add-data models/best_model.pkl:models` to bundle the serialized model
- `--collect-all sklearn` ensures all sklearn submodules are collected (critical — sklearn uses lazy imports extensively)
- `--collect-all joblib` — model loading dependency

**Cross-platform constraint (critical):** PyInstaller does NOT cross-compile. A Linux binary must be built inside a Linux container; macOS binary must be built on macOS. The build runs inside the existing Docker environment — no host Python needed. Output binary: `src/<modelname>/v1/dist/predict` (Linux/macOS) or `predict.exe` (Windows).

**Alternative considered — Nuitka 2.5:** Compiles Python to C, ~2–3× faster startup, better IP protection. Rejected for DoML: requires C compiler on build host, ~10× slower build time, complex hook system for numpy/sklearn. PyInstaller is pragmatic for a framework that generates binaries on demand.

---

### Web Service — FastAPI
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | `0.115.6` | Async web framework, auto OpenAPI docs at `/docs` |
| `uvicorn[standard]` | `0.32.1` | ASGI server (includes websockets, http-tools) |
| `pydantic` | `2.10.3` | Request/response models; dynamically built from feature schema |
| `jinja2` | `3.1.6` | Already pinned — auto-generated prediction form HTML |
| `python-multipart` | `0.0.20` | Required for HTML form POST (multipart/form-data) |

**Inference Docker image:** `python:3.11-slim` base (~150MB). Full ML deps add ~1.4GB. Trimmed image (only inference libs, no Jupyter) ~600MB. DoML generates a dedicated `Dockerfile.serve` — separate from the analysis Docker environment.

**Prediction form pattern:** Jinja2 template reads `model_metadata.json` → renders typed `<input>` fields per feature. Numeric dtypes → `type="number" step="any"`. Categorical (object dtype) → `<select>` populated with training set unique values (stored in metadata). Plain `fetch()` POST to `/predict` — no JS framework, no build step. Response rendered inline.

---

### ONNX / WebAssembly
| Package | Version | Purpose |
|---------|---------|---------|
| `skl2onnx` | `1.17.0` | Convert scikit-learn Pipeline → ONNX |
| `onnxmltools` | `1.12.2` | XGBoost/LightGBM → ONNX (extends skl2onnx) |
| `onnxruntime` | `1.20.1` | Server-side ONNX inference (used in parity testing) |
| `onnxruntime-web` | `1.20.1` | Browser WASM inference (CDN delivery, not pip) |

**ONNX operator coverage for DoML models:**
| Model | ONNX support |
|-------|-------------|
| LinearRegression, Ridge, Lasso | ✅ Full |
| RandomForestRegressor/Classifier | ✅ Full |
| GradientBoostingRegressor/Classifier | ✅ Full |
| XGBRegressor/XGBClassifier | ✅ via onnxmltools |
| LightGBMRegressor/Classifier | ✅ via onnxmltools |
| KMeans | ✅ Full |
| DBSCAN | ❌ No ONNX export — clustering WASM limited to KMeans |
| Prophet / ARIMA (pmdarima) | ❌ No ONNX export — forecasting excluded from WASM target |

**Self-contained HTML delivery pattern:**
1. Convert fitted pipeline → `model.onnx` (skl2onnx)
2. Base64-encode → embed in HTML as JS constant (`const MODEL_B64 = "..."`)
3. Load `onnxruntime-web` from jsDelivr CDN
4. On page load: decode base64 → `Uint8Array` → `ort.InferenceSession.create(buffer)`
5. Form submit: build `ort.Tensor` from inputs → `session.run()` → render output

**Size warning:** Large ensemble models (RF 500 trees) → 50–200MB ONNX. Threshold: warn + block if `model.onnx > 20MB`. Suggest web service target instead.

---

### Performance Benchmarking
- `timeit` (stdlib) — single/batch prediction latency
- `requests` (already pinned) — HTTP endpoint benchmarking for web service target
- `subprocess` (stdlib) — CLI binary invocation timing
- No new packages needed

---

## What NOT to Add
- Triton Inference Server — overkill for framework use case
- TorchScript / TensorRT — no PyTorch in DoML
- MLflow serving — DoML uses own model_metadata.json; MLflow adds registry complexity
- BentoML / Seldon / KServe — external platforms out of scope
- gRPC — REST/HTTP sufficient for single-model inference
