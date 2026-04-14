# Phase 14: CLI Binary Target — Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate `predict.py` (argparse-based), a PyInstaller spec file, and run the PyInstaller build inside the existing jupyter Docker container to produce a `dist/predict/predict` Linux binary — self-contained, no Python required on the target machine.

Phase 14 reads from `src/<modelname>/vN/deployment_metadata.json` (produced by Phase 13) and populates that directory with `predict.py`, `predict.spec`, and `dist/predict/`.

**Requirements in scope:** CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06

</domain>

<decisions>
## Implementation Decisions

### Binary Packaging

- **D-01: `--onedir` packaging**
  - PyInstaller spec uses `--onedir` (not `--onefile`)
  - Produces `dist/predict/` directory containing a `predict` executable
  - Success criteria SC-3 and SC-4 verify the presence and correctness of `dist/predict/predict` (the executable inside the directory)
  - Rationale: faster startup, more reliable than `--onefile`'s temp-dir extraction; matches roadmap spec

### Input Schema

- **D-02: Preprocessed-schema input**
  - The binary accepts data in the format of `data/processed/preprocessed_*` — cleaned/tidy feature values matching what the sklearn Pipeline expects
  - The Pipeline (ColumnTransformer + model) handles encoding, scaling, and imputation internally
  - Users are responsible for applying the same Phase 2 cleaning steps to new data before feeding the binary
  - This means: `feature_schema` reflects preprocessed column names and types (not raw)

### `--help` Example Values

- **D-03: Embed example values at generation time**
  - When `predict.py` is generated, read the first row of `data/processed/preprocessed_*.csv`
  - Hardcode those values into the argparse `--help` strings for each feature
  - The binary is fully self-contained — no runtime file dependency for help display
  - Source: `feature_schema` in `deployment_metadata.json` gives names and types; first preprocessed row gives example values

### Output Format

- **D-04: Classification returns label + probabilities**
  - Single prediction JSON: `{"prediction": "class_a", "probabilities": {"class_a": 0.85, "class_b": 0.15}}`
  - Uses `Pipeline.predict()` for the label and `Pipeline.predict_proba()` for probabilities
  - Other problem types (regression, clustering) return `{"prediction": <value>}` only

- **D-05: Batch output is input columns + prediction column(s)**
  - `--output <path>` writes a CSV that mirrors the input with a `prediction` column appended
  - For classification: also appends one `prob_<class>` column per class (from `predict_proba`)
  - Easy for users to trace which row got which prediction

### Build Container

- **D-06: Reuse existing jupyter container for PyInstaller build**
  - Build runs via `docker compose exec jupyter pyinstaller predict.spec`
  - No separate Dockerfile or build image — sklearn, joblib, and all dependencies already installed
  - Binary targets Linux x86_64 matching the container architecture; `deployment_metadata.json` records `"platform": "linux-x86_64"`

### Claude's Discretion

- Exact argparse structure for `predict.py` (subcommands vs flat flags)
- Whether to use `argparse.RawDescriptionHelpFormatter` or a custom formatter for feature schema display
- Error message wording for exit codes 1 (input validation) and 2 (model error)
- Whether to detect `--input` path vs JSON string by attempting `json.loads()` first or checking for file existence

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §CLI — CLI-01 through CLI-06 define all acceptance criteria for this phase

### Phase 13 outputs
- `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — Phase 13 decisions; `feature_schema` format, directory structure, `deployment_metadata.json` fields
- `.claude/doml/workflows/deploy-model.md` — produces `src/<modelname>/vN/deployment_metadata.json` with `model_file`, `model_name`, `target`, `build_date`, `version`, `feature_schema`

### Prior phase patterns
- `.claude/doml/workflows/modelling.md` — how sklearn Pipeline is built; confirms `.predict()` and `.predict_proba()` are available
- `.claude/skills/doml-deploy-model/SKILL.md` — reference skill structure for SKILL.md format

### Data contracts
- `src/<modelname>/vN/deployment_metadata.json` — fields: `model_file`, `model_name`, `target`, `build_date`, `version`, `feature_schema` (`[{name, type}]`)
- `data/processed/preprocessed_*.csv` — source of example values for `--help`; first row used at predict.py generation time
- `models/best_model.pkl` — sklearn Pipeline; accepts preprocessed-schema input

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `gsd-tools.cjs` commit helper — used by all doml workflows for committing artifacts; same pattern applies
- `AskUserQuestion` pattern — all interactive doml commands use it; follow the same header/options structure
- `docker compose exec jupyter` invocation — established pattern across modelling/iterate workflows for running Python inside container

### Established Patterns
- SKILL.md structure: `name`, `description`, `argument-hint`, `allowed-tools`, `<objective>`, `<execution_context>`, `<context>`, `<process>` — must match existing doml skill files exactly
- Workflow steps numbered with `### Step N —` header
- Config read via: `python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))"`

### Integration Points
- Reads from: `src/<modelname>/vN/deployment_metadata.json`, `data/processed/preprocessed_*.csv` (for example values)
- Writes to: `src/<modelname>/vN/predict.py`, `src/<modelname>/vN/predict.spec`, `src/<modelname>/vN/dist/predict/`
- Updates: `src/<modelname>/vN/deployment_metadata.json` — adds `"platform": "linux-x86_64"` after build
- Build invocation: `docker compose exec jupyter bash -c "cd src/<modelname>/vN && pyinstaller predict.spec"`

</code_context>

<specifics>
## Specific Ideas

- The `--input` flag should accept both a JSON string (`--input '{"age": 35, "income": 50000}'`) and a file path (`--input data.csv` or `--input data.json`) — detect by attempting `json.loads()` first, fall back to file path
- For batch file input: CSV auto-detected by extension; JSON file expected as array of objects
- `--help` feature schema display should be human-readable, not a raw JSON dump — e.g., `age (int, e.g. 35)`, `income (float, e.g. 50000.0)`
- PyInstaller spec must include `--collect-all sklearn`, `--collect-all joblib` per roadmap success criteria SC-2
- `deployment_metadata.json` must be updated with `"platform": "linux-x86_64"` after successful build (success criterion SC-7)

</specifics>

<deferred>
## Deferred Ideas

- Windows/macOS binaries — out of scope for v1.4 (Linux only, built in Docker); listed in REQUIREMENTS.md Future Requirements
- Single-file `--onefile` packaging — decided against in favour of `--onedir`; can revisit in a future iteration if distribution simplicity becomes a priority

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 14-cli-binary-target*
*Context gathered: 2026-04-14*
