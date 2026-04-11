# Phase 9 Context: doml-get-data

**Phase:** 9 — `doml-get-data`
**Milestone:** 3 — Refinement
**Requirements:** CMD-14, DATA-01, DATA-02, DATA-03, DATA-04
**Date:** 2026-04-10

---

## Decisions

### Kaggle authentication — env vars in docker-compose.yml

Kaggle credentials are passed as environment variables in `docker-compose.yml`:

```yaml
environment:
  - KAGGLE_USERNAME=${KAGGLE_USERNAME:-}
  - KAGGLE_KEY=${KAGGLE_KEY:-}
```

The user sets these in their `.env` file or directly in `docker-compose.yml`. The workflow
detects missing/empty vars **inside the container** and prints setup instructions, then stops.
No interactive credential entry. No `~/.kaggle/kaggle.json` file management.

**Setup instructions message should tell the user:**
1. Go to kaggle.com → Account → API → Create New API Token
2. Note the `username` and `key` values from the downloaded JSON
3. Add `KAGGLE_USERNAME` and `KAGGLE_KEY` to `docker-compose.yml` (or `.env`)
4. Rebuild/restart the container: `docker compose up`

### Kaggle CLI location — inside Docker image

`kaggle` CLI is installed in the Docker image (add `kaggle` to `requirements.in`).
All download operations run inside the container — no local Python dependency on the host.

### Container execution — docker compose exec (running container, docker cp out)

Use the already-running `jupyter` container via `docker compose exec`. Since `data/raw/` is
mounted `:ro` inside the container, downloads go to a temp directory inside the container,
then `docker cp` transfers them to the host's `data/raw/` directory (which is writable on
the host). The `:ro` mount constraint is never relaxed.

```bash
# 1. Download + extract inside running container to a temp staging dir
docker compose exec jupyter bash -c "
  mkdir -p /tmp/doml-stage && \
  kaggle datasets download -d owner/slug -p /tmp/doml-stage --unzip
"

# 2. Copy extracted files from container to host data/raw/
docker cp "$(docker compose ps -q jupyter)":/tmp/doml-stage/. ./data/raw/

# 3. Clean up staging dir inside container
docker compose exec jupyter bash -c "rm -rf /tmp/doml-stage"
```

The workflow must check that Docker is running (`docker compose ps`) before proceeding,
and fail with a clear message if the container is not up.

### Staging area — data/raw/.stage/ (dotfolder, gitignored)

All downloads (Kaggle ZIPs, URL files) land in `data/raw/.stage/` first:
- Dotfolder → automatically ignored by `.gitignore` (add `data/raw/.stage/` entry)
- ZIPs are extracted in-place within `.stage/`
- Extracted files (CSV, Parquet, Excel) are moved to `data/raw/`
- `.stage/` is cleaned (emptied) after each successful download run
- If extraction fails, `.stage/` contents are left for debugging

### Download scope — all files

For Kaggle datasets: download all files in the dataset (no user selection).
For URLs: download the file at the URL. If it is a ZIP, extract all contents.

Supported formats landing in `data/raw/`: `*.csv`, `*.tsv`, `*.parquet`, `*.xlsx`, `*.xls`
(`.xls` triggers the existing "unsupported format" warning in new-project scan).

### Git LFS — auto-setup on first download

On first `doml-get-data` run (or if `.gitattributes` doesn't already track data files):
1. Check if git LFS is initialized: `git lfs version 2>/dev/null`
2. If not initialized: `git lfs install`
3. Ensure `.gitattributes` tracks data file types:
   ```
   data/raw/*.csv filter=lfs diff=lfs merge=lfs -text
   data/raw/*.parquet filter=lfs diff=lfs merge=lfs -text
   data/raw/*.xlsx filter=lfs diff=lfs merge=lfs -text
   data/raw/*.zip filter=lfs diff=lfs merge=lfs -text
   ```
4. If `.gitattributes` was modified, print a reminder to `git add .gitattributes && git commit`.

If `git lfs version` fails (LFS not installed on host), print a warning with install
instructions (`git lfs install` via package manager) but **do not stop** — the download
proceeds without LFS setup.

### new-project integration — inline choice, then resume

`new-project.md` is modified so that when `data/raw/` is empty (no supported files found),
instead of exiting with an error, it presents an inline choice:

**AskUserQuestion:**
- "Get data now" → immediately runs the `doml-get-data` acquisition flow inline (source
  selection: Kaggle slug or URL → download → extraction → log). After completion, re-scans
  `data/raw/` and continues the interview.
- "Add files manually" → prints instructions (supported formats, target directory, docker
  compose restart reminder), then presents a second AskUserQuestion: "I've added my files —
  continue". When user confirms, re-scans `data/raw/` and continues the interview. If the
  re-scan still finds no files, loops back to the choice.

### README.md log — full provenance block, always append

Each download appends a provenance block to `data/raw/README.md`:

```markdown
## Download: 2026-04-10 14:23 UTC

| Field | Value |
|-------|-------|
| Source | kaggle: owner/dataset-name |
| Downloaded | 2026-04-10 14:23:47 UTC |
| Files | 3 |

| File | Size | SHA-256 |
|------|------|---------|
| train.csv | 42.3 MB | a1b2c3d4... |
| test.csv | 8.1 MB | e5f6a7b8... |
| sample_submission.csv | 112 KB | c9d0e1f2... |
```

- **Source format:** `kaggle: owner/slug` or `url: https://...`
- **Timestamp:** UTC, ISO-8601 (`2026-04-10T14:23:47Z`) in table, readable label in header
- **SHA-256:** computed inside the container after download (`sha256sum`)
- **File sizes:** human-readable (MB/KB/GB), computed inside container (`du -sh`)
- Re-downloads always append — full download history preserved

---

## Canonical refs

- `REQUIREMENTS.md` — DATA-01, DATA-02, DATA-03, DATA-04 (data acquisition requirements)
- `REQUIREMENTS.md` — CMD-14 (command spec)
- `.claude/doml/workflows/new-project.md` — Steps to modify for empty-data fallback (Step 2 scan)
- `.claude/doml/templates/docker-compose.yml` — Template to update with KAGGLE env vars
- `requirements.in` — Add `kaggle` package
- `data/raw/README.md` — Download log target

---

## Files to Create

- `.claude/skills/doml-get-data/SKILL.md` — skill entry point
- `.claude/doml/workflows/get-data.md` — full acquisition workflow
  - Source selection (Kaggle slug vs URL)
  - Credential check (env vars inside container)
  - Staging + download + extraction
  - Git LFS setup
  - README.md provenance log

## Files to Modify

- `.claude/doml/workflows/new-project.md` — replace empty-data error exit with inline choice
- `.claude/doml/templates/docker-compose.yml` — add KAGGLE env vars to environment block
- `requirements.in` — add `kaggle` (unpinned top-level)
- `requirements.txt` — regenerate after adding kaggle (or note for executor to rebuild)
- `.gitignore` — add `data/raw/.stage/`

---

## Out of Scope for Phase 9

- Kaggle competition downloads (`kaggle competitions download`) — dataset downloads only for now
- Multiple simultaneous downloads / batch mode
- Authentication methods other than env vars (OAuth, service accounts)
- Progress bars or streaming download output
- Automatic dataset versioning / update checking
