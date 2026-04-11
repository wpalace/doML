---
phase: 09-doml-get-data
asvs_level: 1
audited: 2026-04-10
auditor: gsd-secure-phase
block_on: high
result: SECURED
threats_closed: 10
threats_total: 10
---

# Security Audit — Phase 09: doml-get-data

**Phase:** 09 — doml-get-data
**Threats Closed:** 10/10
**ASVS Level:** 1
**Result:** SECURED

---

## Threat Verification

### Mitigate — Evidence Required

| Threat ID | Category | Component | Evidence |
|-----------|----------|-----------|----------|
| T-09-01 | Spoofing | Kaggle credential check | `get-data.md:81-87` — credential check runs inside container via `docker compose exec jupyter bash -c '...'`; sentinel `MISSING_KAGGLE_CREDS` printed from within container environment where vars are set |
| T-09-03 | Tampering | ZIP extraction path traversal | `get-data.md:187` — `unzip -q` targets `./data/raw/.stage/` (scoped directory); `get-data.md:204-206` — only `csv tsv parquet xlsx xls` extensions moved to `data/raw/`; executables and scripts left in `.stage/` then deleted at Step 5e |
| T-09-04 | Information Disclosure | Kaggle API key exposure | `docker-compose.yml:13-14` — `KAGGLE_USERNAME=${KAGGLE_USERNAME:-}` and `KAGGLE_KEY=${KAGGLE_KEY:-}` (empty defaults, no hardcoded values); `.gitignore:36` — `.env` is gitignored; `get-data.md:97-104` — setup instructions direct user to `.env` file |
| T-09-07 | Repudiation | No provenance for failed downloads | `get-data.md:249,277-298` — provenance appended in Step 7, which runs after successful `docker cp` (Step 4c) or URL move (Step 5d); failed runs that stop earlier in the flow never reach Step 7 |
| T-09-08 | Denial of Service | Infinite loop on persistent empty scan | `new-project.md:187-227` — `AskUserQuestion` gate requires explicit user choice each iteration ("Get data now" / "Add files manually"); `loop back to the AskUserQuestion above` at line 206 and 227 confirms loop only advances on user input |
| T-09-10 | Spoofing | Malformed source input in Step 3b | `get-data.md:21` — "If the first token is neither `kaggle` nor `url` (case-insensitive), or if no arguments were provided" triggers usage display and stop; same Step 1 validation applies when workflow is invoked inline from Step 3b |

### Accept — Documented Accepted Risks

| Threat ID | Category | Accepted Rationale |
|-----------|----------|--------------------|
| T-09-02 | Tampering | Files land in `data/raw/` as data-only; no execution step runs downloaded files; local dev tool — user responsible for trusting data source |
| T-09-05 | Denial of Service | No size limit enforced — local dev tool, not a server; user responsible for dataset size; solo developer context |
| T-09-06 | Elevation of Privilege | Container already runs as root by design (`user: root` in docker-compose.yml line 27); no privilege escalation beyond existing container posture |
| T-09-09 | Tampering | Step 3 scan catches `.xls` files with an error (unchanged); other unsupported formats are ignored by the file extension filter and never moved to `data/raw/` |

---

## Unregistered Threat Flags

None — both SUMMARY.md files (09-01 and 09-02) explicitly state "None" under Threat Flags. No new attack surfaces or trust boundaries were introduced beyond what the threat register in the plans covers.

---

## Implementation Files Audited (Read-Only)

- `/home/bill/source/DoML/.claude/doml/workflows/get-data.md` (333 lines)
- `/home/bill/source/DoML/.claude/doml/workflows/new-project.md`
- `/home/bill/source/DoML/.claude/skills/doml-get-data/SKILL.md`
- `/home/bill/source/DoML/.claude/doml/templates/docker-compose.yml`
- `/home/bill/source/DoML/requirements.in`
- `/home/bill/source/DoML/.gitignore`
