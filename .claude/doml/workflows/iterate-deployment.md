# DoML Iterate Deployment Workflow

## Purpose
Iterate an existing deployment to a new version. Validates the leaderboard model matches the
last deployed model, scans src/<modelname>/v*/ for the current highest version, and writes
artifacts to vN+1/. Runs the full deployment target skill and regenerates the performance report.

## Invoked by: /doml-iterate-deployment [--model path] [--target {cli|web|wasm}] [--guidance "text"]

## Workflow

### Step 1 — Validate project state

Read `.planning/STATE.md`. If it does not exist, display and stop:
```
No DoML project found. Run /doml-new-project first.
```

### Step 2 — Read config.json and parse arguments

Read `.planning/config.json`. If missing, display and stop:
```
config.json not found. Run /doml-new-project first.
```

Extract `problem_type` from config.json:
```bash
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
echo "Problem type: $PROBLEM_TYPE"
```

Parse three flags from `$ARGUMENTS` using these exact bash snippets:

```bash
# --model flag (same as deploy-model.md)
MODEL_OVERRIDE=""
if echo "$ARGUMENTS" | grep -q -- '--model'; then
  MODEL_OVERRIDE=$(echo "$ARGUMENTS" | sed 's/.*--model[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi

# --target flag (iterate-specific)
TARGET_OVERRIDE=""
if echo "$ARGUMENTS" | grep -q -- '--target'; then
  TARGET_OVERRIDE=$(echo "$ARGUMENTS" | sed 's/.*--target[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi

# --guidance flag — Python parsing for reliable quoted-string handling
GUIDANCE=""
if echo "$ARGUMENTS" | grep -q -- '--guidance'; then
  GUIDANCE=$(python3 -c "
import sys, re
args = '''${ARGUMENTS}'''
m = re.search(r'--guidance\s+[\"\'](.*?)[\"\'']', args, re.DOTALL)
if not m:
    m = re.search(r'--guidance\s+(\S.*?)(?:\s+--|\Z)', args, re.DOTALL)
if not m:
    m = re.search(r'--guidance\s+(\S+)', args)
print(m.group(1).strip() if m else '')
")
fi
```

### Step 3 — Leaderboard-match guard

Find the most recent `deployment_metadata.json` under `src/`:
```bash
LATEST_META=$(python3 -c "
import glob, re, os
dirs = glob.glob('src/*/*')
versioned = [
    (d, int(re.search(r'/v(\d+)$', d).group(1)))
    for d in dirs
    if re.search(r'/v(\d+)$', d) and os.path.isfile(d + '/deployment_metadata.json')
]
if not versioned:
    print('')
else:
    latest = sorted(versioned, key=lambda x: x[1], reverse=True)[0][0]
    print(latest + '/deployment_metadata.json')
")
if [ -z "$LATEST_META" ]; then
  echo "No previous deployment found. Run /doml-deploy-model first."
  exit 1
fi
```

Resolve the current #1 leaderboard model_file (compare file paths, not display names — avoids
display-name mismatch between leaderboard model column and deployment_metadata.json model_name):
```bash
META_MODEL_FILE=$(python3 -c "
import json
with open('models/model_metadata.json') as f:
    meta = json.load(f)
print(meta.get('model_file', 'models/best_model.pkl'))
")
DEPLOYED_MODEL_FILE=$(python3 -c "
import json
with open('${LATEST_META}') as f:
    meta = json.load(f)
print(meta.get('model_file', ''))
")
```

Guard: if no `--model` override AND model files differ AND leaderboard model is non-empty, stop:
```bash
if [ -z "$MODEL_OVERRIDE" ] && [ "$META_MODEL_FILE" != "$DEPLOYED_MODEL_FILE" ] && [ -n "$META_MODEL_FILE" ]; then
  # Read display names for the message
  NEW_MODEL=$(python3 -c "import json; m=json.load(open('models/model_metadata.json')); print(m.get('model_name', '${META_MODEL_FILE}'))")
  OLD_MODEL=$(python3 -c "import json; m=json.load(open('${LATEST_META}')); print(m.get('model_name', '${DEPLOYED_MODEL_FILE}'))")
  echo ""
  echo "The leaderboard leader has changed since your last deployment."
  echo "Current leader: ${NEW_MODEL}"
  echo "Last deployed:  ${OLD_MODEL}"
  echo ""
  echo "Did you mean to deploy a new model?"
  echo "Run /doml-deploy-model to start a fresh deployment for ${NEW_MODEL}."
  exit 1
fi
```

If `MODEL_OVERRIDE` is set, validate the file exists:
```bash
if [ -n "$MODEL_OVERRIDE" ]; then
  python3 -c "import os, sys; sys.exit(0) if os.path.exists('${MODEL_OVERRIDE}') else sys.exit(1)" || {
    echo "Model file not found: ${MODEL_OVERRIDE}"
    exit 1
  }
  MODEL_FILE="${MODEL_OVERRIDE}"
else
  MODEL_FILE="${META_MODEL_FILE}"
fi
```

### Step 4 — Ensure model_name in model_metadata.json (DEPLOY-05)

```bash
python3 -c "
import json, os, joblib

meta_path = 'models/model_metadata.json'
model_file = '${MODEL_FILE}'

if not os.path.exists(meta_path):
    meta = {'model_file': model_file}
else:
    with open(meta_path) as f:
        meta = json.load(f)

if 'model_name' not in meta:
    model = joblib.load(model_file)
    # Drill into Pipeline to get the final estimator class name (not 'Pipeline')
    if hasattr(model, 'steps'):
        estimator = model.steps[-1][1]
        raw_name = type(estimator).__name__
    else:
        raw_name = type(model).__name__
    meta['model_name'] = raw_name
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f'model_name added to model_metadata.json: {raw_name}')
else:
    print(f'model_name already present: {meta[\"model_name\"]}')
"
```

### Step 5 — Derive MODEL_SLUG

```bash
MODEL_SLUG=$(python3 -c "
import json, re
with open('models/model_metadata.json') as f:
    meta = json.load(f)
raw_name = meta.get('model_name', 'model')
# Strip parentheses and their contents: 'XGBoost (tuned)' -> 'XGBoost tuned'
slug = re.sub(r'\([^)]*\)', '', raw_name)
# Replace non-alphanumeric runs with underscore
slug = re.sub(r'[^a-zA-Z0-9]+', '_', slug)
# Lowercase and strip leading/trailing underscores
slug = slug.strip('_').lower()
print(slug)
")
echo "Model slug: $MODEL_SLUG"
```

### Step 6 — Resolve deployment target

```bash
if [ -n "$TARGET_OVERRIDE" ]; then
  case "$TARGET_OVERRIDE" in
    cli)  TARGET_KEY="cli_binary" ;;
    web)  TARGET_KEY="web_service" ;;
    wasm) TARGET_KEY="onnx_wasm" ;;
    *)
      echo "Unknown --target value: ${TARGET_OVERRIDE}"
      echo "Valid values: cli, web, wasm"
      exit 1
      ;;
  esac
  echo "Target override: ${TARGET_KEY}"
else
  TARGET_KEY=$(python3 -c "
import json
with open('${LATEST_META}') as f:
    meta = json.load(f)
print(meta.get('target', 'cli_binary'))
")
  echo "Target re-used from previous deployment: ${TARGET_KEY}"
fi
```

### Step 7 — Scan for existing versions and set VERSION (D-02)

```bash
VERSION=$(python3 -c "
import glob, re
model_slug = '${MODEL_SLUG}'
existing = glob.glob(f'src/{model_slug}/v*')
versions = [
    int(re.search(r'/v(\d+)$', d).group(1))
    for d in existing
    if re.search(r'/v(\d+)$', d)
]
print(max(versions) + 1 if versions else 1)
")
echo "Deployment version: v${VERSION}"
```

If `VERSION` is greater than 1, announce before creating (D-02):
```bash
if [ "$VERSION" -gt 1 ]; then
  echo "src/${MODEL_SLUG}/v$(($VERSION - 1))/ exists — iterating to v${VERSION}/"
fi
```

### Step 8 — Read feature_schema

```bash
FEATURE_SCHEMA=$(python3 -c "
import json, glob, os

processed_files = sorted(glob.glob('data/processed/preprocessed_*'))
if processed_files:
    import pandas as pd
    df = pd.read_csv(processed_files[0])
    first_row = df.iloc[0] if len(df) > 0 else None
    schema = []
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        entry = {'name': col, 'type': dtype_str}
        # Example value from first data row
        if first_row is not None:
            val = first_row[col]
            entry['example'] = str(val.item() if hasattr(val, 'item') else val)
        else:
            entry['example'] = '0' if ('int' in dtype_str or 'float' in dtype_str) else 'value'
        # Categories for object (categorical) columns; null for numerics
        if dtype_str == 'object':
            cats = sorted(df[col].dropna().unique().tolist())
            entry['categories'] = [str(c) for c in cats]
        else:
            entry['categories'] = None
        schema.append(entry)
else:
    # Fallback: use feature_names from model_metadata.json with unknown type
    with open('models/model_metadata.json') as f:
        meta = json.load(f)
    feature_names = meta.get('feature_names', [])
    schema = [{'name': name, 'type': 'unknown', 'example': 'value', 'categories': None} for name in feature_names]

print(json.dumps(schema))
")
```

### Step 9 — Apply --guidance

If `GUIDANCE` is non-empty:
```
Claude reads the $GUIDANCE string and notes any configuration adjustments that should be
applied when delegating to the target skill. Examples of what guidance can direct:

- "optimize for low latency" → reduce worker count, disable batch padding in web service
- "add batch endpoint" → instruct deploy-web step to include a /predict/batch route
- "use quantized model" → note that quantization requires ONNX reconversion (beyond this step's scope); acknowledge limitation
- "increase gunicorn workers" → apply before invoking deploy-web.md

Guidance is also passed to the performance report narrative step (Step 12f) so Claude's
analysis reflects the intent.

Acknowledge what can and cannot be done with the given guidance for the current target type.
For ONNX/WASM targets: guidance implying model artifact changes cannot be applied by iterate;
user must run /doml-deploy-wasm with the updated model. Fail with a clear message if guidance
requires capabilities beyond what iterate-deployment can modify.
```

If `GUIDANCE` is empty:
```
No guidance provided. Proceeding with same configuration as previous deployment version.
```

### Step 10 — Create deployment directory and write deployment_metadata.json

```bash
python3 -c "
import json, os
from pathlib import Path
from datetime import datetime, timezone

model_file = '${MODEL_FILE}'
model_slug = '${MODEL_SLUG}'
version = ${VERSION}
target_key = '${TARGET_KEY}'
feature_schema = ${FEATURE_SCHEMA}
problem_type = '${PROBLEM_TYPE}'
guidance = '''${GUIDANCE}'''

with open('models/model_metadata.json') as f:
    meta = json.load(f)
model_name = meta.get('model_name', model_slug)

deploy_dir = Path(f'src/{model_slug}/v{version}')
deploy_dir.mkdir(parents=True, exist_ok=True)

metadata = {
    'model_file': model_file,
    'model_name': model_name,
    'target': target_key,
    'problem_type': problem_type,
    'build_date': datetime.now(timezone.utc).isoformat(),
    'version': f'v{version}',
    'feature_schema': feature_schema
}
if guidance.strip():
    metadata['guidance'] = guidance.strip()

with open(deploy_dir / 'deployment_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f'Created: src/{model_slug}/v{version}/deployment_metadata.json')
"
```

### Step 11 — Delegate to target skill

Route based on TARGET_KEY. Always pass `--deploy-dir src/${MODEL_SLUG}/v${VERSION}` to prevent
auto-discovery from selecting the wrong version directory.

```
if TARGET_KEY == "cli_binary":
    Execute @.claude/doml/workflows/deploy-cli.md with --deploy-dir src/${MODEL_SLUG}/v${VERSION}

if TARGET_KEY == "web_service":
    Note web service port conflict possibility:
    If port 8080 is already in use by a previous deployment, display:
      "Port 8080 may already be in use by a previous deployment.
       Stop the previous version with:
         docker compose -f src/{MODEL_SLUG}/v{prev_version}/docker-compose.serve.yml down
       Then re-run /doml-iterate-deployment."
    Execute @.claude/doml/workflows/deploy-web.md with --deploy-dir src/${MODEL_SLUG}/v${VERSION}

if TARGET_KEY == "onnx_wasm":
    Execute @.claude/doml/workflows/deploy-wasm.md with --deploy-dir src/${MODEL_SLUG}/v${VERSION}
```

If GUIDANCE is set, pass the guidance context to the target skill as commentary so it shapes
how the skill configures the deployment (e.g., modify worker counts, add batch endpoint, etc.)
before delegating.

### Step 12 — Generate performance report (PERF-01, PERF-07)

> Note: This step runs AFTER the target-specific deployment skill (deploy-cli / deploy-web /
> deploy-wasm) has completed. It is the only step in this workflow that executes Docker commands.

#### 12a — Copy notebook template

```bash
cp .claude/doml/templates/notebooks/deployment_report.ipynb notebooks/deployment_report.ipynb
echo "Notebook template copied to notebooks/deployment_report.ipynb"
```

#### 12b — Web service only: start container and set URL

If `TARGET_KEY == 'web_service'`:

```bash
# Start the FastAPI container
docker compose -f "src/${MODEL_SLUG}/v${VERSION}/docker-compose.serve.yml" up -d

# Poll GET /health with 30s timeout (1s intervals) until 200
python3 -c "
import time, sys, requests
url = 'http://localhost:8080/health'
deadline = time.time() + 30
while time.time() < deadline:
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            print(f'Web service healthy: {r.json()}')
            sys.exit(0)
    except Exception:
        pass
    time.sleep(1)
print('ERROR: web service did not become healthy within 30 seconds.')
sys.exit(1)
"
if [ $? -ne 0 ]; then
  echo "Web service startup failed — aborting report generation."
  exit 1
fi

DOML_WEB_SERVICE_URL="http://localhost:8080"
echo "Web service URL: $DOML_WEB_SERVICE_URL"
```

For CLI and ONNX targets, set:
```bash
DOML_WEB_SERVICE_URL=""
```

#### 12c — Execute notebook inside Docker

```bash
docker compose exec \
  -e DOML_WEB_SERVICE_URL="${DOML_WEB_SERVICE_URL}" \
  jupyter \
  jupyter nbconvert \
    --to notebook \
    --execute \
    --inplace \
    --timeout=900 \
    notebooks/deployment_report.ipynb
```

If this command exits non-zero, the parity test or another cell raised an error. Display:
```
Notebook execution FAILED. Check notebooks/deployment_report.ipynb for the error cell.
Parity test may have failed — review the AssertionError message in the notebook output.
```
Then stop (do not generate HTML from a failed execution).

#### 12d — Web service only: stop container

If `TARGET_KEY == 'web_service'`:

```bash
docker compose -f "src/${MODEL_SLUG}/v${VERSION}/docker-compose.serve.yml" down
echo "Web service container stopped."
```

#### 12e — Read benchmark results from executed notebook

```python
import json, nbformat
from pathlib import Path

nb_path = Path('notebooks/deployment_report.ipynb')
nb = nbformat.read(str(nb_path), as_version=4)

# Extract plain-text outputs from all code cells
benchmark_outputs = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code':
        for output in cell.get('outputs', []):
            if output.get('output_type') == 'stream':
                benchmark_outputs.append(f"[Cell {i}] " + ''.join(output.get('text', [])))
            elif output.get('output_type') in ('execute_result', 'display_data'):
                data = output.get('data', {})
                if 'text/plain' in data:
                    benchmark_outputs.append(f"[Cell {i}] " + ''.join(data['text/plain']))

benchmark_summary = '\n'.join(benchmark_outputs)
print(benchmark_summary[:3000])  # show first 3000 chars for context
```

#### 12f — Write Claude narrative and inject into Cell 12

Claude Code reads `benchmark_summary` from 12e and writes a 2-3 paragraph narrative
summarising the key findings: latency (mean ± std, p95), batch throughput at each batch size,
memory footprint (model load + per-prediction), projected throughput (req/s), and parity outcome.

The narrative must mention the target type and note that ONNX results are an approximation
(if target is onnx_wasm).

If GUIDANCE was provided, the narrative should also reference the guidance intent and comment
on whether the benchmark results reflect the requested optimisation direction.

Inject the narrative into the notebook by replacing Cell 12 (the placeholder markdown cell):

```python
import nbformat
from pathlib import Path

nb_path = Path('notebooks/deployment_report.ipynb')
nb = nbformat.read(str(nb_path), as_version=4)

# Locate Cell 12 (index 12 — the placeholder markdown)
placeholder = nb.cells[12]
assert placeholder['cell_type'] == 'markdown', \
    f"Expected Cell 12 to be markdown placeholder, got {placeholder['cell_type']}"

narrative_text = """## Performance Summary

{NARRATIVE_WRITTEN_BY_CLAUDE}
"""

placeholder['source'] = narrative_text
nbformat.write(nb, str(nb_path))
print("Narrative injected into Cell 12 of notebooks/deployment_report.ipynb")
```

Replace `{NARRATIVE_WRITTEN_BY_CLAUDE}` with the actual 2-3 paragraph narrative text
before running the script.

#### 12g — Generate HTML report

```bash
docker compose exec jupyter \
  jupyter nbconvert \
    --to html \
    --no-input \
    --output deployment_report \
    notebooks/deployment_report.ipynb
```

#### 12h — Move HTML to reports/

```bash
mkdir -p reports
cp notebooks/deployment_report.html reports/deployment_report.html
echo "HTML report copied to reports/deployment_report.html"
```

#### 12i — Verify: no visible code in HTML

```bash
INPUT_COUNT=$(grep -c 'class="input"' reports/deployment_report.html 2>/dev/null || echo "0")
if [ "$INPUT_COUNT" -gt 0 ]; then
  echo "WARNING: HTML may contain visible code cells (found $INPUT_COUNT 'class=\"input\"' occurrences)."
  echo "Verify reports/deployment_report.html manually."
else
  echo "HTML verification passed: no visible code cells (class=\"input\" count = 0)."
fi
```

#### 12j — Confirm

Display:
```
Performance report generated.

  Notebook:  notebooks/deployment_report.ipynb
  Report:    reports/deployment_report.html

Open reports/deployment_report.html to review benchmark results and narrative.
```

---

**Anti-Pattern addendum (Step 12 only):**
Step 12 is the sole exception to the "NEVER run Docker" rule — it must execute the notebook and
generate HTML inside the jupyter container. All other steps remain pure file I/O.

---

### Step 13 — Update STATE.md and confirm

Update `.planning/STATE.md`: append to the Decisions section under `### Decisions`:
```
[Phase 18]: doml-iterate-deployment completed — {MODEL_SLUG} v{VERSION} → {TARGET_KEY}
```
Update `last_activity` frontmatter field with today's date (YYYY-MM-DD).
Update `stopped_at` to: `doml-iterate-deployment complete — {MODEL_SLUG} v{VERSION}`.

Write the updated STATE.md in-place using the Read then Write tool pattern.

Display confirmation:
```
Deployment iteration complete.

  Model:      {MODEL_FILE} ({model_name})
  Target:     {TARGET_KEY}
  Directory:  src/{MODEL_SLUG}/v{VERSION}/
  Metadata:   src/{MODEL_SLUG}/v{VERSION}/deployment_metadata.json
  Report:     reports/deployment_report.html

Previous version: src/{MODEL_SLUG}/v{VERSION-1}/
New version:      src/{MODEL_SLUG}/v{VERSION}/
```

## Anti-Patterns (do NOT do these)

- NEVER assume version number — always glob src/MODEL_SLUG/v* and increment max (D-02)
- NEVER compare leaderboard display names against model_name — compare model_file paths (Pitfall 1)
- NEVER omit --deploy-dir when calling target skills — pass src/${MODEL_SLUG}/v${VERSION} explicitly (Pitfall 3)
- NEVER shell-interpolate GUIDANCE in shell commands — only pass to Python as heredoc string or via sys.argv
- NEVER modify deploy-model.md — iterate-deployment.md is a standalone workflow (D-05)
- NEVER run Docker outside Step 12 — all other steps are pure file I/O
- Step 12 is the sole exception to the "NEVER run Docker" rule — it must execute the notebook and generate HTML inside the jupyter container. All other steps remain pure file I/O.
