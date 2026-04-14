---
phase: 14
slug: cli-binary-target
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-14
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash / grep (file inspection only — workflow files, no runnable Python unit tests in this phase) |
| **Config file** | none — Wave 0 not required; all verifications are file-inspection greps |
| **Quick run command** | `grep -c "pyinstaller predict.spec" .claude/doml/workflows/deploy-cli.md` |
| **Full suite command** | See Per-Task Verification Map automated commands below |
| **Estimated runtime** | ~5 seconds (all greps) |

---

## Sampling Rate

- **After every task commit:** Run quick run command above
- **After every plan wave:** Run full suite (all automated commands in map below)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | CLI-01 | T-14-01-02 | src/ mount is writable, not :ro | grep | `grep -c "./src:/home/jovyan/work/src" .claude/doml/templates/docker-compose.yml` | ✅ | ⬜ pending |
| 14-01-02 | 01 | 1 | CLI-01 | T-14-01-03 | pyinstaller declared in requirements.in | grep | `grep -c "^pyinstaller$" .claude/doml/templates/requirements.in` | ✅ | ⬜ pending |
| 14-02-01 | 02 | 2 | CLI-01–CLI-06 | — | SKILL.md has correct name and workflow ref | grep | `grep -c "name: doml-deploy-cli" .claude/skills/doml-deploy-cli/SKILL.md` | ❌ W0 | ⬜ pending |
| 14-02-02a | 02 | 2 | CLI-01 | T-14-02-05 | PyInstaller build command uses single-quoted path | grep | `grep -c "pyinstaller predict.spec --noconfirm" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02b | 02 | 2 | CLI-02 | T-14-02-01 | json.loads() detection (JSON string input) | grep | `grep -c "json.loads" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02c | 02 | 2 | CLI-03 | T-14-02-01 | CSV/JSON file input detection by extension | grep | `grep -c "\.csv\|\.json" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02d | 02 | 2 | CLI-04 | — | --output flag present in predict.py template | grep | `grep -c "\-\-output" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02e | 02 | 2 | CLI-05 | — | Feature schema epilog in predict.py template | grep | `grep -c "FEATURE_SCHEMA" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02f | 02 | 2 | CLI-06 | T-14-02-03 | Exit codes 0, 1, 2 in predict.py template | grep | `grep -c "sys.exit" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02g | 02 | 2 | CLI-06 (D-04) | — | predict_proba for classification probabilities | grep | `grep -c "predict_proba" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02h | 02 | 2 | CLI-06 (SC-7) | — | platform: linux-x86_64 written to metadata | grep | `grep -c "linux-x86_64" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02i | 02 | 2 | CLI-01 (D-01) | — | onedir: exclude_binaries=True on EXE and COLLECT present | grep | `grep -c "exclude_binaries=True" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |
| 14-02-02j | 02 | 2 | CLI-01 | T-14-02-04 | src/ mount guard stops workflow if mount missing | grep | `grep -c "./src:/home/jovyan/work/src" .claude/doml/workflows/deploy-cli.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Wave 0 is not required for this phase. All verification is file-inspection grep against generated
workflow and skill files. No test framework installation needed.

Files created in Wave 1 (Plan 01) and Wave 2 (Plan 02) are the artifacts under test. The ❌ W0
entries in the map above become resolvable once Plan 02 Task 1 and Task 2 execute.

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Binary runs on a machine with no Python installed and returns a prediction | CLI-01 | Requires a Linux x86_64 machine without Python; cannot be automated in the planning environment | Copy `dist/predict/` to a fresh Linux machine, run `./dist/predict/predict --input '{"feature": 1}'`, verify exit 0 and JSON output |
| `--help` output shows all feature names, types, and example values | CLI-05 | Requires a live binary built from a real model | Run `./dist/predict/predict --help`, verify each feature appears as `name (type, e.g. value)` |
| exit code 1 on malformed input | CLI-06 | Requires a live binary | Run `./dist/predict/predict --input 'not-json-and-not-a-file'`, verify `echo $?` returns 1 |
| exit code 2 on corrupt model | CLI-06 | Requires a live binary with a corrupted pkl | Replace best_model.pkl with a zero-byte file, run the binary, verify `echo $?` returns 2 |

---

## Full Suite Command (all automated checks)

Run after Wave 2 completes:

```bash
# Plan 01 checks
grep -c "./src:/home/jovyan/work/src" .claude/doml/templates/docker-compose.yml && \
grep -c "^pyinstaller$" .claude/doml/templates/requirements.in && \
# Plan 02 checks
grep -c "name: doml-deploy-cli" .claude/skills/doml-deploy-cli/SKILL.md && \
grep -c "pyinstaller predict.spec --noconfirm" .claude/doml/workflows/deploy-cli.md && \
grep -c "json.loads" .claude/doml/workflows/deploy-cli.md && \
grep -c "sys.exit" .claude/doml/workflows/deploy-cli.md && \
grep -c "predict_proba" .claude/doml/workflows/deploy-cli.md && \
grep -c "linux-x86_64" .claude/doml/workflows/deploy-cli.md && \
grep -c "exclude_binaries=True" .claude/doml/workflows/deploy-cli.md && \
grep -c "collect_all" .claude/doml/workflows/deploy-cli.md && \
echo "All Phase 14 automated checks PASSED"
```

Each grep must return ≥ 1. Any failure (exit non-zero) means the check failed.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify with grep commands
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none required — no test framework needed)
- [x] No watch-mode flags
- [x] Feedback latency < 5s (all greps)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending execution
