---
name: doml-deploy-model
description: "Deploy the top leaderboard model to a chosen target. Reads models/leaderboard.csv (or models/unsupervised_leaderboard.csv for clustering) to resolve the #1 model, prompts interactively for deployment target (CLI binary / Web service (FastAPI + Docker) / ONNX/WASM page), creates src/modelname/vN/ with deployment_metadata.json. Supports --model path/to/model.pkl to override the default model selection."
argument-hint: "[--model path/to/model.pkl]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Deploy the DoML model to a chosen target end-to-end:

1. Validate project state and read config.json
2. Parse --model flag if supplied; otherwise resolve #1 from leaderboard
3. Ensure model_metadata.json has a model_name field (derive from pkl if absent)
4. Derive MODEL_SLUG (filesystem-safe: lowercase, underscores, no parens)
5. Prompt user to select a deployment target: CLI binary / Web service / ONNX/WASM page
6. Scan src/modelname/ for existing vN directories; write to vN+1 if any exist
7. Announce version bump if applicable, then create src/modelname/vN/
8. Write deployment_metadata.json with model_file, model_name, target, build_date, version, feature_schema
9. Update STATE.md and confirm to the user
</objective>

<execution_context>
@.claude/doml/workflows/deploy-model.md
</execution_context>

<context>
Arguments (optional): $ARGUMENTS
</context>

<process>
Execute the deploy-model workflow from @.claude/doml/workflows/deploy-model.md end-to-end.
</process>
