# Pitfalls Research — v1.5 Public Release + Install Scripts

**Domain:** Common mistakes when adding install scripts and multi-AI support to an existing framework
**Researched:** 2026-04-20
**Confidence:** HIGH

---

## Install Script Pitfalls

### P1: Hardcoded branch name breaks after rename
**Problem:** Scripts hardcode `main` branch. If the default branch is renamed or a tagged release URL is used, all existing one-liners break silently (download empty/404 files).
**Prevention:** Use `main` consistently and document it. Add a `VERSION` variable at the top of each script so users can pin to a specific tag: `BASE_URL="https://raw.githubusercontent.com/wpalace/doML/${VERSION:-main}"`.
**Phase:** Install script phase

### P2: Partial install on network failure leaves broken state
**Problem:** If curl fails mid-install (network drop, rate limit, 404), the user has a partially installed framework with some skills missing. They may not notice until a command fails with a cryptic error.
**Prevention:** Detect curl failures (exit code != 0), print a clear error with the failed URL, and exit with a non-zero code. Do not silently continue on individual file failures.
**Phase:** Install script phase

### P3: PowerShell execution policy blocks one-liner on fresh Windows machines
**Problem:** Default Windows execution policy (`Restricted`) prevents running downloaded scripts. The one-liner must include `Set-ExecutionPolicy Bypass -Scope Process` before `iex`.
**Prevention:** The canonical PowerShell one-liner already includes this. Document that it only affects the current session and does not change the system policy.
**Phase:** Install script phase

### P4: Script overwrites user-modified data files
**Problem:** If `data/raw/README.md` or `CLAUDE.md` has been customized by the user and the install script blindly overwrites it on re-run, user work is lost.
**Prevention:** Only overwrite framework files (`.claude/` tree). Check for existing `data/raw/README.md` before writing — skip if present. Write `CLAUDE.md` only on first install; skip if present (or prompt).
**Phase:** Install script phase

### P5: Windows path separators break Bash script on WSL
**Problem:** Users on Windows Subsystem for Linux running the bash script in a directory with Windows-style paths (`C:\Users\...`) can get path separator errors.
**Prevention:** The bash script should use `$(pwd)` for the target directory and only use forward slashes. Document that the bash script is for Linux/macOS/WSL — Windows users should use the PowerShell script.
**Phase:** Install script phase

---

## README / Documentation Pitfalls

### P6: Mermaid diagram not rendering on GitHub
**Problem:** GitHub renders Mermaid in README.md natively, but only in certain code fence formats. Using `\`\`\`mermaid` works; using HTML `<div class="mermaid">` does not render on GitHub.
**Prevention:** Always use fenced code blocks with `mermaid` language identifier. Test by viewing the README on GitHub after push.
**Phase:** README phase

### P7: Quick Start one-liners become stale after repo restructuring
**Problem:** If the install script is moved or renamed, all published one-liners break. Users who bookmarked the README are stuck.
**Prevention:** Keep install scripts at repo root (`install.sh`, `install.ps1`) and never rename them. Document this as a stable API contract.
**Phase:** README phase

---

## Copilot Integration Pitfalls

### P8: Prompt files not recognized without correct frontmatter
**Problem:** Copilot prompt files without valid YAML frontmatter (specifically `mode: agent`) are not treated as agent prompts — they appear as plain markdown files.
**Prevention:** Every `.github/prompts/*.prompt.md` file must include frontmatter with at least `mode` and `description`. Test in VS Code with GitHub Copilot extension to verify recognition.
**Phase:** Copilot support phase

### P9: `copilot-instructions.md` and `AGENTS.md` content drift
**Problem:** If `CLAUDE.md`, `AGENTS.md`, and `.github/copilot-instructions.md` all contain DoML conventions but are maintained separately, they diverge over time. A convention change updated in one file but not the others creates inconsistent AI behavior.
**Prevention:** Treat `AGENTS.md` as the source of truth for shared conventions. `CLAUDE.md` can extend it with Claude-specific content (skill syntax, permission notes). `.github/copilot-instructions.md` extends it with Copilot-specific context. The install script generates all three from templates.
**Phase:** Copilot support phase

### P10: Copilot prompt files expose internal implementation detail
**Problem:** Prompt files in `.github/prompts/` are public (visible in the repo). DoML workflow details (step numbers, internal tool calls) that are Claude Code-specific may confuse Copilot users reading the prompt files.
**Prevention:** Copilot prompt files should be written at a higher level of abstraction than Claude Code SKILL.md files — they describe the intent and expected output, not internal orchestration steps.
**Phase:** Copilot support phase

### P11: AGENTS.md too long for effective context injection
**Problem:** Copilot and Claude Code both inject `AGENTS.md` into every request. If it's too long (> ~2000 tokens), it crowds out other context and the AI may ignore later instructions.
**Prevention:** Keep `AGENTS.md` concise — project overview, key conventions, command list. Detailed workflows stay in `.claude/doml/workflows/` (Claude Code) and `.github/prompts/` (Copilot). AGENTS.md is a pointer, not a manual.
**Phase:** Copilot support phase
