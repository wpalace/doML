# Phase 14: CLI Binary Target - Research

**Researched:** 2026-04-14
**Domain:** PyInstaller packaging, argparse CLI, DoML skill/workflow patterns
**Confidence:** MEDIUM-HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: `--onedir` packaging** — PyInstaller spec uses `--onedir`. Produces `dist/predict/` directory containing a `predict` executable. Success criteria reference `dist/predict/predict` (executable inside the directory).
- **D-02: Preprocessed-schema input** — Binary accepts data in the format of `data/processed/preprocessed_*`. Pipeline (ColumnTransformer + model) handles encoding/scaling/imputation internally. `feature_schema` reflects preprocessed column names and types (not raw).
- **D-03: Embed example values at generation time** — When `predict.py` is generated, read the first row of `data/processed/preprocessed_*.csv` and hardcode those values into argparse `--help` strings for each feature.
- **D-04: Classification returns label + probabilities** — `{"prediction": "class_a", "probabilities": {"class_a": 0.85, "class_b": 0.15}}`. Uses `Pipeline.predict()` and `Pipeline.predict_proba()`. Other problem types return `{"prediction": <value>}` only.
- **D-05: Batch output is input columns + prediction column(s)** — `--output <path>` writes CSV mirroring input with `prediction` column appended. Classification also appends `prob_<class>` columns.
- **D-06: Reuse existing jupyter container for PyInstaller build** — Build runs via `docker compose exec jupyter pyinstaller predict.spec`. No separate Dockerfile. Binary targets Linux x86_64. `deployment_metadata.json` records `"platform": "linux-x86_64"`.

### Claude's Discretion

- Exact argparse structure (subcommands vs flat flags)
- Whether to use `argparse.RawDescriptionHelpFormatter` or a custom formatter for feature schema display
- Error message wording for exit codes 1 (input validation) and 2 (model error)
- Whether to detect `--input` path vs JSON string by attempting `json.loads()` first or checking for file existence

### Deferred Ideas (OUT OF SCOPE)

- Windows/macOS binaries — Linux only in v1.4, built in Docker
- Single-file `--onefile` packaging — decided against in favour of `--onedir`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CLI-01 | User can run self-contained binary on Linux with no Python installed | PyInstaller 6.x `--onedir` bundles all Python + dependencies; `dist/predict/predict` is self-contained |
| CLI-02 | Binary accepts single prediction via `--input '{"feature": value}'` (JSON string) | `json.loads()` detection pattern; argparse flat flag design |
| CLI-03 | Binary accepts batch predictions via `--input data.csv` or `--input data.json` | File extension auto-detection; `pandas.read_csv` / `json.load` |
| CLI-04 | Binary accepts `--output <path>` to write batch results | argparse `--output` flag; pandas `.to_csv()` |
| CLI-05 | `--help` displays feature schema (names, types, example values) | Example values hardcoded at generation time from first preprocessed row |
| CLI-06 | Binary exits 0 on success, 1 on input validation error, 2 on model error | `sys.exit()` with try/except blocks separating ValidationError from model errors |
</phase_requirements>

---

## Summary

Phase 14 requires two parallel deliverables: (1) a DoML skill and workflow (`doml-deploy-cli` / `deploy-cli.md`) that generates `predict.py` and `predict.spec` from `deployment_metadata.json`, then invokes the PyInstaller build inside the existing Docker container; and (2) the `predict.py` Python source template that implements the argparse CLI logic.

The most significant infrastructure finding is that **`src/` is not mounted in the Docker container**. The current `docker-compose.yml` only mounts `data/raw`, `data/external`, `.planning`, `data/processed`, `notebooks`, `reports`, and `models`. The PyInstaller build must run inside Docker (per D-06), but `src/<modelname>/vN/` is on the host filesystem. The workflow must add a `src/` writable volume mount to `docker-compose.yml` before the build step — or use `docker cp` to transfer files in and out. Adding the mount is far simpler and consistent with project patterns.

A second critical finding: **PyInstaller is not in `requirements.txt` or `requirements.in`**. It must be added to `requirements.in` and `requirements.txt` regenerated before the Docker image can be rebuilt with it. The workflow plan must include this step (or install it ad-hoc with pip in the container if a rebuild is too disruptive — but ad-hoc violates REPR-04). The correct approach per CLAUDE.md REPR-04 is to add to `requirements.in`, regenerate `requirements.txt`, and rebuild.

**Primary recommendation:** The plan has three natural tasks — (1) add PyInstaller to requirements + update docker-compose.yml + rebuild, (2) build the `predict.py` template and spec file generation logic, (3) build the SKILL.md + workflow that orchestrates everything.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pyinstaller | 6.19.0 | Package Python app + all deps into self-contained binary | Industry standard for Linux binary distribution of Python apps [VERIFIED: pypi.org/pypi/pyinstaller/json] |
| scikit-learn | 1.8.0 | Model inference (Pipeline.predict, predict_proba) | Already in requirements.txt [VERIFIED: codebase] |
| joblib | 1.5.3 | Load .pkl model artifact | Already in requirements.txt [VERIFIED: codebase] |
| argparse | stdlib | CLI argument parsing | Standard library; no additional dependency |
| json | stdlib | JSON string parsing and output serialisation | Standard library |
| pandas | already installed | Batch CSV/JSON input loading, batch output writing | Already in container |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyinstaller-hooks-contrib | latest (bundled with PyInstaller 6.x) | Community hooks for sklearn, joblib, scipy | Auto-installed as PyInstaller dependency; provides hook-sklearn.py |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `--onedir` | `--onefile` | `--onefile` has slower startup (temp-dir extraction on every run), less reliable; D-01 locks `--onedir` |
| pyinstaller | Nuitka | Nuitka compiles to C; harder to set up, longer build time; PyInstaller is simpler and container-ready |
| pyinstaller | shiv/zipapp | shiv/zipapp require Python on target machine; violates CLI-01 |

**Installation (to add to requirements.in):**
```bash
# Add to requirements.in:
pyinstaller

# Regenerate requirements.txt (run in container):
docker compose run --rm jupyter pip-compile requirements.in

# Rebuild image:
docker compose build
```

**Version verified:** PyInstaller 6.19.0 is current stable release (February 2026). [VERIFIED: pypi.org/pypi/pyinstaller/json]

---

## Architecture Patterns

### Recommended Project Structure (generated output)

```
src/
└── <modelname>/
    └── v1/
        ├── deployment_metadata.json    # Phase 13 output + platform field added by this phase
        ├── predict.py                  # Generated argparse CLI (this phase)
        ├── predict.spec                # Generated PyInstaller spec (this phase)
        └── dist/
            └── predict/               # onedir output — entire directory is the artifact
                ├── predict            # executable (no ./ needed if on PATH; run as ./dist/predict/predict)
                └── _internal/         # PyInstaller 6.x places .so files and data here
```

### Pattern 1: predict.py CLI Structure (flat flags, no subcommands)

**What:** Single entry point with `--input` (JSON string or file path), `--output` (optional file), and auto-detection logic.
**When to use:** Simplest UX for single and batch prediction without subcommand overhead.

```python
# Source: [ASSUMED] argparse stdlib pattern

import argparse
import json
import sys
import os
import joblib
import pandas as pd

def load_input(input_str):
    """Detect JSON string vs file path. json.loads() first, then file check."""
    try:
        data = json.loads(input_str)
        return data, 'json_string'
    except (json.JSONDecodeError, ValueError):
        pass
    if os.path.isfile(input_str):
        if input_str.endswith('.csv'):
            return pd.read_csv(input_str), 'csv_file'
        elif input_str.endswith('.json'):
            with open(input_str) as f:
                return json.load(f), 'json_file'
        else:
            raise ValueError(f"Unrecognised file extension: {input_str}")
    raise ValueError(f"Not a valid JSON string or file path: {input_str}")

def main():
    parser = argparse.ArgumentParser(
        description='DoML model inference CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Feature schema:
  age     (int64,   e.g. 35)
  income  (float64, e.g. 52000.0)
  ...
"""
    )
    parser.add_argument('--input', required=True,
                        help='JSON string or path to CSV/JSON file')
    parser.add_argument('--output', default=None,
                        help='Output path for batch results (CSV)')
    args = parser.parse_args()

    try:
        data, input_type = load_input(args.input)
    except ValueError as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        model = joblib.load('best_model.pkl')  # relative path resolved at build time
        # ... prediction logic
    except Exception as e:
        print(f"Model error: {e}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)
```

### Pattern 2: PyInstaller Spec File for --onedir with collect_all

**What:** Spec file that uses `collect_all` to ensure all sklearn/joblib submodules are collected.
**When to use:** Any sklearn Pipeline build — C-extensions in sklearn are not detected by static analysis alone.

```python
# Source: [CITED: pyinstaller.org/en/stable/spec-files.html] + [CITED: pyinstaller-hooks-contrib community patterns]

from PyInstaller.utils.hooks import collect_all

# Collect all submodules, data files, and binaries for sklearn and joblib
sklearn_datas, sklearn_binaries, sklearn_hiddenimports = collect_all('sklearn')
joblib_datas, joblib_binaries, joblib_hiddenimports = collect_all('joblib')

a = Analysis(
    ['predict.py'],
    pathex=[],
    binaries=sklearn_binaries + joblib_binaries,
    datas=sklearn_datas + joblib_datas,
    hiddenimports=sklearn_hiddenimports + joblib_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # REQUIRED for onedir mode
    name='predict',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='predict',   # produces dist/predict/ directory
)
```

**Key points:**
- `exclude_binaries=True` on EXE is required for onedir; if False it becomes onefile [CITED: PyInstaller docs]
- `COLLECT` is what creates the `dist/predict/` directory; without it, no output directory is produced [CITED: PyInstaller docs]
- `collect_all()` returns a 3-tuple: `(datas, binaries, hiddenimports)` [VERIFIED: WebSearch, pyinstaller-hooks-contrib]

### Pattern 3: exit code separation

**What:** Two try/except blocks — inner for input parsing (exit 1), outer for model execution (exit 2).

```python
# Source: [ASSUMED] standard Unix CLI exit code convention

def main():
    try:
        data, input_type = load_input(args.input)
    except (ValueError, KeyError, pd.errors.ParserError) as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)   # CLI-06: exit 1 = input validation error

    try:
        result = run_prediction(model, data, problem_type)
    except Exception as e:
        print(f"Model error: {e}", file=sys.stderr)
        sys.exit(2)   # CLI-06: exit 2 = model error

    # Output result
    print(json.dumps(result, default=str))
    sys.exit(0)       # CLI-06: exit 0 = success
```

### Pattern 4: model file path in predict.py

**What:** The model file (`best_model.pkl`) must be accessible at binary runtime. For a PyInstaller binary, it needs to be either bundled as a data file or resolved from a known relative location.

**Approach:** Since the workflow generates `predict.py` and the spec, the workflow can write the model relative path into `predict.py` as a constant at generation time:

```python
# Injected at predict.py generation time by the workflow
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'models', 'best_model.pkl')
```

Or more reliably, bundle the model as a data file via the spec:

```python
# In spec file:
datas = sklearn_datas + joblib_datas + [('../../../models/best_model.pkl', '.')]
```

Then in predict.py, use `sys._MEIPASS` for bundled data (PyInstaller sets this for --onefile; for --onedir the `_internal/` dir is alongside the executable):

```python
# Source: [CITED: PyInstaller docs] + [ASSUMED: onedir resolution]
import sys, os
if getattr(sys, 'frozen', False):
    # Running as compiled binary (onedir: _MEIPASS is dist/predict/_internal or dist/predict)
    base = sys._MEIPASS
else:
    # Running as plain Python
    base = os.path.dirname(__file__)
model = joblib.load(os.path.join(base, 'best_model.pkl'))
```

**Decision for planner:** Bundling the model inside the binary is more portable (CLI-01 — runs on Linux machine with no Python). The workflow spec datas list must include the model file. [ASSUMED — exact sys._MEIPASS path for onedir; planner should verify with a test build]

### Anti-Patterns to Avoid

- **Using `--onefile` instead of `--onedir`:** Locked to `--onedir` per D-01; `--onefile` is slower on startup.
- **Omitting `collect_all` for sklearn:** sklearn uses C-extensions and dynamic imports that static analysis misses. Without `collect_all`, the binary will fail at runtime with `ModuleNotFoundError: No module named 'sklearn.utils._typedefs'`. [VERIFIED: github.com/pyinstaller/pyinstaller-hooks-contrib/issues/456]
- **Building from host with local Python:** The binary must be Linux x86_64 (D-06). Build inside the container ensures architecture match.
- **Hardcoding absolute paths in predict.py:** REPR-02 applies; use `sys._MEIPASS` / `os.path.dirname(__file__)` or bundle the model as a data file.
- **Missing `exclude_binaries=True` on EXE:** Without this, COLLECT has nothing to gather and the build may produce wrong output or switch to onefile mode.
- **Running PyInstaller without src/ mounted in Docker:** `src/` is not in `docker-compose.yml` volumes. If not mounted, `docker compose exec jupyter` cannot see or write `src/<modelname>/vN/`. The workflow MUST either add the mount or use `docker cp`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Collecting sklearn submodules | Manually list hiddenimports | `collect_all('sklearn')` in spec | sklearn has 50+ C-extension submodules; hand-lists go stale with sklearn version upgrades |
| Collecting joblib submodules | Manually list hiddenimports | `collect_all('joblib')` in spec | Same issue; joblib is dynamically imported by sklearn |
| Binary cross-platform builds | Custom Dockerfile | Existing jupyter container | D-06 locks this; container already has sklearn/joblib installed |
| JSON output serialisation | Custom serialiser | `json.dumps(result, default=str)` | numpy types (float32, int64) are not JSON-serialisable by default; `default=str` handles them |

**Key insight:** PyInstaller's `collect_all` function exists precisely because ML packages have non-obvious dynamic import trees. Using it is the entire solution to the hidden imports problem.

---

## Common Pitfalls

### Pitfall 1: `src/` Not Mounted in Docker Container

**What goes wrong:** The workflow calls `docker compose exec jupyter bash -c "cd src/<modelname>/vN && pyinstaller predict.spec"` but `src/` has no corresponding Docker volume mount. The `exec` command will fail with `bash: cd: src/...: No such file or directory`.

**Why it happens:** `docker-compose.yml` only mounts `data/raw`, `data/external`, `.planning`, `data/processed`, `notebooks`, `reports`, `models`. `src/` was added by Phase 14 and was never added to the volume config.

**How to avoid:** The workflow (or a prerequisite plan) must add `./src:/home/jovyan/work/src` to docker-compose.yml volumes before attempting the PyInstaller build. This requires a container restart. [VERIFIED: codebase read of docker-compose.yml]

**Warning signs:** `docker compose exec jupyter ls` shows no `src/` directory.

### Pitfall 2: PyInstaller Not Installed in Container

**What goes wrong:** `pyinstaller --version` fails inside the container with `bash: pyinstaller: command not found`.

**Why it happens:** PyInstaller is not in `requirements.in` or `requirements.txt`. [VERIFIED: codebase grep]

**How to avoid:** Add `pyinstaller` to `requirements.in`, regenerate `requirements.txt` via `docker compose run --rm jupyter pip-compile requirements.in`, and rebuild the image. REPR-04 forbids hand-running pip without updating requirements.in.

**Warning signs:** First step of workflow should verify with `docker compose exec jupyter pyinstaller --version`.

### Pitfall 3: sklearn C-Extensions Missing from Binary

**What goes wrong:** Binary runs but crashes at predict time with `ModuleNotFoundError: No module named 'sklearn.utils._typedefs'` or similar.

**Why it happens:** PyInstaller static analysis cannot detect C-extension submodules that sklearn imports via Cython at runtime.

**How to avoid:** Use `collect_all('sklearn')` and `collect_all('joblib')` in the spec file. Keep `pyinstaller-hooks-contrib` updated — it contains fixes for sklearn as sklearn releases new versions. [VERIFIED: github.com/pyinstaller/pyinstaller-hooks-contrib/issues/456 — patches merged for sklearn 1.1.1+]

**Warning signs:** Binary runs but fails on the first `model.predict()` call.

### Pitfall 4: model.pkl Not Available at Runtime

**What goes wrong:** Binary crashes with `FileNotFoundError: No such file or directory: '.../best_model.pkl'`.

**Why it happens:** The model file is on the host's `models/` directory, which is accessible in the container but not inside the frozen binary.

**How to avoid:** Either (a) bundle the model file as a data file in the spec's `datas` list, or (b) resolve the model path relative to the binary's location at runtime using `sys._MEIPASS`. Bundling is cleaner for distribution (CLI-01: runs on machine with no Python installed — `models/` won't exist there).

**Warning signs:** Works when run from the project directory but fails when copied elsewhere.

### Pitfall 5: numpy/pandas dtype not JSON-serialisable

**What goes wrong:** `json.dumps(result)` raises `TypeError: Object of type float32 is not JSON serializable`.

**Why it happens:** sklearn returns numpy typed values (float32, int64, etc.) which standard `json` cannot serialise.

**How to avoid:** Pass `default=str` or convert with `.item()` before serialisation:
```python
def json_safe(obj):
    if hasattr(obj, 'item'):
        return obj.item()
    raise TypeError(f"Not serializable: {type(obj)}")
print(json.dumps(result, default=json_safe))
```
[ASSUMED — standard pattern for numpy/sklearn output]

### Pitfall 6: onedir Binary Run Path

**What goes wrong:** User runs `./dist/predict` (the directory) instead of `./dist/predict/predict` (the executable inside).

**Why it happens:** `--onedir` produces a directory `dist/predict/`, and the actual executable is `dist/predict/predict` (same name as directory). This confuses users expecting a single file.

**How to avoid:** Success criterion SC-3 says "produces `src/<modelname>/v1/dist/predict`" — the plan's confirmation message must show the exact executable path `dist/predict/predict`. Document clearly in workflow output.

### Pitfall 7: Container Restart Required After docker-compose.yml Change

**What goes wrong:** After adding `src/` to docker-compose.yml, the currently-running container still doesn't see `src/`.

**Why it happens:** Volume mounts take effect only on container (re)start.

**How to avoid:** The workflow step that modifies docker-compose.yml must also restart the container: `docker compose down && docker compose up -d`, then wait for readiness before the PyInstaller step.

---

## Code Examples

Verified patterns from official sources:

### Full predict.py Template Structure

```python
# Source: [ASSUMED] — standard argparse + joblib CLI pattern for sklearn models

#!/usr/bin/env python3
"""
DoML prediction CLI — generated by /doml-deploy-cli
Model: {model_name}
Deployment: {version}
Platform: linux-x86_64
"""

import argparse
import json
import os
import sys

import joblib
import pandas as pd

# --- Injected at generation time ---
PROBLEM_TYPE = "{problem_type}"   # regression | classification | clustering
FEATURE_SCHEMA = {feature_schema_json}  # [{"name": "age", "type": "int64"}, ...]
MODEL_NAME = "{model_name}"

# --- Model loading ---
if getattr(sys, 'frozen', False):
    _BASE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_BASE, 'best_model.pkl')


def _feature_help_epilog():
    lines = ["\nFeature schema:"]
    for f in FEATURE_SCHEMA:
        lines.append(f"  {f['name']:<20} ({f['type']:<10}, e.g. {f['example']})")
    return "\n".join(lines)


def _parse_args():
    parser = argparse.ArgumentParser(
        description=f"DoML model inference — {MODEL_NAME}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_feature_help_epilog(),
    )
    parser.add_argument(
        "--input", required=True,
        help="JSON string '{\"feat\": val}' or path to CSV/JSON file"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path for batch predictions (CSV); if omitted, prints to stdout"
    )
    return parser.parse_args()


def _load_input(input_str):
    """Attempt json.loads() first; fall back to file path detection."""
    try:
        parsed = json.loads(input_str)
        # Single dict -> single prediction; list -> batch
        if isinstance(parsed, dict):
            return pd.DataFrame([parsed]), 'single'
        elif isinstance(parsed, list):
            return pd.DataFrame(parsed), 'batch'
        else:
            raise ValueError("JSON input must be an object or array")
    except (json.JSONDecodeError, ValueError) as e:
        if not os.path.isfile(input_str):
            raise ValueError(
                f"Input is not valid JSON and not a file path: {input_str}"
            ) from e
    # File path
    ext = os.path.splitext(input_str)[1].lower()
    if ext == '.csv':
        return pd.read_csv(input_str), 'batch'
    elif ext == '.json':
        with open(input_str) as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return pd.DataFrame(data), 'batch'
        return pd.DataFrame([data]), 'single'
    else:
        raise ValueError(f"Unsupported file extension '{ext}'; use .csv or .json")


def _format_single(prediction, model, problem_type):
    result = {}
    if problem_type in ('regression', 'time_series'):
        result['prediction'] = prediction[0].item() if hasattr(prediction[0], 'item') else prediction[0]
    elif problem_type in ('classification', 'binary_classification', 'multiclass_classification'):
        label = prediction[0]
        result['prediction'] = label.item() if hasattr(label, 'item') else label
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(None)  # placeholder — df passed separately
            classes = model.classes_
            result['probabilities'] = {
                str(c): round(float(p), 6)
                for c, p in zip(classes, proba[0])
            }
    else:
        result['prediction'] = prediction[0].item() if hasattr(prediction[0], 'item') else prediction[0]
    return result


def main():
    args = _parse_args()

    # --- Input validation (exit 1) ---
    try:
        df, input_mode = _load_input(args.input)
    except (ValueError, pd.errors.ParserError, json.JSONDecodeError) as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)

    feature_names = [f['name'] for f in FEATURE_SCHEMA]
    missing = set(feature_names) - set(df.columns)
    if missing:
        print(f"Input error: missing required features: {sorted(missing)}", file=sys.stderr)
        sys.exit(1)

    # --- Model execution (exit 2) ---
    try:
        model = joblib.load(MODEL_PATH)
        predictions = model.predict(df[feature_names])
        probas = None
        if PROBLEM_TYPE in ('classification', 'binary_classification', 'multiclass_classification'):
            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba(df[feature_names])
    except Exception as e:
        print(f"Model error: {e}", file=sys.stderr)
        sys.exit(2)

    # --- Output ---
    if input_mode == 'single':
        result = {'prediction': predictions[0].item() if hasattr(predictions[0], 'item') else predictions[0]}
        if probas is not None:
            result['probabilities'] = {
                str(c): round(float(p), 6)
                for c, p in zip(model.classes_, probas[0])
            }
        print(json.dumps(result))
    else:
        out_df = df.copy()
        out_df['prediction'] = predictions
        if probas is not None:
            for i, c in enumerate(model.classes_):
                out_df[f'prob_{c}'] = probas[:, i]
        if args.output:
            out_df.to_csv(args.output, index=False)
            print(f"Batch results written to {args.output}")
        else:
            print(out_df.to_csv(index=False))

    sys.exit(0)


if __name__ == '__main__':
    main()
```

### predict.spec Template

```python
# Source: [CITED: pyinstaller.org spec-files docs] + [CITED: pyinstaller-hooks-contrib issue #456]

from PyInstaller.utils.hooks import collect_all

sklearn_datas, sklearn_binaries, sklearn_hiddenimports = collect_all('sklearn')
joblib_datas,  joblib_binaries,  joblib_hiddenimports  = collect_all('joblib')

a = Analysis(
    ['predict.py'],
    pathex=[],
    binaries=sklearn_binaries + joblib_binaries,
    datas=sklearn_datas + joblib_datas + [('best_model.pkl', '.')],
    hiddenimports=sklearn_hiddenimports + joblib_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='predict',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='predict',
)
```

### PyInstaller Build Invocation (inside container)

```bash
# After src/ is mounted and docker-compose.yml updated:
docker compose exec jupyter bash -c "
  cd /home/jovyan/work/src/{MODEL_SLUG}/v{VERSION} && \
  pyinstaller predict.spec --distpath dist --workpath /tmp/pyinstaller-work --clean
"
```

Notes:
- `--distpath dist` ensures output is `src/<model>/vN/dist/predict/predict`
- `--workpath /tmp/pyinstaller-work` keeps build artifacts out of `src/` [ASSUMED]
- `--clean` clears cached previous build to avoid stale artifacts [ASSUMED]

### docker-compose.yml Addition Required

```yaml
# Add to volumes section in docker-compose.yml:
volumes:
  # ... existing mounts ...
  - ./src:/home/jovyan/work/src   # Phase 14: deployment target output
```

After this change: `docker compose down && docker compose up -d`

### deployment_metadata.json Update (after successful build)

```python
import json
from pathlib import Path

meta_path = Path(f'src/{MODEL_SLUG}/v{VERSION}/deployment_metadata.json')
with open(meta_path) as f:
    meta = json.load(f)
meta['platform'] = 'linux-x86_64'
with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| PyInstaller 5.x: data files in `dist/predict/` directly | PyInstaller 6.x: data files in `dist/predict/_internal/` | PyInstaller 6.0 (2023) | `sys._MEIPASS` still works; `_internal/` is the bundle root for onedir in v6 |
| Manual `hiddenimports` list for sklearn | `collect_all('sklearn')` + updated hooks-contrib | Ongoing (hooks-contrib fixes merged incrementally) | No manual maintenance of import lists needed |
| `pyinstaller-hooks-contrib` as separate package | Bundled with PyInstaller 5+ | PyInstaller 5.0 | Auto-updated with PyInstaller; no separate install needed |

**Deprecated/outdated:**
- `sklearn.externals.joblib`: removed in sklearn 0.23; use standalone `joblib` package directly (already in requirements.txt)
- `--onefile` mode for ML models: discouraged due to startup latency from temp-dir extraction on each run; `--onedir` is the modern default for performance-sensitive use

---

## Infrastructure Gap: src/ Volume Mount

> This is the single most likely plan-blocking issue. It must be addressed before the PyInstaller build step.

**Current state:** `docker-compose.yml` has no `./src` volume mount.
**Required state:** `./src:/home/jovyan/work/src` added under `volumes` in the `jupyter` service.
**Impact of missing:** `docker compose exec jupyter bash -c "cd src/..."` will fail; PyInstaller cannot see or write `src/`.
**Plan action required:** A task (likely Wave 0 or Plan 1 Step 1) must: (1) read docker-compose.yml, (2) add the src mount, (3) restart the container.

---

## Skill and Workflow Structure

The new skill must follow the established DoML pattern exactly. Based on reading `doml-deploy-model` (SKILL.md + deploy-model.md) and `doml-anomaly-detection`:

### SKILL.md for `/doml-deploy-cli`

Required fields:
```yaml
---
name: doml-deploy-cli
description: "Generate predict.py and predict.spec for the CLI binary target, run PyInstaller inside the jupyter container, and produce dist/predict/predict. Reads src/<modelname>/vN/deployment_metadata.json (from /doml-deploy-model)."
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
...numbered list of steps...
</objective>

<execution_context>
@.claude/doml/workflows/deploy-cli.md
</execution_context>

<context>
Arguments (optional): $ARGUMENTS
</context>

<process>
Execute the deploy-cli workflow from @.claude/doml/workflows/deploy-cli.md end-to-end.
</process>
```

### deploy-cli.md Workflow Structure

Recommended step sequence:
1. Validate project state (STATE.md exists)
2. Locate `deployment_metadata.json` — find latest `src/*/v*/deployment_metadata.json` with `target: cli_binary`
3. Read feature_schema, model_file, model_name, version from metadata
4. Read first row of `data/processed/preprocessed_*.csv` for example values
5. Verify PyInstaller installed (`docker compose exec jupyter pyinstaller --version`)
6. Verify `src/` mounted in docker-compose.yml; if missing, add mount and restart container
7. Generate `predict.py` from template (inject feature_schema, model_name, problem_type, example values, model path)
8. Generate `predict.spec` from template (inject script path, model file path for datas)
9. Run PyInstaller build: `docker compose exec jupyter bash -c "cd src/.../vN && pyinstaller predict.spec ..."`
10. Verify `dist/predict/predict` exists and is executable
11. Update `deployment_metadata.json` with `"platform": "linux-x86_64"`
12. Update STATE.md
13. Confirm with summary of output path

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `sys._MEIPASS` is the correct mechanism to locate bundled files in PyInstaller 6.x onedir builds | Code Examples | Model file won't load at binary runtime; fix: adjust path resolution |
| A2 | `--workpath /tmp/pyinstaller-work` and `--clean` flags are valid on the `pyinstaller` CLI | Code Examples | Build command syntax error; fix: remove unknown flags |
| A3 | `default=str` / `.item()` reliably handles all numpy dtype serialisation cases | Code Examples | JSON output may include non-serialisable values; fix: use numpy's `float()` cast instead |
| A4 | The model pkl file should be bundled inside the binary via spec `datas` (not resolved from host `models/` at runtime) | Architecture Patterns | If resolved from host, binary fails when run on a machine without the project; CLI-01 requires standalone operation |
| A5 | PyInstaller 6.x `_internal/` placement of data files is transparent to `sys._MEIPASS` | State of the Art | If `sys._MEIPASS` doesn't point to `_internal/`, model load path breaks |

---

## Open Questions (RESOLVED)

1. **Model file bundling vs runtime path resolution**
   - What we know: `models/best_model.pkl` is on the host, accessible inside the container via the `models/` volume mount
   - What's unclear: Whether it's better to (a) include the model in the spec `datas` (self-contained binary, CLI-01 satisfied) or (b) have `predict.py` load from `../../../models/best_model.pkl` relative to `dist/predict/predict` (simpler spec, but binary is not portable)
   - Recommendation: Bundle the model in the binary (`datas` entry in spec) for CLI-01 compliance. The planner should note this adds model file size to the binary.
   - RESOLVED: Plan 02 bundles the model via `datas=[('{model_rel}', '.')]` in predict.spec and predict.py loads via `sys._MEIPASS` at runtime. Binary is fully self-contained per CLI-01.

2. **Container restart disruption**
   - What we know: Adding `src/` volume mount requires `docker compose down && docker compose up -d`
   - What's unclear: Whether the user has other services or notebooks open that a restart would interrupt
   - Recommendation: The workflow step should warn the user before restarting and confirm the restart is acceptable.
   - RESOLVED: Plan 02 workflow Step 5 checks for the `src/` mount and halts with user instructions if missing — no automatic restart is performed. The user decides when to restart.

3. **PyInstaller version pinning**
   - What we know: Current latest is 6.19.0; `pyinstaller-hooks-contrib` is bundled
   - What's unclear: Whether to pin `pyinstaller==6.19.0` in requirements.in or leave unpinned
   - Recommendation: Pin to `pyinstaller==6.19.0` per REPR-04 (all deps pinned with `==`). Regenerate requirements.txt after adding.
   - RESOLVED: Plan 01 Task 2 adds `pyinstaller` unpinned to `requirements.in` per CLAUDE.md REPR-04 — `requirements.in` holds top-level deps unpinned, `pip-compile` generates the pinned `requirements.txt`. The workflow instructs the user to run `pip-compile` and rebuild, which pins the version.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker (docker compose) | PyInstaller build inside container | Unknown (container not running during research) | — | None — build requires container per D-06 |
| PyInstaller | CLI binary build | NOT FOUND in requirements.txt/requirements.in | — | Must add to requirements.in and rebuild image |
| scikit-learn | Model inference | Available in container | 1.8.0 | — |
| joblib | Model pkl loading | Available in container | 1.5.3 | — |
| pandas | Batch input/output | Available in container | (installed) | — |
| `./src` volume mount | PyInstaller writes to src/ | NOT PRESENT in docker-compose.yml | — | Must add mount and restart container |

**Missing dependencies with no fallback:**
- PyInstaller: must be added to requirements.in, requirements.txt regenerated, Docker image rebuilt
- `src/` volume mount: must be added to docker-compose.yml and container restarted

**Missing dependencies with fallback:**
- None identified for the fallback category

---

## Validation Architecture

> `nyquist_validation: true` in .planning/config.json — this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | None found — see Wave 0 |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CLI-01 | Binary is self-contained Linux executable | smoke | `test -f src/*/v*/dist/predict/predict && file src/*/v*/dist/predict/predict \| grep -q ELF` | No — Wave 0 |
| CLI-02 | Binary accepts JSON string input | integration | `./dist/predict/predict --input '{"age": 35}' \| python3 -c "import json,sys; d=json.load(sys.stdin); assert 'prediction' in d"` | No — Wave 0 |
| CLI-03 | Binary accepts CSV and JSON file input | integration | pytest test with temp file fixtures | No — Wave 0 |
| CLI-04 | Binary writes batch output to `--output` file | unit/integration | pytest test asserting output CSV exists and has prediction column | No — Wave 0 |
| CLI-05 | `--help` shows feature names, types, example values | unit | `./dist/predict/predict --help \| grep -q "e.g."` | No — Wave 0 |
| CLI-06 | Exit codes 0/1/2 | unit | pytest test checking subprocess returncode for valid/invalid input/model error | No — Wave 0 |

Note: CLI-01 requires a running binary — this is an integration/smoke test that requires the build to have completed. Unit tests for predict.py logic can run without the binary using plain Python.

### Wave 0 Gaps

- [ ] `tests/test_predict_cli.py` — pytest tests for predict.py logic (exit codes, input parsing, output format) — covers CLI-02 through CLI-06
- [ ] `tests/conftest.py` — shared fixtures: dummy sklearn Pipeline, sample preprocessed CSV
- [ ] No test for CLI-01 can run in automated pre-commit (requires Docker build); mark as manual smoke test in plan

---

## Security Domain

> `security_enforcement` absent from config.json — treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — CLI binary, no auth |
| V3 Session Management | No | N/A — CLI binary, stateless |
| V4 Access Control | No | N/A — CLI binary |
| V5 Input Validation | Yes | argparse type checking + explicit feature name validation before model call |
| V6 Cryptography | No | No keys/secrets in scope |

### Known Threat Patterns for CLI Binary

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `--input` file path | Tampering | `os.path.isfile()` check; do not pass user-supplied path to shell commands |
| Pickle deserialization (joblib.load) | Tampering | Model file path is hardcoded at build time from trusted source; never accept model path from user input |
| JSON injection in `--input` string | Tampering | `json.loads()` safely parses; output is JSON not executed |

**Note:** The model is loaded from a path determined at build time (bundled or set at generation). Never expose a `--model` flag to end users of the binary — that would allow arbitrary pickle loading. [ASSUMED — standard security guidance for ML binaries]

---

## Sources

### Primary (HIGH confidence)
- Codebase read: `docker-compose.yml` — confirmed `src/` not mounted [VERIFIED: codebase]
- Codebase read: `requirements.in`, `requirements.txt` — confirmed PyInstaller absent [VERIFIED: codebase]
- Codebase read: `deploy-model.md` — confirmed `feature_schema` format, directory structure, integration points [VERIFIED: codebase]
- PyPI JSON API: `pypi.org/pypi/pyinstaller/json` — confirmed version 6.19.0 [VERIFIED]

### Secondary (MEDIUM confidence)
- `github.com/pyinstaller/pyinstaller-hooks-contrib/issues/456` — sklearn hidden import resolution via hooks-contrib [CITED]
- WebSearch: PyInstaller `collect_all()` function signature and usage in spec files [VERIFIED via multiple sources]
- WebSearch: PyInstaller 6.x onedir spec structure (`exclude_binaries=True`, COLLECT required) [VERIFIED via docs references]

### Tertiary (LOW confidence)
- `sys._MEIPASS` path resolution for onedir in PyInstaller 6.x — training knowledge, docs inaccessible (403) [ASSUMED]
- `--workpath` and `--clean` CLI flags — training knowledge [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — package versions verified from codebase and PyPI
- Architecture: MEDIUM — spec file pattern verified via multiple sources; predict.py pattern is ASSUMED standard practice
- Pitfalls: HIGH — `src/` mount gap and missing PyInstaller are VERIFIED from codebase; sklearn hidden imports VERIFIED from hooks-contrib issue

**Research date:** 2026-04-14
**Valid until:** 2026-05-14 (PyInstaller and sklearn versions stable; hooks-contrib patches additive)
