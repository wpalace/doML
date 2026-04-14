"""Tests for Phase 09 — doml-get-data (CMD-14, DATA-01, DATA-02, DATA-03, DATA-04)

Verifies that:
- SKILL.md for doml-get-data exists with correct frontmatter (CMD-14)
- get-data.md workflow covers both Kaggle and URL flows (DATA-01, DATA-02)
- get-data.md contains critical correctness guards (docker cp /., pre-run cleanup, etc.)
- get-data.md appends provenance to README.md with SHA-256 (DATA-04)
- new-project.md contains EMPTY_DATA_DIR sentinel + Step 3b acquisition loop (DATA-03)
- Config files updated: docker-compose.yml template (KAGGLE env vars), requirements.in (kaggle), .gitignore (.stage/)
"""
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

SKILL_MD = REPO_ROOT / ".claude" / "skills" / "doml-get-data" / "SKILL.md"
GET_DATA_WF = REPO_ROOT / ".claude" / "doml" / "workflows" / "get-data.md"
NEW_PROJECT_WF = REPO_ROOT / ".claude" / "doml" / "workflows" / "new-project.md"
DOCKER_COMPOSE_TMPL = REPO_ROOT / ".claude" / "doml" / "templates" / "docker-compose.yml"
REQUIREMENTS_IN = REPO_ROOT / "requirements.in"
GITIGNORE = REPO_ROOT / ".gitignore"


# ---------------------------------------------------------------------------
# Gap 1: CMD-14 / 09-01 — SKILL.md exists with correct frontmatter
# ---------------------------------------------------------------------------

def test_get_data_skill_file_exists():
    """SKILL.md for doml-get-data must exist (CMD-14)."""
    assert SKILL_MD.exists(), (
        f"Expected SKILL.md at {SKILL_MD} — doml-get-data skill not created"
    )


def test_get_data_skill_has_correct_name():
    """SKILL.md must declare name: doml-get-data (CMD-14)."""
    content = SKILL_MD.read_text()
    assert "name: doml-get-data" in content, (
        "SKILL.md does not contain 'name: doml-get-data' in frontmatter"
    )


def test_get_data_skill_has_argument_hint():
    """SKILL.md must include argument-hint for kaggle/url invocation forms (CMD-14)."""
    content = SKILL_MD.read_text()
    assert "argument-hint" in content, (
        "SKILL.md missing argument-hint — skill invocation pattern undocumented"
    )


def test_get_data_skill_references_workflow():
    """SKILL.md must reference get-data.md via execution_context (CMD-14)."""
    content = SKILL_MD.read_text()
    assert "get-data.md" in content, (
        "SKILL.md execution_context does not reference get-data.md"
    )


# ---------------------------------------------------------------------------
# Gap 2: DATA-01 / 09-02 — get-data.md workflow exists and covers Kaggle flow
# ---------------------------------------------------------------------------

def test_get_data_workflow_exists():
    """get-data.md workflow must exist (DATA-01, DATA-02)."""
    assert GET_DATA_WF.exists(), (
        f"Expected workflow at {GET_DATA_WF} — get-data.md not created"
    )


def test_get_data_workflow_minimum_size():
    """get-data.md must be at least 150 lines (DATA-01, DATA-02)."""
    lines = GET_DATA_WF.read_text().splitlines()
    assert len(lines) >= 150, (
        f"get-data.md has only {len(lines)} lines — workflow appears incomplete (need ≥150)"
    )


def test_get_data_workflow_has_kaggle_flow():
    """get-data.md must contain Kaggle download flow (DATA-01)."""
    content = GET_DATA_WF.read_text()
    assert "kaggle" in content.lower(), (
        "get-data.md contains no Kaggle flow — DATA-01 not implemented"
    )


def test_get_data_workflow_kaggle_credential_sentinel():
    """get-data.md must check for MISSING_KAGGLE_CREDS inside container (DATA-01)."""
    content = GET_DATA_WF.read_text()
    assert "MISSING_KAGGLE_CREDS" in content, (
        "get-data.md missing MISSING_KAGGLE_CREDS credential check sentinel — "
        "missing-credentials path is not machine-readable"
    )


def test_get_data_workflow_docker_cp_trailing_dot():
    """get-data.md must use docker cp with trailing /. to copy contents not the directory (DATA-01)."""
    content = GET_DATA_WF.read_text()
    assert "/tmp/doml-stage/." in content or "doml-stage/." in content, (
        "get-data.md docker cp path is missing trailing /. — "
        "docker cp will copy the directory itself instead of its contents"
    )


def test_get_data_workflow_container_id_head_1():
    """get-data.md must use head -1 to get container ID for scaled-service compatibility (DATA-01)."""
    content = GET_DATA_WF.read_text()
    assert "head -1" in content, (
        "get-data.md does not limit container ID to head -1 — "
        "docker compose ps -q returns multiple IDs for scaled services"
    )


# ---------------------------------------------------------------------------
# Gap 3: DATA-02 / 09-03 — get-data.md covers URL flow
# ---------------------------------------------------------------------------

def test_get_data_workflow_has_url_flow():
    """get-data.md must contain URL download flow (DATA-02)."""
    content = GET_DATA_WF.read_text()
    assert "curl" in content, (
        "get-data.md contains no curl command — URL download flow (DATA-02) not implemented"
    )


def test_get_data_workflow_url_validation():
    """get-data.md must validate URL starts with http:// or https:// (DATA-02)."""
    content = GET_DATA_WF.read_text()
    has_http_check = "http://" in content and "https://" in content
    assert has_http_check, (
        "get-data.md does not validate URL protocol prefix — invalid URLs not rejected"
    )


def test_get_data_workflow_url_filename_stripping():
    """get-data.md must strip query strings from downloaded filename (DATA-02)."""
    content = GET_DATA_WF.read_text()
    # Query-string stripping: cut -d'?' -f1
    assert "cut -d'?' -f1" in content or 'cut -d"?" -f1' in content, (
        "get-data.md missing query-string stripping from URL filename — "
        "URLs with ?token= parameters will produce invalid filenames"
    )


# ---------------------------------------------------------------------------
# Gap 4: DATA-03 / 09-04 — new-project.md EMPTY_DATA_DIR integration
# ---------------------------------------------------------------------------

def test_new_project_workflow_empty_data_sentinel():
    """new-project.md must use EMPTY_DATA_DIR sentinel for empty data/raw/ (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    assert "EMPTY_DATA_DIR" in content, (
        "new-project.md missing EMPTY_DATA_DIR sentinel — "
        "empty data/raw/ is still a fatal error instead of a recoverable condition"
    )


def test_new_project_workflow_exit_code_2():
    """new-project.md must raise SystemExit(2) for empty data, not SystemExit(1) (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    assert "SystemExit(2)" in content, (
        "new-project.md does not use SystemExit(2) for empty data — "
        "agent cannot distinguish empty-dir from fatal error"
    )


def test_new_project_workflow_step_3b_acquisition_loop():
    """new-project.md must contain Step 3b data acquisition fallback (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    assert "Step 3b" in content or "3b" in content, (
        "new-project.md missing Step 3b acquisition loop — "
        "empty data/raw/ case has no fallback path"
    )


def test_new_project_workflow_inline_get_data_invocation():
    """new-project.md Step 3b must reference get-data.md for inline invocation (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    assert "get-data.md" in content or "get-data" in content, (
        "new-project.md Step 3b does not reference get-data workflow — "
        "inline acquisition flow is not wired up"
    )


def test_new_project_workflow_three_choice_question():
    """new-project.md Step 3b must offer Kaggle, URL, and manual as separate choices (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    has_kaggle_choice = "Kaggle dataset" in content or "kaggle dataset" in content.lower()
    has_url_choice = "Direct download URL" in content or "download URL" in content
    has_manual_choice = "Add files manually" in content
    assert has_kaggle_choice and has_url_choice and has_manual_choice, (
        "new-project.md Step 3b does not offer all three source choices (Kaggle / URL / manual) — "
        "source type must be known before asking for the dataset slug"
    )


def test_new_project_workflow_credential_check_before_slug():
    """new-project.md Step 3b must run credential pre-check before asking for Kaggle slug (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    assert "credential" in content.lower() or "KAGGLE_CREDS_OK" in content or "Step 1.5" in content, (
        "new-project.md Step 3b does not gate the Kaggle slug question behind a credential check — "
        "user can be asked for a dataset before knowing credentials are missing"
    )


def test_new_project_workflow_credential_confirmation_loop():
    """new-project.md must prompt for confirmation after creating .env — not stop and re-run (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    has_confirm_prompt = "done" in content or "continue" in content
    no_rerun_instruction = "re-run /doml-new-project" not in content
    assert has_confirm_prompt and no_rerun_instruction, (
        "new-project.md still tells the user to re-run /doml-new-project after credential setup — "
        "should instead pause with AskUserQuestion and proceed once credentials are confirmed"
    )


def test_new_project_workflow_credential_restart_instruction():
    """new-project.md confirmation prompt must tell the user to restart the container after updating .env."""
    content = NEW_PROJECT_WF.read_text()
    assert "docker compose down" in content or "docker compose restart" in content, (
        "new-project.md credential confirmation does not include a container restart step — "
        "running container will not pick up .env changes without restart"
    )


def test_new_project_workflow_slug_is_free_text():
    """new-project.md Kaggle slug question must be free-text only with no options (DATA-03)."""
    content = NEW_PROJECT_WF.read_text()
    assert "no options" in content or "free-text" in content or "free text" in content, (
        "new-project.md Kaggle slug AskUserQuestion is not explicitly marked as free-text — "
        "Claude may present it as multiple choice instead of requiring the user to type the slug"
    )


# ---------------------------------------------------------------------------
# Credential pre-check: get-data.md Step 1.5
# ---------------------------------------------------------------------------

def test_get_data_workflow_has_credential_precheck_step():
    """get-data.md must contain a credential pre-check step before Docker check."""
    content = GET_DATA_WF.read_text()
    assert "KAGGLE_CREDS_OK" in content or "credential pre-check" in content.lower(), (
        "get-data.md missing credential pre-check (KAGGLE_CREDS_OK) — "
        "missing credentials are not caught until deep in the Kaggle flow"
    )


def test_get_data_workflow_credential_precheck_before_docker():
    """get-data.md credential pre-check must appear before the Docker check."""
    content = GET_DATA_WF.read_text()
    cred_pos = content.find("KAGGLE_CREDS_OK")
    docker_pos = content.find("docker compose ps")
    assert cred_pos != -1 and docker_pos != -1 and cred_pos < docker_pos, (
        "get-data.md credential pre-check appears after Docker check — "
        "user hits Docker errors before learning credentials are missing"
    )


def test_get_data_workflow_creates_env_placeholder():
    """get-data.md must create .env with xxxxxxxx placeholders when credentials are missing."""
    content = GET_DATA_WF.read_text()
    assert "xxxxxxxxxxxxxxxx" in content, (
        "get-data.md missing xxxxxxxxxxxxxxxx placeholder — "
        ".env file is not created with placeholder values when credentials are absent"
    )


def test_get_data_workflow_env_file_created():
    """get-data.md must write to .env when credentials are missing."""
    content = GET_DATA_WF.read_text()
    assert ".env" in content, (
        "get-data.md does not reference .env file — "
        "credential placeholder file will not be created"
    )


def test_get_data_workflow_placeholder_check():
    """get-data.md credential check must reject xxxxxxxxxxxxxxxx placeholder values as unconfigured."""
    content = GET_DATA_WF.read_text()
    # The check must compare against the placeholder string so a .env with unedited placeholders fails
    assert '"xxxxxxxxxxxxxxxx"' in content or "'xxxxxxxxxxxxxxxx'" in content, (
        "get-data.md does not treat xxxxxxxxxxxxxxxx as an unconfigured credential — "
        "a .env with unedited placeholders would be accepted as valid"
    )


# ---------------------------------------------------------------------------
# Gap 5: DATA-04 / 09-05 — get-data.md appends provenance to README.md
# ---------------------------------------------------------------------------

def test_get_data_workflow_provenance_append():
    """get-data.md must append provenance to README.md (never overwrite) (DATA-04)."""
    content = GET_DATA_WF.read_text()
    # Must use >> (append) not > (overwrite) for README.md
    assert ">> ./data/raw/README.md" in content or ">> data/raw/README.md" in content, (
        "get-data.md does not append to README.md (no >> redirect found) — "
        "provenance may overwrite existing download history"
    )


def test_get_data_workflow_sha256_hash():
    """get-data.md must compute SHA-256 for provenance logging (DATA-04)."""
    content = GET_DATA_WF.read_text()
    assert "sha256sum" in content, (
        "get-data.md missing sha256sum command — provenance block will lack integrity hash"
    )


def test_get_data_workflow_provenance_blank_line_guard():
    """get-data.md must add blank line before README.md append to prevent line merging (DATA-04)."""
    content = GET_DATA_WF.read_text()
    # The blank-line guard: echo "" >> README.md before the provenance block
    assert 'echo "" >> ./data/raw/README.md' in content or "echo '' >> ./data/raw/README.md" in content, (
        "get-data.md missing blank-line guard before README.md append — "
        "provenance block may merge with existing last line"
    )


def test_get_data_workflow_provenance_source_labels():
    """get-data.md must log source as 'kaggle: ...' or 'url: ...' format (DATA-04)."""
    content = GET_DATA_WF.read_text()
    assert "kaggle:" in content and "url:" in content, (
        "get-data.md missing source label formats ('kaggle:' or 'url:') in provenance block"
    )


# ---------------------------------------------------------------------------
# Gap 6: Pre-run cleanup — .stage/ cleared at start of every run
# ---------------------------------------------------------------------------

def test_get_data_workflow_prerun_cleanup():
    """get-data.md must clean .stage/ at run start to prevent stale-data contamination."""
    content = GET_DATA_WF.read_text()
    # Pre-run cleanup before download begins
    assert "rm -rf ./data/raw/.stage" in content or "rm -rf data/raw/.stage" in content, (
        "get-data.md missing pre-run .stage/ cleanup — "
        "stale files from a previous failed run may appear as new downloads"
    )


# ---------------------------------------------------------------------------
# Gap 7: Config files — docker-compose template, requirements.in, .gitignore, Dockerfile
# ---------------------------------------------------------------------------

def test_dockerfile_template_installs_kaggle():
    """templates/Dockerfile must install kaggle as a dedicated pip layer (belt-and-suspenders)."""
    dockerfile = REPO_ROOT / ".claude" / "doml" / "templates" / "Dockerfile"
    content = dockerfile.read_text()
    assert "pip install" in content and "kaggle" in content, (
        "templates/Dockerfile does not install kaggle — "
        "image will lack the kaggle CLI even if requirements.txt is stale"
    )


def test_template_requirements_in_has_kaggle():
    """templates/requirements.in must include kaggle so new projects get it on first pip-compile."""
    tmpl_req_in = REPO_ROOT / ".claude" / "doml" / "templates" / "requirements.in"
    content = tmpl_req_in.read_text()
    kaggle_lines = [l.strip() for l in content.splitlines() if l.strip() == "kaggle"]
    assert kaggle_lines, (
        "templates/requirements.in missing kaggle — "
        "new projects will not include it when pip-compile regenerates requirements.txt"
    )


def test_get_data_workflow_credential_restart_instruction():
    """get-data.md Step 1.5 missing-credential message must include a container restart step."""
    content = GET_DATA_WF.read_text()
    assert "docker compose down" in content or "docker compose restart" in content, (
        "get-data.md credential instructions do not tell the user to restart the container — "
        "a running container will not pick up .env changes without restart"
    )


def test_docker_compose_template_has_kaggle_username():
    """docker-compose.yml template must include KAGGLE_USERNAME env var slot (DATA-01)."""
    content = DOCKER_COMPOSE_TMPL.read_text()
    assert "KAGGLE_USERNAME" in content, (
        "docker-compose.yml template missing KAGGLE_USERNAME env var — "
        "new projects will have no slot to set Kaggle credentials"
    )


def test_docker_compose_template_has_kaggle_key():
    """docker-compose.yml template must include KAGGLE_KEY env var slot (DATA-01)."""
    content = DOCKER_COMPOSE_TMPL.read_text()
    assert "KAGGLE_KEY" in content, (
        "docker-compose.yml template missing KAGGLE_KEY env var — "
        "new projects will have no slot to set Kaggle credentials"
    )


def test_requirements_in_has_kaggle():
    """requirements.in must list kaggle package so it is installed in Docker image (DATA-01)."""
    content = REQUIREMENTS_IN.read_text()
    lines = content.splitlines()
    # Must have a bare 'kaggle' line (not a comment)
    kaggle_lines = [l.strip() for l in lines if l.strip() == "kaggle"]
    assert kaggle_lines, (
        "requirements.in does not contain a 'kaggle' package line — "
        "kaggle CLI will not be installed in the Docker image"
    )


def test_gitignore_has_stage_dir():
    """`.gitignore` must exclude data/raw/.stage/ from git (prevents staging dir from being committed)."""
    content = GITIGNORE.read_text()
    assert "data/raw/.stage/" in content, (
        ".gitignore missing data/raw/.stage/ entry — "
        "staging directory may be accidentally committed to git history"
    )
