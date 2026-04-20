# Phase 19: Public Release Docs — Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the public-facing documentation for the DoML GitHub repo: `README.md` (Quick Start one-liners, full Mermaid new-project flow diagram, command table, requirements), `LICENSE` (MIT), and a donation section with PayPal + Venmo links.

This phase does NOT implement install scripts (Phase 20) or Copilot support (Phase 21). The Quick Start one-liners reference `install.sh` / `install.ps1` which will exist after Phase 20 — placeholders are acceptable.

**Requirements in scope:** DOC-01, DOC-02, DOC-03, DOC-04, DOC-05

</domain>

<decisions>
## Implementation Decisions

### GitHub Identity

- **D-01: GitHub repo is `wpalace/doML`**
  - Raw file base URL: `https://raw.githubusercontent.com/wpalace/doML/main/`
  - Quick Start one-liners reference:
    - Bash: `bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)`
    - PowerShell: `irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex`
  - These URLs will be live after Phase 20 ships the install scripts

### LICENSE File

- **D-02: MIT license, exact copyright line**
  - `Copyright (c) 2026 William W Palace, III`
  - Standard MIT license body (no modifications)

### Donation Section

- **D-03: Use `.github/FUNDING.yml` — do NOT put donation links inline in README**
  - PayPal and Venmo addresses are intentionally kept out of the README body
  - GitHub renders the Sponsor button from `FUNDING.yml`; that is the only entry point for donations
  - `FUNDING.yml` already contains `https://paypal.me/WilliamPalace442` and `https://venmo.com/William-Palace`

- **D-04: Tone — lightly self-aware, developer-relatable**
  - Acknowledge the AI token investment honestly but with dry humor
  - Specifically call out that the highest tier Claude Max plan was purchased just to build this project
  - Keep it brief (2–3 sentences max) — earnest but not heavy
  - Support section should reference the Sponsor button, not paste raw payment URLs
  - Example framing: "Building DoML consumed a meaningful amount of AI compute — and yes, the top-tier Claude Max plan was purchased specifically to build this. If it saves you time, contributions are appreciated via the **Sponsor** button at the top of this page."

### Mermaid Diagram (DOC-03)

- **D-05: Full-detail flow diagram — all branches, all decision points**
  - Diagram must show:
    1. **Data source decision** — "Existing data in /data?" → Yes (proceed) / No → `/doml-get-data` (Kaggle or direct URL download)
    2. **Business Understanding** — `/doml-business-understanding`
    3. **Time factor decision** — "Time series?" → Yes → `/doml-forecasting` branch / No → problem type fork
    4. **Problem type fork** (4 branches from single decision node):
       - Regression → `/doml-modelling`
       - Classification → `/doml-modelling`
       - Clustering → `/doml-modelling`
       - Dimensionality Reduction → `/doml-modelling`
    5. **Data Understanding** — `/doml-data-understanding` (runs before modelling, after BU)
    6. **Optional anomaly detection** — `Optional: /doml-anomaly-detection` after modelling
    7. **Deployment decision** — "Deploy?" → Yes → deployment target fork:
       - CLI binary → `/doml-deploy-model` (CLI)
       - Web service → `/doml-deploy-model` (Web)
       - ONNX/WASM → `/doml-deploy-model` (WASM)
    8. **Iterate** — `/doml-iterate-deployment` shown as a loop back from deployed state
  - Use `flowchart TD` (top-down)
  - Node labels use the actual command names (e.g., `/doml-business-understanding`) for discoverability
  - Fenced `\`\`\`mermaid` block — renders natively on GitHub

### README Structure & Depth

- **D-06: No badges** — clean prose header, no shields.io badge row

- **D-07: Full command table — all 13 `/doml-*` commands**
  - Markdown table: `Command | Description | Key flags`
  - Commands to include (all current DoML commands):
    - `/doml-new-project`
    - `/doml-business-understanding`
    - `/doml-data-understanding`
    - `/doml-modelling`
    - `/doml-iterate`
    - `/doml-anomaly-detection`
    - `/doml-forecasting`
    - `/doml-get-data`
    - `/doml-deploy-model`
    - `/doml-deploy-cli`
    - `/doml-deploy-web`
    - `/doml-deploy-wasm`
    - `/doml-iterate-deployment`
    - `/doml-progress`
  - Key flags column: only show flags that users would actually set (e.g., `--guidance`, `--target`, `--file`) — skip internal flags

- **D-08: README section order**
  1. Title + one-line description
  2. What is DoML? (2–3 paragraph description)
  3. Requirements (Docker + Claude Code or GitHub Copilot)
  4. Quick Start (bash + PowerShell one-liners)
  5. How It Works (Mermaid diagram)
  6. Commands (full table)
  7. Reproducibility (brief: seeds, relative paths, immutable raw data — links to CLAUDE.md for detail)
  8. Support the Project (donation section)

</decisions>

<specifics>
- The repo will be public at `https://github.com/wpalace/doML`
- Install scripts (`install.sh`, `install.ps1`) do not exist yet — Quick Start one-liners should reference the Phase 20 URLs as-is (they'll be accurate after Phase 20)
- The CLAUDE.md in this repo is the installed project's CLAUDE.md (shipped by the install script) — it is NOT the framework source; README should not conflate the two
- `/doml-progress` is also a valid command to list in the table (status/reporting utility)
</specifics>

<deferred>
- GitHub Actions CI / automated install script validation — deferred to future milestone
- Signed releases / checksum verification — deferred to future milestone
- GEMINI.md / Gemini CLI support — deferred to future milestone
</deferred>
