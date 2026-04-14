---
name: doml-deploy-cli
description: "Build a self-contained Linux CLI binary from a deployed model. Reads src/<modelname>/vN/deployment_metadata.json (created by /doml-deploy-model), generates predict.py with argparse input handling and predict.spec with PyInstaller onedir packaging, then runs the build inside the existing Jupyter Docker container to produce dist/predict/predict. Supports --deploy-dir path/to/vN to target a specific deployment directory."
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
Generate a self-contained Linux CLI binary for the DoML deployed model:

1. Validate project state and locate the deployment directory
2. Read deployment_metadata.json for model_file, model_name, version, feature_schema, problem_type
3. Read the first data row of data/processed/preprocessed_*.csv for example values (D-03)
4. Check that src/ is mounted in docker-compose.yml; warn and instruct if not
5. Verify pyinstaller is installed in the container; instruct how to install if not
6. Generate predict.py from embedded template (argparse, --input JSON/file, --output, exit codes 0/1/2)
7. Generate predict.spec from embedded template (collect_all sklearn + joblib, onedir, bundle model)
8. Run PyInstaller build: docker compose exec jupyter bash -c "cd .../vN && pyinstaller predict.spec"
9. Verify dist/predict/predict exists after build
10. Update deployment_metadata.json with "platform": "linux-x86_64"
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
