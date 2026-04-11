# Phase 9: doml-get-data — Research

**Researched:** 2026-04-10
**Domain:** Data acquisition skill — Kaggle API, URL downloads, Docker exec, Git LFS, provenance logging
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Kaggle authentication — env vars in docker-compose.yml**
Kaggle credentials passed as `KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables in `docker-compose.yml`. User sets them in `.env` or directly in `docker-compose.yml`. Workflow detects missing/empty vars inside the container and prints setup instructions, then stops. No interactive credential entry. No `~/.kaggle/kaggle.json` file management.

**Kaggle CLI location — inside Docker image**
`kaggle` CLI installed in the Docker image (add `kaggle` to `requirements.in`). All download operations run inside the container — no local Python dependency on the host.

**Container execution — docker compose exec (running container, docker cp out)**
Use already-running `jupyter` container via `docker compose exec`. Since `data/raw/` is mounted `:ro` inside the container, downloads go to a temp directory inside the container, then `docker cp` transfers them to the host's `data/raw/` directory (writable on host). The `:ro` mount constraint is never relaxed.

Exact staging pattern:
```bash
# 1. Download + extract inside running container to temp staging dir
docker compose exec jupyter bash -c "
  mkdir -p /tmp/doml-stage && \
  kaggle datasets download -d owner/slug -p /tmp/doml-stage --unzip
"
# 2. Copy extracted files from container to host data/raw/
docker cp "$(docker compose ps -q jupyter)":/tmp/doml-stage/. ./data/raw/
# 3. Clean up staging dir inside container
docker compose exec jupyter bash -c "rm -rf /tmp/doml-stage"
```

Workflow must check that Docker is running (`docker compose ps`) before proceeding, and fail with a clear message if the container is not up.

**Staging area — data/raw/.stage/ (dotfolder, gitignored)**
All downloads land in `data/raw/.stage/` first. Dotfolder → automatically ignored by `.gitignore`. ZIPs extracted in-place within `.stage/`. Extracted files (CSV, Parquet, Excel) moved to `data/raw/`. `.stage/` cleaned after each successful run. If extraction fails, `.stage/` contents left for debugging.

**Download scope — all files**
Kaggle: download all files in the dataset. URL: download the file at the URL. If it is a ZIP, extract all contents. Supported formats: `*.csv`, `*.tsv`, `*.parquet`, `*.xlsx`, `*.xls`.

**Git LFS — auto-setup on first download**
1. Check if LFS initialized: `git lfs version 2>/dev/null`
2. If not initialized: `git lfs install`
3. Ensure `.gitattributes` tracks: `*.csv`, `*.parquet`, `*.xlsx`, `*.zip` under `data/raw/`
4. If `.gitattributes` modified, print reminder to commit it
5. If `git lfs version` fails (LFS not installed on host), print warning with install instructions but do NOT stop — download proceeds without LFS setup

**new-project integration — inline choice, then resume**
`new-project.md` Step 3 modified so that when `data/raw/` is empty, instead of exiting with an error, it presents an inline AskUserQuestion:
- "Get data now" → runs doml-get-data acquisition flow inline → re-scans → continues interview
- "Add files manually" → prints instructions → second AskUserQuestion: "I've added my files — continue" → re-scans → if still empty, loops back to the choice

**README.md log — full provenance block, always append**
Each download appends a provenance block to `data/raw/README.md` with: heading with readable timestamp, source (kaggle: owner/slug or url: https://...), ISO-8601 UTC timestamp, file count, and per-file table with name, human-readable size, SHA-256 hash. Re-downloads always append — full history preserved.

### Claude's Discretion

None specified.

### Deferred Ideas (OUT OF SCOPE)
- Kaggle competition downloads (`kaggle competitions download`) — dataset downloads only
- Multiple simultaneous downloads / batch mode
- Authentication methods other than env vars (OAuth, service accounts)
- Progress bars or streaming download output
- Automatic dataset versioning / update checking
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CMD-14 | `doml-get-data` dedicated skill — fetches datasets from Kaggle or direct URLs into `data/raw/`; runnable standalone or invoked automatically by `doml-new-project` when `data/raw/` is empty | SKILL.md + workflow file pattern confirmed from Phase 8 skills; Kaggle CLI verified at 1.6.17 |
| DATA-01 | Accepts Kaggle dataset slug (`owner/dataset-name`) and downloads files to `data/raw/` using Kaggle API | `kaggle datasets download -d owner/slug -p /path --unzip` confirmed via CLI help [VERIFIED: local kaggle 1.6.17] |
| DATA-02 | Accepts a direct URL (CSV, Parquet, Excel) and downloads to `data/raw/` | `curl -L -o outfile url` pattern; ZIP detection and unzip via bash; confirmed tools available [VERIFIED: curl 8.7.1, sha256sum 9.4] |
| DATA-03 | Invoked automatically by `doml-new-project` when `data/raw/` is empty — prompts user for source before continuing interview | new-project.md Step 3 currently exits with error on empty scan; modification identified; inline AskUserQuestion flow specified in CONTEXT.md |
| DATA-04 | Logs each download to `data/raw/README.md` with source URL/slug and download timestamp | data/raw/README.md exists and has existing content; append pattern required |
</phase_requirements>

---

## Summary

Phase 9 implements a new DoML skill — `doml-get-data` — that downloads datasets from Kaggle or direct URLs into `data/raw/`, and integrates with `doml-new-project` as a fallback when `data/raw/` is empty. The implementation follows established DoML patterns: a SKILL.md entry point that delegates to a workflow markdown file.

The core technical challenge is the read-only mount constraint: `data/raw/` is mounted `:ro` inside the container (INFR-05), so downloads cannot land there directly. The user has decided the workaround: download to `/tmp/doml-stage` inside the container, then use `docker cp` to transfer files to the host `data/raw/` directory. All Kaggle operations run inside the container using the `kaggle` CLI (to be added to `requirements.in`). URL downloads use `curl` on the host to avoid container exec complexity for simple HTTP fetches, but SHA-256 computation for provenance can be done on the host too.

Four files must be created or modified. The new files are `.claude/skills/doml-get-data/SKILL.md` and `.claude/doml/workflows/get-data.md`. The modified files are `new-project.md` (Step 3 empty-data behavior), `docker-compose.yml` template (add Kaggle env vars), `requirements.in` (add `kaggle`), and `.gitignore` (add `data/raw/.stage/`). Git LFS is not installed on this host, so the workflow must gracefully degrade — warn but proceed.

**Primary recommendation:** Follow the exact staging architecture from CONTEXT.md. The only discretion area is URL download implementation — use `curl -L` on the host (available at 8.7.1) rather than routing URL downloads through the container, since no Kaggle auth is needed and it simplifies the workflow.

---

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|---|---|---|---|
| kaggle CLI | 1.6.17 [VERIFIED: local install] | Kaggle dataset download inside container | Official Kaggle API client; only supported method |
| curl | 8.7.1 [VERIFIED: host] | URL file downloads | Available in container and on host; standard HTTP download tool |
| docker compose exec | (docker compose v2) [VERIFIED: host] | Run commands in running container | Container-first architecture established in Phase 3 |
| docker cp | (docker compose v2) [VERIFIED: host] | Transfer files from container to host | Only way to write to `data/raw/` given `:ro` mount |
| sha256sum | 9.4 [VERIFIED: host] | Compute file hashes for provenance log | Standard GNU coreutils; present in container base image |
| git lfs | NOT INSTALLED [VERIFIED: host] | Track large data files in git | Graceful degrade required — warn, don't stop |

### Supporting

| Tool | Version | Purpose | When to Use |
|---|---|---|---|
| unzip / --unzip flag | built-in | Extract ZIP archives | When Kaggle dataset or URL download is a ZIP |
| du -sh | built-in | Human-readable file sizes for provenance log | After each download inside container |
| date -u | built-in | UTC timestamps | Provenance block generation |

### Installation

Add to `requirements.in` (will be pip-installed in Docker image):
```bash
kaggle
```

Then rebuild: `docker compose build`

Note: `requirements.txt` is pip-compile output — executor must note this needs regeneration or document the rebuild step.

---

## Architecture Patterns

### Recommended File Structure

```
.claude/
└── skills/
    └── doml-get-data/
        └── SKILL.md          # skill entry point (new)
.claude/doml/
└── workflows/
    └── get-data.md           # full acquisition workflow (new)
data/raw/
└── .stage/                   # gitignored staging dir (created at runtime)
```

### Pattern 1: SKILL.md Entry Point (consistent with all Phase 8 skills)

Every DoML command follows the same SKILL.md → workflow delegation pattern. `doml-get-data` must match:

```yaml
---
name: doml-get-data
description: "Download datasets from Kaggle or direct URLs into data/raw/"
argument-hint: "kaggle owner/dataset-name | url https://..."
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Acquire a dataset into data/raw/ from Kaggle or a direct URL.
</objective>

<execution_context>
@.claude/doml/workflows/get-data.md
</execution_context>

<context>
Arguments: $ARGUMENTS
</context>
```

[VERIFIED: compared against doml-business-understanding/SKILL.md, doml-modelling/SKILL.md, doml-data-understanding/SKILL.md — all follow this structure]

### Pattern 2: Workflow Step Structure (consistent with existing workflows)

The `get-data.md` workflow follows the same numbered step format as `business-understanding.md` and `new-project.md`:

```markdown
### Step 1 — Check Docker is running
### Step 2 — Parse arguments (kaggle | url)
### Step 3 — Kaggle flow (if kaggle)
  - Check KAGGLE_USERNAME + KAGGLE_KEY env vars inside container
  - Download to /tmp/doml-stage inside container
  - docker cp to host data/raw/
  - Clean up /tmp/doml-stage
### Step 4 — URL flow (if url)
  - Validate URL extension
  - curl -L -o data/raw/.stage/filename url
  - If ZIP: unzip into .stage/, move supported files to data/raw/
  - Clean up .stage/
### Step 5 — Git LFS setup
### Step 6 — Compute provenance (SHA-256, sizes, timestamps)
### Step 7 — Append provenance block to data/raw/README.md
### Step 8 — Display summary
```

### Pattern 3: Docker Container Check (established in new-project.md Step 2)

[VERIFIED: new-project.md Step 2]

```bash
docker compose ps --services --filter status=running 2>/dev/null | grep -q jupyter
```

If not running, emit clear error — do not auto-start (unlike new-project.md which starts it). The user must have Docker running for `doml-get-data` to work.

### Pattern 4: Kaggle Credential Check Inside Container

Since credentials are env vars in docker-compose.yml, check them from within the container:

```bash
docker compose exec jupyter bash -c '
  if [ -z "$KAGGLE_USERNAME" ] || [ -z "$KAGGLE_KEY" ]; then
    echo "MISSING_KAGGLE_CREDS"
    exit 1
  fi
  echo "CREDS_OK"
'
```

On `MISSING_KAGGLE_CREDS`, display the setup instructions (4-step process from CONTEXT.md) and stop.

### Pattern 5: docker cp After Staged Download

[VERIFIED: decision in CONTEXT.md; `docker compose ps -q` confirmed command exists]

```bash
# Get container ID
CONTAINER_ID=$(docker compose ps -q jupyter)

# Copy from staged dir to host data/raw/
docker cp "${CONTAINER_ID}:/tmp/doml-stage/." ./data/raw/
```

Note: `docker cp SRC/.` copies directory contents (not the directory itself). This is the correct syntax.

### Pattern 6: URL Download on Host (Discretion Call)

URL downloads do not require Kaggle auth or special container capabilities. Using `curl` on the host is simpler and avoids container exec round-trips:

```bash
# Detect filename from URL
FILENAME=$(basename "$URL" | cut -d'?' -f1)
mkdir -p ./data/raw/.stage
curl -L -o "./data/raw/.stage/${FILENAME}" "$URL"
```

ZIP detection:
```bash
if [[ "$FILENAME" == *.zip ]]; then
  unzip -q "./data/raw/.stage/${FILENAME}" -d "./data/raw/.stage/"
  rm "./data/raw/.stage/${FILENAME}"
fi
```

Move supported formats to data/raw/:
```bash
for ext in csv tsv parquet xlsx xls; do
  find ./data/raw/.stage -maxdepth 1 -name "*.${ext}" -exec mv {} ./data/raw/ \;
done
```

### Pattern 7: Provenance Block Format

[VERIFIED: specified verbatim in CONTEXT.md]

SHA-256 and file sizes can be computed on the host after `docker cp`:

```bash
for f in ./data/raw/*.csv ./data/raw/*.parquet ./data/raw/*.xlsx; do
  [ -f "$f" ] && sha256sum "$f" | awk '{print $1}'
  [ -f "$f" ] && du -sh "$f" | awk '{print $1}'
done
```

### Anti-Patterns to Avoid

- **Writing directly to `data/raw/` inside the container:** The `:ro` mount will cause "Read-only file system" errors. Always use `/tmp/doml-stage` for in-container staging.
- **Storing Kaggle credentials in files:** No `~/.kaggle/kaggle.json` creation. Env vars only.
- **Blocking on missing git LFS:** If `git lfs version` fails, warn and continue. Never stop the download.
- **Overwriting existing README.md:** Always append provenance blocks. Never overwrite the file header.
- **Using `kaggle datasets download` without `--unzip`:** Without this flag, you get a ZIP inside a ZIP. Always pass `--unzip`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP downloads with redirects | Custom Python download loop | `curl -L` | Handles 301/302 redirects, partial downloads, TLS — curl is proven |
| ZIP extraction | Custom Python zipfile logic | `--unzip` flag (Kaggle) / `unzip` (URL ZIPs) | Built-in tools handle edge cases; in-container `--unzip` keeps it atomic |
| SHA-256 hashing | Python hashlib loop | `sha256sum` (host) or inside container | Standard coreutils, always available |
| Kaggle auth | Custom API call | `kaggle` CLI | CLI handles auth token injection, rate limits, and API versioning |
| Docker container ID | Parsing `docker compose ps` text output | `docker compose ps -q jupyter` | Machine-readable ID, no text parsing fragility |

---

## Common Pitfalls

### Pitfall 1: `docker cp` path trailing slash semantics

**What goes wrong:** `docker cp CONTAINER:/tmp/doml-stage ./data/raw/` copies the `doml-stage` directory itself, not its contents.

**Why it happens:** Docker cp follows `tar`-like semantics. Without trailing `/.`, it copies the directory.

**How to avoid:** Always use `docker cp CONTAINER:/tmp/doml-stage/. ./data/raw/` — the trailing `/.` copies contents.

**Warning signs:** A `doml-stage` subdirectory appears inside `data/raw/` after copy.

### Pitfall 2: Kaggle env vars set in `.env` but not visible in container

**What goes wrong:** User puts `KAGGLE_USERNAME=x` in `.env`, but the container was started before the file was created. The env var check inside the container returns empty.

**Why it happens:** `docker compose up -d` reads `.env` at startup, not at `exec` time. An already-running container doesn't pick up new `.env` entries without restart.

**How to avoid:** The credential-missing error message must tell the user to run `docker compose down && docker compose up -d` (not just restart). Step the user through this explicitly.

**Warning signs:** Credentials appear correct in `.env` but the check still fails.

### Pitfall 3: `kaggle datasets download --unzip` extracts nested ZIPs only one level

**What goes wrong:** Some Kaggle datasets contain ZIP-of-ZIPs. `--unzip` extracts the outer ZIP but leaves inner ZIPs intact.

**Why it happens:** The Kaggle CLI `--unzip` flag only handles the outermost archive.

**How to avoid:** After `--unzip`, scan for remaining `.zip` files in `.stage/` and recursively unzip them. Flag this in the workflow comment as a known edge case with a "check for nested ZIPs" step.

**Warning signs:** `.zip` files appear in `data/raw/` after download.

### Pitfall 4: `docker compose ps -q` returns multiple IDs if scaled

**What goes wrong:** If the user has somehow scaled the jupyter service, `-q` returns multiple lines. `docker cp` with multiple IDs fails.

**Why it happens:** `-q` returns one line per container instance.

**How to avoid:** Use `docker compose ps -q jupyter | head -1` to take the first container only.

### Pitfall 5: URL filename extraction fails for URLs with query parameters

**What goes wrong:** `basename "https://example.com/data.csv?token=abc"` yields `data.csv?token=abc` — not a valid filename.

**Why it happens:** `basename` strips path components but not query strings.

**How to avoid:** Strip query string: `FILENAME=$(basename "$URL" | cut -d'?' -f1)`. Then strip fragment: add `| cut -d'#' -f1`.

### Pitfall 6: `data/raw/.stage/` not cleaned when download fails mid-way

**What goes wrong:** On failure, `.stage/` contains partial files. A subsequent run may see stale data.

**Why it happens:** No cleanup on error path.

**How to avoid:** Use a trap-based cleanup or explicitly check for and clean `.stage/` at the START of each run (before download), not just at the end. The CONTEXT decision says: leave `.stage/` on extraction failure for debugging — but DO clean it at the start of a fresh run.

### Pitfall 7: git LFS not installed — `git lfs install` fails silently or errors confusingly

**What goes wrong:** `git lfs version` returns exit 127 (command not found). The subsequent `git lfs install` also fails. If not handled, the workflow appears to crash on LFS setup.

**Why it happens:** git-lfs is a separate package not bundled with git. [VERIFIED: `git lfs version` returns "git-lfs: not found" on this host]

**How to avoid:** Wrap the entire LFS block in: `if git lfs version &>/dev/null; then ... else echo "Warning: git-lfs not installed. Skipping LFS setup. Install with: sudo apt install git-lfs"; fi`. Never let LFS failure abort the download.

### Pitfall 8: Appending to `data/raw/README.md` when the file doesn't end with a newline

**What goes wrong:** Appended markdown section merges with the last line of the existing README, causing broken formatting.

**Why it happens:** Some editors/tools omit trailing newlines.

**How to avoid:** Before appending, check if README.md ends with a newline; if not, add one. In bash: `echo "" >> ./data/raw/README.md` before the provenance block.

---

## Code Examples

### Check Docker is running and get container ID

```bash
# Check jupyter service is running
if ! docker compose ps --services --filter status=running 2>/dev/null | grep -q jupyter; then
  echo "Error: The DoML Docker container is not running. Start it with: docker compose up -d"
  exit 1
fi

# Get container ID (first instance)
CONTAINER_ID=$(docker compose ps -q jupyter | head -1)
```

### Kaggle download inside container + docker cp to host

```bash
# 1. Ensure staging dir exists inside container
docker compose exec jupyter bash -c "rm -rf /tmp/doml-stage && mkdir -p /tmp/doml-stage"

# 2. Download and unzip inside container
docker compose exec jupyter bash -c "
  kaggle datasets download -d '${SLUG}' -p /tmp/doml-stage --unzip --quiet
"

# 3. Move extracted files to host data/raw/ via docker cp
docker cp "${CONTAINER_ID}:/tmp/doml-stage/." ./data/raw/

# 4. Clean up
docker compose exec jupyter bash -c "rm -rf /tmp/doml-stage"
```

### URL download on host

```bash
FILENAME=$(basename "$URL" | cut -d'?' -f1 | cut -d'#' -f1)
mkdir -p ./data/raw/.stage

curl -L -o "./data/raw/.stage/${FILENAME}" "$URL"

# If ZIP, extract
if [[ "$FILENAME" == *.zip ]]; then
  unzip -q "./data/raw/.stage/${FILENAME}" -d "./data/raw/.stage/"
  rm "./data/raw/.stage/${FILENAME}"
fi

# Move supported formats to data/raw/
for ext in csv tsv parquet xlsx xls; do
  find ./data/raw/.stage -maxdepth 2 -name "*.${ext}" -exec mv {} ./data/raw/ \;
done

# Cleanup .stage
rm -rf ./data/raw/.stage
```

### Compute provenance info on host

```bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
READABLE_TS=$(date -u +"%Y-%m-%d %H:%M UTC")

# Per-file info (for newly arrived files)
FILE_TABLE=""
for f in "${NEW_FILES[@]}"; do
  HASH=$(sha256sum "$f" | awk '{print $1}')
  SIZE=$(du -sh "$f" | awk '{print $1}')
  NAME=$(basename "$f")
  FILE_TABLE="${FILE_TABLE}| ${NAME} | ${SIZE} | ${HASH} |\n"
done
```

### Append provenance block to README.md

```bash
# Ensure trailing newline before appending
echo "" >> ./data/raw/README.md

cat >> ./data/raw/README.md << PROVENANCE

## Download: ${READABLE_TS}

| Field | Value |
|-------|-------|
| Source | ${SOURCE_TYPE}: ${SOURCE_VALUE} |
| Downloaded | ${TIMESTAMP} |
| Files | ${FILE_COUNT} |

| File | Size | SHA-256 |
|------|------|---------|
${FILE_TABLE}
PROVENANCE
```

### Git LFS setup (graceful degrade)

```bash
if git lfs version &>/dev/null; then
  git lfs install
  LFS_NEEDED=false
  for pattern in "data/raw/*.csv" "data/raw/*.parquet" "data/raw/*.xlsx" "data/raw/*.zip"; do
    if ! grep -q "$pattern" .gitattributes 2>/dev/null; then
      echo "${pattern} filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
      LFS_NEEDED=true
    fi
  done
  if [ "$LFS_NEEDED" = true ]; then
    echo "Reminder: Run 'git add .gitattributes && git commit -m \"chore: add LFS tracking for data files\"'"
  fi
else
  echo "Warning: git-lfs is not installed on this system. Large data files will not be LFS-tracked."
  echo "To install: sudo apt install git-lfs (Ubuntu) or brew install git-lfs (macOS)"
fi
```

### new-project.md Step 3 — empty data/raw/ modification

Replace the current `raise SystemExit(1)` for empty directory with a check that returns a sentinel value, then in the calling context present an AskUserQuestion:

```markdown
**If scan returns empty (no supported files found):**

Ask using AskUserQuestion:
"data/raw/ is empty. How would you like to get your data?
  → Get data now (Kaggle or URL)
  → Add files manually"

If "Get data now":
  Run the get-data workflow inline (Steps 2–7 of get-data.md).
  After completion, re-run the Step 3 DuckDB scan.
  If still empty: loop back to this choice.
  If files found: continue to Step 4.

If "Add files manually":
  Print:
  "Add CSV, Parquet, or XLSX files to ./data/raw/ on your host machine.
   Docker mounts the directory automatically — no restart needed.
   Note: .xls files are not supported; convert to .xlsx or .csv first."
  Ask using AskUserQuestion:
  "I've added my files — continue"
  Re-run the Step 3 DuckDB scan.
  If still empty: loop back to the top choice.
  If files found: continue to Step 4.
```

---

## Runtime State Inventory

This phase adds new files and modifies workflow text — it is not a rename/refactor. However, the `data/raw/` mount configuration and Docker environment state are relevant.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | `data/raw/README.md` exists with existing content (16 lines) | Workflow must append, never overwrite — verified append-safe |
| Live service config | `docker-compose.yml` template and project-level file both exist; neither has KAGGLE env vars yet | Add `KAGGLE_USERNAME` and `KAGGLE_KEY` environment entries to both template and project file |
| OS-registered state | None — no scheduled tasks or system services | None |
| Secrets/env vars | `KAGGLE_USERNAME`, `KAGGLE_KEY` not yet in docker-compose.yml; user sets in `.env` or directly | Code adds the env var slots; values remain user-supplied |
| Build artifacts | `requirements.in` does not currently include `kaggle`; `requirements.txt` must be regenerated after adding it | Add `kaggle` to `requirements.in`; executor documents that `docker compose build` is required |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker / docker compose | Container exec, docker cp | Check required at runtime | Running: No containers up [VERIFIED] | No fallback — user must start container |
| kaggle CLI (host) | Verification only; runtime use is inside container | Yes [VERIFIED: 1.6.17] | 1.6.17 | N/A — installed in container image |
| curl | URL downloads on host | Yes [VERIFIED] | 8.7.1 | wget (also available at 1.21.4) |
| sha256sum | Provenance hashing | Yes [VERIFIED] | 9.4 | `openssl dgst -sha256` |
| unzip | ZIP extraction for URL downloads | Check during workflow | Likely available (standard Linux) | python3 -m zipfile -e |
| git lfs | LFS tracking for large files | NOT installed [VERIFIED] | — | Graceful degrade: warn + skip |

**Missing dependencies with no fallback:**
- Docker container must be running. The workflow must check and emit a clear error message with start instructions.

**Missing dependencies with fallback:**
- git-lfs: not installed on this host. Workflow warns and continues without LFS setup.

---

## Validation Architecture

`nyquist_validation` is `true` in `.planning/config.json` [VERIFIED].

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (in `requirements.in`) |
| Config file | None detected (no pytest.ini or pyproject.toml with pytest config) |
| Quick run command | `pytest tests/ -x -q` (if tests exist) |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CMD-14 | SKILL.md created and loadable | smoke | Manual inspection (no CLI test harness) | ❌ Wave 0 |
| DATA-01 | Kaggle slug download produces files in data/raw/ | integration | Requires live Kaggle credentials + network | manual-only |
| DATA-02 | URL download produces files in data/raw/ | integration | Requires network + URL | manual-only |
| DATA-03 | new-project.md presents choice when data/raw/ empty | smoke | Manual inspection of workflow text | manual-only |
| DATA-04 | README.md receives appended provenance block | unit | Inspect file after download run | manual-only |

**Automated testing note:** This phase produces workflow markdown files (not Python code). There is no unit-testable logic. Validation is by inspection and manual smoke test. The `pytest` framework is present but not applicable to workflow markdown files. The planner should treat all test verification as **manual smoke tests** and not plan automated test creation tasks.

### Wave 0 Gaps

None — no test framework setup needed for workflow-only phase.

---

## Project Constraints (from CLAUDE.md)

| Directive | Impact on This Phase |
|-----------|---------------------|
| `data/raw/` is immutable — read-only mount in container (INFR-05) | Downloads cannot write to `data/raw/` from inside container. Must use `/tmp/doml-stage` + `docker cp` pattern |
| Never hardcode absolute paths — use PROJECT_ROOT env var (REPR-02) | Not directly applicable to workflow markdown, but provenance log must not hardcode paths |
| Never modify files in `data/raw/` | Confirmed: workflow moves files in from staging, does not modify existing files |
| Never commit raw data files to git | Confirmed: `.gitignore` already excludes `data/raw/*` except `.gitkeep` and `README.md` |
| `requirements.in` is source of truth — never edit `requirements.txt` by hand (REPR-04) | Add `kaggle` to `requirements.in` only; document that `requirements.txt` must be regenerated |
| DuckDB first for tabular profiling | Not applicable to this phase (data acquisition, not analysis) |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | URL downloads are simpler to run on the host with `curl` than routing through `docker compose exec` | Architecture Patterns, Pattern 6 | If container has different curl capabilities needed (e.g., auth headers), host approach may miss them — but no auth is needed for simple public URLs |
| A2 | `unzip` is available on the host Linux system | Code Examples | URL-based ZIP extraction would fail; fallback to `python3 -m zipfile -e` would be needed |
| A3 | `data/raw/.stage/` dotfolder is automatically excluded from docker-compose.yml `:ro` mount scope | Standard Stack | If docker ignores dotfolder but still exposes it `:ro`, staging writes to `.stage/` inside the container would fail — but `.stage/` is on the HOST, not inside container, so this is safe by design |
| A4 | The existing `data/raw/README.md` has no content that would conflict with appended provenance blocks | Runtime State Inventory | The README ends with prose text; appending markdown section headers is safe |

---

## Open Questions

1. **Should `doml-get-data` be invocable standalone from the CLI arguments?**
   - What we know: CONTEXT.md specifies `doml-get-data kaggle owner/dataset-name` and `doml-get-data url https://...` as the invocation forms
   - What's unclear: SKILL.md uses `$ARGUMENTS` — the workflow needs to parse the first token as `kaggle` or `url` and the second as the slug/URL
   - Recommendation: Workflow Step 1 parses `$ARGUMENTS` with a simple bash split; if first token is neither "kaggle" nor "url", print usage and stop

2. **Should the `docker-compose.yml` template be modified to add Kaggle env vars, or only the project-level `docker-compose.yml`?**
   - What we know: CONTEXT.md says to update `docker-compose.yml` template; the template is what `doml-new-project` copies into new projects
   - What's unclear: The project-level `docker-compose.yml` (already copied for this project) also needs updating for current use
   - Recommendation: Modify BOTH files — template for future projects, project-level file for immediate use in this project

3. **How should the `.stage/` directory interact with the `:ro` container mount?**
   - What we know: `data/raw/` is mounted `:ro` inside the container. `.stage/` is a subdirectory on the HOST under `data/raw/`
   - What's unclear: Does the container see `.stage/` as `:ro` because it's under the mounted volume path?
   - Recommendation: This is safe by design — `.stage/` is only written to from the HOST side (URL downloads use host curl). Kaggle downloads use `/tmp/doml-stage` INSIDE the container (completely separate). The decision to use `/tmp/doml-stage` (not `data/raw/.stage/`) for in-container staging is correct.

---

## Sources

### Primary (HIGH confidence)
- [VERIFIED: local kaggle CLI 1.6.17] — `kaggle datasets download` flags confirmed via `--help`
- [VERIFIED: local tools] — curl 8.7.1, sha256sum 9.4, wget 1.21.4 all confirmed present
- [VERIFIED: .claude/doml/workflows/new-project.md] — Step 3 exact code and empty-data error path confirmed
- [VERIFIED: .claude/doml/templates/docker-compose.yml] — Kaggle env vars absent; `:ro` mount confirmed
- [VERIFIED: /home/bill/source/DoML/requirements.in] — `kaggle` not yet in deps
- [VERIFIED: /home/bill/source/DoML/.gitignore] — `data/raw/*` excluded; `.stage/` not yet listed
- [VERIFIED: git lfs version] — NOT installed on host
- [VERIFIED: SKILL.md files for doml-business-understanding, doml-modelling, doml-data-understanding] — SKILL.md pattern established and consistent

### Secondary (MEDIUM confidence)
- [CITED: CONTEXT.md] — All architecture decisions, staging pattern, provenance format verbatim

### Tertiary (LOW confidence)
- [ASSUMED] — `unzip` is available in the container image (jupyter/datascience-notebook is Debian-based; unzip typically present but not verified)
- [ASSUMED] — `docker compose ps -q jupyter` returns exactly one line in normal single-container use

---

## Metadata

**Confidence breakdown:**
- Skill/workflow file structure: HIGH — verified against 3 existing Phase 8 skills
- Kaggle CLI flags: HIGH — verified via `--help` on installed 1.6.17
- Docker exec + cp pattern: HIGH — specified verbatim in CONTEXT.md; commands confirmed available
- git LFS: HIGH (not installed, confirmed) — graceful degrade path required
- URL download implementation: MEDIUM — curl confirmed on host; edge cases (redirects, auth) not exhaustively tested
- new-project.md modification: HIGH — exact step identified; modification scope is small and well-defined

**Research date:** 2026-04-10
**Valid until:** 2026-05-10 (stable CLI tooling; Kaggle API versioning is slow-moving)
