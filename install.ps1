#Requires -Version 5.1
# install.ps1 — DoML framework installer
#
# Usage:
#   irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
#   .\install.ps1 -Version v1.5
#
# Version pin via environment variable (for pipe-to-iex mode, where -Version cannot be passed):
#   $env:DOML_VERSION = "v1.5"; irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
#
# Installs the DoML framework into the current working directory.
# Run from an empty project directory before opening Claude Code.
# Requires Windows 10 1803+ (ships bsdtar for .tar.gz extraction).

[CmdletBinding()]
param(
    [string]$Version = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── VERSION resolution ────────────────────────────────────────────────────────
# Allow env var override for pipe-to-iex usage (params cannot be passed in that mode)

if ([string]::IsNullOrEmpty($Version) -and -not [string]::IsNullOrEmpty($env:DOML_VERSION)) {
    $Version = $env:DOML_VERSION
}

if ([string]::IsNullOrEmpty($Version)) {
    $ArchiveUrl  = "https://github.com/wpalace/doML/archive/refs/heads/main.tar.gz"
    $ArchiveRoot = "doML-main"
} else {
    $ArchiveUrl  = "https://github.com/wpalace/doML/archive/refs/tags/$Version.tar.gz"
    $ArchiveRoot = "doML-$Version"
}

# ── Temp dir ──────────────────────────────────────────────────────────────────

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("doml-install-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempDir | Out-Null

try {

    # ── Download ──────────────────────────────────────────────────────────────

    $ArchiveFile = Join-Path $TempDir "doml.tar.gz"
    Write-Host "Downloading DoML framework..."
    try {
        Invoke-WebRequest -Uri $ArchiveUrl -OutFile $ArchiveFile -UseBasicParsing
    } catch {
        Write-Error "ERROR: Failed to download DoML archive."
        Write-Error "       URL: $ArchiveUrl"
        Write-Error "       Check your internet connection and that the VERSION tag exists on GitHub."
        Write-Error "       Details: $($_.Exception.Message)"
        exit 1
    }
    Write-Host "Download complete."

    # ── Extract ───────────────────────────────────────────────────────────────

    Write-Host "Extracting archive..."
    & tar -xzf $ArchiveFile -C $TempDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "ERROR: tar extraction failed (exit code $LASTEXITCODE)."
        Write-Error "       Windows 10 1803+ is required for built-in bsdtar support."
        exit 1
    }

    $SrcDir = Join-Path $TempDir $ArchiveRoot
    if (-not (Test-Path $SrcDir -PathType Container)) {
        Write-Error "ERROR: Expected archive root '$ArchiveRoot' not found after extraction."
        Write-Error "       Found: $(Get-ChildItem $TempDir | Select-Object -ExpandProperty Name)"
        exit 1
    }

    # ── Install skills (always overwrite) ────────────────────────────────────

    Write-Host "Installing DoML skills..."
    $skillsDir = Join-Path $SrcDir ".claude" "skills"
    foreach ($skillSrcDir in (Get-ChildItem -Path $skillsDir -Directory -Filter "doml-*")) {
        $destDir = Join-Path ".claude" "skills" $skillSrcDir.Name
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir | Out-Null
        }
        Copy-Item -Path (Join-Path $skillSrcDir.FullName "SKILL.md") `
                  -Destination (Join-Path $destDir "SKILL.md") -Force
    }
    Write-Host "  Skills installed."

    # ── Install workflows (always overwrite) ─────────────────────────────────

    Write-Host "Installing DoML workflows..."
    $destWorkflows = Join-Path ".claude" "doml" "workflows"
    if (-not (Test-Path $destWorkflows)) {
        New-Item -ItemType Directory -Path $destWorkflows -Force | Out-Null
    }
    Copy-Item -Path (Join-Path $SrcDir ".claude" "doml" "workflows" "*.md") `
              -Destination $destWorkflows -Force
    Write-Host "  Workflows installed."

    # ── Install templates (always overwrite, recursive) ───────────────────────

    Write-Host "Installing DoML templates..."
    $destTemplates = Join-Path ".claude" "doml" "templates"
    if (-not (Test-Path $destTemplates)) {
        New-Item -ItemType Directory -Path $destTemplates -Force | Out-Null
    }
    Get-ChildItem -Path (Join-Path $SrcDir ".claude" "doml" "templates") |
        Copy-Item -Destination $destTemplates -Recurse -Force
    Write-Host "  Templates installed."

    # ── Install CLAUDE.md (skip if already present) ───────────────────────────

    if (Test-Path "CLAUDE.md") {
        Write-Host "  CLAUDE.md already exists — skipping (will not overwrite)."
    } else {
        Copy-Item -Path (Join-Path $SrcDir "CLAUDE.md") -Destination "CLAUDE.md"
        Write-Host "  CLAUDE.md installed."
    }

    # ── Create data directories (never delete existing contents) ─────────────

    Write-Host "Creating data directories..."
    foreach ($dir in @("data\raw", "data\processed", "data\external")) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
        }
    }
    Write-Host "  data\raw\, data\processed\, data\external\ ready."

    # ── Done ──────────────────────────────────────────────────────────────────

    Write-Host ""
    Write-Host "DoML framework installed successfully."
    if (-not [string]::IsNullOrEmpty($Version)) {
        Write-Host "Version: $Version"
    } else {
        Write-Host "Version: main (latest)"
    }
    Write-Host ""
    Write-Host "Next step: open this directory in Claude Code and run:"
    Write-Host "  /doml-new-project"

} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
