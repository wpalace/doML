# Phase 21: Copilot Support + `--target` Flag — Research

**Researched:** 2026-04-22
**Domain:** Bash/PowerShell scripting, GitHub Copilot agent skills, AGENTS.md format
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01: `--target` accepts only `claude` or `copilot` — no `both`**
The flag is mutually exclusive. There is no `--target both` option. Users pick one target per install run.

**D-02: Default target is `claude`**
When `--target` is omitted, the script installs the Claude Code framework (same behavior as phase 20). Copilot files are only generated when explicitly requested.

**D-03: Copilot SKILL.md files are a direct copy — no transformation**
GitHub Copilot uses the same SKILL.md format as Claude Code (same frontmatter: `name`, `description`, `allowed-tools`). The install script copies each `doml-*` skill directory's SKILL.md verbatim from the extracted archive into `.github/skills/doml-*/SKILL.md`. No content transformation required.

**D-04: `.github/copilot-instructions.md` is CLAUDE.md — same file, different location**
The repo's `CLAUDE.md` is installed as `.github/copilot-instructions.md` for the copilot target. No separate Copilot-specific instructions template is maintained.

**D-05: `AGENTS.md` is a static template in the repo**
A pre-authored `AGENTS.md` template lives in the DoML repo root. Installed at user's project root when `--target copilot` is selected. Static, no runtime generation.

**D-06: Always overwrite everything on re-run (both targets)**
All installed files are always overwritten. This changes the Phase 20 behavior of skipping CLAUDE.md if already present — Phase 21 overwrites it.

**D-07: Files installed per target**

| Path (claude target) | Behavior |
|---|---|
| `.claude/skills/doml-*/SKILL.md` | Always overwrite |
| `.claude/doml/workflows/*.md` | Always overwrite |
| `.claude/doml/templates/**` | Always overwrite |
| `CLAUDE.md` | Always overwrite |
| `data/raw/`, `data/processed/`, `data/external/` | Create if missing; never delete contents |

| Path (copilot target) | Behavior |
|---|---|
| `.github/skills/doml-*/SKILL.md` | Always overwrite |
| `.github/copilot-instructions.md` | Always overwrite |
| `AGENTS.md` | Always overwrite |
| `data/raw/`, `data/processed/`, `data/external/` | Create if missing; never delete contents |
| `.claude/` directory | NOT created |

**D-08: `AGENTS.md` source path in archive**
Static `AGENTS.md` template lives at the repo root. Installed: `$SRC/AGENTS.md` → `./AGENTS.md`.

**D-09: PowerShell parameter name**
Bash: `--target claude` or `--target copilot`
PowerShell: `-Target claude` or `-Target copilot`

### Claude's Discretion

None noted in CONTEXT.md — all key decisions are locked.

### Deferred Ideas (OUT OF SCOPE)

- `.github/prompts/*.prompt.md` files — the skills folder approach (D-03) replaces the older prompt-file approach; `.prompt.md` files are not generated
- `--target both` option — explicitly excluded (D-01)
- Copilot-specific content transformations — same SKILL.md content for both tools (D-03)
- `.agents/skills/` installation — Copilot uses `.github/skills/`
- `GEMINI.md` or `--target gemini` — deferred to future milestone
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INST-07 | Install scripts accept `--target claude\|copilot` (default: `claude`) | Bash `getopts`/argument parsing patterns; PowerShell `[string]$Target` param |
| INST-08 | With `--target copilot`, script installs Copilot files (SKILL.md copy, copilot-instructions.md, AGENTS.md) | D-03/D-04/D-05 verify this is a pure copy operation — no transformation needed |
| COP-01 | `AGENTS.md` generated at user project root — universal cross-agent instructions | AGENTS.md is standard Markdown, no required fields; static template is the approach |
| COP-02 | `.github/copilot-instructions.md` generated — always-on Copilot project instructions | File is just a copy of `CLAUDE.md`; 2-page limit applies (CLAUDE.md is ~5KB, borderline) |
| COP-03 | `.github/prompts/doml-*.prompt.md` files generated (per REQUIREMENTS.md) | **SUPERSEDED by D-03/CONTEXT.md**: `.prompt.md` files are OUT OF SCOPE; SKILL.md in `.github/skills/` is the Copilot integration |
| COP-04 | Copilot prompt files invocable via `#doml-new-project` in VS Code Copilot Chat | **SUPERSEDED by D-03**: SKILL.md files in `.github/skills/doml-*/` are invocable via `/doml-new-project` slash commands in VS Code Copilot Chat |

**Note:** COP-03 and COP-04 in REQUIREMENTS.md describe `.prompt.md` generation. CONTEXT.md D-03 explicitly supersedes this approach with the SKILL.md copy strategy. The locked decisions govern. Skills in `.github/skills/` satisfy the intent of COP-04 (invocability via `#doml-*` / `/doml-*` in Copilot Chat).
</phase_requirements>

---

## Summary

Phase 21 extends the Phase 20 install scripts (`install.sh` and `install.ps1`) with a `--target claude|copilot` flag. The implementation is a straightforward scripting task with three work areas: (1) argument parsing for the new flag, (2) a new copilot install branch that copies SKILL.md files to `.github/skills/`, copies `CLAUDE.md` as `.github/copilot-instructions.md`, and copies the static `AGENTS.md` template, and (3) changing the CLAUDE.md overwrite behavior from "skip if present" to "always overwrite" for both targets.

The research confirms that the SKILL.md format is identical between Claude Code and GitHub Copilot — both read from `.github/skills/`, `.claude/skills/`, or `.agents/skills/`. No transformation is needed; copying is the correct implementation. GitHub Copilot in VS Code discovers skills in `.github/skills/` automatically and makes them invocable as `/skill-name` slash commands in Copilot Chat.

A new `AGENTS.md` static template must be authored and committed to the DoML repo root before this phase executes. It is installed verbatim to user project roots under `--target copilot`. The template should be tool-neutral Markdown covering DoML conventions, project structure, and command references.

**Primary recommendation:** Implement as a two-branch conditional (`if [[ "$TARGET" == "copilot" ]]`) in each script, keeping the download/extract logic shared. Author the `AGENTS.md` template in the same task as the scripting changes so it is present in the archive when the copilot branch copies it.

---

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Bash | Built-in | `install.sh` scripting | Already in use (Phase 20) |
| PowerShell | 5.1+ | `install.ps1` scripting | Already in use (Phase 20) |
| `set -euo pipefail` | — | Bash error handling | Already established in install.sh |
| `$ErrorActionPreference = "Stop"` | — | PS error handling | Already established in install.ps1 |

### No New Dependencies

This phase adds no new tools or libraries. All work is within existing shell scripts. The skills format is already established.

**Version verification:** No packages to verify — this is a pure shell scripting task.

---

## Architecture Patterns

### Recommended Project Structure Changes

```
DoML repo root
├── install.sh          # MODIFIED: add --target flag + copilot branch
├── install.ps1         # MODIFIED: add -Target param + copilot branch
├── CLAUDE.md           # EXISTING: also serves as copilot-instructions.md source
├── AGENTS.md           # NEW: static template, committed to repo root
└── .claude/
    └── skills/
        └── doml-*/
            └── SKILL.md    # EXISTING: copied to .github/skills/ for copilot target
```

When a user runs `--target copilot`, the archive already contains all needed source files. No Copilot-specific source files are maintained separately.

### Pattern 1: Bash Argument Parsing with Default

The install script currently takes no positional arguments. Add `--target` using a `while` loop (not `getopts`, which doesn't handle long options):

```bash
# Source: pattern established for long-option parsing in bash
TARGET="claude"   # D-02: default

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            TARGET="${2:-}"
            if [[ "$TARGET" != "claude" && "$TARGET" != "copilot" ]]; then
                echo "ERROR: --target must be 'claude' or 'copilot'." >&2
                exit 1
            fi
            shift 2
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            exit 1
            ;;
    esac
done
```

### Pattern 2: PowerShell Param Declaration

Follows the existing `-Version` parameter convention (D-09):

```powershell
# Source: matches existing install.ps1 param style
[CmdletBinding()]
param(
    [string]$Version = "",
    [string]$Target  = "claude"   # D-02: default
)

# Validate target
if ($Target -ne "claude" -and $Target -ne "copilot") {
    Write-Error "ERROR: -Target must be 'claude' or 'copilot'."
    exit 1
}
```

### Pattern 3: Copilot Install Branch (Bash)

```bash
if [[ "$TARGET" == "copilot" ]]; then
    # Skills → .github/skills/
    echo "Installing DoML skills (Copilot)..."
    for skill_src_dir in "$SRC/.claude/skills"/doml-*/; do
        skill_name="$(basename "$skill_src_dir")"
        dest_dir=".github/skills/${skill_name}"
        mkdir -p "$dest_dir"
        cp "${skill_src_dir}SKILL.md" "${dest_dir}/SKILL.md"
    done

    # CLAUDE.md → .github/copilot-instructions.md
    mkdir -p ".github"
    cp "$SRC/CLAUDE.md" ".github/copilot-instructions.md"

    # AGENTS.md
    cp "$SRC/AGENTS.md" "AGENTS.md"

    # Data dirs
    mkdir -p "data/raw" "data/processed" "data/external"

    echo "DoML framework installed successfully (copilot target)."
    echo "Next step: open this directory in GitHub Copilot and use /doml-new-project"
else
    # claude target — existing logic, but CLAUDE.md now always overwritten
    ...
fi
```

### Pattern 4: CLAUDE.md Overwrite Change (D-06)

The Phase 20 conditional skip becomes an unconditional copy:

```bash
# Before (Phase 20):
if [[ -f "CLAUDE.md" ]]; then
    echo "  CLAUDE.md already exists — skipping."
else
    cp "$SRC/CLAUDE.md" "CLAUDE.md"
fi

# After (Phase 21, D-06):
cp "$SRC/CLAUDE.md" "CLAUDE.md"
echo "  CLAUDE.md installed."
```

### Pattern 5: AGENTS.md Static Template Content

AGENTS.md uses plain Markdown. No required frontmatter. No required sections. The file should be tool-neutral (no Claude-specific syntax). Recommended content for DoML:

```markdown
# AGENTS.md — DoML Analysis Project

Cross-agent instructions for AI coding assistants working in this DoML project.

## Project Overview
[DoML conventions, what this project is, data scientist workflow]

## Project Structure
[data/raw, data/processed, models, notebooks, reports]

## Reproducibility Rules
[SEED=42, relative paths, read-only raw data]

## Available Commands
[list of /doml-* commands with one-line descriptions]

## What NOT To Do
[same prohibitions as CLAUDE.md but tool-neutral language]
```

### Anti-Patterns to Avoid

- **Separate copilot source files:** Do not maintain a parallel set of Copilot-specific SKILL.md content. D-03 mandates verbatim copy.
- **Using `getopts` for `--target`:** `getopts` in bash only handles single-character flags. Use the `while`/`case` pattern for long options.
- **PowerShell env-var env-only approach for -Target:** Unlike `-Version` (which needed env-var fallback for pipe-to-iex), `-Target claude` can be passed directly since `install.ps1 -Target copilot` is the intended usage. However, for consistency, consider supporting `$env:DOML_TARGET` as a fallback (same pattern as `$env:DOML_VERSION`).
- **Not creating `.github/` directory:** `mkdir -p ".github"` is required before writing `copilot-instructions.md`.
- **Skipping the AGENTS.md commit:** If `AGENTS.md` is not committed to the repo root before the release tag, the `$SRC/AGENTS.md` copy will fail. The template must exist in the archive.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SKILL.md format for Copilot | Custom Copilot instruction format | Existing SKILL.md files verbatim | Same format works for both tools — agentskills.io specification [VERIFIED] |
| Copilot project instructions | Tool-neutral instructions template | CLAUDE.md copied as-is | Copilot reads copilot-instructions.md as plain Markdown; existing CLAUDE.md content is already correct format [VERIFIED] |
| Cross-agent instructions | Dynamic generation | Static AGENTS.md template | AGENTS.md is plain Markdown with no required schema; static is simpler and correct [VERIFIED] |

---

## GitHub Copilot Skills: Verified Specification

### Supported Directory Locations

[VERIFIED: docs.github.com/en/copilot/concepts/agents/about-agent-skills]

| Scope | Directories Checked |
|-------|---------------------|
| Project skills | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |
| Personal skills | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |

For DoML's copilot target: install to `.github/skills/doml-*/SKILL.md` (D-03).

### SKILL.md Frontmatter Fields

[VERIFIED: agentskills.io/specification]

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, hyphens only. Must match parent directory name. |
| `description` | Yes | Max 1024 chars. Describes what skill does and when to use it. |
| `license` | No | License name or reference |
| `compatibility` | No | Max 500 chars. Environment requirements. |
| `metadata` | No | Arbitrary key-value map |
| `allowed-tools` | No | Space-separated string. Experimental. |

**Critical:** `name` field must match the parent directory name. DoML skills already follow this — directory `doml-new-project` has `name: doml-new-project`. This constraint is already satisfied.

### SKILL.md Invocation in VS Code Copilot Chat

[VERIFIED: code.visualstudio.com/docs/copilot/customization/agent-skills]

Skills are invoked via `/skill-name` in Copilot Chat. Example: `/doml-new-project`. This satisfies COP-04's invocability requirement. Skills in `.github/skills/` are auto-discovered by VS Code.

### copilot-instructions.md Constraints

[VERIFIED: docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot]

- Location: `.github/copilot-instructions.md`
- Format: Plain Markdown, natural language
- Length guidance: "Instructions must be no longer than 2 pages" (approximately 500-1000 words)
- The existing `CLAUDE.md` is ~5KB (~130 lines). It is borderline on the 2-page guidance but within reason for a detailed project instructions file.
- Content is "always on" — included in every Copilot Chat request in that repo

### AGENTS.md Format

[VERIFIED: agents.md/]

- Plain Markdown. No required frontmatter. No required sections.
- Supported by: GitHub Copilot, Cursor, Windsurf, Gemini CLI, OpenAI Codex, JetBrains Junie, and 20+ platforms
- Location: repo root (or any directory — nearest file to current file wins)
- No size constraints documented; keep it concise for broad agent compatibility

---

## Common Pitfalls

### Pitfall 1: `--target` Validation Omitted

**What goes wrong:** User passes `--target both` or `--target foo`; script silently defaults or fails confusingly.
**Why it happens:** Bash scripts don't enforce enum values automatically.
**How to avoid:** Explicit validation after argument parsing — fail fast with a clear error message listing valid values.
**Warning signs:** Test by running `bash install.sh --target both` — should exit 1 with error message.

### Pitfall 2: `.github/` Directory Not Created

**What goes wrong:** `cp "$SRC/CLAUDE.md" ".github/copilot-instructions.md"` fails with "No such file or directory" if `.github/` doesn't exist in the user's project.
**Why it happens:** New projects have no `.github/` directory.
**How to avoid:** `mkdir -p ".github/skills"` before any copy into `.github/`.

### Pitfall 3: AGENTS.md Missing from Archive

**What goes wrong:** Copilot branch fails at `cp "$SRC/AGENTS.md" "AGENTS.md"` because `AGENTS.md` was not committed to the repo before tagging the release.
**Why it happens:** The script copies from the downloaded archive; files not in git are not in the archive.
**How to avoid:** Commit `AGENTS.md` to the repo root in Wave 1 before any release testing. Verify with `test -f "$SRC/AGENTS.md"` before the copy, and fail fast with a clear error if missing.

### Pitfall 4: CLAUDE.md Overwrite Regression (D-06)

**What goes wrong:** Claude target still skips CLAUDE.md if present (Phase 20 behavior), but D-06 requires always overwriting.
**Why it happens:** The conditional `if [[ -f "CLAUDE.md" ]]` block must be removed for both targets.
**How to avoid:** Remove the conditional entirely for the claude branch. Verify with a test that touches CLAUDE.md before running the script, then confirms it was overwritten.

### Pitfall 5: PowerShell `-Target` Env Var Fallback

**What goes wrong:** Users running `$env:DOML_TARGET = "copilot"; irm ... | iex` expect env var to work the same as the `-Version` env var fallback.
**Why it happens:** PowerShell's pipe-to-iex mode cannot pass named parameters.
**How to avoid:** Add `$env:DOML_TARGET` fallback in the same pattern as `$env:DOML_VERSION` in `install.ps1`. Document this in the usage comment block at the top of the script.

### Pitfall 6: SKILL.md `name` Field Must Match Directory Name

**What goes wrong:** Copilot may reject or not discover skills where `name:` in frontmatter does not match the parent directory name.
**Why it happens:** agentskills.io spec requires this match. [VERIFIED]
**How to avoid:** DoML's existing skills already satisfy this (verified by inspecting `doml-new-project/SKILL.md` — `name: doml-new-project`). No transformation needed; the copy preserves this correct relationship.

---

## Code Examples

### Bash: Full `--target` Parsing Block

```bash
# Source: long-option parsing pattern for bash
TARGET="claude"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            if [[ -z "${2:-}" ]]; then
                echo "ERROR: --target requires a value ('claude' or 'copilot')." >&2
                exit 1
            fi
            TARGET="$2"
            if [[ "$TARGET" != "claude" && "$TARGET" != "copilot" ]]; then
                echo "ERROR: --target must be 'claude' or 'copilot'. Got: '$TARGET'" >&2
                exit 1
            fi
            shift 2
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            exit 1
            ;;
    esac
done
```

### PowerShell: `-Target` Parameter with Env Fallback

```powershell
[CmdletBinding()]
param(
    [string]$Version = "",
    [string]$Target  = ""
)

# Allow env var override for pipe-to-iex usage
if ([string]::IsNullOrEmpty($Target) -and -not [string]::IsNullOrEmpty($env:DOML_TARGET)) {
    $Target = $env:DOML_TARGET
}
if ([string]::IsNullOrEmpty($Target)) {
    $Target = "claude"   # D-02 default
}

if ($Target -ne "claude" -and $Target -ne "copilot") {
    Write-Error "ERROR: -Target must be 'claude' or 'copilot'. Got: '$Target'"
    exit 1
}
```

### Bash: Copilot Install Section

```bash
if [[ "$TARGET" == "copilot" ]]; then
    echo "Installing DoML skills (Copilot target)..."
    for skill_src_dir in "$SRC/.claude/skills"/doml-*/; do
        skill_name="$(basename "$skill_src_dir")"
        dest_dir=".github/skills/${skill_name}"
        mkdir -p "$dest_dir"
        cp "${skill_src_dir}SKILL.md" "${dest_dir}/SKILL.md"
    done
    echo "  Skills installed."

    echo "Installing Copilot instructions..."
    mkdir -p ".github"
    cp "$SRC/CLAUDE.md" ".github/copilot-instructions.md"
    echo "  .github/copilot-instructions.md installed."

    echo "Installing AGENTS.md..."
    if [[ ! -f "$SRC/AGENTS.md" ]]; then
        echo "ERROR: AGENTS.md not found in archive. This is a packaging error." >&2
        exit 1
    fi
    cp "$SRC/AGENTS.md" "AGENTS.md"
    echo "  AGENTS.md installed."

    echo "Creating data directories..."
    mkdir -p "data/raw" "data/processed" "data/external"
    echo "  data/raw/, data/processed/, data/external/ ready."

else
    # claude target
    echo "Installing DoML skills (Claude target)..."
    for skill_src_dir in "$SRC/.claude/skills"/doml-*/; do
        skill_name="$(basename "$skill_src_dir")"
        dest_dir=".claude/skills/${skill_name}"
        mkdir -p "$dest_dir"
        cp "${skill_src_dir}SKILL.md" "${dest_dir}/SKILL.md"
    done
    echo "  Skills installed."

    echo "Installing DoML workflows..."
    mkdir -p ".claude/doml/workflows"
    cp "$SRC/.claude/doml/workflows/"*.md ".claude/doml/workflows/"
    echo "  Workflows installed."

    echo "Installing DoML templates..."
    mkdir -p ".claude/doml/templates"
    cp -r "$SRC/.claude/doml/templates/." ".claude/doml/templates/"
    echo "  Templates installed."

    # D-06: always overwrite CLAUDE.md (no skip)
    cp "$SRC/CLAUDE.md" "CLAUDE.md"
    echo "  CLAUDE.md installed."

    echo "Creating data directories..."
    mkdir -p "data/raw" "data/processed" "data/external"
    echo "  data/raw/, data/processed/, data/external/ ready."
fi
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.github/prompts/*.prompt.md` for Copilot | `.github/skills/*/SKILL.md` (Agent Skills standard) | 2025 (agentskills.io open standard) | SKILL.md is cross-tool; prompt files are Copilot-only |
| Separate Copilot instructions files | CLAUDE.md copied as copilot-instructions.md | N/A (D-04 decision) | One file to maintain |

**Deprecated/outdated:**
- `.github/prompts/*.prompt.md` with `mode: agent` frontmatter: The original COP-03 requirement described this older Copilot approach. The CONTEXT.md D-03 decision replaces it with the SKILL.md approach, which is the current (2026) Agent Skills open standard.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | CLAUDE.md at ~130 lines is within Copilot's "2-page" guidance for copilot-instructions.md | copilot-instructions.md Constraints | Copilot may truncate or ignore the file if too long; low risk as guidance is informal |
| A2 | The `doml-*` skill directories in the archive are under `.claude/skills/` (not a different path) | Copilot Install Branch | Copy would fail or produce empty `.github/skills/`; easily tested |

---

## Environment Availability

Step 2.6: SKIPPED — this phase is pure shell scripting with no external dependencies beyond `curl`, `tar`, and `cp` which are already required by Phase 20's install scripts.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual shell testing (no automated test suite for install scripts) |
| Config file | None — shell scripts are tested by running them |
| Quick run command | `bash install.sh --target copilot` in a temp directory |
| Full suite command | Test matrix: both targets × both scripts × re-run scenario |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INST-07 | `--target claude` default works | smoke | `bash install.sh` in temp dir → `.claude/` present | ❌ Wave 0 |
| INST-07 | `--target copilot` installs copilot files | smoke | `bash install.sh --target copilot` → `.github/skills/` present | ❌ Wave 0 |
| INST-07 | Invalid `--target foo` exits 1 with error | smoke | `bash install.sh --target foo; echo $?` → 1 | ❌ Wave 0 |
| INST-07 | `-Target copilot` works in PowerShell | smoke | `.\install.ps1 -Target copilot` in temp dir | ❌ Wave 0 |
| INST-08 | Copilot target produces correct files | smoke | Check `.github/skills/doml-*/SKILL.md`, `.github/copilot-instructions.md`, `AGENTS.md` exist | ❌ Wave 0 |
| COP-01 | `AGENTS.md` at project root | smoke | `test -f AGENTS.md` after copilot install | ❌ Wave 0 |
| COP-02 | `.github/copilot-instructions.md` matches CLAUDE.md content | smoke | `diff .github/copilot-instructions.md expected_claude.md` | ❌ Wave 0 |
| D-06 | CLAUDE.md overwritten on re-run (claude target) | smoke | Pre-place CLAUDE.md with marker → run script → confirm marker gone | ❌ Wave 0 |

**Note:** These tests are shell commands run manually or in a CI script. No test framework installation needed.

### Sampling Rate

- **Per task commit:** Run the relevant install script in a temp directory, check expected files
- **Per wave merge:** Run full matrix (both targets, both scripts, re-run scenario)
- **Phase gate:** All test scenarios pass before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] Create a `test-install.sh` smoke test script (optional — manual testing is sufficient for this scope)
- [ ] Ensure `AGENTS.md` exists at repo root before any install testing

---

## Security Domain

This phase modifies shell installer scripts. ASVS categories assessed:

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | Yes | Validate `--target` / `-Target` value against allowlist before use |
| V2–V4 Authentication/Session/Access | No | Installer runs locally, no auth |
| V6 Cryptography | No | No crypto operations |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Invalid `--target` value passed to script | Tampering | Allowlist validation + early exit (already in code examples) |
| Path traversal via skill directory names | Tampering | Loop uses `basename` — already established pattern in Phase 20 |
| Archive manipulation (MITM on download) | Tampering | Out of scope for this phase (Phase 20 pattern: curl -fsSL is HTTPS) |

---

## Sources

### Primary (HIGH confidence)
- [agentskills.io/specification](https://agentskills.io/specification) — Full SKILL.md frontmatter spec, directory structure, field constraints
- [docs.github.com/en/copilot/concepts/agents/about-agent-skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) — Supported skill directory locations for GitHub Copilot
- [code.visualstudio.com/docs/copilot/customization/agent-skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) — VS Code Copilot skill invocation via `/skill-name`, frontmatter fields including `argument-hint`, `user-invocable`
- [docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) — copilot-instructions.md format, location, length guidance
- [agents.md/](https://agents.md/) — AGENTS.md format specification, supported tools

### Secondary (MEDIUM confidence)
- [github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md) — GitHub Copilot's AGENTS.md support confirmation

### Codebase (VERIFIED)
- `/home/bill/source/DoML/install.sh` — Phase 20 bash install script (existing pattern to extend)
- `/home/bill/source/DoML/install.ps1` — Phase 20 PowerShell install script (existing pattern to extend)
- `/home/bill/source/DoML/.claude/skills/doml-new-project/SKILL.md` — Confirmed `name:` matches directory name; `allowed-tools` is a list in Claude Code format (space-separated in agentskills spec, Claude uses YAML list)
- `/home/bill/source/DoML/CLAUDE.md` — Confirmed source for copilot-instructions.md installation

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pure shell scripting using established Phase 20 patterns
- Architecture: HIGH — argument parsing patterns are well-established; copilot file structure verified against official docs
- Pitfalls: HIGH — identified from code inspection and official spec review

**Research date:** 2026-04-22
**Valid until:** 2026-07-22 (stable — GitHub Copilot skills spec is now an open standard)

---

## Appendix: DoML Skill Inventory

The following 14 `doml-*` skill directories exist in `.claude/skills/` and will be copied to `.github/skills/` under `--target copilot`:

1. `doml-anomaly-detection`
2. `doml-business-understanding`
3. `doml-data-understanding`
4. `doml-deploy-cli`
5. `doml-deploy-model`
6. `doml-deploy-wasm`
7. `doml-deploy-web`
8. `doml-forecasting`
9. `doml-get-data`
10. `doml-iterate`
11. `doml-iterate-deployment`
12. `doml-modelling`
13. `doml-new-project`
14. `doml-progress`

The loop `for skill_src_dir in "$SRC/.claude/skills"/doml-*/` handles this automatically — no hardcoded list needed.
