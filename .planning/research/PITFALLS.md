# Pitfalls Research — v1.4 Deployment

**Domain:** Common mistakes when adding model deployment to an existing ML analysis framework
**Researched:** 2026-04-14
**Confidence:** HIGH

---

## PyInstaller / CLI Binary Pitfalls

### P1: sklearn hidden imports not collected
**Problem:** PyInstaller's static analysis misses sklearn's runtime-dispatched Cython modules. Binary runs on build machine but crashes on target with `ModuleNotFoundError: sklearn.utils._cython_blas`.
**Prevention:** Use `--collect-all sklearn --collect-all joblib --collect-all threadpoolctl`. Add explicit `--hidden-import` for any Optuna/XGBoost/LightGBM dependencies in the fitted model.
**Phase:** CLI target phase (Phase 14)

### P2: onefile cold-start latency kills benchmarks
**Problem:** `--onefile` extracts the entire payload to a temp directory on each invocation. For sklearn + numpy, this adds 2–4s to every cold start — makes single-prediction benchmarks look terrible.
**Prevention:** Use `--onedir`. The benchmark report should note this distinction and measure warm vs cold start for the CLI target.
**Phase:** CLI target phase + performance report

### P3: Cross-platform binary assumptions
**Problem:** Binary built inside Linux Docker container will not run on macOS/Windows. Generating one binary and documenting it as "portable" is misleading.
**Prevention:** `deployment_metadata.json` records `"platform": "linux-x86_64"`. README in `src/<modelname>/v1/` states the binary is Linux-only; rebuilding for other platforms requires running the build on that platform.
**Phase:** CLI target phase

### P4: Pickle version mismatch
**Problem:** `best_model.pkl` serialized with scikit-learn 1.5 may not load under scikit-learn 1.6 (or vice versa). If the binary bundles a different sklearn version than training, parity test will fail.
**Prevention:** `requirements_serve.txt` pins the exact sklearn version from `requirements.txt`. PyInstaller spec collects from the Docker venv — same versions used for both training and inference.
**Phase:** All deployment targets

---

## FastAPI / Web Service Pitfalls

### P5: Pydantic model built from dynamic feature schema
**Problem:** FastAPI requires Pydantic models at import time for schema generation. Dynamic feature schemas (read from JSON at runtime) don't work with standard `class Model(BaseModel)` syntax.
**Prevention:** Use `pydantic.create_model()` to build the request model dynamically at startup. Example:
```python
fields = {name: (float, ...) for name in feature_names}
PredictRequest = create_model("PredictRequest", **fields)
```
Categorical features use `str` type. This works with FastAPI's dependency injection.
**Phase:** Web service target phase (Phase 15)

### P6: Model loaded per-request (memory / latency spike)
**Problem:** Loading `best_model.pkl` inside the predict endpoint loads it on every request — ~500ms overhead for large ensemble models.
**Prevention:** Load model once in FastAPI lifespan event (`@asynccontextmanager`). Store as app state: `app.state.model = joblib.load(...)`. Reference in endpoint via `request.app.state.model`.
**Phase:** Web service target phase

### P7: Form POST vs JSON POST mismatch
**Problem:** HTML form submits `application/x-www-form-urlencoded`, not `application/json`. A single `/predict` endpoint can't transparently handle both without content-type inspection.
**Prevention:** Use separate form handler (`POST /predict/form` with `Form(...)` params) that converts to JSON and delegates to the main endpoint. Or: use JavaScript `fetch()` in the form to POST JSON — avoids content-type split entirely. DoML uses the JS fetch approach (auto-form already uses fetch).
**Phase:** Web service target phase

---

## ONNX / WASM Pitfalls

### P8: Preprocessing pipeline not exported
**Problem:** `skl2onnx` exports only the final estimator if the sklearn Pipeline isn't handled correctly. Predictions on raw features will be wrong because the OHE/scaling step is skipped.
**Prevention:** Export the entire fitted `Pipeline` object (including `ColumnTransformer` preprocessor) as a single ONNX graph. Use `skl2onnx.convert_sklearn(pipeline, initial_types=[...])` with the full pipeline, not just `pipeline.named_steps['model']`.
**Phase:** ONNX/WASM target phase (Phase 16)

### P9: Input tensor dtype mismatch
**Problem:** `onnxruntime-web` is strict about input tensor dtypes. Float64 inputs to a model converted from Float32 training data will throw `InvalidArgument: Got invalid dimensions`.
**Prevention:** Specify `target_opset=17` and `dtype=np.float32` when calling `convert_sklearn`. In the HTML form JS, cast all numeric inputs to `Float32Array` before creating `ort.Tensor`.
**Phase:** ONNX/WASM target phase

### P10: Large model base64 bloat
**Problem:** A 100MB ONNX model embedded as base64 in HTML becomes 133MB. Browser will OOM or time out loading the page.
**Prevention:** Check `os.path.getsize(model.onnx)` after conversion. If > 20MB, abort WASM target with a clear message: "Model too large for browser inference (XXmb > 20MB limit). Use the web service target instead."
**Phase:** ONNX/WASM target phase

### P11: Forecasting / DBSCAN silently produces wrong output
**Problem:** Prophet and ARIMA don't have a `.predict(X)` sklearn-compatible interface. If deployment code naively calls `model.predict(features)` it will either error or return nonsense.
**Prevention:** Check `problem_type` from `model_metadata.json` before target selection. ONNX/WASM target: block for `forecasting` and `clustering` (when DBSCAN is top model). CLI/web service: use problem-type-aware prediction function (`forecast_predict()` vs `classify_predict()`).
**Phase:** Workflow orchestration phase (Phase 13)

---

## Performance Report Pitfalls

### P12: Parity test tolerance too strict / too loose
**Problem:** Floating-point non-determinism between in-memory model and deployed endpoint can cause parity test to fail spuriously with `atol=0`. Conversely, too-loose tolerance masks real bugs.
**Prevention:** 
- Regression: `np.allclose(in_memory, deployed, atol=1e-4)` — tolerates float32 rounding
- Classification: exact label match required; probability tolerance `atol=0.01`
- Clustering: exact cluster ID match required
- Include assertion results in notebook as pass/fail cell with clear failure message
**Phase:** Performance report phase (Phase 17)

### P13: HTTP overhead dominates web service latency benchmark
**Problem:** Benchmarking `/predict` endpoint with `requests` in a loop includes TCP connection overhead. Single-connection keep-alive vs new connection per request can show 10× difference.
**Prevention:** Use `requests.Session()` for all benchmark HTTP calls (connection pooling). Report both "first request" (cold) and "subsequent requests" (warm, Session) latency separately.
**Phase:** Performance report phase

---

## Iteration Pitfalls

### P14: Version directory collision
**Problem:** `doml-iterate-deployment` creates `v2/` assuming `v1/` exists, but if prior version was deleted or the folder doesn't follow the convention, it creates the wrong version.
**Prevention:** Scan `src/<modelname>/` for existing `vN` directories, take `max(N) + 1`. Never assume `v1` exists.
**Phase:** iterate-deployment phase (Phase 18)

### P15: Deployment_metadata.json not updated on iteration
**Problem:** If `deployment_metadata.json` isn't updated on each iteration, the parity test in the report compares the new deployment against the wrong model's test predictions.
**Prevention:** Always write a fresh `deployment_metadata.json` in each version directory with the correct `model_file`, `iteration`, and `build_date`.
**Phase:** iterate-deployment phase
