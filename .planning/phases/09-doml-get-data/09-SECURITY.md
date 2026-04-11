---
phase: 9
slug: doml-get-data
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-11
---

# Phase 9 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Host → Docker container | `docker compose exec` runs commands inside the container; input (slug/URL) originates from user's CLI arguments | Kaggle slug or URL string |
| External network → host | `curl` downloads file from arbitrary URL supplied by user; file contents are untrusted | Binary file data (CSV/Parquet/Excel) |
| Container → host filesystem | `docker cp` transfers files from `/tmp/doml-stage` to `./data/raw/` on the host | Dataset files |
| Kaggle API | Credential env vars (`KAGGLE_USERNAME`, `KAGGLE_KEY`) passed through docker-compose environment; never written to files | Credentials (env vars only) |
| User input → new-project.md interview | User chooses "Get data now" or "Add files manually"; source slug/URL entered by user passed to get-data workflow | User choice + source string |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-09-01 | Spoofing | Kaggle credential check | mitigate | Credentials checked inside container via `docker compose exec`; `MISSING_KAGGLE_CREDS` sentinel printed from within container where env vars are set (`get-data.md:81-87`) | closed |
| T-09-02 | Tampering | URL download — arbitrary file content | accept | See Accepted Risks | closed |
| T-09-03 | Tampering | ZIP extraction — path traversal | mitigate | `unzip -q` scoped to `./data/raw/.stage/`; only csv/tsv/parquet/xlsx/xls moved to `data/raw/` — executables stay in `.stage/` then deleted (`get-data.md:187,204-206`) | closed |
| T-09-04 | Information Disclosure | Kaggle API key in docker-compose.yml | mitigate | Both vars use `:-` empty default, no hardcoded key (`docker-compose.yml:13-14`); `.env` gitignored (`.gitignore:36`); setup guide directs to `.env` (`get-data.md:97-104`) | closed |
| T-09-05 | Denial of Service | Unbounded download size | accept | See Accepted Risks | closed |
| T-09-06 | Elevation of Privilege | `docker compose exec` runs as root | accept | See Accepted Risks | closed |
| T-09-07 | Repudiation | No provenance for failed downloads | mitigate | Provenance Step 7 runs after successful transfer only; failure paths in Steps 4 and 5 stop before Step 7 (`get-data.md:249,277-298`) | closed |
| T-09-08 | Denial of Service | Infinite loop on persistent empty scan | mitigate | `AskUserQuestion` gate required each iteration; loop never advances autonomously (`new-project.md:187-227`) | closed |
| T-09-09 | Tampering | User bypasses validation via "Add files manually" | accept | See Accepted Risks | closed |
| T-09-10 | Spoofing | Malformed source input in Step 3b | mitigate | Step 1 of get-data.md validates first token is `kaggle` or `url`; displays usage and stops on any other input (`get-data.md:21`) | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-09-01 | T-09-02 | Files land in `data/raw/` as data-only; no execution step runs downloaded files; local dev tool — user responsible for trusting their data source | Bill | 2026-04-11 |
| AR-09-02 | T-09-05 | No size limit enforced — local dev tool, not a server; user responsible for choosing datasets that fit disk; solo developer context | Bill | 2026-04-11 |
| AR-09-03 | T-09-06 | Container already runs as root by design (`docker-compose.yml:27`, per CLAUDE.md `user: root`); no privilege escalation beyond existing container posture | Bill | 2026-04-11 |
| AR-09-04 | T-09-09 | Step 3 scan already catches `.xls` files with an error (unchanged); other unsupported formats are ignored by the extension filter and won't block the interview | Bill | 2026-04-11 |

*Accepted risks do not resurface in future audit runs.*

---

## Audit Trail

### Security Audit 2026-04-11

| Metric | Count |
|--------|-------|
| Threats found | 10 |
| Mitigate verified | 6 |
| Accept documented | 4 |
| Open | 0 |

**Method:** gsd-security-auditor reviewed `get-data.md`, `new-project.md`, `docker-compose.yml`, `.gitignore`, `requirements.in`, `SKILL.md` against STRIDE register from PLAN.md threat models. All mitigations verified by file + line reference.
