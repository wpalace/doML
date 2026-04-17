---
name: doml-iterate-deployment
description: "Iterate an existing deployment to a new version without re-running /doml-deploy-model from scratch. Validates the leaderboard leader matches the last deployed model, scans src/<modelname>/v*/ for the current highest version, and writes to vN+1. Accepts --model path/to/model.pkl (different model → new src/<newmodelname>/v1/), --target {cli|web|wasm} (override target), and --guidance \"text\" (freeform direction applied to configuration before deployment). Regenerates deployment_report.ipynb and deployment_report.html for the new version."
argument-hint: "[--model path/to/model.pkl] [--target {cli|web|wasm}] [--guidance \"text\"]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Iterate an existing DoML deployment to a new version end-to-end:

1. Validate project state (.planning/STATE.md) and read config.json
2. Parse --model, --target, and --guidance flags from $ARGUMENTS
3. Re-read leaderboard (models/leaderboard.csv or unsupervised_leaderboard.csv) and compare the resolved model_file against model_file in the most recent deployment_metadata.json under src/ — stop with a redirect message if they differ and --model was not supplied
4. Ensure model_metadata.json has a model_name field (derive from pkl class name if absent)
5. Derive MODEL_SLUG (filesystem-safe: lowercase, underscores, no parens)
6. Resolve deployment target from --target flag or target field in most recent deployment_metadata.json
7. Scan src/<modelname>/v*/ for existing versions; announce version bump; write to vN+1
8. Read feature_schema from data/processed/preprocessed_* (or fall back to model_metadata.json feature_names)
9. Apply --guidance: Claude reads the guidance text and notes configuration adjustments before delegating to the target skill
10. Create src/<modelname>/vN+1/ and write deployment_metadata.json (fields: model_file, model_name, target, problem_type, build_date, version, feature_schema; optionally guidance)
11. Delegate to target skill: @.claude/doml/workflows/deploy-cli.md, deploy-web.md, or deploy-wasm.md passing --deploy-dir src/${MODEL_SLUG}/v${VERSION}
12. Generate performance report: copy deployment_report.ipynb template, execute in Docker, inject Claude narrative, generate reports/deployment_report.html
13. Update STATE.md and confirm to user
</objective>

<execution_context>
@.claude/doml/workflows/iterate-deployment.md
</execution_context>

<context>
Arguments (optional): $ARGUMENTS
</context>

<process>
Execute the iterate-deployment workflow from @.claude/doml/workflows/iterate-deployment.md end-to-end.
</process>
