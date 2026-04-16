# DoML Deploy Model Workflow

## Purpose
Resolve the best leaderboard model, scaffold the versioned deployment directory, and write
deployment_metadata.json — leaving src/modelname/vN/ ready for the target-specific phase
(Phase 14: CLI binary, Phase 15: web service, Phase 16: ONNX/WASM).

## Invoked by: /doml-deploy-model [--model path/to/model.pkl]

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

Parse `--model` flag from `$ARGUMENTS`:
```bash
MODEL_OVERRIDE=""
if echo "$ARGUMENTS" | grep -q -- '--model'; then
  MODEL_OVERRIDE=$(echo "$ARGUMENTS" | sed 's/.*--model[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi
```

### Step 3 — Resolve model file

If `MODEL_OVERRIDE` is set:
- Validate the file exists: `python3 -c "import os, sys; sys.exit(0) if os.path.exists('${MODEL_OVERRIDE}') else sys.exit(1)"`
- If the file does not exist, display and stop:
  ```
  Model file not found: {MODEL_OVERRIDE}
  Check the path and run /doml-deploy-model --model <correct_path> again.
  ```
- Set `MODEL_FILE="${MODEL_OVERRIDE}"`

If `MODEL_OVERRIDE` is empty:
- Route by `PROBLEM_TYPE`:
  - `regression`, `classification`, `binary_classification`, `multiclass_classification`, `time_series` → `LEADERBOARD="models/leaderboard.csv"`
  - `clustering`, `dimensionality_reduction` → `LEADERBOARD="models/unsupervised_leaderboard.csv"`
  - anything else → display `Unknown problem_type: {PROBLEM_TYPE}` and stop

- Check leaderboard exists:
  ```bash
  if [ ! -f "$LEADERBOARD" ]; then
    echo "No leaderboard found at $LEADERBOARD."
    echo "Run /doml-modelling first to train and evaluate models."
    exit 1
  fi
  ```

- Read model file from model_metadata.json (leaderboard has model names and metrics only, not file paths):
  ```bash
  MODEL_FILE=$(python3 -c "
  import json, os
  meta_path = 'models/model_metadata.json'
  if os.path.exists(meta_path):
      with open(meta_path) as f:
          meta = json.load(f)
      model_file = meta.get('model_file', 'models/best_model.pkl')
  else:
      model_file = 'models/best_model.pkl'
  print(model_file)
  ")
  ```

- Validate the resolved model file exists:
  ```bash
  python3 -c "
  import os, sys
  model_file = '${MODEL_FILE}'
  if not os.path.exists(model_file):
      print(f'Model artifact not found: {model_file}')
      print('Run /doml-modelling or /doml-iterate first.')
      sys.exit(1)
  "
  ```
  If this exits non-zero, stop.

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

### Step 6 — Prompt for deployment target (DEPLOY-03)

Use AskUserQuestion to display:

```
Select deployment target for model: {MODEL_SLUG}

Which deployment target would you like to create?
```

Options:
1. CLI binary
2. Web service (FastAPI + Docker)
3. ONNX/WASM page

Store the response as TARGET_LABEL. Map to TARGET_KEY:
- "CLI binary" → `cli_binary`
- "Web service (FastAPI + Docker)" → `web_service`
- "ONNX/WASM page" → `onnx_wasm`

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
  echo "src/${MODEL_SLUG}/v$(($VERSION - 1))/ exists — deploying to v${VERSION}/"
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

### Step 9 — Create deployment directory and write deployment_metadata.json (DEPLOY-04)

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

with open(deploy_dir / 'deployment_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f'Created: src/{model_slug}/v{version}/deployment_metadata.json')
"
```

### Step 10 — Update STATE.md

Read `.planning/STATE.md`. In the Decisions section under `### Decisions`, append:
```
[Phase 13]: doml-deploy-model completed — {MODEL_SLUG} v{VERSION} → {TARGET_KEY}
```

Update `last_activity` frontmatter field with today's date (YYYY-MM-DD).
Update `stopped_at` to: `Phase 13 deployment skeleton complete — {MODEL_SLUG} v{VERSION}`.

Write the updated STATE.md in-place using the Read then Write tool pattern.

### Step 11 — Confirm

Display:
```
Deployment scaffold complete.

  Model:      {MODEL_FILE} ({model_name})
  Target:     {TARGET_LABEL}
  Directory:  src/{MODEL_SLUG}/v{VERSION}/
  Metadata:   src/{MODEL_SLUG}/v{VERSION}/deployment_metadata.json

Next step: run the target-specific deployment phase.
  CLI binary   → /doml-deploy-cli (Phase 14)
  Web service  → /doml-deploy-web (Phase 15)
  ONNX/WASM    → /doml-deploy-wasm (Phase 16)
```

## Anti-Patterns (do NOT do these)

- NEVER shell-interpolate MODEL_OVERRIDE in shell commands — only pass to Python os.path.exists()
- NEVER hardcode version numbers — always glob src/MODEL_SLUG/v* and increment max (D-02)
- NEVER run Docker — this workflow is pure file I/O; no docker compose exec calls
- NEVER create predict.py, Dockerfile, app.py, or any stub files — those are Phase 14/15/16 (D-05)
- NEVER overwrite existing fields in model_metadata.json — only add model_name if the key is absent
