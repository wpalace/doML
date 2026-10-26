#!/usr/bin/env bash
# Exception (bash standard): dispatch script for every test stage, kept as one file so an agent
# has a single entry point (see MAKE.md). Each stage is a short function.
#
# Usage: tests/run_all.sh [STAGE...]     (no STAGE = all stages, in order)
# Stages: unit check e2e install build docker-e2e deploy kaggle lint grep
# Env:    DOML_E2E_KINDS   problem types for e2e stages (default: all six)
#         DOML_WORK        scratch directory (default: a new mktemp -d)
#         KAGGLE_API_TOKEN enables the kaggle stage (never printed)
#         DOML_COMPOSE_BRIDGE=1  use the default bridge network (hosts where compose DNS fails)
set -Eeuo pipefail
shopt -s inherit_errexit nullglob
IFS=$'\n\t'

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPO
readonly VENV="${REPO}/.venv"
readonly IMAGE="doml-test:latest"
readonly ALL_STAGES=(unit check e2e install build docker-e2e deploy kaggle lint grep)
WORK="${DOML_WORK:-$(mktemp -d)}"
readonly WORK
IFS=' ' read -r -a KINDS <<<"${DOML_E2E_KINDS:-regression classification clustering dimensionality_reduction anomaly forecasting}"
declare -a RESULTS=()

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}
log() { printf '\n==> %s\n' "$*"; }

# Host Python env from the same lock as the image (python 3.14, uv).
ensure_venv() {
  command -v uv >/dev/null || die "uv is required (https://docs.astral.sh/uv/)"
  if [[ ! -x "${VENV}/bin/python" ]]; then
    uv venv --quiet --python 3.14 "$VENV"
  fi
  uv pip sync --quiet --python "${VENV}/bin/python" --require-hashes "${REPO}/requirements.txt"
}

py() { "${VENV}/bin/python" "$@"; }

stage_unit() {
  ensure_venv
  (cd -- "$REPO" && py -m pytest -q -p no:cacheprovider tests </dev/null)
}

stage_check() {
  ensure_venv
  py -m marimo check --strict "${REPO}"/.claude/doml/templates/notebooks/*.py
}

stage_e2e() {
  ensure_venv
  local kind
  for kind in "${KINDS[@]}"; do
    py "${REPO}/tests/e2e/pipeline.py" scaffold "$kind" "${WORK}/venv-${kind}" >/dev/null
    (cd -- "${WORK}/venv-${kind}" \
      && PATH="${VENV}/bin:${PATH}" py "${REPO}/tests/e2e/pipeline.py" execute "$kind" .)
  done
}

stage_install() {
  local target dir
  for target in claude copilot; do
    dir="${WORK}/install-${target}"
    mkdir -p -- "$dir"
    (cd -- "$dir" && DOML_SOURCE_DIR="$REPO" bash "${REPO}/install.sh" --target "$target")
    py "${REPO}/tests/e2e/check_install.py" "$target" "$dir"
    if command -v pwsh >/dev/null; then
      mkdir -p -- "${dir}-ps"
      (cd -- "${dir}-ps" \
        && DOML_SOURCE_DIR="$REPO" DOML_TARGET="$target" pwsh -NoProfile -File "${REPO}/install.ps1")
      diff -r -- "$dir" "${dir}-ps"
    fi
  done
}

stage_build() {
  local start=$SECONDS
  docker build --quiet --tag "$IMAGE" --file "${REPO}/.claude/doml/templates/Dockerfile" \
    "${REPO}/.claude/doml/templates"
  printf 'build: %ss, size: %s, python packages: %s\n' "$((SECONDS - start))" \
    "$(docker image ls "$IMAGE" --format '{{.Size}}')" \
    "$(docker run --rm "$IMAGE" python -m pip list --format=freeze 2>/dev/null | wc -l)"
  docker run --rm --network none "$IMAGE" python -c "import duckdb; duckdb.execute('LOAD excel')"
}

# Each kind runs in its own compose project: data/raw is mounted read-only, as for users.
stage_docker_e2e() {
  local kind dir
  for kind in "${KINDS[@]}"; do
    dir="${WORK}/docker-${kind}"
    py "${REPO}/tests/e2e/pipeline.py" scaffold "$kind" "$dir" >/dev/null
    (cd -- "$dir" && docker compose -p "doml-e2e-${kind//_/-}" run --rm -T \
      -e DOML_EXPECT_RO_RAW=1 -v "${REPO}:/repo:ro" doml \
      python /repo/tests/e2e/pipeline.py execute "$kind" /project)
  done
}

stage_deploy() {
  local kind dir
  for kind in regression classification; do
    dir="${WORK}/docker-${kind}"
    [[ -f "${dir}/models/best_model.pkl" ]] || die "run docker-e2e for ${kind} first"
    PATH="${VENV}/bin:${PATH}" "${REPO}/tests/e2e/deploy_paths.sh" "$dir" \
      cli_binary web_service onnx_wasm
  done
}

stage_kaggle() {
  if [[ -z "${KAGGLE_API_TOKEN:-}" && -z "${KAGGLE_KEY:-}" ]]; then
    printf 'skip: no Kaggle credentials in the environment\n'
    return 0
  fi
  local dir="${WORK}/docker-regression"
  [[ -d "$dir" ]] || die "run docker-e2e first"
  "${REPO}/tests/e2e/kaggle_path.sh" "$dir" "uciml/iris"
}

stage_lint() {
  local scripts=("${REPO}/install.sh" "${REPO}"/tests/*.sh "${REPO}"/tests/e2e/*.sh)
  if command -v shellcheck >/dev/null; then shellcheck "${scripts[@]}"; fi
  if command -v shfmt >/dev/null; then shfmt -d -i 2 -ci -bn "${REPO}"/tests; fi
  ensure_venv
  if py -m ruff --version >/dev/null 2>&1; then py -m ruff check "${REPO}/tests/e2e" "${REPO}/.claude/doml/bin"; fi
}

# The R workflow and Jupyter are gone: nothing outside history/planning may refer to them.
# Allowed: lock files (jupyter-core is a transitive dependency of marimo/plotly), the one-off
# migration tools, and comments that say what marimo replaces.
stage_grep() {
  local pattern='\bR (language|kernel|notebook)|rpy2|IRkernel|tidyverse|renv|\.ipynb|nbconvert'
  pattern+='|papermill|jupyter|nbstripout|jovyan'
  local hits
  hits="$(cd -- "$REPO" && git grep -n -i -E "$pattern" -- . ':!.planning' ':!MIGRATION-*.md' \
    ':!tests/run_all.sh' ':(glob,exclude)**/uv.lock' ':(glob,exclude)**/requirements.txt' \
    | grep -v -i -E 'replaces|No Jupyter|earlier Jupyter|R or Jupyter|ipynb template|rglob\("\*\.ipynb' || true)"
  if [[ -n "$hits" ]]; then
    printf '%s\n' "$hits"
    die "found leftover R/Jupyter references (above)"
  fi
  printf 'no R/Jupyter references outside history, planning and lock files\n'
}

run_stage() {
  local stage="$1" fn="stage_${1//-/_}" start=$SECONDS
  declare -F "$fn" >/dev/null || die "unknown stage: ${stage}"
  log "stage ${stage}"
  # A child process keeps errexit active inside the stage (an `if` would switch it off).
  if DOML_WORK="$WORK" "${BASH_SOURCE[0]}" --stage "$stage"; then
    RESULTS+=("PASS ${stage} ($((SECONDS - start))s)")
  else
    RESULTS+=("FAIL ${stage} ($((SECONDS - start))s)")
  fi
}

main() {
  if [[ "${1:-}" == --stage ]]; then
    "stage_${2//-/_}"
    return
  fi
  local stages=("$@")
  ((${#stages[@]})) || stages=("${ALL_STAGES[@]}")
  mkdir -p -- "$WORK"
  printf 'work dir: %s\n' "$WORK"
  local stage
  for stage in "${stages[@]}"; do run_stage "$stage"; done
  log "summary"
  printf '%s\n' "${RESULTS[@]}"
  [[ "${RESULTS[*]}" != *FAIL* ]]
}

main "$@"
