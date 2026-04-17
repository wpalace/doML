# Phase 17: Performance Report — Research

**Researched:** 2026-04-17
**Domain:** Notebook benchmarking pipeline, latency/memory measurement, nbconvert, Claude narrative injection
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01** — ONNX/WASM target benchmarked via Python `onnxruntime` inside Docker (approximation); report notes "benchmarked via Python onnxruntime; browser performance may vary". No Playwright dependency.
- **D-02** — Web service target: notebook spins up container via `docker compose -f src/<modelname>/vN/docker-compose.serve.yml up -d`, polls `GET /health` (30 s timeout, 1 s intervals), runs benchmarks, tears down in a `finally` block. `POST /predict` for single; loop over rows for batch (HTTP/1.1, no parallelism).
- **D-03** — Trigger is a final step added to `deploy-model.md` orchestrator — after the target-specific skill completes, generate and execute `deployment_report.ipynb`.
- **D-04** — Claude narrative pattern: Claude Code itself writes the narrative and inserts it as a markdown cell via `nbformat` (same pattern as BU/EDA/anomaly-detection workflows — NOT a Python anthropic SDK call inside the notebook).
- **D-05** — Single `deployment_report.ipynb` handles all three targets via conditional Python `if target ==` blocks reading `deployment_metadata.json` at startup. No separate notebooks per target.
- **D-06** — Parity test uses last 100 rows of `data/processed/preprocessed_*.csv` (or all rows if fewer than 100). `feature_schema` from `deployment_metadata.json` determines column order.

### Claude's Discretion

- Exact matplotlib/seaborn chart style for latency distribution plots (box plot or violin — either is fine)
- Whether batch latency is measured as wall-clock per-call or total time / N
- Whether `psutil` or `tracemalloc` is used for memory measurement (psutil process RSS delta is simpler and sufficient — per CONTEXT.md)
- Exact nbconvert CLI flags for code-hidden HTML conversion
- Whether the notebook uses papermill-style parameters or reads `deployment_metadata.json` directly at startup (direct read preferred per CONTEXT.md)
- Port number handling if 8080 is already in use (fail with a clear error is acceptable)

### Deferred Ideas (OUT OF SCOPE)

None stated in CONTEXT.md.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PERF-01 | `notebooks/deployment_report.ipynb` generated after every deployment | D-03 trigger in deploy-model.md; notebook template written by workflow as static nbformat v4 cells |
| PERF-02 | Single-prediction latency (mean ± std, 1000 runs) | `time.perf_counter` loop; warm-up runs; per-target call mechanics documented below |
| PERF-03 | Batch prediction latency at 10, 100, 1 000, 10 000 rows | Loop-based timing for all targets; HTTP loop for web; batch CSV for CLI; session.run loop for ONNX |
| PERF-04 | Parity test: deployed endpoint matches in-memory model within tolerance | `np.allclose(atol=1e-4)` for regression; `==` for classification labels/cluster IDs; last 100 rows of preprocessed_*.csv |
| PERF-05 | Model load memory footprint + per-prediction memory delta | `psutil.Process().memory_info().rss` delta before/after load and before/after first predict |
| PERF-06 | Throughput projection (requests/sec) from latency | `1.0 / mean_latency_seconds` from single-prediction mean |
| PERF-07 | `reports/deployment_report.html` with code hidden, Claude narrative | `jupyter nbconvert --to html --no-input`; Claude Code writes narrative via nbformat injection (same as BU/EDA pattern) |
</phase_requirements>

---

## Summary

Phase 17 builds the performance benchmarking pipeline for DoML's three deployment targets: CLI binary, FastAPI web service, and ONNX/WASM (via Python onnxruntime approximation). The output is a single `deployment_report.ipynb` that conditionally benchmarks the relevant target, plus an HTML report with hidden code and a narrative summary.

The notebook is a static nbformat v4 file template (same construction pattern as all other DoML notebooks). Target-specific logic is handled through Python `if target == 'cli_binary':` blocks gated on `deployment_metadata.json` — not papermill parameters or cell tags. The narrative is injected by Claude Code directly (same as business-understanding and anomaly-detection workflows) — there is no `anthropic` Python SDK call inside the notebook itself.

The most complex implementation area is the web service benchmarking cell: it must start a Docker container, poll `/health`, run all benchmarks, then reliably stop the container in a `finally` block — all from within a notebook cell running inside the jupyter container. This requires careful subprocess management and awareness that `docker` is available in the jupyter container environment.

**Primary recommendation:** Model the `deployment_report.ipynb` template as a static nbformat v4 file written by the workflow (mirroring `anomaly_detection.ipynb`). Write the workflow as a new `deploy-report.md` appended to `deploy-model.md` as a final step call (Step 12).

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `nbformat` | 5.9.2 (confirmed in container) | Build/modify notebook cells programmatically | Established DoML pattern for all notebook templates |
| `time.perf_counter` | stdlib | High-resolution latency measurement | No install; nanosecond resolution; standard for benchmarking |
| `psutil` | 5.9.0 (confirmed on host) | RSS memory delta measurement | Already available in Jupyter base image; simpler than tracemalloc for process-level measurement |
| `requests` | 2.33.1 (pinned in requirements.txt) | HTTP calls to web service `/predict` and `/health` | Already installed; standard HTTP client |
| `subprocess` | stdlib | CLI binary invocation; Docker container start/stop | No install needed |
| `onnxruntime` | (must be added to requirements.in — see below) | ONNX/WASM target benchmarking inside Docker | D-01 decision; Python ORT is the approximation |
| `numpy` | already in image | Parity comparison (`np.allclose`, `np.array_equal`) | Standard numerical comparison |
| `pandas` | already in image | Read `preprocessed_*.csv` for parity test data | Standard data loading |
| `matplotlib` or `seaborn` | already in image | Latency distribution charts | Already installed in jupyter/datascience-notebook |
| `joblib` | already in image | Load `best_model.pkl` for in-memory parity reference | Same package used by sklearn Pipeline serialization |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json` | stdlib | Parse deployment_metadata.json, format CLI input | All targets |
| `glob` | stdlib | Locate `preprocessed_*.csv` | Parity test data resolution |
| `IPython.display` | in image | Render Markdown, display DataFrames in notebook | All display cells |
| `tracemalloc` | stdlib | Python object-level memory tracing | Not needed — psutil RSS delta is sufficient per CONTEXT.md discretion |

### Requirements Changes Needed

`onnxruntime` is **NOT** currently in `requirements.in` or `requirements.txt`. [VERIFIED: grep of requirements.in and requirements.txt] It must be added for the WASM benchmark cells to work inside Docker.

`psutil` is available on the host [VERIFIED: `python3 -c "import psutil"` exited 0] but its presence inside the Docker container needs to be confirmed at implementation time — the `jupyter/datascience-notebook` image typically includes it via conda.

**Installation addition needed:**
```
# requirements.in — add to existing ML stack section
onnxruntime
```

Then regenerate `requirements.txt` per REPR-04: `docker compose run --rm jupyter pip-compile requirements.in`

---

## Architecture Patterns

### Notebook Structure (deployment_report.ipynb)

The notebook is a static nbformat v4 file written by the workflow, following the exact same pattern as `anomaly_detection.ipynb` and other DoML templates. All cells are written as Python code cells or Markdown cells. Target-specific sections use `if target == 'cli_binary':` / `elif target == 'web_service':` / `elif target == 'onnx_wasm':` guards.

**Recommended cell order:**

```
Cell 0: Markdown header — "# Deployment Performance Report"
Cell 1: Setup — REPR-01 seed, REPR-02 PROJECT_ROOT, imports
Cell 2: Load deployment_metadata.json — set target, model_name, version, feature_schema, deploy_dir
Cell 3: Load test data (last 100 rows of preprocessed_*.csv)
Cell 4: Load in-memory model (joblib.load) for parity reference; measure load RSS delta (PERF-05)
Cell 5: TARGET ROUTING — if/elif block that calls target-specific benchmark functions
  Cell 5a (CLI): Warm-up + 1000-run single-predict timing; batch at [10,100,1000,10000]
  Cell 5b (Web): Docker start + health poll + 1000-run timing + batch + Docker stop (finally)
  Cell 5c (ONNX): onnxruntime session load + 1000-run timing + batch at [10,100,1000,10000]
Cell 6: Parity test — compare deployed output vs in-memory model output
Cell 7: Memory summary — load delta, per-prediction delta (PERF-05)
Cell 8: Throughput projection — 1.0 / mean_single_latency_s (PERF-06)
Cell 9: Latency charts — box/violin plot across batch sizes (Claude discretion)
Cell 10: Results summary table — all metrics consolidated
Cell 11: Caveats markdown — target-specific notes (ONNX approximation caveat for WASM)
```

### Pattern 1: Latency Measurement

**What:** Time `perf_counter` loop with warm-up runs discarded, collect all samples, report mean ± std.
**When to use:** Single-prediction benchmarking (PERF-02); inner loop of batch timing (PERF-03).

```python
# Source: [ASSUMED based on Python stdlib timeit and perf_counter best practices]
import time

# Warm-up: 5 runs discarded (JIT effects, cold-start subprocess, network)
for _ in range(5):
    _ = run_single_predict(row)

# Timed runs
N_RUNS = 1000
latencies = []
for _ in range(N_RUNS):
    t0 = time.perf_counter()
    _ = run_single_predict(row)
    latencies.append(time.perf_counter() - t0)

import numpy as np
mean_ms = np.mean(latencies) * 1000
std_ms  = np.std(latencies) * 1000
print(f"Single-prediction latency: {mean_ms:.2f} ± {std_ms:.2f} ms (n={N_RUNS})")
```

**Why `perf_counter` not `timeit`:** `timeit` disables garbage collection and runs in a subprocess context unsuitable for subprocess/HTTP benchmarks. `perf_counter` is appropriate when the operation under test involves I/O (subprocess, HTTP), which it does for CLI and web targets. [ASSUMED]

**Why 5 warm-up runs:** CLI binary has cold-start subprocess spawn overhead; web service HTTP connection pool warms up; onnxruntime session has JIT. 5 runs is conventional for micro-benchmarks. [ASSUMED]

### Pattern 2: CLI Binary Invocation

**What:** `subprocess.run` with JSON input string, capture stdout, parse result.

```python
# Source: [VERIFIED: Phase 14 CONTEXT.md D-02 defines CLI input format]
import subprocess, json

def run_cli_predict(deploy_dir, row_dict):
    """Run the CLI binary with a JSON row, return parsed prediction."""
    binary = str(deploy_dir / 'dist' / 'predict' / 'predict')
    result = subprocess.run(
        [binary, '--input', json.dumps(row_dict)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLI binary failed (exit {result.returncode}): {result.stderr}")
    return json.loads(result.stdout.strip())
```

**Note:** For batch latency at 10/100/1000/10000 rows, loop `subprocess.run` N times — do NOT use `--input data.csv` (file mode), which writes a result file and doesn't return per-row timing suitable for latency measurement. [ASSUMED]

### Pattern 3: Web Service Container Auto-Start/Stop

**What:** Spin up Docker container from compose file, poll `/health`, benchmark, stop in `finally`.

```python
# Source: [VERIFIED: Phase 15 CONTEXT.md D-03 defines compose file path and port 8080]
import subprocess, time, requests

def start_web_service(deploy_dir):
    compose_file = str(deploy_dir / 'docker-compose.serve.yml')
    subprocess.run(
        ['docker', 'compose', '-f', compose_file, 'up', '-d'],
        check=True
    )
    # Poll /health
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            r = requests.get('http://localhost:8080/health', timeout=2)
            if r.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(1)
    raise TimeoutError("Web service did not start within 30 seconds")

def stop_web_service(deploy_dir):
    compose_file = str(deploy_dir / 'docker-compose.serve.yml')
    subprocess.run(
        ['docker', 'compose', '-f', compose_file, 'down'],
        check=True
    )

# Usage pattern (inside notebook cell):
try:
    start_web_service(deploy_dir)
    # ... run all benchmarks here ...
finally:
    stop_web_service(deploy_dir)
```

**Critical:** The `docker` CLI must be available inside the jupyter container. The jupyter container runs Docker-in-Docker or has the host Docker socket mounted. [ASSUMED — needs verification at implementation time; standard DoML pattern uses `docker compose exec` from host-side, but the notebook runs inside the container.] See Open Questions.

### Pattern 4: onnxruntime Inference

**What:** Load `model.onnx`, prepare float32 input tensor from feature_schema column order, run inference.

```python
# Source: [ASSUMED based on onnxruntime Python API; VERIFIED: Phase 16 CONTEXT.md D-03 defines float32-only tensors]
import onnxruntime as ort
import numpy as np

def load_onnx_session(deploy_dir):
    onnx_path = str(deploy_dir / 'model.onnx')
    return ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])

def run_onnx_predict(session, row_dict, feature_schema, category_map):
    """Build float32 input tensor from a dict; categoricals use ordinal codes."""
    values = []
    for feat in feature_schema:
        name = feat['name']
        val  = row_dict[name]
        if feat.get('categories'):
            # Map string label to integer ordinal
            val = category_map[name][str(val)]
        values.append(float(val))
    tensor = np.array([values], dtype=np.float32)
    input_name = session.get_inputs()[0].name
    result = session.run(None, {input_name: tensor})
    return result[0][0]
```

**Input name discovery:** `session.get_inputs()[0].name` returns the ONNX graph input name — do NOT hardcode it. [ASSUMED]

**category_map:** Phase 16 `deploy-wasm.md` embeds `category_map` in `index.html`. The notebook must reconstruct the same map from `feature_schema` categories at benchmark time (same ordinal encoding logic as Phase 16). [VERIFIED: Phase 16 CONTEXT.md D-03]

### Pattern 5: Memory Measurement with psutil

**What:** RSS delta before/after an operation.

```python
# Source: [ASSUMED; psutil documented at psutil.readthedocs.io]
import psutil, os

proc = psutil.Process(os.getpid())

rss_before_load = proc.memory_info().rss
model = joblib.load(model_path)
rss_after_load = proc.memory_info().rss
load_delta_mb = (rss_after_load - rss_before_load) / 1024 / 1024

rss_before_pred = proc.memory_info().rss
_ = model.predict(single_row_df)
rss_after_pred = proc.memory_info().rss
per_pred_delta_kb = (rss_after_pred - rss_before_pred) / 1024
```

**Caveat:** RSS delta is noisy for small operations and can be negative if GC runs. Take the value as an approximation, not a precise allocation count. Report with a "approximate" qualifier in the notebook. [ASSUMED]

**For ONNX load memory:** Same pattern but wrap `ort.InferenceSession(...)` instead of `joblib.load`. [ASSUMED]

### Pattern 6: Parity Test

**What:** Feed last 100 rows through deployed target AND `model.predict()` in-memory; compare results by problem type.

```python
# Source: [VERIFIED: CONTEXT.md D-06, PERF-04]
import numpy as np

def assert_parity(deployed_preds, inmemory_preds, problem_type):
    if problem_type == 'regression':
        ok = np.allclose(deployed_preds, inmemory_preds, atol=1e-4)
    else:
        # classification, clustering — exact label/ID match
        ok = np.array_equal(deployed_preds, inmemory_preds)
    if not ok:
        n_diff = np.sum(np.abs(np.array(deployed_preds) - np.array(inmemory_preds)) > 1e-4) \
                 if problem_type == 'regression' else np.sum(np.array(deployed_preds) != np.array(inmemory_preds))
        raise AssertionError(f"Parity FAILED: {n_diff} of {len(inmemory_preds)} predictions differ")
    print(f"Parity PASSED: {len(inmemory_preds)} predictions match within tolerance")
```

**Test data loading:**
```python
# Source: [VERIFIED: CONTEXT.md D-06]
import glob, pandas as pd
from pathlib import Path

processed_files = sorted(glob.glob(str(PROJECT_ROOT / 'data' / 'processed' / 'preprocessed_*')))
if not processed_files:
    raise FileNotFoundError("No preprocessed_*.csv found in data/processed/")
df_full = pd.read_csv(processed_files[0])
test_data = df_full.tail(100)  # last 100 rows, or all if fewer
```

### Pattern 7: nbconvert HTML Generation (Code Hidden)

**What:** Convert the executed notebook to HTML with all code cells hidden.

```bash
# Source: [VERIFIED: confirmed in business-understanding.md Step 7b]
docker compose exec jupyter jupyter nbconvert \
  --to html \
  --no-input \
  notebooks/deployment_report.ipynb \
  --output-dir reports \
  --output deployment_report
```

This produces `reports/deployment_report.html`. The `--no-input` flag is the correct flag for hiding code cells (not `--hide-input` which is a different/deprecated variant). [VERIFIED: business-understanding.md and anomaly-detection.md use this exact pattern]

### Pattern 8: Narrative Injection (Claude Code — NOT Python SDK)

**Critical finding:** The "Claude API call" referenced in CONTEXT.md D-04 is NOT a Python `anthropic` SDK call inside the notebook. The pattern established across all DoML workflows (business-understanding, anomaly-detection, iterate) is:

1. Claude Code (the agent) reads the executed notebook outputs
2. Claude Code writes a narrative as a Python script to `/tmp/doml_insert_report_summary.py`
3. The script uses `nbformat` to insert the narrative as a new markdown cell at position 0
4. `python3 /tmp/doml_insert_report_summary.py` is run to apply the insertion

```python
# /tmp/doml_insert_report_summary.py
import nbformat, uuid

NARRATIVE = """[CLAUDE WRITES 2-3 PARAGRAPHS HERE]"""

with open('notebooks/deployment_report.ipynb') as f:
    nb = nbformat.read(f, as_version=4)

cell = nbformat.v4.new_markdown_cell(source='## Performance Summary\n\n' + NARRATIVE)
cell['id'] = uuid.uuid4().hex[:8]
nb.cells.insert(0, cell)

with open('notebooks/deployment_report.ipynb', 'w') as f:
    nbformat.write(nb, f)

print('Narrative inserted')
```

[VERIFIED: business-understanding.md Step 6, anomaly-detection.md Step 7 — both use this exact pattern]

There is no `anthropic` package in `requirements.in`. The narrative is a Claude Code workflow step, not a notebook computation.

### Pattern 9: Notebook Execution Inside Docker

**What:** Execute notebook via `nbconvert --execute` from the host-side workflow.

```bash
# Source: [VERIFIED: business-understanding.md Step 4, anomaly-detection.md Step 5]
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/deployment_report.ipynb \
  --ExecutePreprocessor.timeout=900
```

**Timeout:** Set to 900 seconds (15 minutes) — benchmarking 1000 runs × 3 batch sizes across potentially slow CLI subprocesses requires more time than the 600 s used in analysis notebooks. [ASSUMED — may need tuning]

### Pattern 10: Batch Latency Measurement

**What:** For each batch size N in [10, 100, 1000, 10000], time the total of N sequential single-prediction calls, then divide by N.

```python
# Source: [ASSUMED]
BATCH_SIZES = [10, 100, 1000, 10_000]
batch_results = {}

for n in BATCH_SIZES:
    rows = test_data.head(n) if len(test_data) >= n else pd.concat([test_data] * (n // len(test_data) + 1)).head(n)
    t0 = time.perf_counter()
    for _, row in rows.iterrows():
        _ = run_single_predict(row.to_dict())
    elapsed = time.perf_counter() - t0
    batch_results[n] = {
        'total_s': elapsed,
        'mean_ms': elapsed / n * 1000,
        'rows_per_sec': n / elapsed
    }
```

**Note for 10,000 rows with web service:** 10,000 sequential HTTP requests may take 100–300 seconds depending on container overhead. This is within the extended timeout but should be noted in the plan. [ASSUMED]

### Anti-Patterns to Avoid

- **Hardcoding target names:** Always read `target` from `deployment_metadata.json` — never assume.
- **Skipping warm-up runs:** Cold-start latency for subprocess and HTTP inflates the mean significantly if the first runs are included.
- **Using `timeit.timeit()` for subprocess/HTTP:** `timeit` disables GC and is designed for pure-Python micro-benchmarks, not I/O-bound operations.
- **Hardcoding `model.onnx` path:** Derive from `deploy_dir / 'model.onnx'` — consistent with Phase 16 output.
- **Starting web container outside `try/finally`:** Container leak if benchmark cell raises an exception.
- **Using `--no-input` on the notebook before execution:** Execute first, then convert.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Notebook cell insertion | String manipulation of .ipynb JSON | `nbformat.v4.new_markdown_cell()` + `nbformat.write()` | Handles cell IDs, metadata, version correctly |
| HTTP health polling | Custom retry logic | `requests.get()` in a time-limited while loop | Simple and already in requirements |
| Memory measurement | Manual `sys.getsizeof()` traversal | `psutil.Process().memory_info().rss` delta | Measures actual OS-level allocation including C extensions |
| Latency statistics | Custom rolling stats | `numpy.mean()`, `numpy.std()` | Correct, vectorized, already available |
| ONNX inference | Custom ONNX parser | `onnxruntime.InferenceSession` | The established library; Phase 16 already converted to this format |

---

## Deploy-model.md Integration (D-03)

The current `deploy-model.md` ends at **Step 11** (confirmation display). Phase 17 must add a **Step 12** that:

1. Copies `deployment_report.ipynb` template from `.claude/doml/templates/notebooks/deployment_report.ipynb` to `notebooks/`
2. Executes it via `docker compose exec jupyter jupyter nbconvert --execute --inplace ...`
3. Reads the executed notebook outputs
4. Injects the Claude narrative via `/tmp/doml_insert_report_summary.py`
5. Generates `reports/deployment_report.html` via `--to html --no-input`
6. Verifies the HTML exists

This step must be added to `deploy-model.md` (not a separate workflow file), per D-03.

Alternatively, the step can call a separate `deploy-report.md` workflow that encapsulates the full report pipeline — making it reusable by Phase 18 (`doml-iterate-deployment`). The planner should decide based on DRY principles.

---

## Common Pitfalls

### Pitfall 1: Docker Socket Availability Inside Jupyter Container

**What goes wrong:** The benchmark notebook cells for the web service target call `subprocess.run(['docker', 'compose', ...])` — but the `docker` CLI may not be available inside the running jupyter container.

**Why it happens:** The jupyter container is started by `docker compose up` from the host. The standard `jupyter/datascience-notebook` base image does not include Docker CLI. The workflow's other Docker calls (`docker compose exec jupyter ...`) run from the HOST, not from inside the container.

**How to avoid:** The notebook benchmark cell for the web service target should be run as a **workflow step** (from the host shell, not inside the container), or the workflow should execute the web service benchmarking as a Python script that runs on the host side rather than inside `nbconvert --execute`.

**Alternative:** Write the web service benchmark cell to call a shell script passed in via a temp file, or use the papermill `--parameters` approach to inject the deploy_dir and have the benchmark cell skip Docker management (pre-start and post-stop handled by the workflow).

**Recommended resolution:** The `deploy-model.md` Step 12 starts and stops the web service container from the HOST workflow (not from inside the notebook), and passes a `WEB_SERVICE_RUNNING=true` signal to the notebook. The web service benchmark cell in the notebook assumes the service is already running on port 8080. This is simpler and avoids Docker-in-Docker. [ASSUMED — planner must decide and document in PLAN.md]

### Pitfall 2: 10,000-Row HTTP Benchmark Timeout

**What goes wrong:** 10,000 sequential HTTP requests to `POST /predict` at ~10-50ms each = 100-500 seconds. This exceeds a 600 s nbconvert timeout.

**Why it happens:** HTTP/1.1 with no connection pooling has high per-request overhead; cold connections and JSON serialization add latency.

**How to avoid:** Set `--ExecutePreprocessor.timeout=900` or higher. Alternatively, use a `requests.Session()` to enable HTTP keep-alive (persistent connections), which reduces overhead significantly. For the 10,000-row case, consider timing the first 100 rows and extrapolating — but PERF-03 requires actually running at all four sizes.

**Warning signs:** nbconvert exits with a `TimeoutError` or `CellTimeoutError`.

### Pitfall 3: Parity Test Column Order Mismatch

**What goes wrong:** The deployed endpoint and the in-memory model receive features in different column orders, causing the parity test to fail even when the model is correct.

**Why it happens:** `deployment_metadata.json` `feature_schema` is the authoritative column order. If `test_data` is loaded from CSV and iterated without enforcing this order, the column sequence may differ.

**How to avoid:** Always build input dicts/arrays from `feature_schema` order explicitly:
```python
feature_names = [f['name'] for f in feature_schema]
test_array = test_data[feature_names].values  # enforces order
```

### Pitfall 4: onnxruntime Session Load for Each Benchmark Run

**What goes wrong:** Loading a new `InferenceSession` for each of 1000 benchmark runs. Model load overhead dominates the latency measurement.

**Why it happens:** Confusing "model load memory delta" (PERF-05) with the latency benchmark (PERF-02).

**How to avoid:** Load the session once before the timing loop. Measure load time separately for PERF-05. The 1000-run latency measures inference only, not load.

### Pitfall 5: Negative Memory Delta

**What goes wrong:** `rss_after - rss_before` is negative because GC ran between measurements.

**Why it happens:** Python garbage collection can reclaim memory between the two RSS measurements.

**How to avoid:** Take the absolute value and report as "approximate". Run `gc.collect()` before taking the baseline measurement to get a cleaner baseline. Report in the notebook with a "approximate ± GC noise" qualifier.

### Pitfall 6: Category Map Reconstruction for ONNX

**What goes wrong:** ONNX benchmark cell cannot encode categorical features correctly because `category_map` is embedded in `index.html` (Phase 16) but not in `deployment_metadata.json`.

**Why it happens:** Phase 16 builds `category_map` during HTML generation and inlines it as a JS constant — it is not persisted back to `deployment_metadata.json`.

**How to avoid:** The ONNX benchmark cell must reconstruct `category_map` from `feature_schema` `categories` field (same source Phase 16 used). The `feature_schema` in `deployment_metadata.json` includes `categories: ["EU", "NA", ...]` per categorical feature (set by Phase 15 D-01). Build: `{feat['name']: {label: i for i, label in enumerate(feat['categories'])} for feat in feature_schema if feat.get('categories')}`. [VERIFIED: Phase 15 CONTEXT.md D-01, Phase 16 CONTEXT.md D-03]

---

## Code Examples

### Full Benchmark Cell Structure (Skeleton)

```python
# Source: [ASSUMED — synthesized from established DoML patterns]
import json, glob, time, subprocess, gc, os
import numpy as np, pandas as pd, joblib, psutil
from pathlib import Path
from IPython.display import Markdown, display

PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', '/home/jovyan/work'))

# --- Load deployment metadata ---
deploy_dirs = sorted(glob.glob(str(PROJECT_ROOT / 'src/*/*')))
versioned = [(d, int(re.search(r'/v(\d+)$', d).group(1))) for d in deploy_dirs if re.search(r'/v(\d+)$', d)]
deploy_dir = Path(sorted(versioned, key=lambda x: x[1], reverse=True)[0][0])

with open(deploy_dir / 'deployment_metadata.json') as f:
    meta = json.load(f)

target        = meta['target']          # 'cli_binary' | 'web_service' | 'onnx_wasm'
problem_type  = meta['problem_type']
feature_schema = meta['feature_schema']
model_file    = PROJECT_ROOT / meta['model_file']
feature_names = [f['name'] for f in feature_schema]

# --- Load test data (PERF-04, D-06) ---
processed = sorted(glob.glob(str(PROJECT_ROOT / 'data' / 'processed' / 'preprocessed_*')))
df_full   = pd.read_csv(processed[0])
test_data = df_full[feature_names].tail(100)

# --- In-memory reference (PERF-04) ---
proc = psutil.Process(os.getpid())
gc.collect()
rss_before_load = proc.memory_info().rss
pipeline = joblib.load(model_file)
rss_after_load = proc.memory_info().rss
load_delta_mb = (rss_after_load - rss_before_load) / 1024 / 1024

inmemory_preds = pipeline.predict(test_data)

# --- Target-specific benchmark ---
N_RUNS = 1000
BATCH_SIZES = [10, 100, 1000, 10_000]

if target == 'cli_binary':
    # ... CLI subprocess benchmark ...
    pass
elif target == 'web_service':
    # ... HTTP benchmark (assumes service already running per workflow) ...
    pass
elif target == 'onnx_wasm':
    # ... onnxruntime benchmark ...
    pass
```

### Verify HTML Code Hidden

```bash
# Source: [VERIFIED: business-understanding.md Step 7c]
grep -c 'class="input"' reports/deployment_report.html && \
  echo "CODE_VISIBLE_VIOLATION" || echo "CODE_HIDDEN_OK"
```

---

## Runtime State Inventory

This is not a rename/refactor phase. No runtime state inventory required.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `psutil` Python pkg | PERF-05 memory delta | Confirmed on host | 5.9.0 | tracemalloc (less accurate) |
| `requests` Python pkg | Web service HTTP calls | Confirmed (requirements.txt) | 2.33.1 | — |
| `onnxruntime` Python pkg | WASM benchmark (D-01) | NOT in requirements.in/txt | — | Must add to requirements.in |
| `nbformat` Python pkg | Notebook template construction | Confirmed | 5.9.2 | — |
| `docker` CLI | Web container start/stop | Confirmed on host | 29.3.0 | — |
| `docker` inside jupyter container | Notebook web benchmark cell | UNKNOWN — verify at impl time | — | Run benchmark from host workflow instead |
| `matplotlib` / `seaborn` | Latency charts | In jupyter/datascience-notebook base | — | — |
| `numpy`, `pandas`, `joblib` | Core benchmark ops | In jupyter/datascience-notebook base | — | — |

**Missing dependencies with no fallback:**
- `onnxruntime` must be added to `requirements.in` and the image rebuilt before WASM benchmark cells work.

**Missing dependencies with fallback:**
- `docker` CLI inside jupyter container: if unavailable, web service start/stop should be done from the host workflow (not from inside a notebook cell). This is actually the preferred pattern — see Pitfall 1.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already in requirements.in) |
| Config file | None detected — inline invocation |
| Quick run command | `pytest tests/ -x -q` (if tests exist) |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| PERF-01 | `notebooks/deployment_report.ipynb` generated after deployment | Smoke | Check `test -f notebooks/deployment_report.ipynb` | Workflow verification step |
| PERF-02 | Single-prediction latency (mean ± std, 1000 runs) | Integration | Notebook execution output inspection | Manual-verify: latency values present in executed notebook |
| PERF-03 | Batch latency at 10, 100, 1000, 10000 rows | Integration | Notebook execution output inspection | Manual-verify: all 4 sizes present |
| PERF-04 | Parity test passes within tolerance | Automated | `assert_parity()` raises `AssertionError` on failure — notebook cell fails execution | nbconvert exits non-zero if parity fails |
| PERF-05 | Memory load delta and per-prediction delta | Integration | Notebook output inspection | Manual-verify: positive values, reasonable order of magnitude |
| PERF-06 | Throughput projection | Integration | `1.0 / mean_latency_s` computed in notebook | Manual-verify: value printed |
| PERF-07 | `reports/deployment_report.html` with no code, Claude narrative | Smoke | `grep -c 'class="input"' reports/deployment_report.html` should return 0 | Same verification pattern as BU/EDA |

### Validation Approach

The primary validation for this phase is notebook execution without error (nbconvert exit code 0 means all cells ran). The parity test (PERF-04) is the only requirement that produces a hard assertion failure — all others are observable outputs.

**Manual verification checklist after execution:**
- [ ] `notebooks/deployment_report.ipynb` exists and has cell outputs
- [ ] `reports/deployment_report.html` exists and `grep -c 'class="input"' reports/deployment_report.html` returns 0
- [ ] HTML contains "Performance Summary" heading (narrative injected)
- [ ] Executed notebook has latency stats for all 4 batch sizes
- [ ] Parity test cell shows "PASSED" in output

### Wave 0 Gaps

- [ ] `notebooks/deployment_report.ipynb` — does not exist yet; must be created as the phase template
- [ ] `reports/` directory — created by the workflow if not present
- [ ] No pytest test files for this phase are expected (notebook execution is the test)

*(No existing test infrastructure covers these requirements — all are new.)*

---

## Security Domain

This phase is internal benchmarking infrastructure with no user-facing endpoints, auth, or data ingestion from untrusted sources. ASVS categories do not apply. The web service being benchmarked was designed in Phase 15 without auth (explicitly deferred per Phase 15 CONTEXT.md). The benchmark notebook does not introduce new attack surface.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `time.perf_counter` is appropriate for subprocess/HTTP benchmarks; `timeit` is not | Standard Stack / Pattern 1 | Low — alternative is wrapping timeit with appropriate setup; perf_counter is standard for I/O-bound timing |
| A2 | 5 warm-up runs is sufficient to eliminate cold-start effects for CLI/web/onnxruntime | Pattern 1 | Low — could increase to 10 if first-run latency spikes are visible in distribution charts |
| A3 | `psutil` is available inside the `jupyter/datascience-notebook` Docker image | Environment Availability | Medium — if not, must add `psutil` to requirements.in; fallback to tracemalloc |
| A4 | `docker` CLI is NOT available inside the jupyter container for notebook-level web benchmark | Pitfall 1 | High — if wrong, web benchmark can run inside notebook cell directly; if right, must use host-side orchestration |
| A5 | 900 s nbconvert timeout is sufficient for 10,000-row HTTP benchmark | Pitfall 2 | Medium — if wrong, reduce batch test to 1000 rows or extrapolate from smaller sizes |
| A6 | `category_map` must be reconstructed from `feature_schema` categories; it is not in `deployment_metadata.json` | Pattern 4 / Pitfall 6 | Low — if Phase 16 added category_map to deployment_metadata.json, reconstruction is simpler; read Phase 16 final output to verify |
| A7 | The narrative step is Claude Code writing text (not a Python anthropic SDK call) | Pattern 8 | LOW risk — confirmed across 3 existing workflow files |
| A8 | `requests.Session()` connection pooling reduces per-request overhead for HTTP benchmark | Pattern 3 / Pitfall 2 | Low — benefit is real but not critical to correctness |

---

## Open Questions

1. **Docker CLI inside jupyter container (Pitfall 1)**
   - What we know: `docker compose exec jupyter ...` runs from the host; the jupyter container does not define `docker` CLI in its base image
   - What's unclear: Does the DoML `docker-compose.yml` mount the host Docker socket (`/var/run/docker.sock`) into the jupyter container? If yes, `docker` commands work from inside the container.
   - Recommendation: Planner should check `docker-compose.yml` template for socket mount. If absent, design the web benchmark so the container start/stop is a workflow step (host-side), not a notebook cell.

2. **category_map persistence in deployment_metadata.json (Pitfall 6)**
   - What we know: Phase 16 builds `category_map` at HTML generation time from `feature_schema.categories`
   - What's unclear: Did Phase 16 implementation write `category_map` back to `deployment_metadata.json`?
   - Recommendation: Planner should read `deploy-wasm.md` in full to check. If not persisted, notebook must reconstruct from `feature_schema.categories`.

3. **deploy-report.md as a separate reusable workflow**
   - What we know: D-03 says add a final step to `deploy-model.md`; Phase 18 will also need to run the report
   - What's unclear: Should the report generation be a separate `deploy-report.md` workflow that both `deploy-model.md` and Phase 18's `iterate-deployment.md` can call?
   - Recommendation: Extract to a separate `deploy-report.md` for DRY reuse in Phase 18. Document as two tasks: one for the report workflow file, one for the `deploy-model.md` Step 12 that calls it.

---

## Sources

### Primary (HIGH confidence)
- Codebase: `.claude/doml/workflows/business-understanding.md` — verified narrative injection pattern (Steps 6, 7)
- Codebase: `.claude/doml/workflows/anomaly-detection.md` — verified same pattern
- Codebase: `.planning/phases/17-performance-report/17-CONTEXT.md` — all locked decisions
- Codebase: `.planning/phases/15-web-service-target/15-CONTEXT.md` — web compose file path, port 8080
- Codebase: `.planning/phases/16-onnx-wasm-target/16-CONTEXT.md` — model.onnx path, category_map, float32 tensors
- Codebase: `.planning/phases/14-cli-binary-target/14-CONTEXT.md` — CLI binary path and invocation format
- Codebase: `requirements.in`, `requirements.txt` — confirmed onnxruntime absent, requests present
- Codebase: `.claude/doml/workflows/deploy-model.md` — confirmed ends at Step 11; Step 12 is the insertion point
- System: `python3 -c "import psutil"` — confirmed psutil 5.9.0 available on host
- System: `python3 -c "import nbformat"` — confirmed nbformat 5.9.2
- System: `docker --version` — confirmed Docker 29.3.0

### Secondary (MEDIUM confidence)
- Pattern extrapolation from existing DoML notebooks for benchmark cell structure

### Tertiary (LOW confidence)
- `time.perf_counter` appropriateness for I/O-bound operations vs `timeit` — training knowledge
- psutil RSS delta behavior under GC pressure — training knowledge
- onnxruntime `InferenceSession` API shape — training knowledge (version not confirmed)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified from codebase and system checks
- Architecture patterns: HIGH — verified from 3 existing workflow files using identical patterns
- Pitfalls: MEDIUM — Docker-in-Docker question (A4) is unresolved; others are HIGH
- Parity/latency measurement: MEDIUM — stdlib APIs are stable; specific behavior under load is ASSUMED

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 (stable domain)
