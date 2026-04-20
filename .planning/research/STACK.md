# Stack Research — v1.5 Public Release + Install Scripts

**Domain:** Install scripts, public OSS release, GitHub Copilot support
**Researched:** 2026-04-20
**Confidence:** HIGH

---

## Install Script Stack (No New Dependencies)

Install scripts are pure shell — no pip, npm, or node required on the target machine. All framework files are downloaded as raw files from GitHub.

### Bash (Linux/macOS)
- `curl` is the preferred download tool (`-fsSL` flags: fail-silent, follow-redirects, silent progress)
- `wget` as fallback where curl is unavailable
- Canonical one-liner: `bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)`
- Alternative: `curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh | bash`

### PowerShell (Windows)
- `Invoke-RestMethod` (`irm`) — preferred; simpler than `Invoke-WebRequest` for pipe-to-exec
- Works on PowerShell 5.1 (Windows built-in) and PowerShell 7+
- Canonical one-liner: `Set-ExecutionPolicy Bypass -Scope Process -Force; irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex`
- Execution policy bypass is scoped to the current process only (safe pattern, industry standard)

### GitHub Raw URL Pattern
```
https://raw.githubusercontent.com/wpalace/doML/main/<path>
```
All framework file downloads use this URL base. The install script downloads itself then pulls remaining artifacts.

---

## Copilot Instruction File Formats (as of April 2026)

| File | Scope | Read by | Notes |
|------|-------|---------|-------|
| `AGENTS.md` (repo root) | Whole repo | Copilot, Claude Code, Cursor, Gemini | Universal — widest cross-tool support |
| `.github/copilot-instructions.md` | Whole repo | GitHub Copilot only | Always-on background instructions |
| `.github/instructions/*.instructions.md` | Path-scoped | GitHub Copilot | YAML frontmatter specifies applicableFiles |
| `.github/prompts/*.prompt.md` | On-demand | Copilot in VS Code/JetBrains | Reusable prompt files (like DoML skills) |
| `CLAUDE.md` | Whole repo | Claude Code | DoML already creates this |
| `GEMINI.md` | Whole repo | Gemini CLI | Future scope |

**Key insight:** `AGENTS.md` is now the universal cross-tool instruction file. Both Copilot and Claude Code read it. DoML should generate both `CLAUDE.md` (existing) and `AGENTS.md` (new) with equivalent content, plus `.github/copilot-instructions.md` for Copilot-specific context.

---

## Copilot Skill Equivalent

Claude Code has `.claude/skills/*.md` — on-demand slash commands. The closest Copilot equivalent:
- **`.github/prompts/*.prompt.md`** — reusable prompts invocable in VS Code/JetBrains Copilot Chat
- Prompt files use YAML frontmatter: `mode: agent`, `description:`, `tools:` list
- Invoked via `#` in Copilot Chat (e.g., `#doml-new-project`)

No equivalent to Claude Code's `/skill-name` CLI syntax exists in Copilot — the prompt file approach is the closest parallel.

---

## What NOT to Add
- Node.js / Python in install scripts — pure shell only
- Separate `doml-tools` for Copilot — reuse existing framework files
- GitHub Actions CI for Copilot — out of scope for v1.5
