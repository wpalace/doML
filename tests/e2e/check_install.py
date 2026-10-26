"""Verify a tree produced by install.sh / install.ps1 for one target.

Usage: check_install.py claude|copilot DIR
"""

import sys
from pathlib import Path

NOTEBOOKS = {
    "anomaly_detection", "business_understanding", "data_understanding", "deployment_report",
    "forecasting", "modelling_classification", "modelling_clustering", "modelling_dimreduction",
    "modelling_regression", "preprocessing",
}


def main() -> int:
    target, root = sys.argv[1], Path(sys.argv[2])
    base = root / (".claude" if target == "claude" else ".github")
    doml = base / "doml"
    errors: list[str] = []

    def need(path: Path) -> None:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(root)}")

    for rel in ("bin/doml_nb.py", "templates/Dockerfile", "templates/compose.yaml",
                "templates/pyproject.toml", "templates/uv.lock", "templates/requirements.txt",
                "templates/config.json", "workflows/new-project.md", "workflows/get-data.md"):
        need(doml / rel)
    found = {p.stem for p in (doml / "templates" / "notebooks").glob("*.py")}
    if found != NOTEBOOKS:
        errors.append(f"notebooks differ: missing {NOTEBOOKS - found}, extra {found - NOTEBOOKS}")
    if list((doml / "templates").rglob("*.ipynb")):
        errors.append("an .ipynb template was installed")
    skills = sorted((base / "skills").glob("doml-*/SKILL.md"))
    if len(skills) < 14:
        errors.append(f"only {len(skills)} skills installed")
    for d in ("data/raw", "data/processed", "data/external", "notebooks", "reports", "models"):
        need(root / d)

    if target == "claude":
        need(root / "CLAUDE.md")
    else:
        need(root / "AGENTS.md")
        need(base / "copilot-instructions.md")
        # Copilot has no .claude/ tree: no installed file may point into it.
        for path in base.rglob("*"):
            if path.is_file() and ".claude/doml" in path.read_text(errors="ignore"):
                errors.append(f".claude/doml reference in {path.relative_to(root)}")
        if ".claude/doml" in (root / "AGENTS.md").read_text():
            errors.append(".claude/doml reference in AGENTS.md")
        if (root / ".claude").exists():
            errors.append("copilot target created .claude/")

    for e in errors:
        print(f"FAIL {e}")
    print(f"{'PASS' if not errors else 'FAIL'} install {target}: {len(skills)} skills, "
          f"{len(found)} notebooks")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
