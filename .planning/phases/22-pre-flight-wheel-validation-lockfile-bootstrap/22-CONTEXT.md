# Phase 22: Pre-flight Wheel Validation & Lockfile Bootstrap — Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

De-risk the v1.6 stack before any Dockerfile rewrite. Confirm Python 3.14-or-3.13 + uv 0.11.8 + `quay.io/jupyter/scipy-notebook` resolve cleanly for every dep in `requirements.in`. Drop `ydata-profiling` (no longer in use) and replace its EDA-notebook cell with a DuckDB-based summary. Produce a fresh `requirements.txt` lockfile with hashes — committed but **not yet wired into Docker**. Phase 23 owns the Dockerfile rewrite that consumes this lockfile and tag.

**In scope:**
- Pre-flight validation rig: throwaway scipy-notebook container, `uv pip install --system`, import smoke
- Lockfile regeneration via `uv pip compile … --generate-hashes`
- `ydata-profiling` removal (template `requirements.in` + EDA notebook profiling cell)
- Python target evaluation (3.14 first, 3.13 fallback) — D-03 re-locked here
- scipy-notebook dated tag lookup + pin (root + template Dockerfile `FROM` line only)
- Audit artifact: conda↔uv conflict diff + compile output

**Out of scope (other phases):**
- Dockerfile install-layer rewrite, BuildKit cache mount, import smoke layer (Phase 23)
- R removal sweep (Phase 24)
- CI smoke workflow + fixture data (Phase 25)
</domain>

<decisions>
## Implementation Decisions

### Validation Rig

- **D-22-01:** Pre-flight gate is **compile + install in throwaway container with import smoke**. Steps: (1) `uv pip compile requirements.in --python-version <target> --generate-hashes`, (2) `docker run --rm` a scipy-notebook container, (3) `uv pip install --system -r requirements.txt` inside it, (4) run the import smoke from `research/ARCHITECTURE.md`: `python -c "import duckdb, papermill, shap, prophet, lightgbm, xgboost, onnxruntime, optuna, umap, skl2onnx, pyinstaller"`.
- **D-22-02:** Validation runs as an **inline `docker run --rm` one-liner** — no `Dockerfile.preflight` artifact committed. Phase 22 leaves no Docker-image artifacts behind; Phase 23 owns the real Dockerfile.
- **D-22-03:** `uv pip install --system` (additive). Never `uv pip sync` — it would prune conda-shipped jupyterlab/notebook/ipykernel and break the kernel (`research/PITFALLS.md` #3).
- **D-22-04:** Conda↔uv shadow-risk surface is detected by **`mamba list` ∩ `requirements.in` diff**. Any package in both is flagged in the audit.

### Python Target & Fallback

- **D-22-05:** Python target order is **3.14 first, fall back to 3.13**. With `ydata-profiling` dropped, the only known cap is gone; cp314 wheel coverage for prophet/lightgbm/pmdarima is the remaining unknown (`PITFALLS.md` #1). Whichever resolves cleanly wins.
- **D-22-06:** **D-03 (Python version) is re-locked at the end of Phase 22** based on the pre-flight outcome. PROJECT.md and REQUIREMENTS.md are updated to match in this phase.
- **D-22-07:** **Auto-fallback flow:** if the primary target (3.14) fails any pre-flight step, immediately retry with the next-lower Python (3.13). No manual user gate between attempts. If 3.13 also fails, phase delivers a documented blocking decision in SUMMARY.md and stops the auto-advance chain.
- **D-22-08:** If 3.14 wins, **PY-FUT-01** (Python 3.14 follow-up) is removed from `REQUIREMENTS.md` Future Requirements; if 3.13 wins, PY-FUT-01 stays but its blocker note ("ydata-profiling pin") is replaced with whatever cp314 wheel gap actually blocked (e.g., "lightgbm cp314 wheel pending").

### ydata-profiling Drop

- **D-22-09:** `ydata-profiling` is **removed from `.claude/doml/templates/requirements.in`** (line 31) and from `.claude/doml/templates/requirements.txt` (line 130 pin).
- **D-22-10:** EDA notebook profiling cell is **replaced with a DuckDB `SUMMARIZE` query + hand-rolled summary** (cardinality, null-rate, dtype) presented as a pandas DataFrame. Aligns with CLAUDE.md "DuckDB first" rule.
- **D-22-11:** EDA notebook templates affected: `.claude/doml/templates/notebooks/data_understanding_python.ipynb` (and any other notebook importing `ydata_profiling`). Discover-and-replace exhaustively; verify with `grep -rn "ydata_profiling" .claude/`.
- **D-22-12:** `requirements.in` (root, DoML-itself) cleanup: `pip-tools` removed (PY-04), `numpy<2.4` added (PY-05), `mistune<3` retained (PY-03). No other dep changes — `ydata-profiling` is template-only and never lived in root `requirements.in`.

### scipy-notebook Tag

- **D-22-13:** scipy-notebook dated tag is **looked up at execution time** (`docker pull quay.io/jupyter/scipy-notebook:latest` + inspect to read the dated tag), not pre-pinned to research's assumed `2026-04-21`.
- **D-22-14:** The resolved tag is **pre-written into both Dockerfiles' `FROM` lines** (root `Dockerfile` and `.claude/doml/templates/Dockerfile`) in this phase. Only the `FROM` line — the install-layer rewrite is Phase 23's job. Reduces Phase 23 handoff risk.
- **D-22-15:** Pin format is **tag-only** (`quay.io/jupyter/scipy-notebook:YYYY-MM-DD`), not tag+digest. Matches v1.5 pattern; Jupyter dated tags are immutable per Jupyter Docker Stacks policy.

### Audit Log Artifact

- **D-22-16:** Audit log is a **single Markdown file: `22-AUDIT.md`** in the phase directory. One source of truth; no `audit/` subdirectory.
- **D-22-17:** `22-AUDIT.md` contains: (a) full `mamba list` from scipy-notebook container, (b) conda∩requirements.in conflict diff, (c) `uv pip compile` resolved output as a diff against the v1.5 `requirements.txt`. Go/no-go decision + Python version landed on lives in `22-SUMMARY.md`, not the audit.

### Commit Strategy

- **D-22-18:** Three commits across this phase:
  1. `chore: drop ydata-profiling from template + replace EDA profiling cell` — template `requirements.in`, template `requirements.txt`, EDA notebook(s)
  2. `chore: switch lockfile to uv format (Python <ver>)` — root `requirements.in` (numpy<2.4 added, pip-tools removed), root `requirements.txt` regenerated with hashes; **single isolated commit per `PITFALLS.md` #6** to keep the noisy lockfile diff isolated
  3. `docs(22): pre-flight audit + scipy-notebook tag pin` — `22-CONTEXT.md`, `22-AUDIT.md`, `22-SUMMARY.md`, `Dockerfile`/template `Dockerfile` `FROM` line update, `PROJECT.md` D-03 update if Python version changed

### Claude's Discretion

- Exact CLI invocation of the throwaway-container one-liner (env-var injection, mount paths)
- Format of the conflict-diff section in `22-AUDIT.md` (table vs list)
- DuckDB `SUMMARIZE` query phrasing in the new EDA cell (`SELECT * EXCLUDE (target_col) FROM read_csv(...)` patterns)
- Whether to write a `noxfile.py` / Make target for the validation rig or just shell scripts (tilt: keep it simple — a single bash invocation is fine)
- How to surface "auto-fallback fired" in SUMMARY (banner vs section)
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone Research (read first)
- `.planning/research/SUMMARY.md` — Executive summary; phase ordering rationale; confidence assessment
- `.planning/research/STACK.md` — Pinned versions for every dep; "What NOT to Use" table; Dockerfile sketch
- `.planning/research/ARCHITECTURE.md` — Single-stage Dockerfile structure; `uv pip install` vs sync rationale; cache mount; build budget breakdown
- `.planning/research/PITFALLS.md` §1–5 — Critical pitfalls (prophet cp314 wheel, ydata 3.14 cap, uv pip sync, mistune<3, R refs); §6 lockfile-format diff noise; §15 pre-flight checks

### Project & Roadmap
- `.planning/PROJECT.md` — D-01..D-04 v1.6 locked decisions, milestone goal, build budget (<5 min)
- `.planning/REQUIREMENTS.md` — PY-01..PY-05 (Python modernization), CONT-06 (lockfile regen with hashes); PY-FUT-01 (to be revisited based on Python target outcome)
- `.planning/ROADMAP.md` §Phase 22 — 5 success criteria + Depends on Phase 21

### Code Touched in This Phase
- `requirements.in` (root) — drop pip-tools, add numpy<2.4, retain mistune<3
- `requirements.txt` (root) — regenerate via `uv pip compile --generate-hashes`
- `.claude/doml/templates/requirements.in` — drop ydata-profiling
- `.claude/doml/templates/requirements.txt` — drop ydata-profiling==4.18.1 pin
- `.claude/doml/templates/notebooks/data_understanding_python.ipynb` — replace profiling cell with DuckDB SUMMARIZE
- `Dockerfile` (root) — `FROM` line tag bump only (install layer untouched here)
- `.claude/doml/templates/Dockerfile` — same `FROM` line bump

### Cross-phase Hand-offs
- **From Phase 21:** v1.5 install scripts shipped (no direct dep)
- **To Phase 23:** lockfile + scipy-notebook tag + Python version baseline → consumed by Dockerfile rewrite

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Existing root `Dockerfile`** — current pattern with `USER root` / `mamba install` / `USER ${NB_UID}` / `pip install` / `fix-permissions` is the structural skeleton Phase 23 will rebuild on. Phase 22 only touches the `FROM` line.
- **`.claude/doml/templates/Dockerfile`** — mirrors the root pattern. Same one-line tag bump applies.
- **DuckDB already in `requirements.in`** — the EDA-cell replacement uses an existing dep, no new install.
- **`requirements.in` comment header** — already documents the regenerate command; only the regen instruction (`pip-compile` → `uv pip compile`) needs updating in this phase or carried into Phase 23.

### Established Patterns
- **Dated quay.io tags for reproducibility** (v1.5 pattern: `datascience-notebook:2026-04-02`). New tag follows the same `:YYYY-MM-DD` convention.
- **`requirements.in` is source of truth, `requirements.txt` is generated** — REPR-04. uv preserves this contract; only the generator command changes.
- **EDA notebook cells use `read_csv` / `read_parquet` via DuckDB or pandas** — DuckDB SUMMARIZE replacement plugs into the same pattern.

### Integration Points
- **Pre-flight container** is ephemeral; nothing persists. Outputs (`mamba list`, compile log) are captured to phase dir, not committed back to a built image.
- **Lockfile regeneration** integrates with existing rebuild flow (`docker compose run --rm jupyter <cmd>`) — but in pre-flight we run uv outside the project container in a throwaway scipy-notebook container, since the project container hasn't been rebuilt yet.
- **STATE.md "ydata-profiling deferred"** entry from Phase 01-04 is now resolved by D-22-09 — append a "Phase 22: ydata-profiling dropped entirely" entry.
</code_context>

<specifics>
## Specific Ideas

- **Auto-fallback semantics:** "Try 3.14, fall back to 3.13" means run the full pre-flight gate (compile + install + import smoke) for 3.14 first. Only if any step fails does retry with 3.13 begin. Don't try 3.14 just for compile and 3.13 for install — that's a hybrid that doesn't validate.
- **Single isolated lockfile commit (D-22-18 commit 2)** is non-negotiable per `PITFALLS.md` #6 — otherwise the 100+ line pip-compile→uv format diff swallows real changes in code review.
- **Phase boundary discipline:** Resist the temptation to land Phase 23's install-layer Dockerfile changes early. The `FROM` line tag bump is the only Dockerfile edit allowed in Phase 22.
- **Pre-flight container should mirror Phase 23's intended uv invocation** — same `UV_LINK_MODE=copy`, same `--system` flag — so anything that fails here would fail in Phase 23.
- **Audit raw artifacts:** the full `mamba list` output (~200 lines) goes in `22-AUDIT.md` inline as fenced text, not as a separate `mamba-list.txt` file. Keeps the audit one-clickable.
</specifics>

<deferred>
## Deferred Ideas

- **Wider `requirements.in` audit** — beyond `ydata-profiling`, are other deps unused? (e.g., is `pmdarima` exercised? is `umap-learn` reachable from any active notebook template?) Out of Phase 22 scope; capture as backlog if relevant.
- **Mirror scipy-notebook to `ghcr.io`** — `SLIM-FUT-02` already in REQUIREMENTS.md Future. Stays deferred.
- **Move `pyinstaller` out of main image** — `SLIM-FUT-01` already in REQUIREMENTS.md Future. Stays deferred.
- **PEP 751 / `uv.lock` migration** — `LOCK-FUT-01` already deferred.
- **`Dockerfile.preflight` as a permanent CI artifact** — option B in the validation-rig question; deferred. If we ever want a reusable pre-flight rig (for future Python bumps), revisit.
- **Skimpy/sweetviz EDA profiler** — explicitly rejected (replaces one dep with another). DuckDB SUMMARIZE is the chosen replacement.

</deferred>

---

*Phase: 22-pre-flight-wheel-validation-lockfile-bootstrap*
*Context gathered: 2026-04-30*
