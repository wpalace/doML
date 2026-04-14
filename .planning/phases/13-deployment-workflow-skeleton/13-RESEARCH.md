# Phase 13: Deployment Workflow Skeleton — Research

**Researched:** 2026-04-14
**Domain:** DoML skill/workflow authoring, file I/O, model metadata management
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: No `--target` flag — always interactive**
  - Target selection is always via AskUserQuestion menu (CLI binary / Web service / ONNX/WASM)
  - No `--target` flag on the command — every invocation prompts the user interactively

- **D-02: Auto-increment version with announcement**
  - When `src/<modelname>/v1/` already exists, scan for highest existing `vN` and write to `vN+1`
  - Before creating, print: `"src/<modelname>/v1/ exists — deploying to v2/"` (or whichever version)
  - No confirmation pause — just announce and continue
  - Version scanning is from the filesystem, not assumed (matches ITER-02 pattern in doml-iterate)

- **D-03: Leaderboard-based #1 model resolution (default)**
  - Reads `models/leaderboard.csv` (supervised) or `models/unsupervised_leaderboard.csv` (unsupervised/clustering)
  - `--model <file>` flag overrides and uses the specified model file directly (DEPLOY-02)
  - If no leaderboard file and no `--model` flag: stop with a message directing user to run `/doml-modelling` first

- **D-04: `model_name` derivation (DEPLOY-05)**
  - Check if `model_metadata.json` already has a `model_name` field
  - If missing: load the `.pkl` artifact, call `type(model).__name__`, and add `model_name` to the JSON
  - Write the updated `model_metadata.json` in-place — no other fields modified

- **D-05: Directory + metadata only — no stub files**
  - Phase 13 creates `src/<modelname>/vN/` and writes `deployment_metadata.json` inside it
  - No placeholder `predict.py`, `Dockerfile`, or HTML stubs — those are Phase 14/15/16 responsibilities
  - `deployment_metadata.json` fields: `model_file`, `target`, `build_date`, `feature_schema`, `model_name`, `version`

- **Specific ideas (from CONTEXT.md `<specifics>`):**
  - `model_name` slug: strip parentheses, replace spaces with underscores, lowercase
    (e.g., `"XGBoost (tuned)"` → `xgboost_tuned`)
  - Interactive target menu labels match REQUIREMENTS.md exactly: "CLI binary", "Web service (FastAPI + Docker)", "ONNX/WASM page"
  - `feature_schema` is the full list of `{name, type}` objects (not just names)

### Claude's Discretion

- Exact format of the `model_name` slug (lowercase + underscores is fine)
- Whether to sanitize `model_name` for filesystem safety (strip spaces/parens)
- Step ordering within the workflow (validation before or after target selection)

### Deferred Ideas (OUT OF SCOPE)

- Problem type scope edge cases for clustering and forecasting (handled via config.json routing)
- `--model` override UI beyond the straightforward flag implementation
- No additional deferred items stated

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEPLOY-01 | User can run `doml-deploy-model` to deploy the #1 leaderboard model to a chosen target without specifying a model file | SKILL.md entry point pattern from doml-modelling; leaderboard read pattern from modelling.md |
| DEPLOY-02 | User can override the default model selection with a specific model file or leaderboard rank | `--model <file>` argument parsing pattern from doml-forecasting (`--horizon`, `--target` parsing) |
| DEPLOY-03 | User can choose a deployment target (CLI binary, web service, ONNX/WASM) at run time | AskUserQuestion interactive menu pattern from all existing doml commands |
| DEPLOY-04 | Deployed artifacts written to `src/<modelname>/v1/` with `deployment_metadata.json` | Version scanning pattern from iterate.md (Step 4); mkdir + json.dump pattern |
| DEPLOY-05 | `model_metadata.json` extended with a `model_name` field (derived from estimator class name if not present) | `joblib.load()` + `type(model).__name__` pattern; in-place JSON update pattern |

</phase_requirements>

---

## Summary

Phase 13 implements the `doml-deploy-model` command as two files: a SKILL.md entry point and a `deploy-model.md` workflow. The workflow is pure Python file I/O — it reads leaderboard CSVs and `model_metadata.json`, creates the `src/<modelname>/vN/` directory tree, and writes `deployment_metadata.json`. No Docker execution, no notebook generation.

The implementation follows patterns already established across Phases 8–12. The SKILL.md format is fully defined by the doml-modelling reference. The version-scan-then-increment pattern is established in iterate.md Step 4. The `--model` argument parsing mirrors doml-forecasting's flag handling. AskUserQuestion for interactive menus mirrors every other doml command.

The only genuinely new work is the `model_name` derivation (loading a `.pkl` with `joblib.load()` and calling `type(model).__name__`), the filesystem slug sanitization, and the `deployment_metadata.json` schema.

**Primary recommendation:** Two files to create: `.claude/skills/doml-deploy-model/SKILL.md` and `.claude/doml/workflows/deploy-model.md`. All patterns needed are already in the codebase.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `joblib` | Already pinned in requirements.txt | Load `.pkl` model artifacts | scikit-learn uses joblib for serialization; already the project standard |
| `json` (stdlib) | — | Read/write `model_metadata.json` and `deployment_metadata.json` | Stdlib, no dependency |
| `pathlib` (stdlib) | — | Filesystem path manipulation, directory creation | REPR-02 compliance; cleaner than os.path |
| `datetime` (stdlib) | — | `build_date` ISO 8601 timestamp in deployment_metadata.json | Stdlib |
| `re` (stdlib) | — | Slug sanitization regex | Stdlib |
| `pandas` | Already pinned | Read leaderboard CSV | Already the project standard; used in iterate.md |

[VERIFIED: codebase grep — joblib is used in modelling notebooks; pandas is pinned in requirements.txt; all stdlib modules confirmed available]

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `glob` (stdlib) | — | Version scanning for existing `vN/` directories | Used in iterate.md Step 4 — identical pattern |
| `os` (stdlib) | — | `os.path.exists()` for pre-flight checks | Used everywhere in existing workflows |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `joblib.load()` for pkl | `pickle.load()` | joblib is already the sklearn serialization standard; stick with joblib |
| `pandas` for leaderboard | `duckdb` or `csv` module | pandas is already used in iterate.md for this exact purpose; consistency wins |

**Installation:** No new packages needed. All dependencies are already in `requirements.txt`.

---

## Architecture Patterns

### Recommended Project Structure (files to create)

```
.claude/
├── skills/
│   └── doml-deploy-model/
│       └── SKILL.md               # Entry point for /doml-deploy-model
└── doml/
    └── workflows/
        └── deploy-model.md        # Workflow orchestration (10–11 steps)
src/
└── <modelname>/                   # Created at runtime by the workflow
    └── v1/
        └── deployment_metadata.json
```

### Pattern 1: SKILL.md Entry Point Format

**What:** Every doml command has a SKILL.md with YAML frontmatter + four XML sections
**When to use:** Always — this is the required format for Claude Code skill registration

**Example (from doml-modelling — the canonical reference):**
```yaml
# Source: .claude/skills/doml-modelling/SKILL.md [VERIFIED: codebase]
---
name: doml-deploy-model
description: "Deploy the #1 leaderboard model to a chosen target. Reads models/leaderboard.csv,
  prompts for deployment target (CLI binary / Web service / ONNX/WASM), creates
  src/<modelname>/v1/ with deployment_metadata.json. Supports --model <file> to override
  the default model selection."
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
[single-paragraph objective]
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
```

### Pattern 2: Workflow Step Header Convention

**What:** Each step uses `### Step N — [Action verb] [object]` header
**When to use:** Every step in every workflow file

```markdown
# Source: .claude/doml/workflows/iterate.md [VERIFIED: codebase]
### Step 1 — Read config.json and determine problem type
### Step 2 — Find most recent modelling notebook for this problem type
```

### Pattern 3: config.json Problem Type Routing

**What:** Read problem_type from config.json in a one-liner bash snippet; route with if/elif/else
**When to use:** Any step that needs to know problem type

```bash
# Source: .claude/doml/workflows/modelling.md [VERIFIED: codebase]
PROBLEM_TYPE=$(python3 -c "import json; c=json.load(open('.planning/config.json')); print(c.get('problem_type','regression'))")
```

For Phase 13, use this to decide which leaderboard CSV to read:
- `regression` / `classification` → `models/leaderboard.csv`
- `clustering` / `dimensionality_reduction` → `models/unsupervised_leaderboard.csv`
- `time_series` → `models/forecast_leaderboard.csv` (forecasting phase output)

### Pattern 4: Version Scanning (ITER-02 pattern from iterate.md)

**What:** Glob existing directories, extract version numbers, increment max
**When to use:** Any time a versioned directory needs to be created

```python
# Source: .claude/doml/workflows/iterate.md Step 4 [VERIFIED: codebase]
# Adapted for src/<modelname>/vN/ directories:
VERSION=$(python3 -c "
import glob, re
model_slug = '${MODEL_SLUG}'
pattern = f'src/{model_slug}/v*'
existing = glob.glob(pattern)
versions = [int(re.search(r'/v(\d+)$', d).group(1)) for d in existing if re.search(r'/v(\d+)$', d)]
print(max(versions) + 1 if versions else 1)
")
```

Announcement before creation (D-02):
```bash
if [ "$VERSION" -gt 1 ]; then
  echo "src/${MODEL_SLUG}/v$(($VERSION - 1))/ exists — deploying to v${VERSION}/"
fi
```

### Pattern 5: Leaderboard #1 Model Resolution

**What:** Read leaderboard CSV, get the top-ranked model file path
**When to use:** Default model selection (DEPLOY-01)

```bash
# Source: modelling.md leaderboard verification pattern [VERIFIED: codebase]
# Adapted for model resolution:
MODEL_FILE=$(python3 -c "
import pandas as pd, os
lb = pd.read_csv('models/leaderboard.csv')
# Sort ascending for regression (lower RMSE = better), descending for classification (higher AUC = better)
# The leaderboard template already sorts best model first — read row 0
top_model = lb.iloc[0]
model_file = top_model.get('model_file', 'models/best_model.pkl')
print(model_file)
")
```

**Note:** The exact column name for the model file path in leaderboard.csv must be confirmed
against the actual template output. The modelling notebook templates write `models/best_model.pkl`
as the primary artifact. `model_metadata.json` also records the model file path. Reading from
`model_metadata.json` is more reliable than the leaderboard CSV for the file path.

[ASSUMED] The leaderboard CSV has a `model` column with the model name and a separate
`model_file` column with the file path. If only the model name is in the leaderboard, the
workflow should derive the path from `model_metadata.json` or default to `models/best_model.pkl`.

### Pattern 6: model_name Derivation (DEPLOY-05)

**What:** Load pkl, get class name, sanitize to filesystem-safe slug
**When to use:** When `model_metadata.json` lacks `model_name` field; also for directory naming

```python
# Pattern: load model and derive name [ASSUMED — standard Python/sklearn pattern]
import joblib, re, json

def get_model_name(pkl_path, metadata_path):
    with open(metadata_path) as f:
        meta = json.load(f)
    
    if 'model_name' in meta:
        raw_name = meta['model_name']
    else:
        model = joblib.load(pkl_path)
        raw_name = type(model).__name__
        # Write back to model_metadata.json in-place
        meta['model_name'] = raw_name
        with open(metadata_path, 'w') as f:
            json.dump(meta, f, indent=2)
    
    return raw_name

def slugify_model_name(raw_name):
    # Strip parentheses and their contents: "XGBoost (tuned)" → "XGBoost tuned"
    slug = re.sub(r'\([^)]*\)', '', raw_name)
    # Replace spaces and special chars with underscores
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', slug)
    # Lowercase
    slug = slug.strip('_').lower()
    return slug  # e.g., "xgboost_tuned", "xgbregressor", "kmeans"
```

### Pattern 7: deployment_metadata.json Schema

**What:** The canonical output file written to `src/<modelname>/vN/`
**When to use:** Always — this is the contract for downstream Phases 14–16

```json
{
  "model_file": "models/best_model.pkl",
  "model_name": "XGBRegressor",
  "target": "cli_binary",
  "build_date": "2026-04-14T16:24:19Z",
  "version": "v1",
  "feature_schema": [
    {"name": "age", "type": "float64"},
    {"name": "category", "type": "object"}
  ]
}
```

`feature_schema` is sourced from `model_metadata.json` → `feature_names` + dtype information.
[ASSUMED] The `model_metadata.json` template from Phase 6 stores `feature_names` as a list of strings.
The dtype information may need to be sourced from the preprocessed dataset or inferred from the model's
ColumnTransformer. The simplest approach: store `[{"name": col, "type": str(dtype)}]` read from the
preprocessed dataset's column dtypes.

### Pattern 8: AskUserQuestion for Target Selection

**What:** Interactive menu matching REQUIREMENTS.md labels exactly
**When to use:** DEPLOY-03 — always prompt (D-01: no --target flag)

```
# Pattern from anomaly-detection.md and business-understanding.md [VERIFIED: codebase]
Ask the user with AskUserQuestion:

"Select deployment target:"
Options:
  1. CLI binary
  2. Web service (FastAPI + Docker)  
  3. ONNX/WASM page

Store the result as TARGET_LABEL (display string) and TARGET_KEY (internal key for metadata):
  "CLI binary"                    → target_key = "cli_binary"
  "Web service (FastAPI + Docker)" → target_key = "web_service"
  "ONNX/WASM page"               → target_key = "onnx_wasm"
```

### Pattern 9: STATE.md Update (end-of-workflow pattern)

**What:** Append decision entry to STATE.md Decisions section; update last_activity
**When to use:** Final step of every doml workflow

```bash
# Source: modelling.md Step 9 pattern [VERIFIED: codebase]
# Write to .planning/STATE.md:
# - Update stopped_at to reflect deployment complete
# - Append: [Phase 13]: doml-deploy-model completed — {MODEL_SLUG} v{VERSION} → {TARGET}
# - Update last_activity with today's date
```

### Pattern 10: Argument Parsing for --model Flag

**What:** Parse $ARGUMENTS for `--model <file>` flag
**When to use:** Step 2 of deploy-model.md (DEPLOY-02)

```bash
# Source: forecasting.md argument parsing pattern [VERIFIED: codebase — forecasting.md uses
# this exact pattern for --horizon and --target flags]
MODEL_OVERRIDE=""
if echo "$ARGUMENTS" | grep -q -- '--model'; then
  MODEL_OVERRIDE=$(echo "$ARGUMENTS" | sed 's/.*--model[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi
```

### Anti-Patterns to Avoid

- **Never shell-interpolate user-supplied strings** — the `--model` path should only be used in Python file existence checks via `os.path.exists()`, never in `eval` or `$(...)` expansion
- **Never hardcode version numbers** — always glob `src/<modelname>/v*` and increment max (D-02, ITER-02)
- **Never run Docker** — Phase 13 is pure file I/O; no `docker compose exec jupyter` calls
- **Never create stub files** — `predict.py`, `Dockerfile`, etc. are Phase 14/15/16 responsibilities (D-05)
- **Never overwrite existing metadata fields** — when updating `model_metadata.json`, only add `model_name`; use `json.load` → add key → `json.dump` in-place
- **Never commit raw data or model pickles** — `.gitignore` already excludes `models/*.pkl`

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Model file loading | Custom unpickler | `joblib.load()` | sklearn uses joblib internally; handles Pipeline objects and custom transformers correctly |
| Leaderboard reading | Custom CSV parser | `pd.read_csv()` | Already the project standard; handles the leaderboard format produced by notebook templates |
| Directory creation | Manual `os.makedirs` call chain | `pathlib.Path.mkdir(parents=True, exist_ok=True)` | One call handles nested creation; idempotent |
| JSON read/write | Custom serializer | `json.load()` / `json.dump(indent=2)` | Stdlib; consistent with all existing metadata patterns |
| Slug sanitization | Complex regex engine | Two `re.sub()` calls (strip parens, replace non-alnum) | Simple, readable, tested against known model names |

**Key insight:** The entire Phase 13 workflow is orchestration of stdlib + already-pinned libraries. No new dependencies are needed.

---

## Common Pitfalls

### Pitfall 1: Leaderboard column schema assumptions

**What goes wrong:** The workflow tries to read `model_file` column from leaderboard.csv, but the modelling notebook template writes only `model` (the model name) and CV metrics — not the file path.

**Why it happens:** The leaderboard is designed for model comparison, not deployment; file paths are tracked in `model_metadata.json`, not the leaderboard.

**How to avoid:** Read `model_metadata.json` for the model file path. Use the leaderboard only to identify which model name is ranked #1. Then cross-reference with `model_metadata.json` to get the pkl path. If `model_metadata.json.model_file` is absent, default to `models/best_model.pkl`.

**Warning signs:** `KeyError: 'model_file'` when reading the leaderboard DataFrame.

[ASSUMED — leaderboard schema not verified against actual template output without a live project. The modelling notebooks write `leaderboard.csv` but the exact columns depend on the template cells. The plan should include a step to inspect leaderboard columns before accessing them.]

### Pitfall 2: Pipeline wrapper obscures class name

**What goes wrong:** `type(model).__name__` returns `"Pipeline"` instead of `"XGBRegressor"` because the pkl contains a full sklearn Pipeline (ColumnTransformer + estimator).

**Why it happens:** The modelling notebook wraps the estimator in a Pipeline for preprocessing. `type(pipeline).__name__` is always `"Pipeline"`.

**How to avoid:** Drill into the pipeline to get the final estimator class name:
```python
import joblib
model = joblib.load(pkl_path)
# For sklearn Pipeline:
if hasattr(model, 'steps'):
    estimator = model.steps[-1][1]  # Last step is the estimator
    raw_name = type(estimator).__name__
else:
    raw_name = type(model).__name__
```

**Warning signs:** `deployment_metadata.json` shows `model_name: "Pipeline"` or directory becomes `src/pipeline/v1/`.

### Pitfall 3: Unsupervised leaderboard has no best_model.pkl equivalent

**What goes wrong:** For clustering problems, the leaderboard ranks clustering methods but there may be no single `best_model.pkl` — the unsupervised modelling notebook may serialize multiple models.

**Why it happens:** Unsupervised problems don't have a single "best" model in the same sense as supervised. The clustering notebook writes `cluster_assignments.csv` but may not write a `.pkl`.

**How to avoid:** Check `model_metadata.json` for the model file path first. If the file pointed to doesn't exist, stop with a clear message: `"No model artifact found. Run /doml-modelling or /doml-iterate first."` Do not guess paths.

**Warning signs:** `FileNotFoundError` when calling `joblib.load()` on the resolved pkl path.

[ASSUMED — unsupervised pkl serialization behavior not verified against actual clustering template without a live project.]

### Pitfall 4: src/ directory doesn't exist yet

**What goes wrong:** `mkdir -p src/<modelname>/vN/` fails silently or the Bash tool returns an error because the parent `src/` directory doesn't exist.

**Why it happens:** Phase 13 creates `src/` for the first time. `pathlib.Path.mkdir(parents=True, exist_ok=True)` handles this correctly but only if invoked properly.

**How to avoid:** Use Python's `pathlib` for directory creation:
```python
from pathlib import Path
deploy_dir = Path(f"src/{model_slug}/v{version}")
deploy_dir.mkdir(parents=True, exist_ok=True)
```

**Warning signs:** The workflow creates the wrong directory level or silently skips creation.

### Pitfall 5: feature_schema source — model_metadata.json only has feature names, not types

**What goes wrong:** `deployment_metadata.json` needs `[{name, type}]` objects but `model_metadata.json` only stores `feature_names` as a flat list of strings.

**Why it happens:** The modelling notebook template stores `feature_names` for SHAP and model explainability, but dtype information was not needed there.

**How to avoid:** Two options in priority order:
1. Read the preprocessed dataset from `data/processed/preprocessed_*` and infer dtypes from the actual column dtypes: `df.dtypes.to_dict()`
2. Fall back to marking all features as `"unknown"` type if the preprocessed file is unavailable

The workflow should attempt option 1 and fall back to option 2, not fail hard.

**Warning signs:** `deployment_metadata.json.feature_schema` is a flat list of strings instead of `[{name, type}]` objects.

---

## Code Examples

Verified patterns from official sources:

### SKILL.md — Minimum Viable Structure (doml-deploy-model)

```yaml
# Source: .claude/skills/doml-modelling/SKILL.md [VERIFIED: codebase]
---
name: doml-deploy-model
description: "Deploy the top leaderboard model to a chosen target. Creates src/<modelname>/v1/
  with deployment_metadata.json. Prompts interactively for target (CLI binary, web service,
  ONNX/WASM). Supports --model <file> to override default model selection."
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
Deploy the DoML model to a chosen target:
1. Validate project state and read config.json
2. Resolve the model file (leaderboard #1 or --model override)
3. Ensure model_metadata.json has a model_name field (derive if absent)
4. Prompt user to select a deployment target (CLI binary / Web service / ONNX/WASM)
5. Scan src/<modelname>/ for existing versions; increment to vN+1 if needed
6. Create src/<modelname>/vN/ and write deployment_metadata.json
7. Update STATE.md and confirm to the user
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
```

### Version scanning for src/<modelname>/vN/

```python
# Source: iterate.md Step 4 adapted [VERIFIED: codebase pattern]
import glob, re

model_slug = 'xgbregressor'  # from slugify_model_name()
existing = glob.glob(f'src/{model_slug}/v*')
versions = [
    int(re.search(r'/v(\d+)$', d).group(1))
    for d in existing
    if re.search(r'/v(\d+)$', d)
]
version = max(versions) + 1 if versions else 1
```

### deployment_metadata.json write pattern

```python
# Source: standard json.dump pattern; schema from CONTEXT.md D-05 [VERIFIED: CONTEXT.md]
import json
from datetime import datetime, timezone
from pathlib import Path

deploy_dir = Path(f"src/{model_slug}/v{version}")
deploy_dir.mkdir(parents=True, exist_ok=True)

metadata = {
    "model_file": model_file,          # e.g., "models/best_model.pkl"
    "model_name": raw_model_name,      # e.g., "XGBRegressor"
    "target": target_key,              # e.g., "cli_binary"
    "build_date": datetime.now(timezone.utc).isoformat(),
    "version": f"v{version}",
    "feature_schema": feature_schema   # e.g., [{"name": "age", "type": "float64"}]
}

with open(deploy_dir / "deployment_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

### In-place model_metadata.json update (DEPLOY-05)

```python
# Source: standard Python in-place JSON update pattern [ASSUMED — no existing example in codebase]
import json

meta_path = "models/model_metadata.json"
with open(meta_path) as f:
    meta = json.load(f)

if "model_name" not in meta:
    import joblib
    model = joblib.load(meta.get("model_file", "models/best_model.pkl"))
    # Drill into Pipeline if wrapped
    if hasattr(model, "steps"):
        estimator = model.steps[-1][1]
        meta["model_name"] = type(estimator).__name__
    else:
        meta["model_name"] = type(model).__name__
    
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"model_name added: {meta['model_name']}")
```

---

## Recommended Workflow Step Order

Based on CONTEXT.md D-03 discretion note ("step ordering within the workflow"):

**Recommended order — validation-first:**

1. Validate project state (STATE.md exists)
2. Read config.json; parse `$ARGUMENTS` for `--model` flag
3. Resolve model file (leaderboard #1 or override); stop if not found
4. Ensure `model_name` in model_metadata.json (derive if absent — DEPLOY-05)
5. Derive `MODEL_SLUG` from model_name for directory naming
6. Prompt user for target selection (AskUserQuestion — DEPLOY-03)
7. Scan `src/<MODEL_SLUG>/v*` for existing versions; set VERSION (D-02)
8. Announce version if VERSION > 1
9. Read feature_schema (from preprocessed dataset or model_metadata.json)
10. Create `src/<MODEL_SLUG>/v${VERSION}/`; write `deployment_metadata.json` (DEPLOY-04)
11. Update STATE.md; print confirmation summary

**Rationale:** Validating all inputs (steps 1–5) before prompting the user (step 6) avoids the UX failure of asking a question and then stopping with an error. The user should only be asked to choose a target once we know everything else is ready.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Leaderboard CSV has `model` column (model name) and CV metric columns, but NOT a `model_file` column. File path must come from model_metadata.json. | Pitfall 1, Pattern 5 | Plan must include leaderboard column inspection step; fallback to `models/best_model.pkl` |
| A2 | The modelling notebook writes a single `models/best_model.pkl` for supervised problems; unsupervised may not have a pkl artifact | Pitfall 3 | Plan must handle missing pkl gracefully for unsupervised |
| A3 | `model_metadata.json` `feature_names` is a flat list of strings, not `[{name, type}]` objects | Pitfall 5 | Need preprocessed dataset read step for dtype information |
| A4 | The `feature_names` key in model_metadata.json matches the column names in the preprocessed dataset exactly | Pattern 7 | Mismatch would cause incorrect feature_schema |
| A5 | Unsupervised `model_metadata.json` may have a different schema than supervised (e.g., no `feature_names` for dim_reduction) | Standard Stack | Plan should read metadata defensively with `.get()` fallbacks |

---

## Open Questions (RESOLVED)

1. **Leaderboard column schema** — RESOLVED: `model_file` is read from `model_metadata.json`, not from leaderboard CSV. The leaderboard is used only for ranking (model name/CV metrics). The plan reads model file path exclusively from `model_metadata.json`.

2. **Unsupervised pkl existence** — RESOLVED: The workflow validates `os.path.exists(model_file)` before proceeding and stops with a clear error message ("No model file found at {path}. Run /doml-modelling first.") if the pkl is absent.

3. **feature_schema dtype source for forecasting problems** — RESOLVED: `time_series` problem type is routed to `models/leaderboard.csv` identically to supervised. ONNX/WASM target blocking for forecasting is deferred to Phase 16.

---

## Environment Availability

Phase 13 is pure file I/O — no Docker, no external services, no network calls.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 (local) | Workflow bash snippets | Already required by all workflows | — | — |
| `joblib` | Model pkl loading | Already in requirements.txt | — | — |
| `pandas` | Leaderboard CSV reading | Already in requirements.txt | — | — |
| `pathlib` (stdlib) | Directory creation | Always available | — | — |

No missing dependencies. No external services required.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None defined yet for this project — workflow files are integration-tested by running them |
| Config file | none |
| Quick run command | Manual invocation of `/doml-deploy-model` on a project with a completed modelling phase |
| Full suite command | Same — no automated test suite for workflow files exists in this project |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Notes |
|--------|----------|-----------|-------|
| DEPLOY-01 | `doml-deploy-model` invokable, selects #1 leaderboard model | manual smoke | Requires a project with `models/leaderboard.csv` and `models/best_model.pkl` |
| DEPLOY-02 | `--model <file>` uses specified model | manual smoke | Invoke with `--model models/some_model.pkl` |
| DEPLOY-03 | AskUserQuestion prompts for target | manual smoke | Verify menu appears with correct labels |
| DEPLOY-04 | `src/<modelname>/v1/` created with correct deployment_metadata.json | manual smoke | Verify directory and JSON fields |
| DEPLOY-05 | `model_metadata.json` gains `model_name` field | manual smoke | Run on a metadata file without `model_name` field to verify derivation |

**Note:** The DoML framework uses manual end-to-end smoke testing as its validation strategy. No automated unit test infrastructure exists for workflow files. This matches the pattern of all prior phases.

### Wave 0 Gaps

None — no test infrastructure to create. Validation is by running the workflow against a test project.

---

## Security Domain

Phase 13 handles only local file I/O and model deserialization. No network, no auth, no user-facing endpoints.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | partial | The `--model <file>` path should be validated with `os.path.exists()` before use; never shell-interpolated |
| V6 Cryptography | no | — |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `--model` flag | Tampering | Validate path exists; use pathlib for manipulation; never shell-interpolate |
| Malicious pkl deserialization | Tampering | Out of scope — pkl files are user-controlled artifacts in the same project; no external input |

---

## Sources

### Primary (HIGH confidence)
- `.claude/skills/doml-modelling/SKILL.md` — SKILL.md canonical format
- `.claude/skills/doml-iterate/SKILL.md` — argument-hint and arguments block pattern
- `.claude/skills/doml-forecasting/SKILL.md` — argument-hint with flags pattern
- `.claude/doml/workflows/iterate.md` — version scanning pattern (Step 4), leaderboard reading pattern (Step 3 and 8)
- `.claude/doml/workflows/modelling.md` — problem_type routing, STATE.md update pattern (Step 9)
- `.claude/doml/workflows/anomaly-detection.md` — AskUserQuestion pattern, argument parsing
- `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — all locked decisions, schema decisions

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` — canonical DEPLOY-01..DEPLOY-05 requirements and target label text
- `.planning/ROADMAP.md` — Phase 14/15/16 context for downstream contract decisions

### Tertiary (LOW confidence — flagged as ASSUMED)
- Leaderboard CSV column schema (A1): inferred from modelling.md verification snippets, not confirmed against template source
- Unsupervised pkl existence (A2): inferred from Phase 7 state notes in STATE.md, not verified against clustering template
- feature_names field type in model_metadata.json (A3): inferred from modelling.md narrative, not confirmed against template

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already in project; no new dependencies
- Architecture patterns: HIGH — directly verified from existing workflow/skill files
- Pitfalls: MEDIUM — two pitfalls (A1 leaderboard schema, A2 unsupervised pkl) are ASSUMED; three are verified patterns
- Workflow step order: HIGH — derived from CONTEXT.md decisions and established doml conventions

**Research date:** 2026-04-14
**Valid until:** 2026-05-14 (stable domain — DoML internal conventions don't change between sessions)
