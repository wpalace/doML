# Phase 3 Context: Kickoff Interview

**Phase:** 03 — Kickoff Interview
**Goal:** Implement the guided business context interview — validates data, infers ML problem type, and writes decision framing before any analysis begins.
**Requirements:** INTV-01, INTV-02, INTV-03, INTV-04, INTV-05

---

## Prior Decisions (Carrying Forward)

- Python is the default analysis language; R is opt-in — confirmed at interview (INTV-05)
- Forecasting activates only when time-factor is confirmed in Business Understanding — interview must set this flag explicitly
- `/doml-new-project` currently has Phase 2 stubs for both validation and interview steps — Phase 3 replaces them with real implementations

---

<decisions>

## Decision 1: Problem Type Detection

**Method:** Claude infers + user confirms.

The interview asks for the business question in free text. Claude infers the ML problem type (regression, classification, clustering, time series, or dimensionality reduction), explains its reasoning, and asks the user to confirm or correct.

**Domain research step:** After the user describes their business question, if the domain is recognizable (e.g., "retail churn", "patient readmission"), Claude offers a domain research step — looks up typical success metrics, known data pitfalls, and standard ML approaches for that domain. The user can accept or skip. Domain research summary is included in the PROJECT.md Problem Framing section.

**Rationale:** Infer + confirm is more educational than a list picker and more reliable than pure branching questions. The domain research offer grounds the problem framing with domain-specific context without forcing it on every user.

---

## Decision 2: Interview Output Artifact

**Destination:** PROJECT.md — fill in template placeholders + add a "Problem Framing" section.

The interview populates the PROJECT.md template that Phase 2 generated. Specifically:
- Fills template placeholders: business question, stakeholder, dataset description, expected outcome
- Adds a dedicated **Problem Framing** section containing:
  - The INTV-04 framing sentence: "We are trying to [X] using [metric] as a proxy."
  - ML problem type (confirmed classification)
  - Time-factor flag (yes/no + explanation)
  - Language preference (Python / R)
  - Domain research summary (if research step was accepted)

No separate FRAMING.md. PROJECT.md is the single source of truth that downstream phases (Business Understanding, EDA) read.

**Language preference** is also written to `.planning/config.json` as `analysis_language` (INTV-05).

---

## Decision 3: Data Scan Depth and Timing

**Depth:** Shape + schema only.

DuckDB scans each file in `data/raw/` and surfaces:
- File list with format (CSV / Parquet / Excel)
- Row × column count per file
- Column names with inferred dtypes

No sample rows, no null counts — those belong in the EDA phase notebook.

**Timing:** Scan runs before any interview questions. Output is shown at the top of the interview session. Seeing column names and shapes helps the user answer business questions more accurately (e.g., spotting a date column may confirm time-factor).

---

## Decision 4: Empty /data/ Behavior

**Behavior:** Hard stop with a clear, actionable error message. No partial state is written.

When `/doml-new-project` is run and `data/raw/` is missing, empty, or contains no supported files (CSV / Parquet / .xls / .xlsx), the workflow stops immediately with an error listing:
- What was expected
- Where to put files
- Supported formats

**No `--skip-validation` flag.** Data is always required before the interview can run.

**Deferred idea (future milestone):** Synthetic data generation — allow the interview to run against a generated dataset when no real data is available yet. Not in scope for Milestone 1.

</decisions>

---

<canonical_refs>
- `.planning/PROJECT.md` — template to be filled in by interview output
- `.planning/config.json` — stores `analysis_language` preference (INTV-05)
- `.planning/REQUIREMENTS.md` — INTV-01 through INTV-05 define acceptance criteria
- `.claude/doml/workflows/new-project.md` — Phase 2 stub that Phase 3 replaces with real implementation
- `.claude/doml/templates/` — planning artifact templates stamped at project init
</canonical_refs>

---

<deferred>
## Deferred Ideas

- **Synthetic data generation** (future milestone): Run the kickoff interview against a generated/sample dataset before real data is available. User noted this as a potential future milestone capability.
</deferred>
