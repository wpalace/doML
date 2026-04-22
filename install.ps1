#Requires -Version 5.1
# install.ps1 — DoML framework installer
#
# Usage:
#   irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
#   .\install.ps1 -Version v1.5
#   .\install.ps1 -Target copilot
#
# Version pin via environment variable (for pipe-to-iex mode, where params cannot be passed):
#   $env:DOML_VERSION = "v1.5"; irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
#
# Target via environment variable (for pipe-to-iex mode):
#   $env:DOML_TARGET = "copilot"; irm https://raw.githubusercontent.com/wpalace/doML/main/install.ps1 | iex
#
# -Target flag:
#   claude  (default) — installs .claude\ tree, CLAUDE.md, data\ dirs
#   copilot           — installs .github\skills\, .github\copilot-instructions.md, AGENTS.md, data\ dirs
#
# Installs the DoML framework into the current working directory.
# Run from an empty project directory before opening your AI coding assistant.
# Requires Windows 10 1803+ (ships bsdtar for .tar.gz extraction).

[CmdletBinding()]
param(
    [string]$Version = "",
    [string]$Target  = ""
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

# ── TARGET resolution ─────────────────────────────────────────────────────────
# Allow env var override for pipe-to-iex usage (params cannot be passed in that mode)

if ([string]::IsNullOrEmpty($Target) -and -not [string]::IsNullOrEmpty($env:DOML_TARGET)) {
    $Target = $env:DOML_TARGET
}
if ([string]::IsNullOrEmpty($Target)) {
    $Target = "claude"   # D-02: default target
}

if ($Target -ne "claude" -and $Target -ne "copilot") {
    Write-Error "ERROR: -Target must be 'claude' or 'copilot'. Got: '$Target'"
    exit 1
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

    # ── Install (target-specific) ─────────────────────────────────────────────

    if ($Target -eq "copilot") {

        # Skills → .github\skills\ (D-03: direct copy, no transformation)
        Write-Host "Installing DoML skills (Copilot)..."
        $githubDir = ".github"
        if (-not (Test-Path $githubDir)) {
            New-Item -ItemType Directory -Path $githubDir | Out-Null
        }
        $skillsSrcDir = Join-Path $SrcDir ".claude" "skills"
        foreach ($skillSrcDir in (Get-ChildItem -Path $skillsSrcDir -Directory -Filter "doml-*")) {
            $destDir = Join-Path ".github" "skills" $skillSrcDir.Name
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -Path (Join-Path $skillSrcDir.FullName "SKILL.md") `
                      -Destination (Join-Path $destDir "SKILL.md") -Force
        }
        Write-Host "  Skills installed to .github\skills\."

        # CLAUDE.md → .github\copilot-instructions.md (D-04)
        Write-Host "Installing Copilot instructions..."
        Copy-Item -Path (Join-Path $SrcDir "CLAUDE.md") `
                  -Destination (Join-Path ".github" "copilot-instructions.md") -Force
        Write-Host "  .github\copilot-instructions.md installed."

        # AGENTS.md (D-05, D-08)
        Write-Host "Installing AGENTS.md..."
        $agentsSrc = Join-Path $SrcDir "AGENTS.md"
        if (-not (Test-Path $agentsSrc)) {
            Write-Error "ERROR: AGENTS.md not found in archive. This is a packaging error."
            Write-Error "       Expected: $agentsSrc"
            exit 1
        }
        Copy-Item -Path $agentsSrc -Destination "AGENTS.md" -Force
        Write-Host "  AGENTS.md installed."

        # Data dirs (never delete contents)
        Write-Host "Creating data directories..."
        foreach ($dir in @("data\raw", "data\processed", "data\external")) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir | Out-Null
            }
        }
        Write-Host "  data\raw\, data\processed\, data\external\ ready."

        Write-Host ""
        Write-Host "DoML framework installed successfully (copilot target)."
        if (-not [string]::IsNullOrEmpty($Version)) {
            Write-Host "Version: $Version"
        } else {
            Write-Host "Version: main (latest)"
        }
        Write-Host ""
        Write-Host "Next step: open this directory in GitHub Copilot and use /doml-new-project"

    } else {

        # claude target (default)

        # Skills → .claude\skills\ (always overwrite)
        Write-Host "Installing DoML skills (Claude)..."
        $skillsSrcDir = Join-Path $SrcDir ".claude" "skills"
        foreach ($skillSrcDir in (Get-ChildItem -Path $skillsSrcDir -Directory -Filter "doml-*")) {
            $destDir = Join-Path ".claude" "skills" $skillSrcDir.Name
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir | Out-Null
            }
            Copy-Item -Path (Join-Path $skillSrcDir.FullName "SKILL.md") `
                      -Destination (Join-Path $destDir "SKILL.md") -Force
        }
        Write-Host "  Skills installed."

        # Workflows (always overwrite)
        Write-Host "Installing DoML workflows..."
        $destWorkflows = Join-Path ".claude" "doml" "workflows"
        if (-not (Test-Path $destWorkflows)) {
            New-Item -ItemType Directory -Path $destWorkflows -Force | Out-Null
        }
        Copy-Item -Path (Join-Path $SrcDir ".claude" "doml" "workflows" "*.md") `
                  -Destination $destWorkflows -Force
        Write-Host "  Workflows installed."

        # Templates (always overwrite, recursive)
        Write-Host "Installing DoML templates..."
        $destTemplates = Join-Path ".claude" "doml" "templates"
        if (-not (Test-Path $destTemplates)) {
            New-Item -ItemType Directory -Path $destTemplates -Force | Out-Null
        }
        Get-ChildItem -Path (Join-Path $SrcDir ".claude" "doml" "templates") |
            Copy-Item -Destination $destTemplates -Recurse -Force
        Write-Host "  Templates installed."

        # CLAUDE.md (D-06: always overwrite — no skip)
        Copy-Item -Path (Join-Path $SrcDir "CLAUDE.md") -Destination "CLAUDE.md" -Force
        Write-Host "  CLAUDE.md installed."

        # Data dirs (never delete contents)
        Write-Host "Creating data directories..."
        foreach ($dir in @("data\raw", "data\processed", "data\external")) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir | Out-Null
            }
        }
        Write-Host "  data\raw\, data\processed\, data\external\ ready."

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

    }

} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
