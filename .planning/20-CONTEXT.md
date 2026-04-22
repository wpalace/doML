# Phase 20 Context: Install Scripts — Claude Target

## Phase Summary

Implement `install.sh` (Bash) and `install.ps1` (PowerShell) that download the DoML framework
from a GitHub release archive and scaffold `.claude/`, `CLAUDE.md`, and `data/` in the user's
project directory — without requiring a git clone.

---

## Locked Decisions

### D-01: Archive-based download (not individual file curls)

Scripts download a single `.tar.gz` release archive from GitHub, extract to a temp directory,
cherry-pick only the needed paths, then delete the temp directory.

**Why:** Atomic (one failure point vs. N), no manifest file to maintain, VERSION pin falls out
naturally from the URL, and simpler script logic overall.

**Archive URLs:**
```
# Unversioned (main branch):
https://github.com/wpalace/doML/archive/refs/heads/main.tar.gz

# Version-pinned (on release):
https://github.com/wpalace/doML/archive/refs/tags/v1.5.tar.gz
```

GitHub auto-creates these archives on every tag/release — no GitHub Actions workflow needed.

---

### D-02: Single `.tar.gz` for both Bash and PowerShell

Both `install.sh` and `install.ps1` use the same `.tar.gz` archive. Windows Terminal ships
`bsdtar` (Windows 10 1803+), so tar extraction works cross-platform without a separate zip.

**Fallback:** If tar causes Windows compatibility issues in practice, switch `install.ps1` to the
GitHub-generated `.zip` at the same URL with `.zip` extension. Do not implement this fallback
preemptively.

---

### D-03: Install into CWD

Scripts install into the current working directory. No directory argument, no prompting.

**User flow:**
```bash
mkdir my-analysis && cd my-analysis
bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)
```

```powershell
mkdir my-analysis; cd my-analysis
irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
```

---

### D-04: Files installed by the script

Cherry-picked from the extracted archive into CWD:

| Source path in archive | Destination |
|---|---|
| `.claude/skills/doml-*/SKILL.md` | `.claude/skills/doml-*/SKILL.md` |
| `.claude/doml/workflows/*.md` | `.claude/doml/workflows/*.md` |
| `.claude/doml/templates/**` | `.claude/doml/templates/**` |
| `CLAUDE.md` | `CLAUDE.md` (skipped if already present — see D-06) |

Also created as empty directories (never populated by the script):
- `data/raw/`
- `data/processed/`
- `data/external/`

**NOT installed** (generated later by `/doml-new-project` from templates):
- `Dockerfile`
- `docker-compose.yml`
- `requirements.in` / `requirements.txt`

---

### D-05: VERSION pin via environment variable / parameter

```bash
# Bash
VERSION=v1.5 bash install.sh
# default: main branch
```

```powershell
# PowerShell
irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex -Version v1.5
# or: .\install.ps1 -Version v1.5
```

When `VERSION` is set, substitute `refs/heads/main` → `refs/tags/$VERSION` in the archive URL.

---

### D-06: Idempotency rules

| Path | Re-run behavior |
|---|---|
| `.claude/skills/doml-*/` | Always overwrite (update framework files) |
| `.claude/doml/workflows/` | Always overwrite |
| `.claude/doml/templates/` | Always overwrite |
| `CLAUDE.md` | Skip if file already exists — never overwrite |
| `data/raw/`, `data/processed/`, `data/external/` | Create if missing; never delete contents |

---

### D-07: Fail-fast on download failure

If the archive download fails (non-zero curl exit code or HTTP error), the script must:
1. Print a clear error message including the URL that failed
2. Exit immediately with a non-zero exit code
3. Leave no partial state (temp directory cleaned up before exit)

---

### D-08: CLAUDE.md source

Install the repo root `CLAUDE.md` as-is. It already contains all analysis conventions,
DuckDB rules, reproducibility rules, and the DoML command reference — exactly what Claude Code
needs in a user's analysis project.

---

## Out of Scope (Phase 21)

- `--target claude|copilot|both` flag
- `AGENTS.md` and `.github/copilot-instructions.md` generation
- GitHub Actions workflow for curated release artifacts
- `.zip` fallback for PowerShell (only if tar fails in practice)
