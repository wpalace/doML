---
name: doml-deploy-wasm
description: "Deploy the top leaderboard model as a self-contained ONNX/WebAssembly browser page. Reads src/<modelname>/vN/deployment_metadata.json (created by /doml-deploy-model), converts the full sklearn Pipeline to ONNX via skl2onnx inside Docker (replacing OHE with OrdinalEncoder for float32-only inputs), downloads onnxruntime-web 1.17.3 binaries, enforces the 20 MB bundle size gate, and generates a self-contained index.html that runs inference in any browser with no server and no network requests. Supports --deploy-dir path/to/vN to target a specific deployment directory."
argument-hint: "[--deploy-dir src/<modelname>/vN]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Generate all ONNX/WASM artifacts for the DoML deployed model:

1. Validate project state and locate the deployment directory
2. Read deployment_metadata.json for model_file, model_name, version, feature_schema (with categories), problem_type
3. Block unsupported problem types: forecasting and DBSCAN clustering (WASM-04)
4. Check Docker container is running and skl2onnx is available inside the container
5. Run ONNX conversion inside Docker — full sklearn Pipeline exported as single ONNX graph with float32-only inputs (D-02, D-03)
6. Download onnxruntime-web 1.17.3 binaries (ort.min.js + ort-wasm.wasm) at generation time; cache in /tmp/doml_ort_1.17.3/
7. Enforce 20 MB size gate over (ORT JS text + WASM base64 + model.onnx base64); suggest web service target if exceeded (WASM-05)
8. Generate src/<modelname>/vN/index.html — ORT JS inlined, WASM as base64 blob URL, model as base64, prediction form auto-generated from feature_schema
9. Update deployment_metadata.json with index_html path
10. Update STATE.md and display summary with open instructions
</objective>

<execution_context>
@.claude/doml/workflows/deploy-wasm.md
</execution_context>

<context>
Arguments (optional): $ARGUMENTS
</context>

<process>
Execute the deploy-wasm workflow from @.claude/doml/workflows/deploy-wasm.md end-to-end.
</process>
