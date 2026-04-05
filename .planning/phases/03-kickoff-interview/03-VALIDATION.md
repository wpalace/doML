---
phase: 03
slug: kickoff-interview
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-05
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — Wave 0 installs pytest and adds to requirements.in |
| **Quick run command** | `pytest tests/test_data_scan.py -x` |
| **Full suite command** | `pytest tests/ -x` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_data_scan.py -x`
- **After every plan wave:** Run `pytest tests/ -x`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-02-01 | 02 | 0 | INTV-03 | — | N/A | unit | `pytest tests/test_data_scan.py -x` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | INTV-03 | — | N/A | unit | `pytest tests/test_data_scan.py::test_csv_scan -x` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 1 | INTV-03 | — | N/A | unit | `pytest tests/test_data_scan.py::test_parquet_scan -x` | ❌ W0 | ⬜ pending |
| 03-02-04 | 02 | 1 | INTV-03 | — | N/A | unit | `pytest tests/test_data_scan.py::test_xlsx_scan -x` | ❌ W0 | ⬜ pending |
| 03-02-05 | 02 | 1 | INTV-03 | — | N/A | unit | `pytest tests/test_data_scan.py::test_empty_dir_raises -x` | ❌ W0 | ⬜ pending |
| 03-02-06 | 02 | 1 | INTV-03 | — | N/A | unit | `pytest tests/test_data_scan.py::test_xls_not_supported -x` | ❌ W0 | ⬜ pending |
| 03-01-01 | 01 | 1 | INTV-04, INTV-05 | — | N/A | grep | `grep -c "analysis_language\|We are trying to" .claude/doml/workflows/new-project.md` | ✅ | ⬜ pending |
| 03-01-02 | 01 | 2 | INTV-01, INTV-02 | — | N/A | manual | Task 3 human-verify checkpoint | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_data_scan.py` — stubs for INTV-03 (scan, empty dir, missing dir, xls unsupported, csv, parquet, xlsx)
- [ ] `tests/fixtures/` — sample CSV, Parquet, and XLSX files for scan tests
- [ ] `requirements.in` — add `pytest` (unpinned top-level), then run `pip-compile requirements.in` to regenerate `requirements.txt`

Note: `test_project_output.py` and `test_interview_workflow.py` are NOT applicable for Phase 3. Plan 03-01 modifies `.claude/doml/workflows/new-project.md` — a workflow instruction file, not Python code. INTV-01, INTV-02, INTV-04, INTV-05 are verified by grep checks on the workflow file + the blocking human-verify checkpoint (Plan 03-01 Task 3).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Domain research step offered and domain summary written to PROJECT.md | INTV-01 | Requires LLM inference — cannot be unit tested | Run `/doml-new-project` in a test project with a known domain (e.g., "retail churn"), verify domain research section appears in PROJECT.md |
| Problem type confirmation dialog makes sense for given business question | INTV-01 | Requires subjective review of LLM reasoning | Run interview with regression and classification examples, verify inferred type matches expected |
| Docker excel extension autoloads on first `.xlsx` read | INTV-03 | Requires running inside the Docker container | Run `docker compose exec jupyter python -c "import duckdb; duckdb.sql(\"SELECT * FROM read_xlsx('tests/fixtures/sample.xlsx')\").show()"` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
