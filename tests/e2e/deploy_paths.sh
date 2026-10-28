#!/usr/bin/env bash
# Run the deploy workflows (deploy-model + cli/web/wasm + performance report) against a
# project that tests/e2e/pipeline.py has already scaffolded and executed.
# The commands come straight from the workflow Markdown (tests/e2e/extract_blocks.py).
#
# Usage: deploy_paths.sh PROJECT_DIR TARGET...      TARGET: cli_binary | web_service | onnx_wasm
# Needs: docker compose; python3 on PATH with pandas + joblib (host-side workflow steps).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly REPO
readonly EXTRACT="${REPO}/tests/e2e/extract_blocks.py"
readonly WF=".claude/doml/workflows"

project="$1"
shift
cd "$project"
docker compose up -d --build --wait >/dev/null

fail=0
for target in "$@"; do
  case "$target" in
    cli_binary) wf=deploy-cli ;;
    web_service) wf=deploy-web ;;
    onnx_wasm) wf=deploy-wasm ;;
    *)
      echo "unknown target: $target" >&2
      exit 2
      ;;
  esac
  # Step 12 of deploy-model has web-only blocks (12 start service, 18 stop) and a
  # non-web block (13 empty URL).
  if [[ "$target" == web_service ]]; then report_drop=13; else report_drop=12,18; fi
  script="$(mktemp)"
  {
    echo 'ARGUMENTS=""'
    echo "TARGET_KEY=${target}"
    echo 'LEADERBOARD=models/leaderboard.csv'
    echo 'set -o pipefail'
    python3 "$EXTRACT" "${WF}/deploy-model.md" --to 9
    python3 "$EXTRACT" "${WF}/${wf}.md"
    echo 'cat > /tmp/doml_performance.md <<EOF_PERF'
    echo 'Deploy-path test: performance narrative written by tests/e2e/deploy_paths.sh.'
    echo 'EOF_PERF'
    python3 "$EXTRACT" "${WF}/deploy-model.md" --from 12 --drop "16,${report_drop}"
    # shellcheck disable=SC2016  # expands later, inside the generated script
    echo 'echo "DEPLOY_DIR=${DEPLOY_DIR:-src/${MODEL_SLUG}/v${VERSION}}"'
  } >"$script"
  log="reports/deploy_${target}.log"
  if bash "$script" >"$log" 2>&1 \
    && grep -q NO_CELL_ERRORS_OK "$log"; then
    echo "PASS ${target} ($(grep -m1 '^DEPLOY_DIR=' "$log" | cut -d= -f2))"
  else
    echo "FAIL ${target} (log: ${project}/${log})"
    tail -15 "$log"
    fail=1
  fi
  rm -f "$script"
done
docker compose down -t 2 >/dev/null 2>&1 || true
exit "$fail"
