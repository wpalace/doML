# Requirements: DoML — Do Machine Learning

**Defined:** 2026-04-04
**Updated:** 2026-04-20 — Milestone v1.5 Public Release + Install Scripts
**Core Value:** A data scientist can drop a dataset into `/data`, answer a few questions, and get a fully reproducible, peer-reviewable ML analysis with stakeholder-ready summaries — without re-inventing the process each time.

---

## Milestone v1.5 Requirements — Public Release + Install Scripts

### Install Scripts (INST)

- [ ] **INST-01**: User can run a single bash one-liner to install the DoML Claude framework into their project without cloning the repo
- [ ] **INST-02**: User can run a single PowerShell one-liner to install the DoML Claude framework into their project without cloning the repo
- [ ] **INST-03**: Install scripts accept a `VERSION` variable/parameter to pin downloads to a specific release tag instead of `main`
- [ ] **INST-04**: Install scripts create the full `.claude/` tree (skills, workflows, templates), `CLAUDE.md`, and `data/raw|processed|external/` directories
- [ ] **INST-05**: Install scripts fail fast with a clear error message if any file download fails, rather than silently continuing with a partial install
- [ ] **INST-06**: Install scripts are safe to re-run: framework files are always updated; `data/` contents are never deleted; `CLAUDE.md` is skipped if already present
- [ ] **INST-07**: Install scripts accept `--target claude|copilot|both` (default: `both`)
- [ ] **INST-08**: With `--target copilot` or `both`, the script downloads Claude framework files and then programmatically generates Copilot equivalents (`AGENTS.md`, `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md`) — no separate Copilot source files live in the repo

### Public Release Docs (DOC)

- [ ] **DOC-01**: `README.md` exists at repo root with project description, Quick Start section, command list, and requirements (Docker + Claude Code or GitHub Copilot)
- [ ] **DOC-02**: Quick Start section contains copy-paste bash and PowerShell one-liners that download and run the install script directly from GitHub
- [ ] **DOC-03**: `README.md` includes a Mermaid diagram showing the DoML new-project decision flow (data check → get-data branch → Business Understanding → Data Understanding → problem type fork → Modelling → optional anomaly detection → Deployment decision)
- [ ] **DOC-04**: `LICENSE` file contains the MIT license with Copyright (c) 2026 William W Palace, III
- [ ] **DOC-05**: `README.md` includes a donation section with PayPal and Venmo links and a brief, honest note about the AI token investment made in building DoML

### Copilot Support (COP)

- [ ] **COP-01**: `AGENTS.md` is generated in the user's project root — universal cross-tool instructions readable by GitHub Copilot, Claude Code, Cursor, and Gemini
- [ ] **COP-02**: `.github/copilot-instructions.md` is generated — always-on Copilot project instructions derived from `CLAUDE.md` content, adapted to be tool-neutral
- [ ] **COP-03**: `.github/prompts/doml-*.prompt.md` files are generated for each DoML command, with valid `mode: agent` frontmatter, by transforming the corresponding `SKILL.md` content
- [ ] **COP-04**: Copilot prompt files are invocable via `#doml-new-project` (and equivalent for each command) in GitHub Copilot Chat in VS Code

---

## Future Requirements (deferred from v1.5)

- `GEMINI.md` at repo root for Gemini CLI support
- `--target gemini` flag in install scripts
- GitHub Actions workflow for automated framework file validation
- npm/pip package distribution as an alternative to the install script
- Signed releases / checksum verification for install script downloads
- Windows/macOS native binary of the install script (currently PowerShell + Bash only)
- GitHub Sponsors integration (alternative to PayPal/Venmo direct links)

---

## Out of Scope

- **Copilot extension packaging (VSIX)** — prompt files are the Copilot integration; no extension required
- **GitHub Actions CI** — automated testing of install scripts deferred to a future milestone
- **Cloud deployment or CDN hosting** of DoML artifacts — GitHub raw URLs are sufficient
- **Cursor-specific config** — AGENTS.md covers Cursor; no Cursor-specific files needed
- **Re-implementing DoML commands in Copilot** — Copilot prompt files delegate to the same workflows; no separate Copilot implementation

---

## Traceability

| REQ-ID | Phase |
|--------|-------|
| DOC-01 – DOC-05 | Phase 19 |
| INST-01 – INST-06 | Phase 20 |
| COP-01 – COP-04, INST-07 – INST-08 | Phase 21 |
