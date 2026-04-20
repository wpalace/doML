# Research Summary — v1.5 Public Release + Install Scripts

**Project:** DoML — Do Machine Learning
**Milestone:** v1.5 Public Release + Install Scripts
**Researched:** 2026-04-20

---

## Stack Additions

No new Python/Node packages. Install scripts are pure shell.

| Tool | Purpose |
|------|---------|
| `curl` / `Invoke-RestMethod` | Download framework files from raw.githubusercontent.com |
| Bash (POSIX) | Linux/macOS install script |
| PowerShell 5.1+ | Windows install script |

New files added to the repo (not to user projects):
- `install.sh` — Bash install script
- `install.ps1` — PowerShell install script
- `README.md` — Public documentation
- `LICENSE` — MIT
- `AGENTS.md` — Universal cross-tool instructions (repo root)
- `.github/copilot-instructions.md` — Copilot-specific always-on instructions
- `.github/prompts/*.prompt.md` — Copilot equivalents of DoML skills

---

## Key Feature Decisions

**Install script approach:** Manifest-driven individual file downloads from `raw.githubusercontent.com`. No git clone, no zip extraction, no auth required. Versioned via `VERSION` variable (defaults to `main`).

**Target flag:** `--target claude|copilot|both` (default: `both`). Allows users to install only what they need.

**Idempotency:** Framework files always overwrite (users shouldn't edit them). `data/raw/README.md` skipped if present. `CLAUDE.md` skipped if present on re-runs (user may have customized it).

**AGENTS.md strategy:** Source of truth for shared conventions. `CLAUDE.md` extends with Claude-specific content. `.github/copilot-instructions.md` extends with Copilot-specific context. Keep AGENTS.md under ~2000 tokens.

**Copilot skills:** `.github/prompts/*.prompt.md` files with `mode: agent` frontmatter — invoked via `#doml-new-project` in Copilot Chat. Higher-level than Claude Code SKILL.md files — intent + output, not internal steps.

**Mermaid diagram:** GitHub-native `\`\`\`mermaid` fenced blocks. Show full new-project decision flow: data check → get-data branch → BU → EDA → problem type fork → modelling → anomaly detection branch → deployment decision.

**Donation section:** Honest 2–3 sentence note. Acknowledge Claude/Anthropic token investment. Matter-of-fact, not apologetic. PayPal + Venmo links.

---

## Watch Out For

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Partial install on network failure | HIGH | Fail fast on any curl error; print failed URL |
| Copilot prompt files missing frontmatter | HIGH | Every `.prompt.md` must have `mode: agent` + `description` |
| AGENTS.md / CLAUDE.md / copilot-instructions.md content drift | MEDIUM | AGENTS.md is source of truth; others extend it |
| PowerShell execution policy blocks one-liner | MEDIUM | Include `Set-ExecutionPolicy Bypass -Scope Process` in one-liner |
| Mermaid not rendering on GitHub | MEDIUM | Use fenced `\`\`\`mermaid` blocks only |
| Install script overwrites user `data/raw/README.md` | MEDIUM | Check file existence before writing |
| AGENTS.md too long for effective context | MEDIUM | Keep under ~2000 tokens — pointer not manual |

---

## Recommended Build Order (Phases 19–22)

| Phase | Scope |
|-------|-------|
| 19 | README.md + LICENSE + donation section + Mermaid diagram |
| 20 | `install.sh` + `install.ps1` (Claude target only — core install) |
| 21 | `AGENTS.md` + `.github/copilot-instructions.md` + `.github/prompts/*.prompt.md` |
| 22 | Extend install scripts with `--target` flag; end-to-end verification for both targets |
