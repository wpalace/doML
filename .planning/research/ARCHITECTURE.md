# Architecture Research — v1.5 Public Release + Install Scripts

**Domain:** Install script architecture, Copilot file layout integration
**Researched:** 2026-04-20
**Confidence:** HIGH

---

## Existing Framework File Layout (what install scripts must reproduce)

```
.claude/
  skills/
    doml-new-project/SKILL.md
    doml-business-understanding/SKILL.md
    doml-data-understanding/SKILL.md
    doml-modelling/SKILL.md
    doml-iterate/SKILL.md
    doml-forecasting/SKILL.md
    doml-anomaly-detection/SKILL.md
    doml-get-data/SKILL.md
    doml-deploy-model/SKILL.md
    doml-deploy-cli/SKILL.md
    doml-deploy-web/SKILL.md
    doml-deploy-wasm/SKILL.md
    doml-iterate-deployment/SKILL.md
    doml-progress/SKILL.md
  doml/
    workflows/           # orchestration .md files
    templates/
      notebooks/         # .ipynb templates
  get-shit-done/         # GSD framework (required by some workflows)
CLAUDE.md                # project-level Claude instructions
data/
  raw/
    README.md
  processed/
  external/
```

---

## New Files Added by v1.5

```
install.sh               # Bash install script
install.ps1              # PowerShell install script
README.md                # Public repo documentation
LICENSE                  # MIT license
AGENTS.md                # Universal cross-tool instructions (new)
.github/
  copilot-instructions.md     # Copilot-specific always-on instructions
  prompts/
    doml-new-project.prompt.md
    doml-business-understanding.prompt.md
    doml-data-understanding.prompt.md
    doml-modelling.prompt.md
    doml-iterate.prompt.md
    doml-forecasting.prompt.md
    doml-anomaly-detection.prompt.md
    doml-get-data.prompt.md
    doml-deploy-model.prompt.md
    doml-iterate-deployment.prompt.md
    doml-progress.prompt.md
```

---

## Install Script Architecture

### Approach: Manifest-driven download
The install script maintains a list of files to download. Each file is fetched individually from `raw.githubusercontent.com`. This avoids requiring git, zip extraction tools, or GitHub API auth.

```bash
BASE_URL="https://raw.githubusercontent.com/wpalace/doML/main"

FILES=(
  ".claude/skills/doml-new-project/SKILL.md"
  ".claude/skills/doml-business-understanding/SKILL.md"
  # ... all framework files
  "CLAUDE.md"
)

for f in "${FILES[@]}"; do
  mkdir -p "$(dirname "$f")"
  curl -fsSL "$BASE_URL/$f" -o "$f"
  echo "  ✓ $f"
done
```

### Target Flag
```bash
install.sh [--target claude|copilot|both]   # default: both
install.ps1 [-Target claude|copilot|both]   # default: both
```

- `claude` — installs `.claude/` tree + `CLAUDE.md` + `AGENTS.md`
- `copilot` — installs `.github/copilot-instructions.md` + `.github/prompts/` + `AGENTS.md`
- `both` (default) — installs everything

### Idempotency Rules
- Create directories: always safe
- Download framework files: always overwrite (user shouldn't edit framework files)
- `data/raw/`, `data/processed/`, `data/external/`: create if absent, never delete contents
- `data/raw/README.md`: write only if not present (user may have customized)

---

## Copilot Prompt File Format

```markdown
---
mode: agent
description: "Run the DoML Business Understanding phase..."
tools:
  - read_file
  - create_file
  - run_terminal_command
---

[prompt content — equivalent to SKILL.md content adapted for Copilot]
```

Prompt files are invoked in Copilot Chat with `#filename` (without `.prompt.md` extension).

---

## AGENTS.md vs CLAUDE.md Content Strategy

- `CLAUDE.md` — exists, contains DoML-specific Claude Code instructions (REPR rules, paths, conventions)
- `AGENTS.md` — new; contains the same core DoML conventions in a more neutral voice (no Claude-specific references); both AI tools read it

Both files should agree on:
- Reproducibility rules (seeds, relative paths, read-only raw data)
- Directory structure conventions
- DuckDB-first for tabular data
- Tidy data before feature engineering

---

## Build Order Recommendation

| Phase | Deliverable |
|-------|-------------|
| 19 | README.md + LICENSE + donation section + Mermaid diagram |
| 20 | install.sh + install.ps1 (Claude target) — core install scripts |
| 21 | AGENTS.md + .github/copilot-instructions.md + .github/prompts/ (Copilot target) |
| 22 | Extend install scripts with --target flag; verify end-to-end for both targets |
