# Milestones

## v1.5 Public Release + Install Scripts (Shipped: 2026-04-30)

**Scope:** Phases 19, 20, 21 — 5 plans (3 with SUMMARY, 2 without)
**Timeline:** 2026-04-20 → 2026-04-29 (10 days)
**Git range:** `19577b1..4e90677` — 32 commits, 40 files changed, +7,265 / -513 lines

**Goal:** Make DoML publicly consumable — Bash and PowerShell install scripts that bootstrap the framework from GitHub (no repo clone required), polished README with Quick Start one-liners and Mermaid process diagram, MIT license, donation info, and GitHub Copilot support so the framework works with both Claude Code and GitHub Copilot.

### Key Accomplishments

1. **`README.md` + `LICENSE`** — Public README with Quick Start one-liners (bash + PowerShell), Mermaid new-project flow diagram, command table, AI token investment note; MIT LICENSE with `Copyright (c) 2026 William W Palace, III`.
2. **`.github/FUNDING.yml`** — Donations routed via GitHub's Sponsor button (PayPal + Venmo URLs in FUNDING.yml, kept out of the README body per locked decision D-03).
3. **`install.sh` + `install.ps1`** — Archive-based installers (no `git clone` required); support `VERSION=v1.5` / `-Version v1.5` / `$env:DOML_VERSION` pinning; fail-fast on download error with URL details; idempotent `data/` preservation.
4. **Tool-neutral `AGENTS.md`** — Cross-agent instruction template at repo root covering project structure, reproducibility rules, all 14 DoML commands, DuckDB guidance, and prohibited actions. Compatible with Copilot, Cursor, Gemini, and Claude.
5. **`--target claude|copilot` flag** — Both install scripts gain `--target` / `-Target` (default: `claude`). Copilot branch installs SKILL.md files to `.github/skills/`, workflows to `.github/doml/workflows/`, templates to `.github/doml/templates/`, `CLAUDE.md` as `.github/copilot-instructions.md`, and `AGENTS.md` at project root.
6. **D-06 always-overwrite `CLAUDE.md`** — Replaces skip-if-present so framework upgrades pull in CLAUDE.md changes; `data/` contents are still preserved.

### Locked Design Decisions

- **D-01 (Phase 21):** No `--target both`. Only `claude` and `copilot`.
- **D-02 (Phase 21):** Default target = `claude`, not `both`.
- **D-03 (Phase 21):** SKILL.md files installed under `.github/skills/` replace the originally-specified `.github/prompts/*.prompt.md` approach.
- **D-03 (Phase 19):** Donation routing via `.github/FUNDING.yml` and the GitHub Sponsor button — no inline PayPal/Venmo links in README body.
- **D-06:** `CLAUDE.md` is always overwritten on install (was: skipped if present).

### Known Gaps (accepted as tech debt — see `milestones/v1.5-MILESTONE-AUDIT.md`)

| Gap | Severity | Notes |
|-----|----------|-------|
| **Phase 19 missing SUMMARY.md + VERIFICATION.md** | paperwork | Artifacts (README, LICENSE, FUNDING.yml) shipped and meet ROADMAP success criteria. GSD verification step skipped during execution. |
| **Phase 20 missing SUMMARY.md + VERIFICATION.md (×2 plans)** | paperwork | Artifacts (install.sh, install.ps1) shipped and meet ROADMAP success criteria. GSD verification step skipped during execution. |
| **REQUIREMENTS.md text stale for INST-07, INST-08, COP-03** | paperwork | Original spec text describes superseded design. ROADMAP success criteria reflect locked decisions D-01/D-02/D-03; REQUIREMENTS.md text was never updated. |
| **REQUIREMENTS.md not updated for D-06 INST-06 divergence** | paperwork | INST-06 spec says CLAUDE.md skip-if-present; D-06 changed to always-overwrite. Behavior is correct; spec text not updated. |
| **DOC-05 wording mismatch** | paperwork | Spec says "donation section with PayPal and Venmo links". Implementation uses GitHub Sponsor button + `.github/FUNDING.yml` (which contains the PayPal+Venmo URLs). Functionally equivalent; spec text could be updated. |
| **Phase 21 VERIFICATION.md stale** | tech debt | VERIFICATION.md written 2026-04-22; commits 2fa0413 and 4e90677 added material logic (`.github/doml/workflows/`, `.github/doml/templates/` install) that VERIFICATION.md does not cover. |
| **Phase 21 VALIDATION.md draft** | tech debt | `nyquist_compliant: false`, `wave_0_complete: false`. Phase 19 and 20 have no VALIDATION.md. |
| **COP-04 needs VS Code human verification** | human-test | SKILL.md invocability via `/doml-*` in Copilot Chat cannot be verified from CLI. |
| **README typos** | polish | "Future Milestones" section has misspellings: `cababilities`, `qutomation`, `tereis`/`sereis`, `framewowrk`. |
| **Phase 10 — 3 unresolved `human_uat` items** | carryover | Outside v1.5 scope; flagged by cross-phase audit. |

### Audit Outcome

- **Status:** `gaps_found` (accepted)
- **Score:** 8/15 requirements fully satisfied, 5 diverged-by-design (acceptable per locked decisions), 1 partial (DOC-05 wording), 1 human-needed (COP-04)
- **Substance:** all 14/15 ROADMAP success criteria met (1 needs human test)
- **Bookkeeping:** incomplete (see Known Gaps)

---
