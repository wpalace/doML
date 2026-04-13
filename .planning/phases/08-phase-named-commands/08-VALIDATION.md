---
phase: 08
slug: phase-named-commands
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
---

# Phase 08 — Validation Strategy

> Nyquist validation contract for Phase 08: phase-named-commands.
> Reconstructed from artifacts (State B) — no prior VALIDATION.md existed.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none (standard pytest discovery) |
| **Quick run command** | `python -m pytest tests/test_phase08_skills.py -v` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~0.1 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_phase08_skills.py -v`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** <1 second

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-T1 | 01 | 1 | CMD-10 | — | N/A | content | `python -m pytest tests/test_phase08_skills.py::test_business_understanding_skill_file_exists tests/test_phase08_skills.py::test_business_understanding_skill_has_correct_name -v` | ✅ | ✅ green |
| 08-01-T2 | 01 | 1 | CMD-10 | — | No execute-phase.md references (old command isolation) | content | `python -m pytest tests/test_phase08_skills.py::test_business_understanding_workflow_no_execute_phase_dependency -v` | ✅ | ✅ green |
| 08-01-T3 | 01 | 1 | CMD-10 | — | N/A | content | `python -m pytest tests/test_phase08_skills.py::test_business_understanding_workflow_has_guidance_parameter -v` | ✅ | ✅ green |
| 08-02-T1 | 02 | 1 | CMD-11 | — | N/A | content | `python -m pytest tests/test_phase08_skills.py::test_data_understanding_skill_file_exists tests/test_phase08_skills.py::test_data_understanding_skill_has_correct_name -v` | ✅ | ✅ green |
| 08-02-T2 | 02 | 1 | CMD-11 | — | No execute-phase.md references (old command isolation) | content | `python -m pytest tests/test_phase08_skills.py::test_data_understanding_workflow_no_execute_phase_dependency -v` | ✅ | ✅ green |
| 08-03-T1 | 03 | 1 | CMD-12 | — | N/A | content | `python -m pytest tests/test_phase08_skills.py::test_modelling_skill_file_exists tests/test_phase08_skills.py::test_modelling_skill_has_correct_name -v` | ✅ | ✅ green |
| 08-03-T2 | 03 | 1 | CMD-12 | — | No execute-phase.md references; all 4 problem types routed | content | `python -m pytest tests/test_phase08_skills.py::test_modelling_workflow_routes_regression tests/test_phase08_skills.py::test_modelling_workflow_routes_classification tests/test_phase08_skills.py::test_modelling_workflow_routes_clustering tests/test_phase08_skills.py::test_modelling_workflow_routes_dimensionality_reduction tests/test_phase08_skills.py::test_modelling_workflow_no_execute_phase_dependency -v` | ✅ | ✅ green |
| 08-04-T1 | 04 | 2 | CMD-10/11/12 | — | Old skill dirs deleted (supply-chain hygiene) | existence | `python -m pytest tests/test_phase08_skills.py::test_old_execute_phase_skill_directory_deleted tests/test_phase08_skills.py::test_old_plan_phase_skill_directory_deleted -v` | ✅ | ✅ green |
| 08-04-T2 | 04 | 2 | CMD-10/11/12 | — | Old workflow files deleted | existence | `python -m pytest tests/test_phase08_skills.py::test_old_execute_phase_workflow_deleted tests/test_phase08_skills.py::test_old_plan_phase_workflow_deleted -v` | ✅ | ✅ green |
| 08-04-T3 | 04 | 2 | CMD-10/11/12 | — | CLAUDE.md contains no old command refs (documentation integrity) | content | `python -m pytest tests/test_phase08_skills.py::test_claude_md_no_execute_phase_reference tests/test_phase08_skills.py::test_claude_md_no_plan_phase_reference -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements (tests generated retroactively via /gsd-validate-phase).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| End-to-end `/doml-business-understanding` run produces HTML report | CMD-10 | Requires live Docker + Jupyter container running with dataset in data/raw/ | Run `/doml-business-understanding` in a live Claude Code session with a project that has completed Phase 1 setup |
| End-to-end `/doml-data-understanding` run produces eda_report.html | CMD-11 | Requires live Docker + nbconvert execution | Run `/doml-data-understanding` in a live Claude Code session with preprocessed data |
| End-to-end `/doml-modelling` routing for all 4 problem types | CMD-12 | Requires live Docker + trained model artifacts | Run `/doml-modelling` for each of: regression, classification, clustering, dim_reduction |

---

## Validation Sign-Off

- [x] All tasks have automated verify command
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 not needed — tests generated retroactively, all green
- [x] No watch-mode flags
- [x] Feedback latency <1s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-13

---

## Validation Audit 2026-04-13

| Metric | Count |
|--------|-------|
| Gaps found | 10 |
| Resolved | 10 |
| Escalated to manual-only | 0 |
| Tests generated | 23 |
| Tests passing | 23 |
