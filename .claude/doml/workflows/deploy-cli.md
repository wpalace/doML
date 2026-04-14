# DoML Deploy CLI Workflow

## Purpose
Generate predict.py and predict.spec, run PyInstaller inside the Jupyter Docker container, and
produce src/<modelname>/vN/dist/predict/predict — a self-contained Linux binary requiring no
Python on the target machine.

## Invoked by: /doml-deploy-cli [--deploy-dir src/<modelname>/vN]

## Workflow

### Step 1 — Validate project state

Read `.planning/STATE.md`. If it does not exist, display and stop:
```
No DoML project found. Run /doml-new-project first.
```

### Step 2 — Locate deployment directory

Parse `--deploy-dir` flag from `$ARGUMENTS`:
```bash
DEPLOY_DIR=""
if echo "$ARGUMENTS" | grep -q -- '--deploy-dir'; then
  DEPLOY_DIR=$(echo "$ARGUMENTS" | sed 's/.*--deploy-dir[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi
```

If `DEPLOY_DIR` is empty, find the most recent deployment directory:
```bash
if [ -z "$DEPLOY_DIR" ]; then
  DEPLOY_DIR=$(python3 -c "
import glob, re, sys, os
dirs = glob.glob('src/*/*')
versioned = [(d, int(re.search(r'/v(\d+)$', d).group(1))) for d in dirs if re.search(r'/v(\d+)$', d) and os.path.isfile(d + '/deployment_metadata.json')]
if not versioned:
    print('')
else:
    latest = sorted(versioned, key=lambda x: x[1], reverse=True)[0][0]
    print(latest)
")
  if [ -z "$DEPLOY_DIR" ]; then
    echo "No deployment directory found. Run /doml-deploy-model first."
    exit 1
  fi
  echo "Using deployment directory: $DEPLOY_DIR"
fi
```

Validate the deployment directory exists and contains deployment_metadata.json:
```bash
if [ ! -f "$DEPLOY_DIR/deployment_metadata.json" ]; then
  echo "deployment_metadata.json not found in $DEPLOY_DIR"
  echo "Run /doml-deploy-model first to scaffold the deployment directory."
  exit 1
fi
```

### Step 3 — Read deployment_metadata.json

```bash
python3 -c "
import json, sys, os

deploy_dir = '${DEPLOY_DIR}'
with open(deploy_dir + '/deployment_metadata.json') as f:
    meta = json.load(f)

model_file = meta.get('model_file', 'models/best_model.pkl')
model_name = meta.get('model_name', 'model')
version = meta.get('version', 'v1')
feature_schema = meta.get('feature_schema', [])
target = meta.get('target', 'cli_binary')

if target != 'cli_binary':
    print(f'ERROR: deployment_metadata.json target is \"{target}\", not \"cli_binary\".')
    print('This deployment was not created for the CLI target.')
    print('Run /doml-deploy-model and select \"CLI binary\" to create a CLI deployment.')
    sys.exit(1)

# Write env vars to a temp file for shell to read
with open('/tmp/doml_cli_meta.sh', 'w') as f:
    f.write(f'MODEL_FILE=\"{model_file}\"\n')
    f.write(f'MODEL_NAME=\"{model_name}\"\n')
    f.write(f'VERSION=\"{version}\"\n')
    f.write(f'FEATURE_SCHEMA_JSON={json.dumps(json.dumps(feature_schema))}\n')

print(f'Model: {model_name} ({model_file}), version: {version}')
print(f'Feature schema: {len(feature_schema)} features')
"
if [ $? -ne 0 ]; then exit 1; fi
source /tmp/doml_cli_meta.sh
```

Read problem_type from config.json:
```bash
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
echo "Problem type: $PROBLEM_TYPE"
```

### Step 4 — Read example values from first preprocessed row (D-03)

```bash
python3 -c "
import glob, json, sys

processed_files = sorted(glob.glob('data/processed/preprocessed_*'))
feature_schema = json.loads('${FEATURE_SCHEMA_JSON}')

if processed_files:
    import pandas as pd
    df = pd.read_csv(processed_files[0], nrows=1)
    if len(df) == 0:
        # No data rows — fall back to type-based placeholders
        examples = {f['name']: ('0' if 'int' in f['type'] else '0.0' if 'float' in f['type'] else 'value') for f in feature_schema}
    else:
        first_row = df.iloc[0]
        examples = {}
        for f in feature_schema:
            col = f['name']
            if col in first_row.index:
                val = first_row[col]
                examples[col] = str(val.item() if hasattr(val, 'item') else val)
            else:
                examples[col] = '0'
else:
    examples = {f['name']: ('0' if 'int' in f['type'] else '0.0' if 'float' in f['type'] else 'value') for f in feature_schema}

# Merge examples into feature_schema
enriched = []
for f in feature_schema:
    enriched.append({'name': f['name'], 'type': f['type'], 'example': examples.get(f['name'], '0')})

print(json.dumps(enriched))
" > /tmp/doml_feature_schema_enriched.json
if [ $? -ne 0 ]; then
  echo "Failed to read example values from preprocessed data."
  exit 1
fi
ENRICHED_SCHEMA=$(cat /tmp/doml_feature_schema_enriched.json)
echo "Example values loaded."
```

### Step 5 — Check src/ volume mount and pyinstaller availability

Check that docker-compose.yml has the src/ volume mount:
```bash
if ! grep -q "./src:/home/jovyan/work/src" docker-compose.yml 2>/dev/null; then
  echo ""
  echo "SETUP REQUIRED: The src/ directory is not mounted in your Docker container."
  echo ""
  echo "Add this line to the volumes: block in docker-compose.yml (after the models mount):"
  echo "      - ./src:/home/jovyan/work/src"
  echo ""
  echo "Then run: docker compose down && docker compose up -d"
  echo ""
  echo "Re-run /doml-deploy-cli after the container restarts."
  exit 1
fi
```

Check that the container is running:
```bash
if ! docker compose ps jupyter 2>/dev/null | grep -q "Up\|running"; then
  echo "Jupyter container is not running. Start it with: docker compose up -d"
  exit 1
fi
```

Check pyinstaller is available in the container:
```bash
if ! docker compose exec jupyter pyinstaller --version 2>/dev/null; then
  echo ""
  echo "SETUP REQUIRED: pyinstaller is not installed in the Docker container."
  echo ""
  echo "1. Add 'pyinstaller' to requirements.in"
  echo "2. Run: docker compose run --rm jupyter pip-compile requirements.in"
  echo "3. Run: docker compose build"
  echo "4. Run: docker compose up -d"
  echo ""
  echo "Re-run /doml-deploy-cli after the image is rebuilt."
  exit 1
fi
echo "PyInstaller available in container."
```

### Step 6 — Generate predict.py

Derive the container path for the deployment directory (host ./src maps to /home/jovyan/work/src):
```bash
DEPLOY_DIR_CONTAINER="/home/jovyan/work/$(echo "$DEPLOY_DIR" | sed 's|^\./||')"
```

Read the enriched schema into Python for embedding:
```bash
python3 << 'PYEOF'
import json, os, sys

deploy_dir = os.environ.get('DEPLOY_DIR', '')
problem_type = os.environ.get('PROBLEM_TYPE', 'regression')
model_name = os.environ.get('MODEL_NAME', 'model')
version = os.environ.get('VERSION', 'v1')

with open('/tmp/doml_feature_schema_enriched.json') as f:
    enriched_schema = json.load(f)

# Build the feature schema epilog lines for argparse RawDescriptionHelpFormatter
epilog_lines = ["\nFeature schema (preprocessed-schema format):"]
for feat in enriched_schema:
    epilog_lines.append(f"  {feat['name']:<24} ({feat['type']:<12}  e.g. {feat['example']})")
epilog_lines.append("")
epilog_lines.append("Input must be in preprocessed format (same columns as data/processed/preprocessed_*).")
epilog_lines.append("The model pipeline handles encoding and scaling internally.")
feature_help_epilog = "\n".join(epilog_lines)

predict_py = f'''#!/usr/bin/env python3
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

# --- Injected at generation time (D-02, D-03) ---
PROBLEM_TYPE = {json.dumps(problem_type)}
MODEL_NAME = {json.dumps(model_name)}
FEATURE_SCHEMA = {json.dumps(enriched_schema)}

# --- Model loading (D-06, Pitfall 4) ---
# Bundle best_model.pkl as data file in spec; load from _MEIPASS when frozen
if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_BASE, "best_model.pkl")


def _feature_help_epilog():
    lines = ["\\nFeature schema (preprocessed-schema format):"]
    for feat in FEATURE_SCHEMA:
        lines.append(f"  {{feat[\\'name\\']:<24}} ({{feat[\\'type\\']:<12}}  e.g. {{feat[\\'example\\']}})")
    lines.append("")
    lines.append("Input must be in preprocessed format (same columns as data/processed/preprocessed_*).")
    lines.append("The model pipeline handles encoding and scaling internally.")
    return "\\n".join(lines)


def _parse_args():
    parser = argparse.ArgumentParser(
        description=f"DoML model inference — {{MODEL_NAME}}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_feature_help_epilog(),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="JSON string \\'{{\\\"feature\\\": value}}\\' or path to .csv / .json file",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path for batch predictions (CSV); if omitted, prints JSON to stdout",
    )
    return parser.parse_args()


def _load_input(input_str):
    """Attempt json.loads() first; fall back to file path detection (Specifics note)."""
    try:
        parsed = json.loads(input_str)
        if isinstance(parsed, dict):
            return pd.DataFrame([parsed]), "single"
        elif isinstance(parsed, list):
            return pd.DataFrame(parsed), "batch"
        else:
            raise ValueError("JSON input must be an object or array of objects")
    except (json.JSONDecodeError, ValueError) as json_err:
        if not os.path.isfile(input_str):
            raise ValueError(
                f"Input is neither valid JSON nor an existing file path: {{input_str}}"
            ) from json_err

    ext = os.path.splitext(input_str)[1].lower()
    if ext == ".csv":
        return pd.read_csv(input_str), "batch"
    elif ext == ".json":
        with open(input_str) as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return pd.DataFrame(data), "batch"
        return pd.DataFrame([data]), "single"
    else:
        raise ValueError(f"Unsupported file extension \\'{{ext}}\\'; use .csv or .json")


def _json_safe(obj):
    """Convert numpy scalars to Python native types for JSON serialisation (Pitfall 5)."""
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(f"Not JSON serialisable: {{type(obj)}}")


def main():
    args = _parse_args()

    # --- Input validation (CLI-06: exit 1) ---
    try:
        df, input_type = _load_input(args.input)
    except (ValueError, KeyError, pd.errors.ParserError) as e:
        print(f"Input error: {{e}}", file=sys.stderr)
        sys.exit(1)

    # --- Model execution (CLI-06: exit 2) ---
    try:
        model = joblib.load(MODEL_PATH)
        predictions = model.predict(df)
        proba = None
        if PROBLEM_TYPE in ("classification", "binary_classification", "multiclass_classification"):
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(df)
    except Exception as e:
        print(f"Model error: {{e}}", file=sys.stderr)
        sys.exit(2)

    # --- Format output (D-04, D-05) ---
    if input_type == "single":
        result = {{}}
        val = predictions[0]
        result["prediction"] = val.item() if hasattr(val, "item") else val
        if proba is not None:
            classes = model.classes_
            result["probabilities"] = {{
                str(cls): float(p)
                for cls, p in zip(classes, proba[0])
            }}
        print(json.dumps(result, default=_json_safe))
    else:
        # Batch output (D-05): input columns + prediction + optional prob_<class> columns
        out_df = df.copy()
        out_df["prediction"] = [
            (v.item() if hasattr(v, "item") else v) for v in predictions
        ]
        if proba is not None:
            classes = model.classes_
            for i, cls in enumerate(classes):
                out_df[f"prob_{{cls}}"] = proba[:, i].tolist()

        if args.output:
            out_df.to_csv(args.output, index=False)
            print(f"Predictions written to {{args.output}} ({{len(out_df)}} rows)")
        else:
            print(out_df.to_json(orient="records", default_handler=str))

    sys.exit(0)


if __name__ == "__main__":
    main()
'''

out_path = os.path.join(deploy_dir, "predict.py")
with open(out_path, "w") as f:
    f.write(predict_py)
print(f"Generated: {out_path}")
PYEOF
export DEPLOY_DIR MODEL_NAME PROBLEM_TYPE VERSION
if [ $? -ne 0 ]; then
  echo "Failed to generate predict.py"
  exit 1
fi
```

### Step 7 — Generate predict.spec

```bash
python3 << 'PYEOF'
import json, os

deploy_dir = os.environ.get('DEPLOY_DIR', '')
model_file = os.environ.get('MODEL_FILE', 'models/best_model.pkl')

# Relative path from src/<modelname>/vN/ to the model file (three levels up to project root)
model_rel = os.path.relpath(model_file, deploy_dir)

spec_content = f"""# predict.spec — generated by /doml-deploy-cli
# D-01: --onedir packaging (faster startup, no temp-dir extraction)
# CLI-01: collects all sklearn + joblib C-extensions (Pitfall 3)

from PyInstaller.utils.hooks import collect_all

sklearn_datas, sklearn_binaries, sklearn_hiddenimports = collect_all('sklearn')
joblib_datas, joblib_binaries, joblib_hiddenimports = collect_all('joblib')

a = Analysis(
    ['predict.py'],
    pathex=[],
    binaries=sklearn_binaries + joblib_binaries,
    datas=sklearn_datas + joblib_datas + [('{model_rel}', '.')],
    hiddenimports=sklearn_hiddenimports + joblib_hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # REQUIRED for onedir — if False this becomes onefile
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
"""

out_path = os.path.join(deploy_dir, "predict.spec")
with open(out_path, "w") as f:
    f.write(spec_content)
print(f"Generated: {out_path}")
PYEOF
export DEPLOY_DIR MODEL_FILE
if [ $? -ne 0 ]; then
  echo "Failed to generate predict.spec"
  exit 1
fi
```

### Step 8 — Run PyInstaller build inside Docker container

```bash
# Derive container-side path
DEPLOY_DIR_CONTAINER="/home/jovyan/work/$(echo "$DEPLOY_DIR" | sed 's|^\./||')"
echo "Building inside container at: $DEPLOY_DIR_CONTAINER"
echo "This may take 2-5 minutes..."

docker compose exec jupyter bash -c "cd '$DEPLOY_DIR_CONTAINER' && pyinstaller predict.spec --noconfirm"
BUILD_EXIT=$?

if [ $BUILD_EXIT -ne 0 ]; then
  echo ""
  echo "PyInstaller build failed (exit code $BUILD_EXIT)."
  echo ""
  echo "Common causes:"
  echo "  - sklearn C-extension missing: ensure predict.spec uses collect_all('sklearn')"
  echo "  - src/ not writable in container: check ./src:/home/jovyan/work/src mount in docker-compose.yml"
  echo "  - pyinstaller version mismatch: rebuild with docker compose build"
  echo ""
  echo "Re-run /doml-deploy-cli after fixing the issue."
  exit 1
fi
echo "PyInstaller build complete."
```

### Step 9 — Verify binary and update deployment_metadata.json (SC-7)

```bash
PREDICT_BIN="$DEPLOY_DIR/dist/predict/predict"
if [ ! -f "$PREDICT_BIN" ]; then
  echo "Build appeared to succeed but dist/predict/predict not found at $PREDICT_BIN"
  echo "Check PyInstaller output above for unexpected directory name."
  exit 1
fi

echo "Binary produced: $PREDICT_BIN"

python3 -c "
import json, os

deploy_dir = '${DEPLOY_DIR}'
meta_path = os.path.join(deploy_dir, 'deployment_metadata.json')

with open(meta_path) as f:
    meta = json.load(f)

meta['platform'] = 'linux-x86_64'
meta['binary_path'] = os.path.join(deploy_dir, 'dist', 'predict', 'predict')

with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2)

print(f'deployment_metadata.json updated with platform: linux-x86_64')
"
if [ $? -ne 0 ]; then
  echo "Failed to update deployment_metadata.json"
  exit 1
fi
```

### Step 10 — Update STATE.md and confirm

Read `.planning/STATE.md`. In the `### Decisions` section, append:
```
[Phase 14]: doml-deploy-cli completed — {MODEL_NAME} {VERSION} → dist/predict/predict (linux-x86_64)
```

Update `last_activity` frontmatter field with today's date (YYYY-MM-DD format).
Update `stopped_at` to: `Phase 14 CLI binary built — {MODEL_NAME} {VERSION}`.

Write the updated STATE.md in-place using the Read then Write tool pattern.

Display:
```
CLI binary build complete.

  Model:      {MODEL_FILE} ({MODEL_NAME})
  Version:    {VERSION}
  Binary:     {DEPLOY_DIR}/dist/predict/predict
  Platform:   linux-x86_64
  Packaging:  --onedir (dist/predict/ directory)

To run predictions:
  Single:   ./dist/predict/predict --input '{"feature": value, ...}'
  Batch:    ./dist/predict/predict --input data.csv --output results.csv
  Help:     ./dist/predict/predict --help

The binary is self-contained. Copy dist/predict/ to any Linux x86_64 machine and run it.
No Python installation required.

Next step: run /doml-deploy-web (Phase 15) or /doml-iterate-deployment.
```

## Anti-Patterns (do NOT do these)

- NEVER build with `--onefile` — D-01 locks `--onedir`; onefile is slower and less reliable
- NEVER omit `collect_all('sklearn')` from spec — C-extensions will be missing (Pitfall 3)
- NEVER build from the host — binary must match Linux x86_64 container architecture (D-06)
- NEVER assume src/ is mounted — Step 5 checks explicitly and instructs the user if not
- NEVER shell-interpolate untrusted user input — DEPLOY_DIR is validated via file existence check
- NEVER hardcode model path in predict.py — use sys._MEIPASS for frozen binary portability
- NEVER call predict_proba without hasattr check — not all estimators support it
