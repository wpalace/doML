# Phase 16: ONNX/WASM Target — Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Convert the full sklearn Pipeline to ONNX via skl2onnx (inside Docker), enforce the 20 MB size gate, and generate a self-contained `index.html` with onnxruntime-web and the model embedded as base64 — all written into `src/<modelname>/vN/`.

Phase 16 reads from `src/<modelname>/vN/deployment_metadata.json` (produced by Phase 13 / extended by Phase 15 for `categories` per D-01). Running the page in any browser, with no web server, must execute full inference via ONNX.

**Requirements in scope:** WASM-01, WASM-02, WASM-03, WASM-04, WASM-05

</domain>

<decisions>
## Implementation Decisions

### onnxruntime-web Delivery

- **D-01: Fully self-contained — ORT JS and WASM embedded as base64 data URIs**
  - `ort.min.js` (~480 KB) is downloaded at workflow time and inlined as a `<script>` block (not a base64 URI — inline is valid since it's JS text)
  - `ort-wasm.wasm` (~2.5 MB) is embedded as a `data:application/wasm;base64,...` data URI and pointed to via `ort.env.wasm.wasmPaths`
  - The ONNX model itself is embedded as a base64 string (same pattern)
  - **No network requests at any time** — the page works offline from the first open
  - ORT and WASM binaries are downloaded by the workflow (via `curl` or `wget` inside Docker, or from the container's local npm cache) at generation time — not at page-open time
  - Total HTML overhead before model: ~3–4 MB. The 20 MB size gate (WASM-05) covers everything: ORT + WASM + model.onnx base64
  - Size gate check: `len(base64(ort.min.js)) + len(base64(ort-wasm.wasm)) + len(base64(model.onnx))` must be < 20 MB; if exceeded, block with message suggesting web service target

### Conversion Step Placement

- **D-02: Conversion runs entirely inside the new `doml-deploy-wasm` skill**
  - `deploy-model.md` (Phase 13) is **not modified** — model.onnx is a WASM-target artifact only
  - The WASM skill workflow runs conversion (`skl2onnx` inside Docker), size-checks, and generates `index.html` — fully self-contained
  - `model.onnx` is written to `src/<modelname>/vN/model.onnx` alongside `index.html`
  - Conversion runs via `docker compose exec jupyter python3 -c "..."` — same Docker-exec pattern as Phase 14 (PyInstaller) and Phase 15 (category scan)

### Categorical Tensor Encoding

- **D-03: Ordinal-encode at export time; JS receives integers only**
  - At conversion time, build a `category_map: {feature_name: {label: integer}}` dict from `deployment_metadata.json`'s `categories` field (already populated by Phase 15 D-01)
  - The skl2onnx export uses a pipeline where `OrdinalEncoder` replaces `OneHotEncoder` for the ONNX export path, OR the existing Pipeline's OHE is replaced with an `OrdinalEncoder` clone scoped to the categorical columns for this export only
  - `category_map` is embedded in `index.html` as a JS constant
  - The form renders `<select>` dropdowns with human-readable labels; JS converts the selection to its integer code before building the ONNX input tensor
  - ONNX graph receives only `float32` tensors — no string inputs anywhere
  - **Benefit:** onnxruntime-web string tensor support is version-dependent and inconsistent across browsers; numeric-only inputs are universally supported

### Unsupported Estimator Handling

- **D-04: Attempt conversion, surface error with web service suggestion**
  - The workflow runs `skl2onnx.convert_sklearn(pipeline, ...)` inside Docker and captures stderr/stdout
  - If conversion raises `ConversionError` or any exception, the workflow:
    1. Prints the error message verbatim (so the user knows which operator failed)
    2. Suggests: "ONNX/WASM target is not supported for this estimator. Consider the web service target: `/doml-deploy-model --target web`"
    3. Exits without writing any output files
  - No pre-allowlist check — attempt first, fail informatively
  - This is in addition to the existing WASM-04 blocks (forecasting, DBSCAN) which are checked before conversion is attempted

### Problem Type Blocks (WASM-04)

- Forecasting problem type → block before conversion with clear message
- DBSCAN clustering → block before conversion with clear message
- KMeans clustering → supported (ONNX can represent KMeans)
- Regression / Classification → supported

### Size Gate (WASM-05)

- After conversion, compute total base64 size: ORT JS inline text + WASM base64 URI + model.onnx base64
- If total exceeds 20 MB: block with message "ONNX/WASM bundle exceeds 20 MB ({size} MB). Consider the web service target."
- ORT download pinned to a specific version (e.g., onnxruntime-web 1.17.x) to ensure reproducible file sizes

### Claude's Discretion

- Exact CSS styling for the prediction result card (same minimal inline-styles approach as Phase 15 D-04)
- Whether the `index.html` result display for classification uses probability bars (matching Phase 15 D-04) or a simpler table — consistency with Phase 15 is preferred
- ORT version pin selection (latest stable 1.x at time of implementation)
- Whether the ORT WASM binary is downloaded fresh by the workflow or extracted from an npm package inside the container
- ONNX opset version passed to skl2onnx (use latest supported by the ORT version pinned)
- Whether `model.onnx` is kept on disk after `index.html` is generated (keeping it is fine — useful for debugging)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §WASM — WASM-01 through WASM-05 define all acceptance criteria for this phase

### Phase 13 outputs
- `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — directory structure, `deployment_metadata.json` fields
- `.claude/doml/workflows/deploy-model.md` — produces `deployment_metadata.json`; NOT modified by this phase

### Phase 15 patterns
- `.planning/phases/15-web-service-target/15-CONTEXT.md` — D-01 (categories in feature_schema), D-03 (ordinal encoding for JS form), D-04 (classification probability display)
- D-01 from Phase 15: `deployment_metadata.json` already contains `categories: ["EU", "NA", ...]` per categorical feature — use this as the source for `category_map`

### Phase 14 patterns
- `.planning/phases/14-cli-binary-target/14-CONTEXT.md` — Docker-exec invocation pattern, workflow step structure

### Prior phase patterns
- `.claude/doml/workflows/deploy-cli.md` — reference for workflow step structure and `gsd-tools.cjs` commit pattern
- `.claude/skills/doml-deploy-web/SKILL.md` — reference SKILL.md format for new `doml-deploy-wasm` skill

### Data contracts
- `src/<modelname>/vN/deployment_metadata.json` — fields: `model_file`, `model_name`, `target`, `build_date`, `version`, `feature_schema` (`[{name, type, categories}]`)
- `models/best_model.pkl` — sklearn Pipeline; full Pipeline (ColumnTransformer + estimator) exported to ONNX
- `data/processed/preprocessed_*.csv` — not read by this phase (categories already in `deployment_metadata.json`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `gsd-tools.cjs` commit helper — same pattern as all other doml workflows
- `docker compose exec jupyter python3 -c "..."` — established Docker-exec pattern (Phase 14 PyInstaller, Phase 15 category scan)
- `deployment_metadata.json` feature_schema with `categories` — already populated by Phase 13+15; read directly for D-03 category_map

### Established Patterns
- SKILL.md structure: `name`, `description`, `argument-hint`, `allowed-tools`, `<objective>`, `<execution_context>`, `<context>`, `<process>` — must match existing doml skill files exactly
- Workflow steps numbered with `### Step N —` header
- Config read via: `python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))"`

### Integration Points
- Reads from: `src/<modelname>/vN/deployment_metadata.json` (written by Phase 13)
- Writes to: `src/<modelname>/vN/model.onnx`, `src/<modelname>/vN/index.html`
- Runs ONNX conversion inside Docker (skl2onnx must be added to requirements.in template)
- Downloads ORT JS+WASM binaries at generation time (not at browser-open time)
- Does NOT modify `deploy-model.md`
- Service port: N/A — no server; user opens `index.html` directly in browser (via `file://` or double-click)

</code_context>

<specifics>
## Specific Ideas

- skl2onnx conversion: replace categorical OHE columns in the Pipeline copy with `OrdinalEncoder` before export, so the ONNX graph accepts float32 for all inputs. Build `category_map` from `deployment_metadata.json` `categories` field at the same time.
- ORT WASM path override: `ort.env.wasm.wasmPaths = { 'ort-wasm.wasm': WASM_DATA_URI };` where `WASM_DATA_URI` is the embedded base64 blob
- Tensor construction in JS: iterate `feature_schema` in order, look up each feature's value from the form — numerics as `parseFloat`, categoricals via `CATEGORIES[name][value]` — build a flat `Float32Array` and create a single 2D `ort.Tensor('float32', data, [1, n_features])`
- ONNX session creation: `const session = await ort.InferenceSession.create(MODEL_BUFFER);` where `MODEL_BUFFER` is `Uint8Array.from(atob(MODEL_B64), c => c.charCodeAt(0))`
- Size gate: compute in Python — `import base64, os; total = len(ort_js_text.encode()) + len(base64.b64encode(wasm_bytes)) + len(base64.b64encode(onnx_bytes))` — compare to `20 * 1024 * 1024`
- skl2onnx dependency: add `skl2onnx` to requirements.in template (same pattern as pyinstaller in Phase 14 D-02)

</specifics>

<deferred>
## Deferred Ideas

- String tensor support — deferred; ordinal encoding is the reliable path for onnxruntime-web
- Progressive Web App manifest — deferred to future milestone per REQUIREMENTS.md
- Multi-worker / streaming WASM inference — not applicable for this target
- Windows/macOS Docker for ONNX conversion — Linux container is the standard; same Docker-exec pattern as Phase 14
- SHAP explanations in the WASM page — deferred to future milestone per REQUIREMENTS.md

</deferred>

---

*Phase: 16-onnx-wasm-target*
*Context gathered: 2026-04-16*
