---
phase: 9
slug: doml-get-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in `requirements.in`) |
| **Config file** | none — no pytest.ini or pyproject.toml with pytest config |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | ~5 seconds (manual-only phase — minimal automated tests) |

---

## Sampling Rate

- **After every task commit:** Manual inspection per task acceptance criteria
- **After every plan wave:** Manual smoke test of affected workflow files
- **Before `/gsd-verify-work`:** All manual verifications must be signed off
- **Max feedback latency:** N/A — workflow markdown phase, no automated feedback loop

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01 | 01 | 1 | CMD-14 | — | N/A | smoke | manual inspection | ❌ Wave 0 | ⬜ pending |
| 09-02 | 01 | 1 | DATA-01 | — | N/A | manual | Kaggle credentials + network required | N/A | ⬜ pending |
| 09-03 | 01 | 1 | DATA-02 | — | N/A | manual | Network + URL required | N/A | ⬜ pending |
| 09-04 | 01 | 2 | DATA-03 | — | N/A | manual | Inspect workflow text for empty-data branch | N/A | ⬜ pending |
| 09-05 | 01 | 2 | DATA-04 | — | N/A | manual | Inspect README.md provenance block after download | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

None — Existing pytest infrastructure covers the project; no new test stubs required. This phase produces workflow markdown files only — no Python code with unit-testable logic.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SKILL.md created and loadable by Claude Code | CMD-14 | No CLI test harness for skill loading | Read `.claude/skills/doml-get-data/SKILL.md`, verify frontmatter and content |
| Kaggle slug download → files in `data/raw/` | DATA-01 | Requires live Kaggle credentials + network | Run `doml-get-data kaggle owner/dataset-name` in a project, confirm files appear |
| URL download → files in `data/raw/` | DATA-02 | Requires live network + URL | Run `doml-get-data url https://example.com/file.csv`, confirm file appears |
| `doml-new-project` offers data acquisition when `data/raw/` empty | DATA-03 | Workflow markdown — must inspect prompt text | In a project with empty `data/raw/`, run `/doml-new-project` and verify AskUserQuestion is presented |
| `data/raw/README.md` receives provenance entry | DATA-04 | File state depends on actual download run | After any download, open `data/raw/README.md` and verify new entry with source URL and timestamp |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency documented
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
