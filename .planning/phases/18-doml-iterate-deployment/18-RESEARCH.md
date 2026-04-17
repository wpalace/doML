# Phase 18: doml-iterate-deployment — Research

**Researched:** 2026-04-17
**Domain:** DoML workflow authoring — iterate-deployment skill, argument parsing, version scanning, target delegation, performance report reuse
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01**: Leaderboard-match guard — re-read leaderboard, compare leader against `deployment_metadata.json`. Same model → version bump. Different model → stop and display a structured error message directing user to `/doml-deploy-model`.
- **D-02**: Version scanning — `glob('src/<modelname>/v*')`, `max(N) + 1`. Announce before creating. New-model path (explicit `--model <different.pkl>`) → `src/<newmodelname>/v1/`.
- **D-03**: `--target` flag (optional) — if omitted re-use `target` from most recent `deployment_metadata.json`; if provided, override for this iteration.
- **D-04**: `--guidance "<text>"` — freeform string applied by Claude before delegating; passed to performance report narrative step. Running without `--guidance` is valid.
- **D-05**: New standalone `iterate-deployment.md` — dedicated workflow, does NOT modify `deploy-model.md`. Delegates to `deploy-cli.md` / `deploy-web.md` / `deploy-wasm.md` exactly as `deploy-model.md` does. Replicates Step 12 (performance report) inline or by reference.
- **D-06**: Three valid no-new-model scenarios — config/guidance change, target change, baseline refresh. All produce `vN+1/` with fresh report.

### Claude's Discretion

- Exact argument parsing implementation (`--guidance` quoted string extraction via `sed`)
- Whether guidance application is a discrete workflow step or inline commentary before delegating to target skills
- Whether `deployment_metadata.json` includes a `guidance` field for traceability (recommended but not required)
- Port conflict handling if iterating on a web service while the previous version's container is still running (fail with clear error is acceptable)
- Whether the skill name slug in `src/` uses `model_name` directly from metadata or sanitizes it (same convention as deploy-model)

### Deferred Ideas (OUT OF SCOPE)

None documented in CONTEXT.md.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ITER-01 | User can run `doml-iterate-deployment` without re-running `doml-deploy-model` from scratch | SKILL.md entry point + `iterate-deployment.md` workflow; leaderboard guard validates state before running |
| ITER-02 | Same model → `src/<modelname>/v<N+1>/` (version scanned from filesystem, not assumed) | deploy-model.md Step 7 version-scan snippet is directly reusable; see Code Examples §1 |
| ITER-03 | Different model → `src/<newmodelname>/v1/` as new folder | Explicit `--model <file>` flag bypasses leaderboard guard; version scan of new slug yields 1 |
| ITER-04 | Accepts `--guidance` parameter to shape iteration direction | doml-iterate SKILL.md uses positional `direction` string; deploy-model.md uses `sed`-based flag parsing — combine both patterns |
| ITER-05 | Works without a new model (inference tuning, target change, baseline refresh) | D-06 defines three explicit paths; target re-use from `deployment_metadata.json` (D-03) enables target-change case |
</phase_requirements>

---

## Summary

Phase 18 creates two new files: `.claude/skills/doml-iterate-deployment/SKILL.md` and `.claude/doml/workflows/iterate-deployment.md`. No existing files are modified.

`iterate-deployment.md` is structurally a reduced version of `deploy-model.md` with three extra steps prepended (leaderboard-match guard, version scan announcement, guidance application) and the interactive target-selection step replaced by flag-based target resolution. The bulk of the logic — model slug derivation, directory creation, `deployment_metadata.json` writing, delegation to a target skill, and the full Step 12 performance report sequence — is unchanged from `deploy-model.md` and can be copied verbatim or referenced directly.

The primary implementation risk is the leaderboard-match guard: the logic for reading the leaderboard leader and comparing it against the previously deployed model is new code with no existing template. All other steps have direct precedents in the existing codebase.

**Primary recommendation:** Structure `iterate-deployment.md` as a linear 12-step workflow mirroring `deploy-model.md` steps 1–2 and 4–12, inserting the leaderboard guard as Step 3, replacing the interactive target prompt (old Step 6) with flag-based resolution, and keeping Step 12 (performance report) verbatim.

---

## Standard Stack

### Core (inherited — no new dependencies)

| Component | Source | Purpose |
|-----------|--------|---------|
| `SKILL.md` entry point | `.claude/skills/doml-*/` pattern | Claude Code command registration |
| `iterate-deployment.md` workflow | `.claude/doml/workflows/` pattern | Orchestration logic |
| `deployment_metadata.json` | Written by deploy-model.md Step 9 | Source of truth for last deployed model/version/target |
| `models/leaderboard.csv` or `models/unsupervised_leaderboard.csv` | Written by doml-modelling | Source of truth for current #1 model |
| `deploy-cli.md` / `deploy-web.md` / `deploy-wasm.md` | Phases 14–16 | Target skills; invoked unchanged |
| `deployment_report.ipynb` template | `.claude/doml/templates/notebooks/` | Performance report template; copied per deploy-model.md Step 12a |

[VERIFIED: file read] All files above exist in the repository at time of research.

### No New Python Packages Required

`iterate-deployment.md` uses only `glob`, `re`, `json`, `os`, `pathlib`, `datetime` — all standard library or already in `requirements.txt`. [VERIFIED: codebase grep of deploy-model.md imports]

---

## Architecture Patterns

### deploy-model.md Structure (the pattern to replicate)

`deploy-model.md` is a numbered-step prose workflow (not executable code) read by Claude Code. Each step contains bash snippets Claude executes via the Bash tool or Python scripts Claude runs via Bash. The structure is:

```
Step 1  — Validate project state (.planning/STATE.md exists)
Step 2  — Read config.json + parse CLI flags
Step 3  — Resolve model file (leaderboard or --model override)
Step 4  — Ensure model_name in model_metadata.json
Step 5  — Derive MODEL_SLUG
Step 6  — Prompt for deployment target (AskUserQuestion — INTERACTIVE)
Step 7  — Scan for existing versions; set VERSION
Step 8  — Read feature_schema from data/processed/
Step 9  — Create deployment directory; write deployment_metadata.json
Step 10 — Update STATE.md
Step 11 — Confirm to user
Step 12 — Generate performance report (Docker; only Docker step)
```

[VERIFIED: file read of deploy-model.md]

### iterate-deployment.md Structure (recommended)

```
Step 1  — Validate project state (same as deploy-model.md Step 1)
Step 2  — Read config.json + parse CLI flags (--model, --target, --guidance)
Step 3  — NEW: Leaderboard-match guard (read leaderboard; read latest deployment_metadata.json; compare; stop if different model unless --model was supplied)
Step 4  — Ensure model_name in model_metadata.json (same as deploy-model.md Step 4)
Step 5  — Derive MODEL_SLUG (same as deploy-model.md Step 5)
Step 6  — Resolve target from --target flag or deployment_metadata.json (replaces AskUserQuestion)
Step 7  — Scan for existing versions; set VERSION (same as deploy-model.md Step 7)
Step 8  — Read feature_schema from data/processed/ (same as deploy-model.md Step 8)
Step 9  — Apply --guidance (Claude reads guidance text; modifies configuration commentary before delegating)
Step 10 — Create deployment directory; write deployment_metadata.json (same as Step 9 of deploy-model.md, adding optional guidance field)
Step 11 — Delegate to target skill (deploy-cli.md / deploy-web.md / deploy-wasm.md)
Step 12 — Generate performance report (verbatim copy of deploy-model.md Step 12)
Step 13 — Update STATE.md + confirm
```

Steps 1, 4, 5, 7, 8, 10, 12 are direct copies from `deploy-model.md`. Steps 2, 3, 6, 9, 11, 13 are new or significantly adapted.

### SKILL.md Format (verified pattern)

All doml skills use this exact YAML frontmatter + body structure:

```yaml
---
name: doml-iterate-deployment
description: "..."
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
...numbered list of what the workflow does...
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
```

[VERIFIED: file read of doml-deploy-model/SKILL.md and doml-deploy-cli/SKILL.md]

`AskUserQuestion` is listed in `allowed-tools` on all deploy skills even when not always called — keep it in for consistency and in case guidance disambiguation is needed.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version scanning | Custom counter | Existing snippet from deploy-model.md Step 7 | Already handles edge cases (no existing dirs → v1, multiple gaps handled by max()) |
| Model slug derivation | New slug logic | Exact snippet from deploy-model.md Step 5 | Slug must match what deploy-model.md wrote — using the same code guarantees consistency |
| feature_schema reading | New data scan | Exact snippet from deploy-model.md Step 8 | Reads same preprocessed files in same order |
| Performance report | Custom benchmark code | Full Step 12 from deploy-model.md (12a–12j) | Template already handles all three targets; Step 12 is the only Docker step — anti-pattern comment must carry forward |
| `deployment_metadata.json` write | Ad-hoc JSON write | Extend the Step 9 Python block from deploy-model.md | Existing block handles all required fields; iterate only adds optional `guidance` field |

---

## deployment_metadata.json Schema (from Phase 13 D-05)

[VERIFIED: file read of deploy-model.md Step 9 and 13-CONTEXT.md D-05]

```json
{
  "model_file": "models/best_model.pkl",
  "model_name": "XGBRegressor",
  "target": "cli_binary",
  "problem_type": "regression",
  "build_date": "2026-04-17T19:00:00+00:00",
  "version": "v2",
  "feature_schema": [
    {"name": "col1", "type": "float64", "example": "1.5", "categories": null},
    {"name": "col2", "type": "object", "example": "EU", "categories": ["EU", "NA", "APAC"]}
  ]
}
```

Field notes:
- `feature_schema` entries have `categories` (list or null) — added in Phase 15 D-01
- `target` values: `"cli_binary"`, `"web_service"`, `"onnx_wasm"`
- `version` is `"vN"` (string with prefix), not an integer
- `model_file` is a relative path from project root (e.g. `models/best_model.pkl`)
- Additional fields may be present: deploy-cli.md adds `"platform"` and `"binary_path"` after building

The **most recently written** `deployment_metadata.json` under `src/` is identified by finding the highest version number across all `src/*/v*` directories. The leaderboard-match guard reads this file.

---

## Code Examples

### Version Scanning (from deploy-model.md Step 7 — verbatim reuse)
[VERIFIED: file read]

```bash
VERSION=$(python3 -c "
import glob, re
model_slug = '${MODEL_SLUG}'
existing = glob.glob(f'src/{model_slug}/v*')
versions = [
    int(re.search(r'/v(\d+)$', d).group(1))
    for d in existing
    if re.search(r'/v(\d+)$', d)
]
print(max(versions) + 1 if versions else 1)
")
echo "Deployment version: v${VERSION}"
```

Announcement (only when bumping):
```bash
if [ "$VERSION" -gt 1 ]; then
  echo "src/${MODEL_SLUG}/v$(($VERSION - 1))/ exists — iterating to v${VERSION}/"
fi
```

### Finding the Latest deployment_metadata.json (for leaderboard guard)
[VERIFIED: pattern derived from deploy-cli.md Step 2 — same glob pattern]

```bash
LATEST_META=$(python3 -c "
import glob, re, os
dirs = glob.glob('src/*/*')
versioned = [
    (d, int(re.search(r'/v(\d+)$', d).group(1)))
    for d in dirs
    if re.search(r'/v(\d+)$', d) and os.path.isfile(d + '/deployment_metadata.json')
]
if not versioned:
    print('')
else:
    latest = sorted(versioned, key=lambda x: x[1], reverse=True)[0][0]
    print(latest + '/deployment_metadata.json')
")
if [ -z "$LATEST_META" ]; then
  echo "No previous deployment found. Run /doml-deploy-model first."
  exit 1
fi
```

### Argument Parsing Pattern (from deploy-model.md Step 2)
[VERIFIED: file read]

```bash
# --model flag
MODEL_OVERRIDE=""
if echo "$ARGUMENTS" | grep -q -- '--model'; then
  MODEL_OVERRIDE=$(echo "$ARGUMENTS" | sed 's/.*--model[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi

# --target flag (iterate-specific)
TARGET_OVERRIDE=""
if echo "$ARGUMENTS" | grep -q -- '--target'; then
  TARGET_OVERRIDE=$(echo "$ARGUMENTS" | sed 's/.*--target[[:space:]]\+\([^[:space:]]*\).*/\1/')
fi

# --guidance flag (quoted string — sed captures everything after --guidance to end of string,
# or up to the next -- flag)
GUIDANCE=""
if echo "$ARGUMENTS" | grep -q -- '--guidance'; then
  GUIDANCE=$(echo "$ARGUMENTS" | sed "s/.*--guidance[[:space:]]\+['\"]\\?\\([^'\"]*\\)['\"]\\?.*/\\1/")
fi
```

Note: `--guidance` content may include spaces. The sed approach above captures up to an unquoted boundary. An alternative that is more reliable for complex quoted strings: Claude Code can read `$ARGUMENTS` as a raw string and use Python to parse it.

```bash
GUIDANCE=$(python3 -c "
import sys, re
args = '''${ARGUMENTS}'''
m = re.search(r'--guidance\s+[\"'\''](.+?)[\"'\'']', args)
if not m:
    m = re.search(r'--guidance\s+(\S+)', args)
print(m.group(1) if m else '')
")
```

### Leaderboard Leader Resolution (for leaderboard guard)
[VERIFIED: pattern from deploy-model.md Step 3]

```bash
LEADERBOARD_LEADER=$(python3 -c "
import json, os, sys
problem_type = '${PROBLEM_TYPE}'
if problem_type in ('regression', 'classification', 'binary_classification',
                    'multiclass_classification', 'time_series'):
    lb_path = 'models/leaderboard.csv'
else:
    lb_path = 'models/unsupervised_leaderboard.csv'

if not os.path.exists(lb_path):
    print('')
    sys.exit(0)

import pandas as pd
df = pd.read_csv(lb_path)
# Leaderboard first row = #1 model
print(df.iloc[0]['model'] if len(df) > 0 else '')
")
```

### Leaderboard Guard Logic
[VERIFIED: logic derived from 18-CONTEXT.md D-01]

```bash
# Read model_name from most recent deployment
DEPLOYED_MODEL=$(python3 -c "
import json
with open('${LATEST_META}') as f:
    meta = json.load(f)
print(meta.get('model_name', ''))
")

if [ -z "$MODEL_OVERRIDE" ] && [ "$LEADERBOARD_LEADER" != "$DEPLOYED_MODEL" ] && [ -n "$LEADERBOARD_LEADER" ]; then
  echo ""
  echo "The leaderboard leader has changed since your last deployment."
  echo "Current leader: ${LEADERBOARD_LEADER}"
  echo "Last deployed:  ${DEPLOYED_MODEL}"
  echo ""
  echo "Did you mean to deploy a new model?"
  echo "Run /doml-deploy-model to start a fresh deployment for ${LEADERBOARD_LEADER}."
  exit 1
fi
```

### Target Resolution from Flag or Metadata
[VERIFIED: logic derived from 18-CONTEXT.md D-03]

```bash
if [ -n "$TARGET_OVERRIDE" ]; then
  # Map CLI shorthand to internal keys
  case "$TARGET_OVERRIDE" in
    cli)  TARGET_KEY="cli_binary" ;;
    web)  TARGET_KEY="web_service" ;;
    wasm) TARGET_KEY="onnx_wasm" ;;
    *)
      echo "Unknown --target value: ${TARGET_OVERRIDE}"
      echo "Valid values: cli, web, wasm"
      exit 1
      ;;
  esac
  echo "Target override: ${TARGET_KEY}"
else
  TARGET_KEY=$(python3 -c "
import json
with open('${LATEST_META}') as f:
    meta = json.load(f)
print(meta.get('target', 'cli_binary'))
")
  echo "Target re-used from previous deployment: ${TARGET_KEY}"
fi
```

### Performance Report Step (Step 12 of deploy-model.md — copied verbatim)
[VERIFIED: file read of deploy-model.md Steps 12a–12j]

Steps 12a through 12j from `deploy-model.md` are copied verbatim into `iterate-deployment.md`. The only variable that changes is `VERSION` and `MODEL_SLUG` (which are set earlier in the workflow). All bash variables referenced in Step 12 (`TARGET_KEY`, `MODEL_SLUG`, `VERSION`, `DOML_WEB_SERVICE_URL`) are available because they are set in the iterate workflow's earlier steps.

The anti-pattern addendum must also be copied:
> Step 12 is the sole exception to the "NEVER run Docker" rule — it must execute the notebook and generate HTML inside the jupyter container. All other steps remain pure file I/O.

---

## Steps Safe to Delegate vs. Needing Adaptation

| Step | deploy-model.md equivalent | iterate-deployment.md treatment |
|------|---------------------------|----------------------------------|
| Validate state | Step 1 | **Copy verbatim** |
| Read config + parse flags | Step 2 | **Adapt** — add `--target` and `--guidance` flag parsing alongside `--model` |
| Leaderboard-match guard | (none) | **New** — Step 3 |
| Ensure model_name | Step 4 | **Copy verbatim** |
| Derive MODEL_SLUG | Step 5 | **Copy verbatim** |
| Target selection | Step 6 (AskUserQuestion) | **Replace** — flag-based resolution from `--target` or prior `deployment_metadata.json` |
| Version scan | Step 7 | **Copy verbatim** |
| Feature schema | Step 8 | **Copy verbatim** |
| Apply guidance | (none) | **New** — Step 9; Claude reads GUIDANCE string and notes configuration adjustments |
| Create dir + write metadata | Step 9 | **Copy + extend** — add optional `guidance` field |
| Delegate to target skill | (implied by Step 11 confirm) | **New explicit step** — invoke `@.claude/doml/workflows/deploy-cli.md` etc. with `--deploy-dir` |
| Performance report | Step 12 | **Copy verbatim (12a–12j)** |
| Update STATE.md + confirm | Steps 10–11 | **Adapt** — change phase reference and confirm message |

---

## SKILL.md for doml-iterate-deployment — Required Content

The SKILL.md must include in `<objective>`:

1. Validate project state and read `config.json`
2. Parse `--model`, `--target`, and `--guidance` flags
3. Re-read leaderboard to confirm the current #1 model matches the last deployed model (or stop with redirect message)
4. Ensure `model_metadata.json` has a `model_name` field
5. Derive `MODEL_SLUG` (filesystem-safe: lowercase, underscores, no parens)
6. Resolve deployment target from `--target` flag or prior `deployment_metadata.json`
7. Scan `src/<modelname>/v*/` for existing versions; write to `vN+1`
8. Announce version bump before creating directory
9. Apply `--guidance` to configuration direction before delegating to target skill
10. Create `src/<modelname>/vN+1/` and write `deployment_metadata.json`
11. Delegate to the appropriate target skill (`deploy-cli.md` / `deploy-web.md` / `deploy-wasm.md`)
12. Generate performance report (copy of `deploy-model.md` Step 12)
13. Update `STATE.md` and confirm

The `description` field should mirror `doml-deploy-model` but clarify the iterate scope:
```
"Iterate an existing deployment to a new version without re-running /doml-deploy-model from scratch.
Validates the leaderboard leader matches the last deployed model, scans src/<modelname>/v*/ for the
current highest version, and writes to vN+1. Accepts --model path/to/model.pkl (different model →
new src/<newmodelname>/v1/), --target {cli|web|wasm} (override target), and --guidance \"text\"
(freeform direction applied to configuration before deployment). Regenerates deployment_report.ipynb
and deployment_report.html for the new version."
```

---

## Common Pitfalls

### Pitfall 1: Comparing model names across leaderboard and metadata

**What goes wrong:** Leaderboard `model` column may contain display names like `"XGBoost (tuned)"` while `model_name` in `deployment_metadata.json` was derived from `type(estimator).__name__` → `"XGBRegressor"`. A string equality check will always fail.
**Why it happens:** Phase 13 derives `model_name` from the class name, not from the leaderboard column.
**How to avoid:** The guard should compare `model_name` from `deployment_metadata.json` against the `model_name` field in `model_metadata.json` (which was written at the same derivation step), NOT against the raw leaderboard `model` column. Alternatively, read the `model_file` path from the leaderboard (if available) and compare file paths.
**Warning signs:** Leaderboard leader check always triggers the mismatch warning even when nothing changed.

[ASSUMED — exact column name and content format of leaderboard.csv not read in this session; planner should verify column names match what deploy-model.md Step 3 reads.]

**Safer guard approach:** Compare the `model_file` path from `model_metadata.json` (what the leaderboard resolves to) against `model_file` in `deployment_metadata.json`. File paths are not display-name dependent.

```bash
META_MODEL_FILE=$(python3 -c "
import json
with open('models/model_metadata.json') as f:
    meta = json.load(f)
print(meta.get('model_file', 'models/best_model.pkl'))
")
DEPLOYED_MODEL_FILE=$(python3 -c "
import json
with open('${LATEST_META}') as f:
    meta = json.load(f)
print(meta.get('model_file', ''))
")
# Compare file paths, not display names
```

### Pitfall 2: Step 12 variable scope

**What goes wrong:** Step 12 in `deploy-model.md` uses shell variables (`TARGET_KEY`, `MODEL_SLUG`, `VERSION`) set in earlier steps. Copying Step 12 verbatim requires these same variable names to exist when Step 12 runs.
**Why it happens:** Shell variable names in the performance report step are not parameterized.
**How to avoid:** Use the same variable names in `iterate-deployment.md` throughout. Do not rename `TARGET_KEY` to `TARGET` or `MODEL_SLUG` to `SLUG`.

### Pitfall 3: `--deploy-dir` vs. creating a new directory

**What goes wrong:** `deploy-cli.md`, `deploy-web.md`, and `deploy-wasm.md` accept `--deploy-dir src/<modelname>/vN`. When `iterate-deployment.md` invokes them, it must pass the **new** `vN+1` directory (created in its own Step 10), not the old directory.
**Why it happens:** Target skills auto-discover the latest `deployment_metadata.json` if `--deploy-dir` is omitted. At the point `iterate-deployment.md` invokes them, it has just created `vN+1/` which contains a fresh `deployment_metadata.json`. If `--deploy-dir` is omitted, the target skill's auto-discovery will find `vN+1/` correctly (it is the newest). Passing `--deploy-dir` explicitly is safer.
**How to avoid:** Always pass `--deploy-dir src/${MODEL_SLUG}/v${VERSION}` when invoking target skills from `iterate-deployment.md`.

### Pitfall 4: Web service port conflict on iteration

**What goes wrong:** If the previous version's web service container is still running on port 8080, the new version's `docker compose up` will fail with "port already in use".
**How to avoid:** D-06 / CONTEXT.md D-06 states "fail with clear error is acceptable". `iterate-deployment.md` should display:
```
Port 8080 may already be in use by a previous deployment.
Stop the previous version with:
  docker compose -f src/{MODEL_SLUG}/v{VERSION-1}/docker-compose.serve.yml down
Then re-run /doml-iterate-deployment.
```

### Pitfall 5: `--guidance` with no new model on the ONNX target

**What goes wrong:** `--guidance "use quantized model"` on an ONNX target cannot actually quantize the ONNX model because `deploy-wasm.md` runs the ONNX conversion each time. Guidance that implies changes to the model artifact cannot be applied by the iterate workflow — only by re-running `doml-deploy-wasm` from scratch.
**How to avoid:** Guidance is documented as "shapes configuration direction" — it is interpreted by Claude as commentary/context before delegating, not as a programmatic transform. Claude should acknowledge in the guidance application step what can and cannot be done with the given guidance for the target type.

---

## Validation Architecture

`nyquist_validation` is `true` in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual verification (no automated test suite for workflow files) |
| Config file | None — workflow files are markdown prose |
| Quick run command | Invoke `/doml-iterate-deployment` against a fixture project |
| Full suite command | Same — workflow correctness validated by execution |

This phase produces only two files: a SKILL.md and a workflow markdown. There is no Python module to unit-test. Validation is by functional smoke test.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated? | How to Verify |
|--------|----------|-----------|------------|---------------|
| ITER-01 | `/doml-iterate-deployment` is invokable in Claude Code | smoke | No | Claude Code recognizes the command; no error on startup |
| ITER-02 | Same model → `src/<modelname>/v<N+1>/` (scanned, not assumed) | functional | No | Run against a project with `src/xgb/v1/`; verify `v2/` created |
| ITER-03 | Different model → `src/<newmodelname>/v1/` | functional | No | Run with `--model models/other_model.pkl`; verify new slug dir |
| ITER-04 | `--guidance` accepted and shapes direction | functional | No | Run with `--guidance "optimize latency"`; verify no crash; verify guidance applied |
| ITER-05 | Works without new model (target change, config, baseline) | functional | No | Run without `--model`; verify `vN+1/` created and report generated |

### Wave 0 Gaps

None — no test files required for this phase. Validation is done by running the command in a project with an existing `src/<modelname>/v1/` deployment.

---

## Environment Availability

Step 2.6: Relevant only to the **performance report** step (Step 12), which is a direct copy from `deploy-model.md`. The environment requirements for Step 12 are the same as for `deploy-model.md`:

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker + `docker compose` | Step 12 notebook execution | Expected present (already required by Phases 13–17) | — | None — Step 12 fails without Docker |
| Jupyter Docker container running | Step 12 | Expected present | — | User must run `docker compose up -d` |
| `onnxruntime` (Python) | Step 12 WASM target bench | Added in Phase 17 to requirements.in | — | None for WASM target |

No new environment dependencies introduced by Phase 18.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Leaderboard `model` column contains display names that may not match `model_name` in `deployment_metadata.json` | Pitfall 1 | Guard logic would break if names unexpectedly match; safer to compare `model_file` paths |
| A2 | Target skills (`deploy-cli.md`, `deploy-web.md`, `deploy-wasm.md`) auto-discover the newest `deployment_metadata.json` when `--deploy-dir` is omitted | Pitfall 3 | If auto-discovery uses a different sort key, it might pick the wrong directory |
| A3 | Phase 17 added `onnxruntime` to `requirements.in` before Phase 18 executes | Environment section | Step 12 WASM benchmarking would fail at notebook execution |

---

## Open Questions

1. **Leaderboard leader comparison field**
   - What we know: `leaderboard.csv` has a `model` column (used in deploy-model.md Step 3 for display only); `model_metadata.json` has `model_name` (from class name); `deployment_metadata.json` has both `model_name` and `model_file`.
   - What's unclear: Whether the leaderboard `model` column value is normalized consistently enough to compare against `model_name`. Not directly verified — deploy-model.md Step 3 reads `model_file` from `model_metadata.json`, not from the leaderboard.
   - Recommendation: Compare `model_file` paths (from `model_metadata.json` vs. `deployment_metadata.json`) rather than display names. This is unambiguous and already normalized.

2. **How iterate-deployment invokes target skills**
   - What we know: `deploy-model.md` ends at Step 11 (confirm) without explicitly invoking a target skill — the user runs `/doml-deploy-cli` etc. as a separate command.
   - What's unclear: D-05 says iterate-deployment "delegates to the same existing target skills exactly as deploy-model.md does" — but deploy-model.md actually just creates the scaffold and leaves target invocation to the user. "Delegates" in D-05 likely means the iterate workflow should invoke the target workflow directly (via `@.claude/doml/workflows/deploy-cli.md` reference or by running the equivalent steps inline).
   - Recommendation: The planner should treat "delegate" as: after creating `vN+1/deployment_metadata.json`, invoke `@.claude/doml/workflows/deploy-cli.md` (or web/wasm) passing `--deploy-dir src/${MODEL_SLUG}/v${VERSION}`. This matches the Phase 17 D-03 pattern where `deploy-model.md` calls into target skills before running Step 12.

---

## Sources

### Primary (HIGH confidence)
- [VERIFIED: file read] `.claude/doml/workflows/deploy-model.md` — full workflow structure, Step 12 detail, variable names, argument parsing snippets, anti-patterns
- [VERIFIED: file read] `.claude/skills/doml-deploy-model/SKILL.md` and `.claude/skills/doml-deploy-cli/SKILL.md` — SKILL.md format, frontmatter fields, `<objective>` structure
- [VERIFIED: file read] `.planning/phases/18-doml-iterate-deployment/18-CONTEXT.md` — all locked decisions D-01 through D-06
- [VERIFIED: file read] `.planning/phases/13-deployment-workflow-skeleton/13-CONTEXT.md` — D-05 `deployment_metadata.json` fields
- [VERIFIED: file read] `.planning/phases/17-performance-report/17-CONTEXT.md` — D-03 (trigger placement), D-04 (narrative injection pattern), D-05 (target routing)
- [VERIFIED: file read] `.claude/skills/doml-iterate/SKILL.md` — `direction` argument pattern, positional vs. flag argument handling
- [VERIFIED: file read] `.claude/doml/workflows/deploy-cli.md` — `--deploy-dir` flag parsing pattern (Steps 2–3)
- [VERIFIED: file read] `.claude/doml/templates/notebooks/deployment_report.ipynb` — confirmed Cell 12 is the markdown placeholder at index 12, target routing, variables read at notebook startup

### Secondary (MEDIUM confidence)
- [VERIFIED: file read] `.planning/REQUIREMENTS.md` §ITER — acceptance criteria for ITER-01 through ITER-05
- [VERIFIED: file read] `.planning/config.json` — nyquist_validation: true confirmed

---

## Metadata

**Confidence breakdown:**
- Workflow structure (steps, variables, patterns): HIGH — read directly from deploy-model.md
- SKILL.md format: HIGH — read from two existing skills
- deployment_metadata.json schema: HIGH — read from deploy-model.md Step 9 and 13-CONTEXT.md D-05
- Leaderboard comparison logic: MEDIUM — field names inferred from deploy-model.md Step 3 code; exact leaderboard.csv schema not directly read
- Guidance parsing (sed approach): MEDIUM — sed flag parsing pattern verified; multi-word quoted string edge cases marked as discretionary

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 (workflow files are stable; no external dependencies)
