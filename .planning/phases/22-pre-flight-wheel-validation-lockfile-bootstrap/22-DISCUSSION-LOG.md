# Phase 22: Pre-flight Wheel Validation & Lockfile Bootstrap — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-30
**Phase:** 22-pre-flight-wheel-validation-lockfile-bootstrap
**Areas discussed:** Validation depth, ydata-profiling failure path, scipy-notebook tag selection, Audit log artifact

---

## Validation depth

### Q1: Minimum gate to declare "go"

| Option | Description | Selected |
|--------|-------------|----------|
| Compile-only (lightest) | `uv pip compile` resolves and call it done. ~30s. Misses runtime issues. | |
| Compile + install in throwaway container | Compile + scipy-notebook container + `uv pip install --system` + import smoke from ARCHITECTURE.md | ✓ |
| Compile + install + nbconvert/papermill smoke | Above plus HTML conversion + 1-cell papermill. +2-3 min. | |
| Full notebook smoke (10 templates) | Every notebook via papermill against fixtures. Overlaps Phase 25. | |

**User's choice:** Compile + install in throwaway container (Recommended).

### Q2: Validation rig

| Option | Description | Selected |
|--------|-------------|----------|
| Inline `docker run --rm` one-liner | No Dockerfile artifact committed. | ✓ |
| Tiny `Dockerfile.preflight` in phase dir | Reusable but commits a one-shot artifact. | |
| Use Phase 23's draft Dockerfile early | Bleeds Phase 23 work; violates boundary. | |

**User's choice:** Inline `docker run --rm` one-liner (Recommended).

### Q3: Conda↔uv conflict surfacing

| Option | Description | Selected |
|--------|-------------|----------|
| Mamba list ∩ requirements.in diff | Audit-log artifact; explicit shadow-risk surface. | ✓ |
| Just runtime smoke | Rely on `import notebook` to verify. Less informative. | |
| Both | Belt and suspenders. | |

**User's choice:** Mamba list ∩ requirements.in diff (Recommended).

### Q4: Pre-flight failure handling

| Option | Description | Selected |
|--------|-------------|----------|
| Document failures + blocking decision in SUMMARY | User makes the milestone-level call. Phase 23 stays blocked. | |
| Auto-fall-back to Python 3.12 and re-validate | Auto-retry one Python step lower if primary fails. | ✓ |
| Hard-fail and stop the milestone | Treat any failure as milestone abort. | |

**User's choice:** Auto-fall-back. Note: target order later updated to "3.14 first, 3.13 fallback" once ydata was dropped (see ydata-profiling section).

---

## ydata-profiling failure path

### Q1: Success criterion

| Option | Description | Selected |
|--------|-------------|----------|
| Must install + import (hard requirement) | Pre-flight requires `from ydata_profiling import ProfileReport`. | |
| Must install + run on fixture | Above plus `ProfileReport(small_df).to_html()`. | |
| Install only — runtime defer to EDA phase | Accept install success; defer runtime. | |

**User's choice:** "I don't think we are using y-data profiling today. This can probably be dropped." — answer triggered a follow-up question on whether to drop entirely vs. validate-and-drop-on-failure.

### Q2: If ydata-profiling breaks under both 3.13 and 3.12

| Option | Description | Selected |
|--------|-------------|----------|
| Drop ydata-profiling from requirements.in | Remove + replace EDA cell with DuckDB. | ✓ |
| Pin to known-good older version | Carry forward conda 3.13 deferred state. Risk: unknown version. | |
| Block milestone | Surface to user. | |

**User's choice:** Drop ydata-profiling.

### Q3 (follow-up): Drop scope (template + EDA notebook)

| Option | Description | Selected |
|--------|-------------|----------|
| Drop everywhere now (Phase 22 scope) | Template `requirements.in` + EDA notebook profiling cell + re-evaluate Python 3.14 | ✓ |
| Drop from requirements.in only; mark EDA cell TODO | Skip-on-import-error; defer EDA refactor. | |
| Keep ydata-profiling, validate as planned | Validate per success criterion #5; auto-fallback. | |
| Drop from template and unblock 3.14 in this phase | Same as option 1 plus explicitly bump D-03 to 3.14. | |

**User's choice:** Drop everywhere now (Phase 22 scope).

### Q4 (follow-up): Python target order

| Option | Description | Selected |
|--------|-------------|----------|
| 3.14 first, fall back to 3.13 | Try 3.14; fall back if non-ydata cp314 wheel gap blocks. | ✓ |
| Stick with 3.13 (lock as-is) | Keep D-03 = 3.13. Lower risk. | |
| 3.14 only — hard requirement | Block if 3.14 wheels missing. | |

**User's choice:** 3.14 first, fall back to 3.13 (Recommended).

### Q5 (follow-up): EDA cell replacement

| Option | Description | Selected |
|--------|-------------|----------|
| DuckDB SUMMARIZE + hand-rolled summary table | DuckDB built-in profiling + cardinality/null/dtype. | ✓ |
| pandas-profiling alternative (skimpy/sweetviz) | Replace one dep with another. | |
| Defer EDA refactor to a separate follow-up phase | Delete cell with TODO. | |

**User's choice:** DuckDB SUMMARIZE (Recommended).

---

## scipy-notebook tag selection

### Q1: How is the tag chosen?

| Option | Description | Selected |
|--------|-------------|----------|
| Look up latest stable at exec time, record what we landed on | Most recent + reproducible. | ✓ |
| Pin `2026-04-21` from research now | Skip lookup; risk stale. | |
| Pin to a specific known-good tag from a tag list | Interactive selection. | |

**User's choice:** Look up at exec time (Recommended).

### Q2: Where is the tag pinned?

| Option | Description | Selected |
|--------|-------------|----------|
| Only in CONTEXT.md and SUMMARY.md | Phase 23 consumes; cleanest boundary. | |
| Also pre-write to root + template Dockerfiles | Update `FROM` line in both Dockerfiles now. Reduces handoff risk. | ✓ |
| Pin in `.env` or `requirements.in` comment | Awkward — tag isn't a Python dep. | |

**User's choice:** Pre-write `FROM` line in both Dockerfiles (Recommended).

### Q3: Tag-only or tag+digest?

| Option | Description | Selected |
|--------|-------------|----------|
| Tag only | `:YYYY-MM-DD`. Matches v1.5 pattern; immutable per Jupyter policy. | ✓ |
| Tag + digest | `:YYYY-MM-DD@sha256:...`. Strictly tamper-proof; verbose. | |

**User's choice:** Tag only (Recommended).

---

## Audit log artifact

### Q1: Audit log location

| Option | Description | Selected |
|--------|-------------|----------|
| Single `22-AUDIT.md` in phase dir | All artifacts in one Markdown file. | ✓ |
| Inline in 22-SUMMARY.md | No separate file; SUMMARY may grow long. | |
| Raw artifacts in `audit/` subdir | Separate raw files; most rigorous. | |

**User's choice:** Single `22-AUDIT.md` (Recommended).

### Q2: Audit content (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| Mamba list of base image (full) | Complete `mamba list` from scipy-notebook. | ✓ |
| Conflict diff (conda ∩ requirements.in) | Shadow-risk surface; required for Pitfall #3. | ✓ |
| uv pip compile resolved output (full requirements.txt diff) | Old vs new requirements.txt diff + uv resolution log. | ✓ |
| Go/no-go decision rationale + Python version landed on | Plain-English summary. | (delegated to SUMMARY.md per CONTEXT D-22-17) |

**User's choice:** First three. Go/no-go decision lives in SUMMARY.md instead.

### Q3: Commit strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Three commits: drop-ydata, lockfile-regen, audit-record | Clean bisect; isolated lockfile commit per Pitfall #6. | ✓ |
| Single commit per success criterion (5 commits) | Maximum granularity. | |
| Two commits: code-changes, then docs/audit | Risks Pitfall #6 noisy diff swallowing ydata drop. | |

**User's choice:** Three commits (Recommended).

---

## Claude's Discretion

- Exact CLI invocation of throwaway-container one-liner
- Format of the conflict-diff section in `22-AUDIT.md` (table vs list)
- DuckDB `SUMMARIZE` query phrasing in the new EDA cell
- Bash script vs noxfile/Make target for validation rig
- How to surface "auto-fallback fired" in SUMMARY (banner vs section)

## Deferred Ideas

- Wider `requirements.in` unused-dep audit beyond ydata-profiling
- Mirror scipy-notebook to ghcr.io (SLIM-FUT-02 — already deferred)
- Move pyinstaller out of main image (SLIM-FUT-01 — already deferred)
- PEP 751 / `uv.lock` migration (LOCK-FUT-01 — already deferred)
- `Dockerfile.preflight` as a reusable CI rig
- skimpy/sweetviz EDA profiler — explicitly rejected
