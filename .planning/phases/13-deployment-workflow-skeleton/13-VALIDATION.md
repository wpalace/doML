---
phase: 13
slug: deployment-workflow-skeleton
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-14
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (existing) |
| **Config file** | pytest.ini or pyproject.toml (if present) |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | DEPLOY-01 | — | N/A | file check | `test -f .claude/skills/doml-deploy-model/SKILL.md` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | DEPLOY-02 | — | N/A | file check | `test -f .claude/doml/workflows/deploy-model.md` | ❌ W0 | ⬜ pending |
| 13-01-03 | 01 | 2 | DEPLOY-03 | — | N/A | manual | See manual verifications | — | ⬜ pending |
| 13-01-04 | 01 | 2 | DEPLOY-04 | — | N/A | file check | `grep -q "deployment_metadata.json" .claude/doml/workflows/deploy-model.md` | ❌ W0 | ⬜ pending |
| 13-01-05 | 01 | 2 | DEPLOY-05 | — | N/A | manual | See manual verifications | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.claude/skills/doml-deploy-model/` directory must exist before task execution
- [ ] `.claude/doml/workflows/` directory must exist before task execution

*Existing test infrastructure covers standard phase requirements. Wave 0 creates missing directories.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `doml-deploy-model` invokable in Claude Code | DEPLOY-01 | Requires live Claude Code session | Invoke `/doml-deploy-model` in Claude Code and verify it runs |
| Model selection and target prompting | DEPLOY-02/03 | Requires interactive session with AskUserQuestion | Run workflow without args and verify leaderboard #1 is pre-selected; run with `--model` and verify override works |
| `src/<modelname>/v1/` directory created with correct metadata | DEPLOY-04 | Depends on real model artifacts in `models/` | After running workflow, verify directory exists and `deployment_metadata.json` contains required fields |
| `model_metadata.json` gains `model_name` field | DEPLOY-05 | Requires real model pkl in `models/` | After running workflow, verify `model_name` key exists in metadata JSON |

*All phase behaviors are fundamentally interactive/manual — no automated test suite applies.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
