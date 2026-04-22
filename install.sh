#!/usr/bin/env bash
# install.sh — DoML framework installer
#
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)
#   VERSION=v1.5 bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)
#   bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh) --target copilot
#
# --target flag:
#   claude  (default) — installs .claude/ tree, CLAUDE.md, data/ dirs
#   copilot           — installs .github/skills/, .github/copilot-instructions.md, AGENTS.md, data/ dirs
#
# Installs the DoML framework into the current working directory.
# Run from an empty project directory before opening your AI coding assistant.

set -euo pipefail

# ── Argument parsing ──────────────────────────────────────────────────────────

TARGET="claude"   # D-02: default target

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

# ── URL and archive root ──────────────────────────────────────────────────────

VERSION="${VERSION:-}"

if [[ -n "$VERSION" ]]; then
    ARCHIVE_URL="https://github.com/wpalace/doML/archive/refs/tags/${VERSION}.tar.gz"
    ARCHIVE_ROOT="doML-${VERSION}"
else
    ARCHIVE_URL="https://github.com/wpalace/doML/archive/refs/heads/main.tar.gz"
    ARCHIVE_ROOT="doML-main"
fi

# ── Temp dir with guaranteed cleanup ─────────────────────────────────────────

TMPDIR="$(mktemp -d)"

cleanup() {
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

# ── Download ──────────────────────────────────────────────────────────────────

echo "Downloading DoML framework..."
if ! curl -fsSL --output "$TMPDIR/doml.tar.gz" "$ARCHIVE_URL"; then
    echo "ERROR: Failed to download DoML archive." >&2
    echo "       URL: $ARCHIVE_URL" >&2
    echo "       Check your internet connection and that the VERSION tag exists on GitHub." >&2
    exit 1
fi
echo "Download complete."

# ── Extract ───────────────────────────────────────────────────────────────────

echo "Extracting archive..."
tar -xzf "$TMPDIR/doml.tar.gz" -C "$TMPDIR"
SRC="$TMPDIR/$ARCHIVE_ROOT"

if [[ ! -d "$SRC" ]]; then
    echo "ERROR: Expected archive root '$ARCHIVE_ROOT' not found after extraction." >&2
    echo "       Archive contents: $(ls "$TMPDIR")" >&2
    exit 1
fi

# ── Install (target-specific) ─────────────────────────────────────────────────

if [[ "$TARGET" == "copilot" ]]; then

    # Skills → .github/skills/ (D-03: direct copy, no transformation)
    echo "Installing DoML skills (Copilot)..."
    mkdir -p ".github"
    for skill_src_dir in "$SRC/.claude/skills"/doml-*/; do
        skill_name="$(basename "$skill_src_dir")"
        dest_dir=".github/skills/${skill_name}"
        mkdir -p "$dest_dir"
        cp "${skill_src_dir}SKILL.md" "${dest_dir}/SKILL.md"
    done
    echo "  Skills installed to .github/skills/."

    # CLAUDE.md → .github/copilot-instructions.md (D-04)
    echo "Installing Copilot instructions..."
    cp "$SRC/CLAUDE.md" ".github/copilot-instructions.md"
    echo "  .github/copilot-instructions.md installed."

    # AGENTS.md (D-05, D-08)
    echo "Installing AGENTS.md..."
    if [[ ! -f "$SRC/AGENTS.md" ]]; then
        echo "ERROR: AGENTS.md not found in archive. This is a packaging error." >&2
        echo "       Expected: ${SRC}/AGENTS.md" >&2
        exit 1
    fi
    cp "$SRC/AGENTS.md" "AGENTS.md"
    echo "  AGENTS.md installed."

    # Data dirs (never delete contents)
    echo "Creating data directories..."
    mkdir -p "data/raw" "data/processed" "data/external"
    echo "  data/raw/, data/processed/, data/external/ ready."

    echo ""
    echo "DoML framework installed successfully (copilot target)."
    if [[ -n "$VERSION" ]]; then
        echo "Version: ${VERSION}"
    else
        echo "Version: main (latest)"
    fi
    echo ""
    echo "Next step: open this directory in GitHub Copilot and use /doml-new-project"

else

    # claude target (default)

    # Skills → .claude/skills/ (always overwrite)
    echo "Installing DoML skills (Claude)..."
    for skill_src_dir in "$SRC/.claude/skills"/doml-*/; do
        skill_name="$(basename "$skill_src_dir")"
        dest_dir=".claude/skills/${skill_name}"
        mkdir -p "$dest_dir"
        cp "${skill_src_dir}SKILL.md" "${dest_dir}/SKILL.md"
    done
    echo "  Skills installed."

    # Workflows (always overwrite)
    echo "Installing DoML workflows..."
    mkdir -p ".claude/doml/workflows"
    cp "$SRC/.claude/doml/workflows/"*.md ".claude/doml/workflows/"
    echo "  Workflows installed."

    # Templates (always overwrite, recursive)
    echo "Installing DoML templates..."
    mkdir -p ".claude/doml/templates"
    cp -r "$SRC/.claude/doml/templates/." ".claude/doml/templates/"
    echo "  Templates installed."

    # CLAUDE.md (D-06: always overwrite — no skip)
    cp "$SRC/CLAUDE.md" "CLAUDE.md"
    echo "  CLAUDE.md installed."

    # Data dirs (never delete contents)
    echo "Creating data directories..."
    mkdir -p "data/raw" "data/processed" "data/external"
    echo "  data/raw/, data/processed/, data/external/ ready."

    echo ""
    echo "DoML framework installed successfully."
    if [[ -n "$VERSION" ]]; then
        echo "Version: ${VERSION}"
    else
        echo "Version: main (latest)"
    fi
    echo ""
    echo "Next step: open this directory in Claude Code and run:"
    echo "  /doml-new-project"

fi
