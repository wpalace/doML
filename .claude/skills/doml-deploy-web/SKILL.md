---
name: doml-deploy-web
description: "Deploy the top leaderboard model as a FastAPI web service. Reads src/<modelname>/vN/deployment_metadata.json (created by /doml-deploy-model), generates app.py (dynamic Pydantic model, /predict, /health, /schema, / endpoints), a Jinja2 prediction form template, requirements.serve.txt, Dockerfile.serve, and docker-compose.serve.yml. Running docker compose -f docker-compose.serve.yml up starts the service on port 8080 with no additional setup. Supports --deploy-dir path/to/vN to target a specific deployment directory."
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
Generate all web service artifacts for the DoML deployed model:

1. Validate project state and locate the deployment directory
2. Read deployment_metadata.json for model_file, model_name, version, feature_schema, problem_type
3. Check that src/ is mounted in docker-compose.yml; warn if not (informational only — not a blocker)
4. Copy the model file to the deployment directory as model.pkl
5. Generate app.py — FastAPI app with dynamic Pydantic request model and all four endpoints
6. Generate templates/index.html — Jinja2 prediction form with typed inputs and inline-fetch submission
7. Generate requirements.serve.txt — pinned Python dependencies
8. Generate Dockerfile.serve — python:3.14-slim base image
9. Generate docker-compose.serve.yml — maps host port 8080 to container port 8080
10. Update deployment_metadata.json with web_service_port: 8080
</objective>

<execution_context>
@.claude/doml/workflows/deploy-web.md
</execution_context>

<context>
Arguments (optional): $ARGUMENTS
</context>

<process>
Execute the deploy-web workflow from @.claude/doml/workflows/deploy-web.md end-to-end.
</process>
