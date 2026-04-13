"""Tests for Phase 08 — Named Commands (CMD-10, CMD-11, CMD-12)

Verifies that:
- The three new SKILL.md files exist with correct names
- The three workflow files are self-contained (no execute-phase.md dependency)
- Workflow files contain required parameter and routing patterns
- Old skill directories and workflow files have been deleted
- CLAUDE.md contains no references to old command names
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Gap 1: CMD-10 / 08-01 — BU SKILL.md exists with correct name
# ---------------------------------------------------------------------------

def test_business_understanding_skill_file_exists():
    """SKILL.md for doml-business-understanding must exist."""
    skill_path = REPO_ROOT / ".claude" / "skills" / "doml-business-understanding" / "SKILL.md"
    assert skill_path.exists(), (
        f"Expected SKILL.md at {skill_path} — doml-business-understanding skill not created"
    )


def test_business_understanding_skill_has_correct_name():
    """SKILL.md must declare name: doml-business-understanding."""
    skill_path = REPO_ROOT / ".claude" / "skills" / "doml-business-understanding" / "SKILL.md"
    content = skill_path.read_text()
    assert "name: doml-business-understanding" in content, (
        "SKILL.md does not contain 'name: doml-business-understanding' in frontmatter"
    )


# ---------------------------------------------------------------------------
# Gap 2: CMD-10 / 08-01 — business-understanding.md contains no execute-phase refs
# ---------------------------------------------------------------------------

def test_business_understanding_workflow_exists():
    """business-understanding.md workflow file must exist."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "business-understanding.md"
    assert wf_path.exists(), (
        f"Expected workflow at {wf_path} — business-understanding.md not created"
    )


def test_business_understanding_workflow_no_execute_phase_dependency():
    """business-understanding.md must not reference execute-phase.md as a dependency."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "business-understanding.md"
    content = wf_path.read_text()
    # Must not import/reference the old monolithic workflow file
    assert "execute-phase.md" not in content, (
        "business-understanding.md still references execute-phase.md — workflow is not self-contained"
    )
    assert "doml-execute-phase" not in content, (
        "business-understanding.md still references /doml-execute-phase — user-facing messages not updated"
    )


# ---------------------------------------------------------------------------
# Gap 3: CMD-10 / 08-01 — business-understanding.md contains --guidance handling
# ---------------------------------------------------------------------------

def test_business_understanding_workflow_has_guidance_parameter():
    """business-understanding.md must handle the optional --guidance parameter."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "business-understanding.md"
    content = wf_path.read_text()
    # Either the literal flag or the GUIDANCE variable must appear
    has_guidance = "--guidance" in content or "GUIDANCE" in content
    assert has_guidance, (
        "business-understanding.md contains no --guidance or GUIDANCE handling"
    )


# ---------------------------------------------------------------------------
# Gap 4: CMD-11 / 08-02 — DU SKILL.md exists with correct name
# ---------------------------------------------------------------------------

def test_data_understanding_skill_file_exists():
    """SKILL.md for doml-data-understanding must exist."""
    skill_path = REPO_ROOT / ".claude" / "skills" / "doml-data-understanding" / "SKILL.md"
    assert skill_path.exists(), (
        f"Expected SKILL.md at {skill_path} — doml-data-understanding skill not created"
    )


def test_data_understanding_skill_has_correct_name():
    """SKILL.md must declare name: doml-data-understanding."""
    skill_path = REPO_ROOT / ".claude" / "skills" / "doml-data-understanding" / "SKILL.md"
    content = skill_path.read_text()
    assert "name: doml-data-understanding" in content, (
        "SKILL.md does not contain 'name: doml-data-understanding' in frontmatter"
    )


# ---------------------------------------------------------------------------
# Gap 5: CMD-11 / 08-02 — data-understanding.md contains no execute-phase refs
# ---------------------------------------------------------------------------

def test_data_understanding_workflow_exists():
    """data-understanding.md workflow file must exist."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "data-understanding.md"
    assert wf_path.exists(), (
        f"Expected workflow at {wf_path} — data-understanding.md not created"
    )


def test_data_understanding_workflow_no_execute_phase_dependency():
    """data-understanding.md must not reference execute-phase.md as a dependency."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "data-understanding.md"
    content = wf_path.read_text()
    assert "execute-phase.md" not in content, (
        "data-understanding.md still references execute-phase.md — workflow is not self-contained"
    )
    assert "doml-execute-phase" not in content, (
        "data-understanding.md still references /doml-execute-phase — user-facing messages not updated"
    )


# ---------------------------------------------------------------------------
# Gap 6: CMD-12 / 08-03 — Modelling SKILL.md exists with correct name
# ---------------------------------------------------------------------------

def test_modelling_skill_file_exists():
    """SKILL.md for doml-modelling must exist."""
    skill_path = REPO_ROOT / ".claude" / "skills" / "doml-modelling" / "SKILL.md"
    assert skill_path.exists(), (
        f"Expected SKILL.md at {skill_path} — doml-modelling skill not created"
    )


def test_modelling_skill_has_correct_name():
    """SKILL.md must declare name: doml-modelling."""
    skill_path = REPO_ROOT / ".claude" / "skills" / "doml-modelling" / "SKILL.md"
    content = skill_path.read_text()
    assert "name: doml-modelling" in content, (
        "SKILL.md does not contain 'name: doml-modelling' in frontmatter"
    )


# ---------------------------------------------------------------------------
# Gap 7: CMD-12 / 08-03 — modelling.md routes all 4 problem types, no execute-phase refs
# ---------------------------------------------------------------------------

def test_modelling_workflow_exists():
    """modelling.md workflow file must exist."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "modelling.md"
    assert wf_path.exists(), (
        f"Expected workflow at {wf_path} — modelling.md not created"
    )


def test_modelling_workflow_no_execute_phase_dependency():
    """modelling.md must not reference execute-phase.md as a dependency."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "modelling.md"
    content = wf_path.read_text()
    assert "execute-phase.md" not in content, (
        "modelling.md still references execute-phase.md — workflow is not self-contained"
    )
    assert "doml-execute-phase" not in content, (
        "modelling.md still references /doml-execute-phase — user-facing messages not updated"
    )


def test_modelling_workflow_routes_regression():
    """modelling.md must handle the regression problem type."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "modelling.md"
    content = wf_path.read_text()
    assert "regression" in content, (
        "modelling.md does not mention 'regression' — supervised routing incomplete"
    )


def test_modelling_workflow_routes_classification():
    """modelling.md must handle the classification problem type."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "modelling.md"
    content = wf_path.read_text()
    assert "classification" in content, (
        "modelling.md does not mention 'classification' — supervised routing incomplete"
    )


def test_modelling_workflow_routes_clustering():
    """modelling.md must handle the clustering problem type."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "modelling.md"
    content = wf_path.read_text()
    assert "clustering" in content, (
        "modelling.md does not mention 'clustering' — unsupervised routing incomplete"
    )


def test_modelling_workflow_routes_dimensionality_reduction():
    """modelling.md must handle the dimensionality_reduction problem type."""
    wf_path = REPO_ROOT / ".claude" / "doml" / "workflows" / "modelling.md"
    content = wf_path.read_text()
    assert "dimensionality_reduction" in content, (
        "modelling.md does not mention 'dimensionality_reduction' — unsupervised routing incomplete"
    )


# ---------------------------------------------------------------------------
# Gap 8: CMD-10/11/12 / 08-04 — Old skill directories do NOT exist
# ---------------------------------------------------------------------------

def test_old_execute_phase_skill_directory_deleted():
    """Old doml-execute-phase skill directory must not exist after Phase 8 cleanup."""
    old_dir = REPO_ROOT / ".claude" / "skills" / "doml-execute-phase"
    assert not old_dir.exists(), (
        f"Old skill directory still exists at {old_dir} — Phase 8 cleanup did not complete"
    )


def test_old_plan_phase_skill_directory_deleted():
    """Old doml-plan-phase skill directory must not exist after Phase 8 cleanup."""
    old_dir = REPO_ROOT / ".claude" / "skills" / "doml-plan-phase"
    assert not old_dir.exists(), (
        f"Old skill directory still exists at {old_dir} — Phase 8 cleanup did not complete"
    )


# ---------------------------------------------------------------------------
# Gap 9: CMD-10/11/12 / 08-04 — Old workflow files do NOT exist
# ---------------------------------------------------------------------------

def test_old_execute_phase_workflow_deleted():
    """Old execute-phase.md workflow must not exist after Phase 8 cleanup."""
    old_wf = REPO_ROOT / ".claude" / "doml" / "workflows" / "execute-phase.md"
    assert not old_wf.exists(), (
        f"Old workflow still exists at {old_wf} — Phase 8 cleanup did not complete"
    )


def test_old_plan_phase_workflow_deleted():
    """Old plan-phase.md workflow must not exist after Phase 8 cleanup."""
    old_wf = REPO_ROOT / ".claude" / "doml" / "workflows" / "plan-phase.md"
    assert not old_wf.exists(), (
        f"Old workflow still exists at {old_wf} — Phase 8 cleanup did not complete"
    )


# ---------------------------------------------------------------------------
# Gap 10: CMD-10/11/12 / 08-04 — CLAUDE.md contains no references to old commands
# ---------------------------------------------------------------------------

def test_claude_md_no_execute_phase_reference():
    """CLAUDE.md must not reference /doml-execute-phase after Phase 8 cleanup."""
    claude_md = REPO_ROOT / "CLAUDE.md"
    content = claude_md.read_text()
    assert "doml-execute-phase" not in content, (
        "CLAUDE.md still references doml-execute-phase — DoML Framework section not updated"
    )


def test_claude_md_no_plan_phase_reference():
    """CLAUDE.md must not reference /doml-plan-phase after Phase 8 cleanup."""
    claude_md = REPO_ROOT / "CLAUDE.md"
    content = claude_md.read_text()
    assert "doml-plan-phase" not in content, (
        "CLAUDE.md still references doml-plan-phase — DoML Framework section not updated"
    )
