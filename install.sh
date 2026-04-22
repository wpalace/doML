#!/usr/bin/env bash
# install.sh — DoML framework installer
#
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)
#   VERSION=v1.5 bash <(curl -fsSL https://raw.githubusercontent.com/wpalace/doML/main/install.sh)
#
# Installs the DoML framework into the current working directory.
# Run from an empty project directory before opening Claude Code.

set -euo pipefail

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

# ── Install skills (always overwrite) ────────────────────────────────────────

echo "Installing DoML skills..."
for skill_src_dir in "$SRC/.claude/skills"/doml-*/; do
    skill_name="$(basename "$skill_src_dir")"
    dest_dir=".claude/skills/${skill_name}"
    mkdir -p "$dest_dir"
    cp "${skill_src_dir}SKILL.md" "${dest_dir}/SKILL.md"
done
echo "  Skills installed."

# ── Install workflows (always overwrite) ─────────────────────────────────────

echo "Installing DoML workflows..."
mkdir -p ".claude/doml/workflows"
cp "$SRC/.claude/doml/workflows/"*.md ".claude/doml/workflows/"
echo "  Workflows installed."

# ── Install templates (always overwrite, recursive) ──────────────────────────

echo "Installing DoML templates..."
mkdir -p ".claude/doml/templates"
cp -r "$SRC/.claude/doml/templates/." ".claude/doml/templates/"
echo "  Templates installed."

# ── Install CLAUDE.md (skip if already present) ───────────────────────────────

if [[ -f "CLAUDE.md" ]]; then
    echo "  CLAUDE.md already exists — skipping (will not overwrite)."
else
    cp "$SRC/CLAUDE.md" "CLAUDE.md"
    echo "  CLAUDE.md installed."
fi

# ── Create data directories (never delete existing contents) ─────────────────

echo "Creating data directories..."
mkdir -p "data/raw" "data/processed" "data/external"
echo "  data/raw/, data/processed/, data/external/ ready."

# ── Done ──────────────────────────────────────────────────────────────────────

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
