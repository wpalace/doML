---
phase: 17-performance-report
plan: 01
status: completed
---

# Plan 17-01 Summary — Notebook Template + onnxruntime Dependency

## What was done

**Task 1: requirements.in**
- Added `onnxruntime` to the ML stack section with comment `# ONNX runtime for WASM target benchmarking (Phase 17 — PERF-01)`

**Task 2: deployment_report.ipynb**
- Written as valid nbformat v4 JSON with 13 cells (11 code + 2 markdown)
- Cell 0: Markdown header
- Cell 1: Imports, REPR-01 (SEED=42), REPR-02 (PROJECT_ROOT from env), WEB_SERVICE_URL from DOML_WEB_SERVICE_URL
- Cell 2: Load deployment_metadata.json via glob, extract target/model/feature_schema, reconstruct category_map
- Cell 3: Load preprocessed CSV, tail(100), select columns per feature_schema
- Cell 4: joblib.load with psutil RSS delta for model load memory
- Cell 5: Target routing — cli_binary (subprocess), web_service (requests, health check, no docker), onnx_wasm (onnxruntime)
- Cell 6: 5 warm-up + 1000 timed single-prediction runs; mean/std/p50/p95/p99; histogram saved to notebooks/
- Cell 7: Batch benchmark over BATCH_SIZES = [10, 100, 1000, 10_000]
- Cell 8: Parity test with hard AssertionError for regression/classification/clustering
- Cell 9: Per-prediction memory delta (10 runs via psutil RSS)
- Cell 10: Throughput projection = 1000.0 / mean_latency_ms
- Cell 11: Summary table (pd.DataFrame.style.hide) + batch results
- Cell 12: Placeholder markdown for workflow narrative injection

## Verification results

| Check | Result |
|-------|--------|
| `grep -c onnxruntime requirements.in` | 1 ✓ |
| nbformat v4, 13 cells, 11 code | PASS ✓ |
| No `anthropic` in notebook | 0 ✓ |
| No `docker` in notebook | 0 ✓ |
| `DOML_WEB_SERVICE_URL` present | 2 ✓ |
| `AssertionError` present | 1 ✓ |
| Unique cell ids | PASS ✓ |
| Cell 12 placeholder text | PASS ✓ |
