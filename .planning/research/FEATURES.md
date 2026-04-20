# Feature Research — v1.5 Public Release + Install Scripts

**Domain:** OSS release infrastructure, install scripts, Copilot support
**Researched:** 2026-04-20
**Confidence:** HIGH

---

## Table Stakes

### Install Scripts (Bash + PowerShell)
- Download and install all DoML framework files into the current working directory
- Create `.claude/` directory tree with all skills, workflows, templates, references
- Create `CLAUDE.md` at project root
- Create `AGENTS.md` at project root (universal cross-tool instructions)
- Create `data/raw/`, `data/processed/`, `data/external/` directory structure
- Create `data/raw/README.md` (immutability notice)
- No git clone required — pulls files individually from raw.githubusercontent.com
- Works from any empty or new project directory
- Idempotent: safe to re-run without overwriting user data files
- Progress feedback: print each step as it completes
- Error handling: fail fast with clear message if download fails

### README.md
- Project name, tagline, one-paragraph description
- Quick Start section with copy-paste one-liners (Linux bash + Windows PowerShell)
- What DoML does (the ML analysis pipeline: BU → EDA → Modelling → Deployment)
- Mermaid diagram: new project flow (major decisions + phase steps)
- List of available commands with one-line descriptions
- Requirements (Docker, Claude Code or GitHub Copilot)
- Donation section (PayPal + Venmo) with authentic AI token cost note
- MIT license badge + link to LICENSE

### LICENSE
- MIT license text
- Copyright (c) 2026 William W Palace, III

### Copilot Support
- `.github/copilot-instructions.md` — Copilot equivalent of `CLAUDE.md`
- `.github/prompts/doml-new-project.prompt.md` — prompt file for `/doml-new-project` equivalent
- `.github/prompts/` files for each major DoML command
- Install script extended: `--target claude` (default) or `--target copilot` or `--target both`
- `AGENTS.md` at repo root — universal instructions read by both Claude Code and Copilot

---

## Differentiators

### Mermaid Diagram Content
The process flow diagram should show:
- Start → does `data/` have files? (yes/no branch)
  - No → `doml-get-data` (Kaggle or URL)
- Business Understanding phase
- Data Understanding / EDA phase
- Problem type decision: Regression / Classification / Clustering / Forecasting / Dimensionality Reduction
  - Forecasting branch: time_factor=true required
  - Unsupervised branch: no preprocessing step
- Modelling phase (with optional anomaly detection branch after EDA)
- Deployment decision: CLI / Web Service / ONNX-WASM
- doml-iterate loops back to modelling or deployment

### Donation Note Tone
Many OSS authors are honest about AI-assisted development costs. The note should be:
- Genuine, not apologetic
- Brief (2-3 sentences)
- Acknowledge that the framework was developed using Claude (Anthropic) with meaningful token investment
- Clear that donations are optional and appreciated, not expected
- Avoid "cheesy" framing — matter-of-fact works best

---

## Anti-features (out of scope for v1.5)
- Windows/macOS binary distributions of DoML itself — it's a framework, not a compiled tool
- npm/pip package distribution — install script is the distribution mechanism
- GitHub Actions CI/CD setup — out of scope
- Docker Hub image — out of scope
- Copilot extension manifest (VSIX package) — prompt files only, no extension packaging
- GEMINI.md — Gemini CLI support deferred
