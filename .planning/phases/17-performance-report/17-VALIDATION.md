---
phase: 17
slug: performance-report
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-17
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already in requirements.in) + nbconvert execution |
| **Config file** | none — inline invocation |
| **Quick run command** | `test -f notebooks/deployment_report.ipynb && echo OK` |
| **Full suite command** | `jupyter nbconvert --to notebook --execute notebooks/deployment_report.ipynb --output /tmp/report_executed.ipynb && test -f reports/deployment_report.html` |
| **Estimated runtime** | ~120 seconds (CLI target); ~180s (web, includes container start) |

---

## Sampling Rate

- **After every task commit:** Run `test -f notebooks/deployment_report.ipynb && echo OK`
- **After every plan wave:** Run full nbconvert execution suite
- **Before `/gsd-verify-work`:** Full suite must be green (notebook executes, HTML generated, parity passes)
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | PERF-01 | — | N/A | smoke | `test -f notebooks/deployment_report.ipynb` | ❌ W0 | ⬜ pending |
| 17-01-02 | 01 | 1 | PERF-07 | — | N/A | smoke | `test -f reports/deployment_report.html` | ❌ W0 | ⬜ pending |
| 17-01-03 | 01 | 2 | PERF-02 | — | N/A | integration | notebook execution output: latency mean/std present | ❌ W0 | ⬜ pending |
| 17-01-04 | 01 | 2 | PERF-03 | — | N/A | integration | notebook output: all 4 batch sizes (10/100/1000/10000) present | ❌ W0 | ⬜ pending |
| 17-01-05 | 01 | 2 | PERF-04 | — | N/A | automated | nbconvert exits 0 (parity assertion in notebook cell = hard failure if breached) | ❌ W0 | ⬜ pending |
| 17-01-06 | 01 | 2 | PERF-05 | — | N/A | integration | notebook output: memory delta values present and positive | ❌ W0 | ⬜ pending |
| 17-01-07 | 01 | 2 | PERF-06 | — | N/A | integration | notebook output: throughput (req/s) value present | ❌ W0 | ⬜ pending |
| 17-01-08 | 01 | 3 | PERF-07 | — | N/A | smoke | `grep -c 'class="input"' reports/deployment_report.html` returns 0 | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `notebooks/deployment_report.ipynb` — does not exist yet; created as the phase deliverable
- [ ] `reports/` directory — created by workflow if not present
- [ ] No pytest unit test files required — notebook execution IS the test suite for this phase

*Primary validation mechanism: `jupyter nbconvert --execute` exits 0 when all cells succeed, non-zero when any assertion fails (e.g., parity test). This provides automated pass/fail for PERF-04.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Claude narrative present in HTML | PERF-07 | Content quality can't be asserted programmatically | Open `reports/deployment_report.html`, confirm "Performance Summary" section with narrative text |
| Latency mean ± std displayed | PERF-02 | Format assertion fragile; value range varies by model | Check notebook output cell: confirm numeric mean and std displayed |
| Memory values positive and reasonable | PERF-05 | No baseline to assert against | Check notebook output: memory delta > 0 MB |
| HTML has no visible code | PERF-07 | nbconvert --no-input hides input; verify visually | Open HTML in browser, confirm no code cells visible |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
