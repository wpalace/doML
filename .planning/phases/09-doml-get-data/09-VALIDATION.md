---
phase: 9
slug: doml-get-data
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-10
validated: 2026-04-13
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in `requirements.in`) |
| **Config file** | none — no pytest.ini or pyproject.toml with pytest config |
| **Quick run command** | `pytest tests/test_phase09_get_data.py -v` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | <1 second (26 structural/content tests, no I/O) |

---

## Sampling Rate

- **After every task commit:** Manual inspection per task acceptance criteria
- **After every plan wave:** Manual smoke test of affected workflow files
- **Before `/gsd-verify-work`:** All manual verifications must be signed off
- **Max feedback latency:** <1 second (automated structural tests run instantly)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01 | 01 | 1 | CMD-14 | — | N/A | structural | `pytest tests/test_phase09_get_data.py::test_get_data_skill_file_exists` | ✅ | ✅ green |
| 09-02 | 01 | 1 | DATA-01 | T-09-01 | Kaggle creds checked inside container | structural | `pytest tests/test_phase09_get_data.py -k kaggle` | ✅ | ✅ green |
| 09-03 | 01 | 1 | DATA-02 | T-09-02 | URL validated for http/https prefix | structural | `pytest tests/test_phase09_get_data.py -k url` | ✅ | ✅ green |
| 09-04 | 02 | 1 | DATA-03 | T-09-08 | AskUserQuestion gate prevents infinite loop | structural | `pytest tests/test_phase09_get_data.py -k new_project` | ✅ | ✅ green |
| 09-05 | 01 | 1 | DATA-04 | T-09-07 | Provenance only appended on success | structural | `pytest tests/test_phase09_get_data.py -k provenance` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Test file: `tests/test_phase09_get_data.py` (26 tests)

All requirements covered by automated structural assertions. No runtime stubs needed — phase produces workflow markdown files whose correctness is verified by content inspection.

| Test Group | Tests | Requirements | Status |
|------------|-------|--------------|--------|
| CMD-14: SKILL.md structure | 4 | CMD-14 | ✅ |
| DATA-01: Kaggle flow | 6 | DATA-01 | ✅ |
| DATA-02: URL flow | 3 | DATA-02 | ✅ |
| DATA-03: new-project integration | 4 | DATA-03 | ✅ |
| DATA-04: Provenance append | 4 | DATA-04 | ✅ |
| Pre-run cleanup guard | 1 | DATA-01/02 | ✅ |
| Config files | 4 | DATA-01 | ✅ |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Status |
|----------|-------------|------------|-------------------|--------|
| SKILL.md created and loadable by Claude Code | CMD-14 | No CLI test harness for skill loading | Read `.claude/skills/doml-get-data/SKILL.md`, verify frontmatter and content | ✅ Verified via structural test |
| Kaggle slug download → files in `data/raw/` | DATA-01 | Requires live Kaggle credentials + network | Run `doml-get-data kaggle owner/dataset-name` in a project, confirm files appear | ⬜ requires live env |
| URL download → files in `data/raw/` | DATA-02 | Requires live network + URL | Run `doml-get-data url https://example.com/file.csv`, confirm file appears | ⬜ requires live env |
| `doml-new-project` offers data acquisition when `data/raw/` empty | DATA-03 | Workflow markdown — must inspect prompt text | In a project with empty `data/raw/`, run `/doml-new-project` and verify AskUserQuestion is presented | ⬜ requires live env |
| `data/raw/README.md` receives provenance entry | DATA-04 | File state depends on actual download run | After any download, open `data/raw/README.md` and verify new entry with source URL and timestamp | ⬜ requires live env |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency documented
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** 2026-04-13 — 26 structural tests written and passing; live-env behaviors documented as manual-only (network + Docker required)
