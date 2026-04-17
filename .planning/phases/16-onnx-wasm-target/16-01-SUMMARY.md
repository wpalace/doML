---
phase: 16-onnx-wasm-target
plan: 01
subsystem: deployment
tags: [onnx, wasm, onnxruntime-web, skl2onnx, browser-inference, sklearn, docker]

# Dependency graph
requires:
  - phase: 13-deployment-workflow-skeleton
    provides: deployment_metadata.json with feature_schema and model_file fields
  - phase: 15-web-service-target
    provides: categories field in feature_schema (D-01 Phase 15), OrdinalEncoder encoding pattern (D-03)

provides:
  - doml-deploy-wasm skill at .claude/skills/doml-deploy-wasm/SKILL.md
  - deploy-wasm.md 11-step workflow at .claude/doml/workflows/deploy-wasm.md
  - ONNX/WASM generation pipeline: converts sklearn Pipeline to ONNX inside Docker, embeds ORT+model in HTML
affects: [17-iterate-deployment, future-phases-using-wasm-target]

# Tech tracking
tech-stack:
  added: [skl2onnx, onnxruntime-web 1.17.3, OrdinalEncoder (ONNX export path)]
  patterns:
    - Docker-exec ONNX conversion (same pattern as Phase 14 PyInstaller)
    - OHE replaced with OrdinalEncoder for float32-only ONNX graph (D-03)
    - ORT WASM embedded as base64 blob URL (not raw data URI) for browser compatibility (D-01)
    - WASM base64 decoded to Blob URL via URL.createObjectURL() at runtime
    - category_map JSON embedded as JS constant for categorical label-to-int encoding

key-files:
  created:
    - .claude/skills/doml-deploy-wasm/SKILL.md
    - .claude/doml/workflows/deploy-wasm.md
  modified: []

key-decisions:
  - "Conversion runs inside Docker via docker compose exec jupyter python3 — ensures sklearn/skl2onnx version match (D-02)"
  - "OHE replaced with OrdinalEncoder at export time; JS receives integer codes only — no string tensor support needed (D-03)"
  - "ORT WASM converted to Blob URL before assignment to ort.env.wasm.wasmPaths — some browsers reject raw data:application/wasm URIs"
  - "Size gate covers ORT JS text + WASM base64 + model.onnx base64 — total must be under 20 MB (WASM-05)"
  - "forecasting and DBSCAN blocked before any conversion attempt — checked in Step 4 (WASM-04)"

patterns-established:
  - "11-step WASM workflow: validate → locate → read-meta → block-check → docker-check → convert → download-ort → size-gate → generate-html → update-meta → update-state"
  - "category_map printed as last stdout line from conversion script and captured by shell for embedding in HTML"
  - "ORT binaries cached at /tmp/doml_ort_1.17.3/ to avoid re-download on repeated runs"

requirements-completed: [WASM-01, WASM-02, WASM-03, WASM-04, WASM-05]

# Metrics
duration: 3min
completed: 2026-04-17
---

# Phase 16 Plan 01: ONNX/WASM Target Summary

**11-step doml-deploy-wasm skill and workflow: skl2onnx Pipeline conversion inside Docker, onnxruntime-web 1.17.3 binaries embedded as base64, self-contained index.html with auto-generated prediction form running offline in any browser**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-17T19:41:33Z
- **Completed:** 2026-04-17T19:45:21Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created `doml-deploy-wasm` skill at `.claude/skills/doml-deploy-wasm/SKILL.md` — invokable as `/doml-deploy-wasm`
- Created `deploy-wasm.md` 11-step workflow covering full ONNX/WASM generation pipeline (all WASM-01 through WASM-05 requirements)
- Workflow enforces problem type blocks (forecasting, DBSCAN) before conversion, runs ONNX export inside Docker, enforces 20 MB size gate, and generates fully self-contained `index.html`

## Task Commits

Each task was committed atomically:

1. **Task 1: Create .claude/skills/doml-deploy-wasm/SKILL.md** - `4694549` (feat)
2. **Task 2: Create .claude/doml/workflows/deploy-wasm.md** - `d1b1db2` (feat)

**Plan metadata:** `213e4ad` (docs: complete plan)

## Files Created/Modified
- `.claude/skills/doml-deploy-wasm/SKILL.md` — skill entry point for /doml-deploy-wasm; 10-item objective covering all WASM requirements
- `.claude/doml/workflows/deploy-wasm.md` — full 11-step workflow: validate, locate, read-meta, WASM-04 block check, Docker check, ONNX conversion (D-02/D-03), ORT download (D-01), size gate (WASM-05), index.html generation (WASM-01/02/03), metadata update, STATE.md update

## Decisions Made
- ORT WASM binary is embedded as base64 and decoded to a Blob URL at runtime (not a raw `data:application/wasm` data URI) — browsers reject raw WASM data URIs in some environments
- OHE replaced with OrdinalEncoder at conversion time so the ONNX graph accepts only float32 inputs; categorical values are encoded in JS via the embedded `CATEGORIES` map
- `category_map` is printed as the last stdout line of the conversion script so the shell can capture it cleanly without parsing multi-line output
- ORT binaries cached at `/tmp/doml_ort_1.17.3/` keyed to version string — repeated runs skip the download

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 16 Plan 01 complete — doml-deploy-wasm skill and workflow fully implemented
- All WASM-01 through WASM-05 requirements addressed
- Ready for Phase 16 Plan 02 if planned, or for end-to-end testing of the WASM generation pipeline

## Self-Check: PASSED

- FOUND: `.claude/skills/doml-deploy-wasm/SKILL.md`
- FOUND: `.claude/doml/workflows/deploy-wasm.md`
- FOUND: `.planning/phases/16-onnx-wasm-target/16-01-SUMMARY.md`
- FOUND commit: `4694549` (feat: SKILL.md)
- FOUND commit: `d1b1db2` (feat: deploy-wasm.md)
- FOUND commit: `213e4ad` (docs: metadata)

---
*Phase: 16-onnx-wasm-target*
*Completed: 2026-04-17*
