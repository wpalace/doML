# DoML Get Data Workflow

## Purpose
Acquire a dataset into data/raw/ from Kaggle or a direct URL.

## Invoked by: /doml-get-data

---

## Workflow

### Step 1 — Parse arguments and validate input

Parse `$ARGUMENTS` by splitting on whitespace. The first token is the source type; the remainder is the
source value.

Supported invocation forms:
- `doml-get-data kaggle owner/dataset-name`
- `doml-get-data url https://example.com/data.csv`

If the first token is neither `kaggle` nor `url` (case-insensitive), or if no arguments were provided,
display:

```
Usage:
  /doml-get-data kaggle owner/dataset-name
  /doml-get-data url https://example.com/data.csv

Examples:
  /doml-get-data kaggle titanic/titanic-dataset
  /doml-get-data url https://example.com/data.csv
```

Then stop.

Set variables:
- `SOURCE_TYPE`: `"kaggle"` or `"url"` (lowercase)
- `SOURCE_VALUE`: the slug (`owner/dataset-name`) or URL string

---

### Step 2 — Check Docker is running

```bash
if ! docker compose ps --services --filter status=running 2>/dev/null | grep -q jupyter; then
  echo "Error: The DoML Docker container is not running."
  echo "Start it with: docker compose up -d"
  exit 1
fi

# Get container ID (first instance only — handles scaled services gracefully)
CONTAINER_ID=$(docker compose ps -q jupyter | head -1)
```

If the container is not running, display:
```
Error: The DoML Docker container is not running.
Start it with: docker compose up -d
```
Then stop.

---

### Step 3 — Clean staging area at run start

Before any download, ensure `.stage/` is clean so stale files from a previous failed run never appear as
new downloads:

```bash
rm -rf ./data/raw/.stage
mkdir -p ./data/raw/.stage
```

---

### Step 4 — Kaggle flow (if SOURCE_TYPE == "kaggle")

#### Step 4a — Verify Kaggle credentials inside container

```bash
docker compose exec jupyter bash -c '
  if [ -z "$KAGGLE_USERNAME" ] || [ -z "$KAGGLE_KEY" ]; then
    echo "MISSING_KAGGLE_CREDS"
    exit 1
  fi
  echo "CREDS_OK"
'
```

If the output contains `MISSING_KAGGLE_CREDS`, display:

```
Kaggle credentials are not set. To fix this:

1. Go to https://www.kaggle.com → Account → API → Create New API Token
2. The downloaded JSON file contains "username" and "key" values
3. Add these to docker-compose.yml under the jupyter service's environment block:
     - KAGGLE_USERNAME=your_username_here
     - KAGGLE_KEY=your_key_here
   Or create a .env file in the project root with:
     KAGGLE_USERNAME=your_username_here
     KAGGLE_KEY=your_key_here
4. Restart the container so the new env vars take effect:
     docker compose down && docker compose up -d
   (Note: a running container does not pick up .env changes without restart)
```

Then stop.

#### Step 4b — Download and extract inside container

```bash
# Clean in-container staging dir first
docker compose exec jupyter bash -c "rm -rf /tmp/doml-stage && mkdir -p /tmp/doml-stage"

# Download and unzip (--unzip handles the outer ZIP; nested ZIPs handled below)
docker compose exec jupyter bash -c "
  kaggle datasets download -d '${SLUG}' -p /tmp/doml-stage --unzip --quiet
"
```

After extraction, check for nested ZIPs (kaggle --unzip only extracts one level):

```bash
docker compose exec jupyter bash -c "
  find /tmp/doml-stage -name '*.zip' | while read z; do
    echo \"Extracting nested ZIP: \$z\"
    unzip -q \"\$z\" -d \"\$(dirname \$z)/\"
    rm \"\$z\"
  done
"
```

#### Step 4c — Copy files to host data/raw/ via docker cp

```bash
# IMPORTANT: trailing /. copies directory contents, not the directory itself
docker cp "${CONTAINER_ID}:/tmp/doml-stage/." ./data/raw/
```

Pitfall: `docker cp CONTAINER:/tmp/doml-stage ./data/raw/` copies the `doml-stage` directory itself.
Always use the `/.` suffix to copy contents only.

#### Step 4d — Clean up in-container staging dir

```bash
docker compose exec jupyter bash -c "rm -rf /tmp/doml-stage"
```

Skip to Step 6.

---

### Step 5 — URL flow (if SOURCE_TYPE == "url")

#### Step 5a — Validate URL format

Check that `SOURCE_VALUE` begins with `http://` or `https://`. If not, display:
```
Error: Invalid URL. Must start with http:// or https://
```
Then stop.

#### Step 5b — Download file to staging dir

```bash
# Strip query string and fragment from filename
FILENAME=$(basename "$URL" | cut -d'?' -f1 | cut -d'#' -f1)

# If filename has no extension or is empty, use a default
if [ -z "$FILENAME" ] || [ "$FILENAME" = "$URL" ]; then
  FILENAME="download"
fi

mkdir -p ./data/raw/.stage
curl -L --progress-bar -o "./data/raw/.stage/${FILENAME}" "$URL"
```

If `curl` exits non-zero, display: `Error: Download failed. Check the URL and your network connection.`
Then stop. Leave `.stage/` in place for debugging (do not clean on failure).

#### Step 5c — Extract ZIP if needed

```bash
if [[ "$FILENAME" == *.zip ]]; then
  echo "Extracting ZIP archive..."
  unzip -q "./data/raw/.stage/${FILENAME}" -d "./data/raw/.stage/"
  rm "./data/raw/.stage/${FILENAME}"

  # Handle nested ZIPs (one additional level)
  find ./data/raw/.stage -name '*.zip' | while read z; do
    echo "Extracting nested ZIP: $z"
    unzip -q "$z" -d "$(dirname "$z")/"
    rm "$z"
  done
fi
```

#### Step 5d — Move supported formats to data/raw/

Supported formats: `*.csv`, `*.tsv`, `*.parquet`, `*.xlsx`, `*.xls`

```bash
for ext in csv tsv parquet xlsx xls; do
  find ./data/raw/.stage -maxdepth 2 -name "*.${ext}" -exec mv {} ./data/raw/ \;
done
```

#### Step 5e — Clean up staging dir

```bash
rm -rf ./data/raw/.stage
```

---

### Step 6 — Git LFS setup (graceful degrade)

```bash
if git lfs version &>/dev/null; then
  git lfs install

  LFS_NEEDED=false
  for pattern in "data/raw/*.csv" "data/raw/*.tsv" "data/raw/*.parquet" "data/raw/*.xlsx" "data/raw/*.zip"; do
    if ! grep -q "$pattern" .gitattributes 2>/dev/null; then
      echo "${pattern} filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
      LFS_NEEDED=true
    fi
  done

  if [ "$LFS_NEEDED" = true ]; then
    echo ""
    echo "Reminder: .gitattributes was updated for LFS tracking."
    echo "Run: git add .gitattributes && git commit -m \"chore: add LFS tracking for data files\""
  fi
else
  echo ""
  echo "Warning: git-lfs is not installed. Large data files will not be LFS-tracked."
  echo "To install:"
  echo "  Ubuntu/Debian: sudo apt install git-lfs"
  echo "  macOS:         brew install git-lfs"
  echo ""
  echo "The download has still completed successfully."
fi
```

---

### Step 7 — Compute provenance and append to README.md

Identify newly arrived files (track what was in data/raw/ before vs after, or simply compute for
all files just moved there in this run).

For Kaggle downloads, compute file info on the host after docker cp:

```bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
READABLE_TS=$(date -u +"%Y-%m-%d %H:%M UTC")

# Build file table for newly downloaded files
FILE_TABLE=""
FILE_COUNT=0
for f in ./data/raw/*.csv ./data/raw/*.tsv ./data/raw/*.parquet ./data/raw/*.xlsx ./data/raw/*.xls; do
  [ -f "$f" ] || continue
  HASH=$(sha256sum "$f" | awk '{print $1}')
  SIZE=$(du -sh "$f" | awk '{print $1}')
  NAME=$(basename "$f")
  FILE_TABLE="${FILE_TABLE}| ${NAME} | ${SIZE} | ${HASH} |\n"
  FILE_COUNT=$((FILE_COUNT + 1))
done
```

**Source format strings:**
- Kaggle: `kaggle: owner/dataset-name`
- URL: `url: https://...`

Append to `data/raw/README.md`:

```bash
# Ensure README.md ends with a newline before appending
# (prevents provenance block from merging with existing last line)
echo "" >> ./data/raw/README.md

cat >> ./data/raw/README.md << PROVENANCE

## Download: ${READABLE_TS}

| Field | Value |
|-------|-------|
| Source | ${SOURCE_LABEL} |
| Downloaded | ${TIMESTAMP} |
| Files | ${FILE_COUNT} |

| File | Size | SHA-256 |
|------|------|---------|
$(echo -e "$FILE_TABLE")
PROVENANCE
```

Note: `SOURCE_LABEL` is `"kaggle: ${SLUG}"` for Kaggle downloads or `"url: ${URL}"` for URL downloads.

---

### Step 8 — Display summary

Display a completion summary:

```
doml-get-data complete

Source:    [kaggle: owner/slug  OR  url: https://...]
Files:     N file(s) added to data/raw/
  - filename.csv  (42.3 MB)
  - filename2.csv (8.1 MB)
Provenance logged to data/raw/README.md

Next steps:
  Run /doml-new-project to begin your analysis
  (or if already started: run /doml-data-understanding)
```

---

## Critical Correctness Constraints

- Never write directly to data/raw/ from inside the container — the mount is `:ro`. Always use `/tmp/doml-stage` for in-container staging, then `docker cp`.
- `docker cp` path MUST end with `/.` to copy directory contents, not the directory itself.
- Kaggle credentials MUST be checked inside the container (where the env vars are set), not on the host.
- `.stage/` must be cleaned at the START of each run to prevent stale data from a previous failed run.
- If extraction fails, leave `.stage/` in place for debugging (do not clean on error).
- On missing git-lfs, warn and continue — never abort the download.
- Always append to README.md, never overwrite. Add a blank line before the provenance block to prevent line merging.
