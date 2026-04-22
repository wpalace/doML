---
phase: 21-copilot-support-target-flag
verified: 2026-04-22T15:00:00Z
status: human_needed
score: 5/6 must-haves verified (1 requires human testing)
re_verification: false
human_verification:
  - test: "Open a project directory containing `.github/skills/doml-*/SKILL.md` (installed by `install.sh --target copilot`) in VS Code with the GitHub Copilot Chat extension active. Type `/doml-new-project` in Copilot Chat."
    expected: "Copilot resolves the skill and begins the DoML new-project interview flow."
    why_human: "Requires VS Code + GitHub Copilot Chat extension. Cannot verify SKILL.md invocability from the command line."
---

# Phase 21: Copilot Support + `--target` Flag Verification Report

**Phase Goal:** Extend `install.sh` and `install.ps1` with a `--target claude|copilot` flag (default: `claude`). When `--target copilot` is selected, scripts copy SKILL.md files to `.github/skills/`, install `CLAUDE.md` as `.github/copilot-instructions.md`, and install the static `AGENTS.md` template at the project root — no separate Copilot source files live in the repo.

**Verified:** 2026-04-22T15:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `bash install.sh --target copilot` installs `.github/skills/doml-*/SKILL.md`, `.github/copilot-instructions.md`, `AGENTS.md`, and `data/` dirs — no `.claude/` directory created | VERIFIED | Copilot branch in install.sh confirmed: skills loop writes to `.github/skills/${skill_name}`, CLAUDE.md copied to `.github/copilot-instructions.md`, AGENTS.md guarded and copied; copilot branch contains zero `.claude/` destination references |
| 2 | `AGENTS.md` is installed at the user's project root with tool-neutral DoML conventions | VERIFIED | `/home/bill/source/DoML/AGENTS.md` exists (5173 bytes); contains all required sections (Project Structure, Reproducibility Rules, DoML Commands table with 16 `doml-` references, DuckDB First, What NOT To Do); no `@/` Claude-specific syntax; no frontmatter |
| 3 | `.github/copilot-instructions.md` is installed as a copy of `CLAUDE.md` | VERIFIED | `install.sh` line 104: `cp "$SRC/CLAUDE.md" ".github/copilot-instructions.md"`; `install.ps1` lines 124-125: equivalent `Copy-Item` call |
| 4 | `.github/skills/doml-*/SKILL.md` files are invocable via `/doml-*` in VS Code GitHub Copilot Chat | HUMAN NEEDED | SKILL.md files are installed to the correct Copilot discovery path (`.github/skills/`); actual invocability requires VS Code + Copilot Chat extension |
| 5 | `bash install.sh` (no flag) installs the Claude framework identically to Phase 20, with CLAUDE.md always overwritten | VERIFIED | Default `TARGET="claude"` set at line 20; claude branch installs `.claude/skills/`, workflows, templates; `cp "$SRC/CLAUDE.md" "CLAUDE.md"` at line 159 with no skip-if-present conditional; `CLAUDE.md already exists` string absent from script |
| 6 | `--target foo` exits 1 with `--target must be 'claude' or 'copilot'` | VERIFIED | Lines 30-33: `if [[ "$TARGET" != "claude" && "$TARGET" != "copilot" ]]; then echo "ERROR: --target must be 'claude' or 'copilot'. Got: '$TARGET'" >&2; exit 1; fi` |

**Score:** 5/6 truths verified (1 human-only)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `AGENTS.md` | Static cross-agent instruction template installed to user project root | VERIFIED | Exists at repo root; 5173 bytes; contains `# AGENTS.md`, `doml-new-project`, `PROJECT_ROOT`, `data/raw/`, `DuckDB`; no Claude-specific syntax |
| `install.sh` | Bash installer with `--target claude\|copilot` flag | VERIFIED | Contains `TARGET="claude"`, `--target` case, copilot branch with `.github/skills`, `copilot-instructions.md`, `AGENTS.md` copy; bash syntax valid |
| `install.ps1` | PowerShell installer with `-Target` parameter | VERIFIED | Contains `[string]$Target = ""`, `$env:DOML_TARGET` fallback, copilot branch, `finally` cleanup block; all acceptance criteria met |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `install.sh` copilot branch | `$SRC/AGENTS.md` | `cp "$SRC/AGENTS.md" "AGENTS.md"` | WIRED | Line 114; guarded by `test -f "$SRC/AGENTS.md"` at line 109 |
| `install.sh` copilot branch | `$SRC/.claude/skills/doml-*/` | for loop copying to `.github/skills/` | WIRED | Lines 94-99; loop iterates `"$SRC/.claude/skills"/doml-*/` and writes to `.github/skills/${skill_name}` |
| `install.sh` claude branch | `$SRC/CLAUDE.md` | unconditional `cp` (D-06) | WIRED | Line 159: `cp "$SRC/CLAUDE.md" "CLAUDE.md"` — no skip conditional |
| `install.ps1` copilot branch | `$SrcDir/AGENTS.md` | `Copy-Item $agentsSrc "AGENTS.md"` | WIRED | Lines 130-136; guarded by `Test-Path $agentsSrc` |
| `install.ps1` copilot branch | `$SrcDir/.claude/skills/doml-*/` | foreach loop copying to `.github/skills/` | WIRED | Lines 112-119 |
| `install.ps1` claude branch | `$SrcDir/CLAUDE.md` | unconditional `Copy-Item -Force` (D-06) | WIRED | Line 196: `Copy-Item -Path (Join-Path $SrcDir "CLAUDE.md") -Destination "CLAUDE.md" -Force` |

---

### Data-Flow Trace (Level 4)

Not applicable — phase produces shell scripts and a static Markdown template, not components that render dynamic data.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| install.sh default target is claude | `grep -q 'TARGET="claude"' install.sh` | Match found | PASS |
| install.sh invalid target exits 1 path | `grep -q '--target must be' install.sh` | Match found | PASS |
| install.sh bash syntax valid | `bash -n install.sh` | Exit 0 | PASS |
| install.ps1 env var fallback present | `grep -q 'DOML_TARGET' install.ps1` | Match found | PASS |
| install.ps1 D-06 skip removed | `grep -q 'CLAUDE.md already exists' install.ps1` | No match | PASS |
| AGENTS.md size adequate | `wc -c AGENTS.md` = 5173 bytes | > 2000 | PASS |
| AGENTS.md doml command count | `grep -c "doml-" AGENTS.md` = 16 | >= 14 | PASS |
| Commits documented in summaries exist | `git log --oneline 592fcfb cc2c8f6 85230f7` | All three found | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence / Notes |
|-------------|------------|-------------|--------|-----------------|
| COP-01 | 21-01-PLAN.md | `AGENTS.md` generated in user's project root with cross-tool instructions | SATISFIED | `AGENTS.md` exists at repo root and is installed by `--target copilot` branch |
| COP-02 | 21-02-PLAN.md | `.github/copilot-instructions.md` derived from `CLAUDE.md` content | SATISFIED | Copilot branch: `cp "$SRC/CLAUDE.md" ".github/copilot-instructions.md"` |
| COP-03 | 21-02-PLAN.md | `.github/prompts/doml-*.prompt.md` files generated with `mode: agent` frontmatter | DIVERGED — see note | Phase locked D-03: SKILL.md approach replaces `.prompt.md` approach. No `.prompt.md` files are generated. ROADMAP SC-4 confirms this: "`.github/skills/doml-*/SKILL.md` files are invocable via `/doml-*`" — ROADMAP was updated to reflect the design decision. REQUIREMENTS.md text is stale. |
| COP-04 | 21-02-PLAN.md | Copilot prompt files invocable via `#doml-new-project` in Copilot Chat | NEEDS HUMAN | SKILL.md files installed to `.github/skills/` path; VS Code invocability cannot be verified programmatically |
| INST-07 | 21-02-PLAN.md | Install scripts accept `--target claude\|copilot\|both` (default: `both`) | DIVERGED — see note | Phase locked D-01 (no `both`) and D-02 (default `claude`). REQUIREMENTS.md says `--target both` and default `both`; implemented as `--target claude\|copilot` with default `claude`. ROADMAP goal and success criteria reflect the locked decisions and do not mention `both`. |
| INST-08 | 21-02-PLAN.md | With `--target copilot`, script generates Copilot equivalents including `.github/prompts/*.prompt.md` | DIVERGED — see note | Same as COP-03. `.prompt.md` generation was explicitly excluded per D-03 in CONTEXT.md. AGENTS.md, copilot-instructions.md, and SKILL.md files cover the intent. |

**Note on requirement divergences:** CONTEXT.md locked decisions D-01, D-02, and D-03 during the research phase with explicit rationale before any implementation began. The ROADMAP goal and success criteria were updated to reflect these decisions. The REQUIREMENTS.md text for INST-07, INST-08, and COP-03 is stale — it describes the original requirements spec, not the locked implementation design. The ROADMAP is the authoritative contract for this verification, and all ROADMAP success criteria are met (subject to human verification of SC-4).

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | — | — | — |

install.sh and install.ps1 contain no TODO/FIXME markers, no placeholder returns, no empty handlers. AGENTS.md contains no Claude-specific `@/` syntax and no frontmatter. All three files are substantive implementations.

---

### Human Verification Required

#### 1. Copilot SKILL.md Invocability in VS Code

**Test:** In a project directory, run `install.sh --target copilot` (or simulate by placing SKILL.md files in `.github/skills/doml-new-project/`). Open VS Code with the GitHub Copilot Chat extension. Type `/doml-new-project` in the Copilot Chat panel.

**Expected:** Copilot Chat resolves the skill and initiates the DoML new-project interview, displaying the skill's description and beginning the guided workflow.

**Why human:** Requires an active VS Code installation with GitHub Copilot Chat extension. The `.github/skills/` discovery path and `/skillname` invocation syntax cannot be exercised from the command line.

---

### Gaps Summary

No gaps blocking the phase goal. The phase fully implements the `--target claude|copilot` flag in both install scripts and the static `AGENTS.md` template as described in the ROADMAP goal and all 6 ROADMAP success criteria.

The REQUIREMENTS.md text for INST-07, INST-08, and COP-03 describes an earlier design that was superseded by locked decisions (D-01, D-02, D-03) recorded in 21-CONTEXT.md before implementation. The ROADMAP goal and success criteria — which are the contract for this verification — reflect the final design. No rework is needed.

One item requires human testing before the phase can be marked fully passed: confirming that `.github/skills/doml-*/SKILL.md` files are invocable via `/doml-*` in VS Code GitHub Copilot Chat.

---

_Verified: 2026-04-22T15:00:00Z_
_Verifier: Claude (gsd-verifier)_
