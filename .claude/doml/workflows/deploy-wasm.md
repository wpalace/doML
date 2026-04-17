# DoML Deploy WASM Workflow

## Purpose
Convert the full sklearn Pipeline to ONNX via skl2onnx inside Docker, enforce the 20 MB bundle
size gate, and generate a self-contained `index.html` with onnxruntime-web 1.17.3 and the model
embedded as base64 — written into `src/<modelname>/vN/`. Opening the page in any browser executes
full inference via ONNX with no server and no network requests.

## Invoked by: /doml-deploy-wasm [--deploy-dir src/<modelname>/vN]

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

model_file     = meta.get('model_file', 'models/best_model.pkl')
model_name     = meta.get('model_name', 'model')
version        = meta.get('version', 'v1')
feature_schema = meta.get('feature_schema', [])
target         = meta.get('target', '')

# Write env vars to /tmp for shell to source
with open('/tmp/doml_wasm_meta.sh', 'w') as f:
    f.write(f'MODEL_FILE=\"{model_file}\"\n')
    f.write(f'MODEL_NAME=\"{model_name}\"\n')
    f.write(f'VERSION=\"{version}\"\n')
    f.write(f'FEATURE_SCHEMA_JSON={json.dumps(json.dumps(feature_schema))}\n')

print(f'Model: {model_name} ({model_file}), version: {version}')
print(f'Feature schema: {len(feature_schema)} features')
"
if [ $? -ne 0 ]; then exit 1; fi
source /tmp/doml_wasm_meta.sh
```

Read `PROBLEM_TYPE` from config.json:
```bash
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
echo "Problem type: $PROBLEM_TYPE"
```

### Step 4 — Problem type block check (WASM-04)

Block unsupported problem types before any conversion is attempted.

```bash
# Block forecasting problem type — time series models cannot be exported to ONNX
if [ "$PROBLEM_TYPE" = "forecasting" ]; then
  echo ""
  echo "ONNX/WASM target is not supported for forecasting problem type."
  echo "Time series models (ARIMA, Prophet) cannot be exported to ONNX."
  echo ""
  echo "Consider the web service target: /doml-deploy-web"
  exit 1
fi

# Block DBSCAN clustering — no predict() interface exportable to ONNX
if [ "$PROBLEM_TYPE" = "clustering" ]; then
  ESTIMATOR_CLASS=$(python3 -c "
import joblib
pipeline = joblib.load('${MODEL_FILE}')
estimator = pipeline.steps[-1][1]
print(type(estimator).__name__)
" 2>/dev/null || echo "unknown")
  if echo "$ESTIMATOR_CLASS" | grep -qi "DBSCAN"; then
    echo ""
    echo "ONNX/WASM target is not supported for DBSCAN clustering."
    echo "DBSCAN does not produce an ONNX-exportable predict() interface."
    echo ""
    echo "Consider the web service target: /doml-deploy-web"
    exit 1
  fi
fi
echo "Problem type check passed: $PROBLEM_TYPE"
```

### Step 5 — Check Docker container running and skl2onnx available

Check that the container is running:
```bash
if ! docker compose ps jupyter 2>/dev/null | grep -q "Up\|running"; then
  echo "Jupyter container is not running. Start it with: docker compose up -d"
  exit 1
fi
```

Check skl2onnx is available inside the container:
```bash
if ! docker compose exec jupyter python3 -c "import skl2onnx" 2>/dev/null; then
  echo ""
  echo "SETUP REQUIRED: skl2onnx is not installed in the Docker container."
  echo ""
  echo "1. Add 'skl2onnx' to requirements.in"
  echo "2. Run: docker compose run --rm jupyter pip-compile requirements.in"
  echo "3. Run: docker compose build"
  echo "4. Run: docker compose up -d"
  echo ""
  echo "Re-run /doml-deploy-wasm after the image is rebuilt."
  exit 1
fi
echo "skl2onnx available in container."
```

### Step 6 — Run ONNX conversion inside Docker (D-02, D-03)

Derive container-side paths (host ./src maps to /home/jovyan/work/src):
```bash
DEPLOY_DIR_CONTAINER="/home/jovyan/work/$(echo "$DEPLOY_DIR" | sed 's|^\./||')"
MODEL_FILE_CONTAINER="/home/jovyan/work/$MODEL_FILE"
```

Write the conversion script on the host, copy into the container, and run it. The script:
1. Loads the sklearn Pipeline
2. Reads feature_schema and builds category_map ({feature: {label: int_code}}) from categories lists
3. Replaces any OneHotEncoder in the Pipeline's ColumnTransformer with a pre-fitted OrdinalEncoder
4. Converts the rebuilt Pipeline to ONNX with float32-only inputs
5. Saves model.onnx to the deployment directory inside the container
6. Prints category_map JSON as the last output line (captured by the shell for HTML embedding)

```bash
cat > /tmp/doml_convert_onnx.py << 'PYEOF'
#!/usr/bin/env python3
"""
DoML ONNX conversion script — generated by /doml-deploy-wasm
Runs inside the Jupyter Docker container.
Usage: python3 /tmp/doml_convert_onnx.py <model_file_container> <deploy_dir_container>
"""
import copy, json, sys, os
import numpy as np
import joblib
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.compose import ColumnTransformer

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 doml_convert_onnx.py <model_file> <deploy_dir>", file=sys.stderr)
        sys.exit(1)

    model_file = sys.argv[1]
    deploy_dir = sys.argv[2]

    # Load pipeline
    pipeline = joblib.load(model_file)

    # Read feature_schema and build category_map
    meta_path = os.path.join(deploy_dir, 'deployment_metadata.json')
    with open(meta_path) as f:
        meta = json.load(f)

    feature_schema = meta['feature_schema']
    n_features = len(feature_schema)

    cat_info = {
        f['name']: f['categories']
        for f in feature_schema
        if f.get('categories')
    }
    category_map = {
        name: {cat: i for i, cat in enumerate(cats)}
        for name, cats in cat_info.items()
    }

    # Rebuild ColumnTransformer — replace OneHotEncoder with OrdinalEncoder (D-03)
    ct = pipeline.steps[0][1]  # first step is ColumnTransformer
    new_transformers = []

    for name, transformer, columns in ct.transformers_:
        if name == 'remainder':
            new_transformers.append((name, transformer, columns))
            continue

        # Detect OneHotEncoder anywhere in this transformer (direct or in a Pipeline)
        has_ohe = False
        if hasattr(transformer, 'get_params'):
            class_name = type(transformer).__name__
            if 'OneHot' in class_name:
                has_ohe = True
            elif isinstance(transformer, SKPipeline):
                for step_name, step in transformer.steps:
                    if 'OneHot' in type(step).__name__:
                        has_ohe = True
                        break

        if has_ohe:
            # Build OrdinalEncoder pre-fitted with the known categories
            col_list = list(columns) if not isinstance(columns, list) else columns
            cats_list = [np.array(cat_info[col]) for col in col_list]

            ord_enc = OrdinalEncoder(
                handle_unknown='use_encoded_value',
                unknown_value=-1
            )
            ord_enc.categories_ = cats_list
            ord_enc.n_features_in_ = len(col_list)
            ord_enc.feature_names_in_ = np.array(col_list)
            ord_enc.dtype = np.float64

            if isinstance(transformer, SKPipeline):
                # Replace only the OHE step; keep imputer(s)
                new_steps = []
                for step_name, step in transformer.steps:
                    if 'OneHot' in type(step).__name__:
                        new_steps.append((step_name, ord_enc))
                    else:
                        new_steps.append((step_name, copy.deepcopy(step)))
                new_transformer = SKPipeline(new_steps)
            else:
                new_transformer = ord_enc

            new_transformers.append((name, new_transformer, columns))
        else:
            new_transformers.append((name, copy.deepcopy(transformer), columns))

    # Rebuild ColumnTransformer with updated transformers
    new_ct = ColumnTransformer(
        transformers=new_transformers,
        remainder=ct.remainder,
        sparse_threshold=getattr(ct, 'sparse_threshold', 0.3),
        n_jobs=getattr(ct, 'n_jobs', None),
        transformer_weights=getattr(ct, 'transformer_weights', None),
        verbose=False,
    )
    # Copy fitted attributes
    new_ct.transformers_ = new_transformers
    new_ct.n_features_in_ = ct.n_features_in_
    if hasattr(ct, 'feature_names_in_'):
        new_ct.feature_names_in_ = ct.feature_names_in_
    new_ct._remainder = getattr(ct, '_remainder', ('remainder', 'drop', []))
    new_ct.sparse_output_ = False

    # Build replacement Pipeline
    new_steps = [(pipeline.steps[0][0], new_ct)] + list(pipeline.steps[1:])
    new_pipeline = SKPipeline(new_steps)

    # Convert to ONNX
    try:
        initial_types = [('float_input', FloatTensorType([None, n_features]))]
        onnx_model = convert_sklearn(new_pipeline, initial_types=initial_types)
    except Exception as e:
        print(f"ONNX conversion error: {e}", file=sys.stderr)
        print(str(e))
        print("ONNX/WASM target is not supported for this estimator. Consider the web service target: /doml-deploy-web")
        sys.exit(2)

    # Save ONNX model
    onnx_path = os.path.join(deploy_dir, 'model.onnx')
    with open(onnx_path, 'wb') as f:
        f.write(onnx_model.SerializeToString())

    # Report ONNX graph I/O
    input_names  = [inp.name for inp in onnx_model.graph.input]
    output_names = [out.name for out in onnx_model.graph.output]
    print(f"ONNX inputs:  {input_names}")
    print(f"ONNX outputs: {output_names}")
    print(f"Saved: {onnx_path}")

    # Last line: category_map JSON (captured by the calling shell script)
    print(json.dumps(category_map))

if __name__ == '__main__':
    main()
PYEOF

# Copy to container and run
docker compose cp /tmp/doml_convert_onnx.py jupyter:/tmp/doml_convert_onnx.py
docker compose exec jupyter python3 /tmp/doml_convert_onnx.py \
  "$MODEL_FILE_CONTAINER" "$DEPLOY_DIR_CONTAINER" > /tmp/doml_onnx_result.txt 2>&1
CONV_EXIT=$?

if [ $CONV_EXIT -ne 0 ]; then
  cat /tmp/doml_onnx_result.txt
  echo ""
  echo "ONNX conversion failed (exit code $CONV_EXIT)."
  echo "ONNX/WASM target is not supported for this estimator. Consider the web service target: /doml-deploy-web"
  exit 1
fi

cat /tmp/doml_onnx_result.txt

# Extract category_map JSON from last line of output
CATEGORY_MAP_JSON=$(tail -1 /tmp/doml_onnx_result.txt)
echo "ONNX conversion complete."
echo "model.onnx written to $DEPLOY_DIR/model.onnx"
```

### Step 7 — Download ORT JS + WASM binaries (D-01)

Download onnxruntime-web 1.17.3 binaries at generation time and cache them to avoid
re-downloading on repeated runs.

```bash
ORT_VERSION="1.17.3"
ORT_CACHE="/tmp/doml_ort_${ORT_VERSION}"
ORT_JS="${ORT_CACHE}/ort.min.js"
ORT_WASM="${ORT_CACHE}/ort-wasm.wasm"

mkdir -p "$ORT_CACHE"

if [ ! -f "$ORT_JS" ]; then
  echo "Downloading ort.min.js (onnxruntime-web ${ORT_VERSION})..."
  curl -fsSL "https://unpkg.com/onnxruntime-web@${ORT_VERSION}/dist/ort.min.js" -o "$ORT_JS"
  if [ $? -ne 0 ]; then
    echo "Failed to download ort.min.js. Check internet connection."
    echo "Alternatively, place the file at: $ORT_JS"
    exit 1
  fi
else
  echo "ort.min.js cached at $ORT_JS"
fi

if [ ! -f "$ORT_WASM" ]; then
  echo "Downloading ort-wasm.wasm (onnxruntime-web ${ORT_VERSION})..."
  curl -fsSL "https://unpkg.com/onnxruntime-web@${ORT_VERSION}/dist/ort-wasm.wasm" -o "$ORT_WASM"
  if [ $? -ne 0 ]; then
    echo "Failed to download ort-wasm.wasm. Check internet connection."
    echo "Alternatively, place the file at: $ORT_WASM"
    exit 1
  fi
else
  echo "ort-wasm.wasm cached at $ORT_WASM"
fi
echo "ORT binaries ready."
```

### Step 8 — Size gate check (WASM-05)

Compute the total embedded bundle size: ORT JS inline text + WASM base64 + model.onnx base64.
Reject if it exceeds 20 MB.

```bash
python3 << PYEOF
import base64, sys, os

ort_js_path = '${ORT_JS}'
wasm_path   = '${ORT_WASM}'
onnx_path   = '${DEPLOY_DIR}/model.onnx'

ort_js_bytes = open(ort_js_path, 'rb').read()
wasm_bytes   = open(wasm_path,   'rb').read()
onnx_bytes   = open(onnx_path,   'rb').read()

total_bytes = (
    len(ort_js_bytes) +                    # ORT JS inline text (bytes)
    len(base64.b64encode(wasm_bytes)) +    # WASM base64 string length
    len(base64.b64encode(onnx_bytes))      # model.onnx base64 string length
)
limit = 20 * 1024 * 1024  # 20 MB

ort_mb   = len(ort_js_bytes) / (1024 * 1024)
wasm_mb  = len(wasm_bytes)   / (1024 * 1024)
onnx_mb  = len(onnx_bytes)   / (1024 * 1024)
total_mb = total_bytes       / (1024 * 1024)

print(f"Bundle sizes:")
print(f"  ort.min.js:   {ort_mb:.1f} MB")
print(f"  ort-wasm:     {wasm_mb:.1f} MB (base64)")
print(f"  model.onnx:   {onnx_mb:.1f} MB (base64)")
print(f"  Total:        {total_mb:.1f} MB")

if total_bytes > limit:
    print(f"")
    print(f"ONNX/WASM bundle exceeds 20 MB ({total_mb:.1f} MB).")
    print(f"The model.onnx ({onnx_mb:.1f} MB) is too large to embed in a browser page.")
    print(f"")
    print(f"Consider the web service target: /doml-deploy-web")
    sys.exit(1)
else:
    print(f"Size gate passed: {total_mb:.1f} MB < 20 MB")
PYEOF
if [ $? -ne 0 ]; then exit 1; fi
```

### Step 9 — Generate index.html (WASM-01, WASM-02, WASM-03)

Generate `src/<modelname>/vN/index.html` as a fully self-contained browser page. The page:
- Inlines ORT JS as a `<script>` block (no base64 — plain text embed)
- Embeds the WASM binary as a base64 string; converted to a Blob URL at runtime (D-01)
- Embeds the ONNX model as a base64 string; decoded to Uint8Array at runtime (WASM-01)
- Builds the prediction form dynamically from FEATURE_SCHEMA (WASM-02)
- Runs ONNX inference on form submit and displays the result inline (WASM-03)
- Maps categorical select values to integer codes via CATEGORIES before building the tensor (D-03)

```bash
python3 << 'PYEOF'
import base64, json, os, sys

deploy_dir    = os.environ.get('DEPLOY_DIR', '')
model_name    = os.environ.get('MODEL_NAME', 'model')
version       = os.environ.get('VERSION', 'v1')
problem_type  = os.environ.get('PROBLEM_TYPE', 'regression')
ort_js_path   = os.environ.get('ORT_JS', '')
ort_wasm_path = os.environ.get('ORT_WASM', '')
onnx_path     = os.path.join(deploy_dir, 'model.onnx')
cat_map_json  = os.environ.get('CATEGORY_MAP_JSON', '{}')

# Read raw files
ort_js_text = open(ort_js_path,   'r', encoding='utf-8').read()
wasm_b64    = base64.b64encode(open(ort_wasm_path, 'rb').read()).decode('ascii')
model_b64   = base64.b64encode(open(onnx_path,     'rb').read()).decode('ascii')

# Read feature_schema and category_map
with open(os.path.join(deploy_dir, 'deployment_metadata.json')) as f:
    meta = json.load(f)
feature_schema = meta['feature_schema']
category_map   = json.loads(cat_map_json)

n_features          = len(feature_schema)
feature_schema_json = json.dumps(feature_schema)
category_map_json   = json.dumps(category_map)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DoML — {model_name} Inference</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; }}
h1 {{ font-size: 1.4rem; margin-bottom: 4px; }}
p.meta {{ color: #666; font-size: 0.85rem; margin-top: 0; }}
form div {{ margin: 8px 0; }}
label {{ display: flex; gap: 8px; align-items: center; }}
label span {{ min-width: 160px; font-weight: 500; }}
input[type=number], select {{ padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px; }}
button {{ margin-top: 12px; padding: 8px 24px; background: #2563eb; color: white;
          border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; }}
button:hover {{ background: #1d4ed8; }}
#result {{ margin-top: 20px; padding: 16px; background: #f0fdf4; border: 1px solid #86efac;
           border-radius: 6px; display: none; }}
#result.error {{ background: #fef2f2; border-color: #fca5a5; }}
</style>
</head>
<body>
<h1>{model_name}</h1>
<p class="meta">Version: {version} &nbsp;|&nbsp; Type: {problem_type} &nbsp;|&nbsp; {n_features} features &nbsp;|&nbsp; Offline inference via ONNX/WebAssembly</p>

<form id="predict-form"></form>
<div id="result"></div>

<script>
{ort_js_text}
</script>
<script>
const ORT_WASM_B64   = "{wasm_b64}";
const MODEL_B64      = "{model_b64}";
const FEATURE_SCHEMA = {feature_schema_json};
const CATEGORIES     = {category_map_json};
const PROBLEM_TYPE   = "{problem_type}";

(async () => {{
  // Point ORT at the embedded WASM (D-01)
  // Convert base64 to Blob URL — raw data URIs rejected for WASM by some browsers
  const wasmBytes = Uint8Array.from(atob(ORT_WASM_B64), c => c.charCodeAt(0));
  const wasmBlob  = new Blob([wasmBytes], {{type: 'application/wasm'}});
  const wasmUrl   = URL.createObjectURL(wasmBlob);
  ort.env.wasm.numThreads = 1;  // disable multi-threading for offline file:// use
  ort.env.wasm.wasmPaths  = {{
    'ort-wasm.wasm':               wasmUrl,
    'ort-wasm-simd.wasm':          wasmUrl,
    'ort-wasm-threaded.wasm':      wasmUrl,
    'ort-wasm-simd-threaded.wasm': wasmUrl
  }};

  // Load ONNX model from embedded base64 (WASM-01)
  const modelBytes = Uint8Array.from(atob(MODEL_B64), c => c.charCodeAt(0));
  const session    = await ort.InferenceSession.create(modelBytes);
  const inputName  = session.inputNames[0];
  const outputNames = session.outputNames;

  // Build prediction form from feature_schema (WASM-02)
  const form = document.getElementById('predict-form');
  for (const feat of FEATURE_SCHEMA) {{
    const row   = document.createElement('div');
    const label = document.createElement('label');
    const span  = document.createElement('span');
    span.textContent = feat.name;
    label.appendChild(span);
    if (feat.categories) {{
      // Categorical feature: <select> with human-readable options (WASM-02)
      const sel = document.createElement('select');
      sel.name = feat.name;
      for (const cat of feat.categories) {{
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = cat;
        sel.appendChild(opt);
      }}
      label.appendChild(sel);
    }} else {{
      // Numeric feature: type='number' input (WASM-02)
      const inp = document.createElement('input');
      inp.type = 'number';
      inp.name = feat.name;
      inp.step = 'any';
      inp.required = true;
      inp.placeholder = String(feat.example ?? '0');
      label.appendChild(inp);
    }}
    row.appendChild(label);
    form.appendChild(row);
  }}
  const btn = document.createElement('button');
  btn.type = 'submit';
  btn.textContent = 'Predict';
  form.appendChild(btn);

  // Handle form submit — run ONNX inference (WASM-03)
  form.addEventListener('submit', async (e) => {{
    e.preventDefault();
    const fd   = new FormData(form);
    const data = new Float32Array(FEATURE_SCHEMA.length);
    for (let i = 0; i < FEATURE_SCHEMA.length; i++) {{
      const feat = FEATURE_SCHEMA[i];
      const val  = fd.get(feat.name);
      // Categoricals: map label to integer code via CATEGORIES (D-03)
      // Numerics: parseFloat
      data[i] = feat.categories ? CATEGORIES[feat.name][val] : parseFloat(val);
    }}
    // ONNX tensor: Float32Array with shape [1, n_features] (WASM-01)
    const tensor  = new ort.Tensor('float32', data, [1, FEATURE_SCHEMA.length]);
    const results = await session.run({{[inputName]: tensor}});

    const div = document.getElementById('result');
    div.className = '';
    div.style.display = 'block';

    if (PROBLEM_TYPE === 'regression') {{
      const pred = results[outputNames[0]].data[0];
      div.innerHTML = '<strong>Prediction:</strong> ' + pred.toFixed(4);
    }} else {{
      // Classification: label output + optional probability ZipMap output
      const labelOut = outputNames.find(n => n.includes('label')) ?? outputNames[0];
      const cls      = results[labelOut].data[0];
      let   html     = '<strong>Predicted class:</strong> ' + cls;
      const probOut  = outputNames.find(n => n.includes('prob'));
      if (probOut) {{
        const probMap = results[probOut].data[0];
        const entries = Object.entries(probMap).sort((a, b) => b[1] - a[1]);
        html += '<br><br><strong>Probabilities:</strong><br>';
        for (const [c, p] of entries) {{
          const pct = (p * 100).toFixed(1);
          html += c + ': <strong>' + pct + '%</strong><br>';
        }}
      }}
      div.innerHTML = html;
    }}
  }});

}})().catch(err => {{
  const div = document.getElementById('result');
  div.className = 'error';
  div.style.display = 'block';
  div.innerHTML = '<strong>Error:</strong> ' + err.message +
    '<br><small>Check the browser console for details.</small>';
}});
</script>
</body>
</html>'''

out_path = os.path.join(deploy_dir, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated: {out_path}")
PYEOF
export DEPLOY_DIR MODEL_NAME VERSION PROBLEM_TYPE ORT_JS ORT_WASM CATEGORY_MAP_JSON
if [ $? -ne 0 ]; then
  echo "Failed to generate index.html"
  exit 1
fi
```

### Step 10 — Update deployment_metadata.json

Record the generated artifacts in deployment_metadata.json.

```bash
python3 -c "
import json, os

deploy_dir = '${DEPLOY_DIR}'
meta_path  = os.path.join(deploy_dir, 'deployment_metadata.json')

with open(meta_path) as f:
    meta = json.load(f)

meta['index_html']  = os.path.join(deploy_dir, 'index.html')
meta['onnx_model']  = os.path.join(deploy_dir, 'model.onnx')
meta['ort_version'] = '1.17.3'

with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2)

print('deployment_metadata.json updated.')
"
if [ $? -ne 0 ]; then
  echo "Failed to update deployment_metadata.json"
  exit 1
fi
```

### Step 11 — Update STATE.md and display summary

Read `.planning/STATE.md`. In the `### Decisions` section, append:
```
[Phase 16]: doml-deploy-wasm completed — {MODEL_NAME} {VERSION} → index.html (ONNX/WASM, {PROBLEM_TYPE})
```

Update `last_activity` frontmatter field with today's date (YYYY-MM-DD format).
Update `stopped_at` to: `Phase 16 ONNX/WASM built — {MODEL_NAME} {VERSION}`.

Write the updated STATE.md in-place using the Read then Write tool pattern.

Display:
```
ONNX/WASM build complete.

  Model:        {MODEL_FILE} ({MODEL_NAME})
  Version:      {VERSION}
  ONNX graph:   {DEPLOY_DIR}/model.onnx
  Browser page: {DEPLOY_DIR}/index.html
  ORT version:  1.17.3

To run inference:
  Open {DEPLOY_DIR}/index.html in any browser (double-click or file:// URL).
  Fill in the prediction form and click Predict.
  No server or internet connection required.

Next step: run /doml-deploy-model --model other_model.pkl --target onnx_wasm,
           or /doml-iterate-deployment, or /doml-deploy-web for a server-side target.
```

## Anti-Patterns (do NOT do these)

- NEVER run ONNX conversion on the host — always use `docker compose exec` to run inside the container (D-02); the conversion requires the same sklearn/skl2onnx versions that trained the model
- NEVER pass string tensors to onnxruntime-web — all inputs must be float32; use OrdinalEncoder at export time and the CATEGORIES map in JS to encode categoricals (D-03)
- NEVER skip the size gate check — bundles over 20 MB are rejected before generating index.html (WASM-05); blocked models should use the web service target
- NEVER fetch ORT JS or WASM at page-open time — binaries must be downloaded at generation time and embedded in the HTML; the page must work fully offline (D-01)
- NEVER shell-interpolate untrusted values into python3 inline code — DEPLOY_DIR is validated by file existence check in Step 2; MODEL_FILE is read from the trusted deployment_metadata.json
- NEVER embed the WASM as a plain data URI string in `ort.env.wasm.wasmPaths` without first converting to a Blob URL — some browsers reject raw `data:application/wasm;base64,...` URIs; use `URL.createObjectURL(new Blob([wasmBytes], {type: 'application/wasm'}))` instead
- NEVER omit the forecasting and DBSCAN checks in Step 4 — these must run before any conversion is attempted (WASM-04)
