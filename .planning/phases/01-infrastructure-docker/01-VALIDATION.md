---
phase: 1
slug: infrastructure-docker
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash / docker / pytest (inside container) |
| **Config file** | none — Wave 0 installs pre-commit |
| **Quick run command** | `docker compose config --quiet && echo OK` |
| **Full suite command** | `docker compose build --quiet && docker compose run --rm jupyter python -c "import duckdb; print(duckdb.__version__)"` |
| **Estimated runtime** | ~60-120 seconds (build) |

---

## Sampling Rate

- **After every task commit:** Run `docker compose config --quiet && echo OK`
- **After every plan wave:** Run full suite command above
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01-01 | 1 | INFR-02 | — | N/A | integration | `docker compose build --quiet` | ✅ | ⬜ pending |
| 1-01-02 | 01-01 | 1 | INFR-03 | — | N/A | integration | `docker compose run --rm jupyter python -c "import duckdb; print(duckdb.__version__)"` | ✅ | ⬜ pending |
| 1-01-03 | 01-01 | 1 | INFR-03 | — | N/A | integration | `docker compose run --rm jupyter Rscript -e "library(duckdb); cat('R DuckDB OK\n')"` | ✅ | ⬜ pending |
| 1-02-01 | 01-02 | 1 | INFR-04 | — | N/A | shell | `test -d data/raw && test -d data/processed && test -d data/external && test -d notebooks && test -d reports && test -d models && echo OK` | ✅ | ⬜ pending |
| 1-02-02 | 01-02 | 1 | INFR-05 | — | N/A | shell | `docker compose config | grep -A2 'data/raw' | grep -q 'ro'` | ✅ | ⬜ pending |
| 1-03-01 | 01-03 | 2 | REPR-03 | — | N/A | shell | `pre-commit run nbstripout --all-files 2>&1 | grep -qv 'error'` | ✅ | ⬜ pending |
| 1-03-02 | 01-03 | 2 | INFR-06 | — | N/A | shell | `test -f CLAUDE.md && grep -q 'DoML' CLAUDE.md && echo OK` | ✅ | ⬜ pending |
| 1-03-03 | 01-03 | 2 | REPR-04 | — | N/A | shell | `grep -v '==' requirements.txt | grep -v '^#' | grep -v '^$' | wc -l | grep -q '^0$'` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pre-commit` installed in environment (`pip install pre-commit`)
- [ ] `.pre-commit-config.yaml` present before running nbstripout hook test

*Wave 0 is minimal — this phase creates infrastructure, not application code.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| JupyterLab loads at localhost:8888 | INFR-02 | Requires browser | Run `docker compose up`, navigate to http://localhost:8888, verify Lab UI loads |
| R kernel available in JupyterLab | INFR-02 | Requires browser/UI | In JupyterLab, create new notebook, verify R kernel option appears |
| data/raw is read-only from container | INFR-05 | Docker volume test | `docker compose run --rm jupyter bash -c "touch /home/jovyan/work/data/raw/test.txt"` — should fail with permission error |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
