---
plan: 14-02
status: complete
completed: 2026-04-14
---

# Plan 14-02 Summary — /doml-deploy-cli Skill and Workflow

## What was done

Created two new files that implement the `/doml-deploy-cli` command:

1. **`.claude/skills/doml-deploy-cli/SKILL.md`** — command entry point with correct frontmatter (`name`, `description`, `argument-hint`, `allowed-tools`), references `deploy-cli.md` workflow via `execution_context`.

2. **`.claude/doml/workflows/deploy-cli.md`** — 10-step workflow:
   - Step 1: Validate STATE.md exists
   - Step 2: Locate deployment directory (via `--deploy-dir` or auto-detect latest)
   - Step 3: Read and validate `deployment_metadata.json` (rejects non-cli_binary targets)
   - Step 4: Read first preprocessed row for example values (D-03)
   - Step 5: Check `./src:/home/jovyan/work/src` mount and pyinstaller availability
   - Step 6: Generate `predict.py` (argparse, sys._MEIPASS model loading, exit codes 0/1/2, predict_proba)
   - Step 7: Generate `predict.spec` (collect_all sklearn+joblib, onedir, model bundle)
   - Step 8: Run `pyinstaller predict.spec --noconfirm` inside Docker container
   - Step 9: Verify `dist/predict/predict` exists; update `deployment_metadata.json` with `platform: linux-x86_64`
   - Step 10: Update STATE.md and display completion summary

## Verification

- SKILL.md: `name: doml-deploy-cli` ✓, `@.claude/doml/workflows/deploy-cli.md` reference ✓
- Workflow: 10 steps (`grep -c "^### Step"` → 10) ✓
- `pyinstaller predict.spec --noconfirm` build command present ✓
- `collect_all('sklearn')` and `collect_all('joblib')` present ✓
- `exclude_binaries=True` in EXE() call ✓
- `COLLECT(` present (required for onedir dist/ directory) ✓
- `sys._MEIPASS` frozen binary path resolution ✓
- `sys.exit(0)`, `sys.exit(1)`, `sys.exit(2)` exit codes ✓
- `predict_proba` classification probabilities (D-04) ✓
- `prob_{cls}` batch probability columns (D-05) ✓
- `"platform": "linux-x86_64"` metadata update (SC-7) ✓
- `./src:/home/jovyan/work/src` mount check in Step 5 ✓
- `--deploy-dir` flag parsing ✓
- `target != 'cli_binary'` guard ✓
- `--onefile` appears only in Anti-Patterns (not as recommended option) ✓

## Requirements satisfied

- CLI-01: Binary runs on Linux with no Python (PyInstaller onedir)
- CLI-02: `--input '{"f": v}'` JSON string → single prediction to stdout
- CLI-03: `--input data.csv` and `--input data.json` → batch predictions
- CLI-04: `--output path.csv` writes batch results to file
- CLI-05: `--help` shows feature names, types, example values
- CLI-06: exits 0/1/2 for success/input error/model error
- SC-7: `deployment_metadata.json` gains `"platform": "linux-x86_64"` after successful build
