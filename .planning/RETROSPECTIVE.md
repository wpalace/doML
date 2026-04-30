# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.5 — Public Release + Install Scripts

**Shipped:** 2026-04-30
**Phases:** 3 (19, 20, 21) | **Plans:** 5 | **Sessions:** ~multiple over 10 days
**Git range:** `19577b1..4e90677` — 32 commits, 40 files changed, +7,265 / -513 lines

### What Was Built

- Public `README.md` with Quick Start one-liners (bash + PowerShell), Mermaid new-project flow diagram, command table, and AI token investment note
- MIT `LICENSE` and `.github/FUNDING.yml` (PayPal + Venmo via GitHub Sponsor button)
- `install.sh` and `install.ps1` — archive-based installers with VERSION pinning, fail-fast error handling, and idempotent `data/` preservation
- Tool-neutral `AGENTS.md` template for cross-agent compatibility (Copilot, Cursor, Gemini, Claude)
- `--target claude|copilot` flag on both installers; copilot branch installs SKILL.md to `.github/skills/`, workflows + templates to `.github/doml/`, `CLAUDE.md` as `.github/copilot-instructions.md`, and `AGENTS.md` at project root
- D-06: `CLAUDE.md` always overwritten on install so framework upgrades pull in changes

### What Worked

- **Locking design decisions in CONTEXT.md before implementation** — D-01 (no `--target both`), D-02 (default `claude`), D-03 (SKILL.md replaces `.prompt.md`), D-06 (always-overwrite CLAUDE.md), and Phase 19's D-03 (FUNDING.yml-only donations) prevented re-litigating the design mid-build. ROADMAP success criteria were updated to reflect the locks.
- **Archive-based install** (download tarball, extract, copy from `$SRC`) was simpler than the originally-considered per-file `curl` loop — fewer failure modes and atomic versioning.
- **Phase 21 verification was thorough** for what existed at write time — caught divergences between REQUIREMENTS.md and ROADMAP, documented them explicitly with rationale rather than silently passing.

### What Was Inefficient

- **Phases 19 and 20 were executed without producing SUMMARY.md or VERIFICATION.md.** Plans were marked `[x]` in ROADMAP and the artifacts shipped, but the GSD verification gate was skipped entirely. This left the milestone at 50/53 plans (94%) progress despite all substantive work being done. Closing the gap requires either backfilling the docs or accepting them as Known Gaps in MILESTONES.md.
- **REQUIREMENTS.md text drifted from implementation** as locked decisions accumulated (D-01..D-06, plus Phase 19's D-03). The ROADMAP success criteria were updated; REQUIREMENTS.md was not. Audit caught 5 stale requirement entries (INST-06, INST-07, INST-08, COP-03, DOC-05). Pattern: when a CONTEXT.md decision supersedes a requirement, REQUIREMENTS.md needs an explicit edit, not just a ROADMAP update.
- **Phase 21 VERIFICATION.md went stale within hours of being written.** Material fixes 2fa0413 (workflows path rewrite) and 4e90677 (templates install) landed after VERIFICATION.md was committed; the verification doesn't cover the `.github/doml/workflows/` or `.github/doml/templates/` install paths. Verification is a snapshot, not a contract — post-verification fixes need re-verification or an explicit "amendment" addendum.
- **VALIDATION.md missing for two of three phases** (19, 20). Phase 19 had a VALIDATION.md briefly but it was reverted (commit `05b503d`). Nyquist validation coverage went unaddressed during the milestone.

### Patterns Established

- **`.github/FUNDING.yml` over inline donation links** — GitHub renders the Sponsor button automatically; keeps README clean.
- **Archive-based installers** — `tar -xzf` from a release tag is simpler than per-file `curl` loops.
- **Default to most common case** — `--target claude` rather than `both` reflects the dominant install path; `both` was scoped out.
- **Path rewrites at install time** — install.sh/install.ps1 rewrite `@.claude/doml/workflows/` → `.github/doml/workflows/` for the copilot branch using `sed`/`-replace`. Avoids maintaining two copies of skills/workflows.

### Key Lessons

1. **Lock design decisions in CONTEXT.md before implementing, then update both ROADMAP *and* REQUIREMENTS.md.** Otherwise the audit surfaces "diverged" requirements that are actually validated-by-design — noisy but unavoidable when spec text isn't kept in sync.
2. **Don't skip the GSD verification gate even for "obvious" phases.** Phases 19 and 20 produced README, LICENSE, install.sh, install.ps1 — visible artifacts that "obviously" worked. Skipping SUMMARY/VERIFICATION cost more cleanup later than writing them inline would have.
3. **Verification is a snapshot, not a contract.** When material fixes land post-VERIFICATION.md, either re-verify or append an addendum. A stale verification is worse than no verification because it gives false confidence.
4. **Run `/gsd-validate-phase` per phase, not retroactively.** Two of three phases (19, 20) have no VALIDATION.md; the one that does (21) is in `draft` status with `nyquist_compliant: false`. Catching up retroactively is harder than doing it inline.
5. **Audit before completing the milestone.** Running `/gsd-audit-milestone` first surfaced all the paperwork gaps in one pass and let us make an informed "accept tech debt" decision rather than discovering them piecemeal.

### Cost Observations

- Model mix: predominantly Opus 4.7 (1M context) — quality profile in `.planning/config.json`
- Sessions: estimated 8–12 sessions over 10 days based on commit cadence
- Notable: Phase 21 had a research → plan → execute → verify cycle (~1 day); Phases 19 and 20 collapsed to plan → execute (no verify), which traded GSD bookkeeping for speed but created the audit gaps documented above

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.5 | 3 | 5 | First milestone where two phases skipped SUMMARY+VERIFICATION; surfaced as audit gaps_found and accepted as tech debt |

### Cumulative Quality

| Milestone | VERIFICATIONs | VALIDATIONs | Audit Status |
|-----------|---------------|-------------|--------------|
| v1.5 | 1 of 3 phases | 1 of 3 phases (draft) | gaps_found (accepted) |

### Top Lessons (Verified Across Milestones)

1. Lock design decisions in CONTEXT.md *and* propagate to REQUIREMENTS.md, not just ROADMAP.
2. Don't skip GSD bookkeeping for "obvious" phases — paperwork debt accumulates faster than it pays back.
3. Verification is a snapshot; post-verification fixes need re-verification or an addendum.
