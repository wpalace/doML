# Phase 21 Context: Copilot Support + `--target` Flag

## Phase Summary

Extend `install.sh` and `install.ps1` with a `--target claude|copilot` flag. When `--target copilot`
is selected, the scripts install Copilot-compatible framework files (`.github/skills/`, 
`.github/copilot-instructions.md`, `AGENTS.md`) instead of Claude Code files (`.claude/`).
No separate Copilot source files live in the repo — the same SKILL.md files are reused,
just placed in the Copilot-expected folder structure.

---

## Locked Decisions

### D-01: `--target` accepts only `claude` or `copilot` — no `both`

The flag is mutually exclusive. There is no `--target both` option. Users pick one target per
install run.

**Why:** Clean separation of concerns. A project is either a Claude Code project or a Copilot
project — mixing both in one run adds complexity with little practical benefit.

---

### D-02: Default target is `claude`

When `--target` is omitted, the script installs the Claude Code framework (same behavior as
phase 20). Copilot files are only generated when explicitly requested.

**Why:** Backward-compatible default. Existing users who run the script without a flag get
the same behavior they had before phase 21.

---

### D-03: Copilot SKILL.md files are a direct copy — no transformation

GitHub Copilot uses the **same SKILL.md format** as Claude Code (same frontmatter: `name`,
`description`, `allowed-tools`). The only difference is folder location.

| Claude Code | GitHub Copilot |
|---|---|
| `.claude/skills/doml-*/SKILL.md` | `.github/skills/doml-*/SKILL.md` |

The install script copies each `doml-*` skill directory's SKILL.md verbatim from the extracted
archive into `.github/skills/doml-*/SKILL.md`. No content transformation required.

**Reference:** Copilot project skills can live in `.github/skills/`, `.claude/skills/`, or
`.agents/skills/`. DoML uses target-specific placement so the correct tool picks them up.

---

### D-04: `.github/copilot-instructions.md` is CLAUDE.md — same file, different location

The repo's `CLAUDE.md` is installed as `.github/copilot-instructions.md` for the copilot target.
No separate Copilot-specific instructions template is maintained.

**Why:** CLAUDE.md already contains all analysis conventions, DuckDB rules, reproducibility
rules, and DoML command references in plain Markdown. Copilot reads `.github/copilot-instructions.md`
as always-on project instructions — same content works for both tools.

---

### D-05: `AGENTS.md` is a static template in the repo

A pre-authored `AGENTS.md` template lives in the DoML repo root and is installed at the user's
project root when `--target copilot` is selected. It contains tool-neutral cross-agent
instructions (readable by Copilot, Cursor, Gemini, etc.).

**Why:** Static template is easy to maintain, review, and version. No runtime generation from
CLAUDE.md — avoids fragility if CLAUDE.md format changes.

---

### D-06: Always overwrite everything on re-run

All installed files are always overwritten on re-run, for both targets. This overrides the
phase 20 D-06 rule that skipped CLAUDE.md if already present.

**Why:** The primary re-run use case is upgrading to a later release. Users expect the new
version's files to replace the old ones. Skipping files silently keeps stale versions.

| Path (claude target) | Re-run behavior |
|---|---|
| `.claude/skills/doml-*/` | Always overwrite |
| `.claude/doml/workflows/` | Always overwrite |
| `.claude/doml/templates/` | Always overwrite |
| `CLAUDE.md` | Always overwrite |
| `data/raw/`, `data/processed/`, `data/external/` | Create if missing; never delete contents |

| Path (copilot target) | Re-run behavior |
|---|---|
| `.github/skills/doml-*/` | Always overwrite |
| `.github/copilot-instructions.md` | Always overwrite |
| `AGENTS.md` | Always overwrite |
| `data/raw/`, `data/processed/`, `data/external/` | Create if missing; never delete contents |

---

### D-07: Files installed per target

**`--target claude`** (default — same as phase 20 plus overwrite-always):
- `.claude/skills/doml-*/SKILL.md` — all doml skill directories from archive
- `.claude/doml/workflows/*.md`
- `.claude/doml/templates/**`
- `CLAUDE.md`
- `data/raw/`, `data/processed/`, `data/external/` (create if missing)

**`--target copilot`**:
- `.github/skills/doml-*/SKILL.md` — same SKILL.md files, Copilot location
- `.github/copilot-instructions.md` — installed from repo's `CLAUDE.md`
- `AGENTS.md` — installed from repo's `AGENTS.md` static template
- `data/raw/`, `data/processed/`, `data/external/` (create if missing)
- `.claude/` directory is NOT created

---

### D-08: `AGENTS.md` source path in archive

The static `AGENTS.md` template lives at the repo root (same level as `CLAUDE.md`, `install.sh`).
The install script copies it from `$SRC/AGENTS.md` → `./AGENTS.md`.

---

### D-09: PowerShell parameter name

Bash: `--target claude` or `--target copilot`  
PowerShell: `-Target claude` or `-Target copilot`

Follows the same naming convention as the existing `-Version` parameter in `install.ps1`.

---

## What This Phase Does NOT Include

- `.github/prompts/*.prompt.md` files — the skills folder approach (`D-03`) replaces the
  older prompt-file approach; `.prompt.md` files are not generated
- `--target both` option — explicitly excluded (D-01)
- Copilot-specific content transformations — same SKILL.md content for both tools (D-03)
- `.agents/skills/` installation — out of scope; Copilot uses `.github/skills/`
- `GEMINI.md` or `--target gemini` — deferred to a future milestone
