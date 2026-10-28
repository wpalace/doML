#!/usr/bin/env bash
# Run the get-data Kaggle flow (the workflow's own bash blocks) in a scaffolded project.
# Credentials come only from the environment (KAGGLE_API_TOKEN, or KAGGLE_USERNAME + KAGGLE_KEY);
# this script never prints or stores them.
#
# Usage: kaggle_path.sh PROJECT_DIR OWNER/DATASET
set -Eeuo pipefail

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly REPO
readonly PROJECT="$1" SLUG="$2"

main() {
  cd -- "$PROJECT"
  docker compose up -d --build --wait >/dev/null
  local script before after
  script="$(mktemp)"
  {
    printf 'SOURCE_TYPE=kaggle\nSOURCE_VALUE=%q\nSLUG=%q\nARGUMENTS=%q\n' "$SLUG" "$SLUG" "kaggle $SLUG"
    python3 "${REPO}/tests/e2e/extract_blocks.py" .claude/doml/workflows/get-data.md \
      --drop 8,9,10,11
  } >"$script"
  before="$(find data/raw -maxdepth 1 -type f | wc -l)"
  bash "$script" >reports/get_data_kaggle.log 2>&1 || {
    tail -20 reports/get_data_kaggle.log
    exit 1
  }
  rm -f -- "$script"
  after="$(find data/raw -maxdepth 1 -type f | wc -l)"
  ((after > before)) || {
    printf 'FAIL kaggle: no new files in data/raw\n'
    exit 1
  }
  # The container must see the files and must not be able to change them.
  docker compose exec -T doml python - <<'PY'
import pathlib
raw = pathlib.Path("/project/data/raw")
files = [p for p in raw.iterdir() if p.is_file()]
assert files, "no files visible in /project/data/raw"
try:
    (raw / "write_probe").touch()
except OSError:
    pass
else:
    raise SystemExit("data/raw is writable in the container")
print("container sees", len(files), "files; data/raw is read-only")
PY
  docker compose down -t 2 >/dev/null 2>&1 || true
  printf 'PASS kaggle %s: %s new file(s) in data/raw\n' "$SLUG" "$((after - before))"
}

main "$@"
