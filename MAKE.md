# MAKE.md: develop and test DoML

This file is the single entry point for an agent that develops or tests DoML.
The text uses ASD-STE100 Simplified Technical English.

## 1. Know the parts

| Part | Location |
|---|---|
| Notebook templates (marimo `.py` files) | `.claude/doml/templates/notebooks/` |
| Notebook helper (run, narrative, verify) | `.claude/doml/bin/doml_nb.py` |
| Workflows (agent instructions) | `.claude/doml/workflows/*.md` |
| Skills (slash commands) | `.claude/skills/doml-*/SKILL.md` |
| Image and dependencies | `.claude/doml/templates/{Dockerfile,compose.yaml,pyproject.toml,uv.lock,requirements.txt}` |
| Installers | `install.sh`, `install.ps1` |
| Tests | `tests/` (`tests/run_all.sh` runs all of them) |

The root `Dockerfile`, `compose.yaml`, `pyproject.toml`, `uv.lock` and `requirements.txt` are
copies of the templates. Keep them the same.

## 2. Get the tools

You must have these tools:

- `uv` 0.11 or later.
- Docker Engine with the compose plugin.
- `bash` 5.

These tools are optional. When a tool is not there, the related check is skipped:

- `pwsh` (tests `install.ps1`).
- `shellcheck` and `shfmt` (lint the shell scripts).

## 3. Run all tests

Do this command from the repository root:

```bash
tests/run_all.sh
```

The script makes `.venv` from `requirements.txt`. Then it runs each stage and shows a summary.
A full run takes approximately 30 minutes. The Docker build and the deploy stage use most of the time.

To run only some stages, write their names:

```bash
tests/run_all.sh unit check install
```

| Stage | What it does |
|---|---|
| `unit` | Runs `pytest` on `tests/`. |
| `check` | Runs `marimo check --strict` on all notebook templates. |
| `e2e` | Runs the full pipeline for each problem type in `.venv`, with sample data. |
| `install` | Runs `install.sh` (and `install.ps1`) for the claude and copilot targets. Then it examines the trees. |
| `build` | Builds the image. It shows the build time, the size and the package count. |
| `docker-e2e` | Runs the full pipeline for each problem type in the container. `data/raw` is read-only. |
| `deploy` | Runs the deploy workflows (CLI, web, ONNX/WASM) and the performance report. Run `docker-e2e` first. |
| `kaggle` | Downloads a small public dataset with the get-data workflow. It needs Kaggle credentials. |
| `lint` | Runs `shellcheck`, `shfmt` and `ruff` when they are available. |
| `grep` | Makes sure that no R or Jupyter references remain. |

To keep the scratch files, set `DOML_WORK` to a directory.
To test fewer problem types, set `DOML_E2E_KINDS`. Example: `DOML_E2E_KINDS="regression" tests/run_all.sh e2e`.

## 4. Change a notebook template

1. Edit the `.py` file in `.claude/doml/templates/notebooks/`.
2. Define each variable in one cell only. Use a `_` prefix for names that stay in one cell.
3. Do `uv run marimo check --fix <file>`. This updates the cell signatures.
4. Do `tests/run_all.sh check e2e`.

Do not put outputs or results in a notebook. Reports go to `reports/*.html`.
Narrative text goes to `notebooks/narratives/<notebook>/<section>.md`.

## 5. Change a dependency

1. Edit `dependencies` in `.claude/doml/templates/pyproject.toml`.
2. In `.claude/doml/templates/`, do these commands:

   ```bash
   uv lock
   uv export --frozen --no-emit-project --no-dev -o requirements.txt
   ```

3. Copy `pyproject.toml`, `uv.lock` and `requirements.txt` to the repository root.
4. Do `tests/run_all.sh build docker-e2e`.

## 6. Change a workflow or a skill

1. Edit the Markdown file.
2. Use `docker compose exec -T doml ...` for commands in the container. The `-T` is necessary because agents have no terminal.
3. Use `.claude/doml/...` paths only. The copilot installer changes them to `.github/doml/...`.
4. If you change a deploy workflow, do `tests/run_all.sh docker-e2e deploy`.
   The deploy tests run the bash blocks of the workflow files. Do not change the order of the bash blocks without a check of `tests/e2e/deploy_paths.sh`.

## 7. Keep secrets safe

- Do not write a credential into a file in the repository.
- Do not show a credential in test output.
- Give a credential to Docker by its name only. Example: `docker run -e KAGGLE_API_TOKEN ...`.

## 8. Before you commit

1. Do `tests/run_all.sh unit check install lint grep`.
2. Make sure that all stages show `PASS`.
3. Do not push or open a pull request unless the owner tells you to do it.
