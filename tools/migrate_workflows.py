"""One-off: rewrite DoML workflow Markdown from Jupyter/nbconvert/nbformat to marimo + doml_nb.py."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOOL = "python .claude/doml/bin/doml_nb.py"
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)


def nb_of(code: str) -> str:
    m = re.search(r'("?\$\{?\w+\}?"?|notebooks/[\w./{}-]+?\.ipynb|\[\w+\])(?=\s*\\?\n|\s*$|\s+--)', code.split("nbconvert", 1)[1])
    return m.group(1).replace(".ipynb", ".py") if m else "NOTEBOOK"


def rewrite_block(lang: str, code: str, reports: dict[str, str]) -> str | None:
    if "nbconvert" in code and "--execute" in code:
        nb = nb_of(code)
        t = re.search(r"timeout=\$?\{?(\w+)\}?", code)
        timeout = ("${" + t.group(1) + "}" if not t.group(1).isdigit() else t.group(1)) if t else "1800"
        env = re.findall(r"-e (\w+=\"[^\"]*\")", code)
        envs = "".join(f" \\\n  -e {e}" for e in env)
        report = reports.get(nb.strip('"'), "reports/$(basename " + nb + " .py).html")
        return (f"docker compose exec{envs} doml \\\n  {TOOL} run {nb} \\\n  --report {report} --timeout {timeout}\n")
    if "nbconvert" in code and "--to html" in code:
        nb = nb_of(code)
        report = reports.get(nb.strip('"'), "reports/REPORT.html")
        return ("# Re-export so the report shows the narrative cells written above.\n"
                "# marimo re-runs the notebook (seeded, so results are identical; leaderboard\n"
                "# rows are replaced, not duplicated).\n"
                f"docker compose exec doml \\\n  {TOOL} run {nb} \\\n  --report {report}\n")
    if "nbformat" in code and ("outputs" in code and "code_cells_with_output" in code):
        nb = re.search(r"open\('([^']+)'\)", code)
        nbp = nb.group(1).replace(".ipynb", ".py") if nb else "NOTEBOOK"
        report = reports.get(nbp.strip("'\"$"), reports.get(nbp, "reports/REPORT.html"))
        return (f"# The run step exits non-zero on any cell error; this re-checks the exported report.\n"
                f"python3 .claude/doml/bin/doml_nb.py verify-report {report}\n")
    if "nbformat" in code and "new_markdown_cell" in code and ("NARRATIVE" in code or "INTERPRETATION" in code or "narrative_text" in code):
        section = "interpretation" if "INTERPRETATION" in code else "summary"
        var = "INTERPRETATION" if section == "interpretation" else "NARRATIVE"
        body = re.search(rf'{var}\s*=\s*"""(.*?)"""', code, re.S)
        text = body.group(1) if body else "[WRITE THE TEXT HERE]"
        if section == "summary" and not text.lstrip().startswith("##"):
            text = "## Executive Summary\n\n" + text
        nb = re.search(r"open\('([^']+)'\)", code)
        nbp = nb.group(1).replace(".ipynb", ".py") if nb else "NOTEBOOK"
        return (f"# Narrative sidecar: the notebook renders notebooks/narratives/<stem>/{section}.md\n"
                f"cat > /tmp/doml_{section}.md <<'DOML_EOF'\n{text.strip()}\nDOML_EOF\n"
                f"python3 .claude/doml/bin/doml_nb.py narrative {nbp} {section} /tmp/doml_{section}.md\n")
    return None


def migrate(path: Path) -> None:
    s = path.read_text(encoding="utf-8")
    reports: dict[str, str] = {}
    for _, code in FENCE.findall(s):
        if "nbconvert" in code and "--to html" in code:
            out = re.search(r"--output[ =]\"?([\w${}]+)\"?", code)
            d = re.search(r"--output-dir[ =](\S+)", code)
            if out:
                reports[nb_of(code).strip('"')] = f"{(d.group(1) if d else 'reports')}/{out.group(1)}.html"
    lang_map = {}

    def repl(m: re.Match) -> str:
        new = rewrite_block(m.group(1), m.group(2), reports)
        if new is None:
            return m.group(0)
        return f"```bash\n{new}```"

    s = FENCE.sub(repl, s)
    subs = [
        (r"\.ipynb\b", ".py"),
        (r"docker compose exec jupyter\b", "docker compose exec doml"),
        (r"docker compose run --rm jupyter\b", "docker compose run --rm doml"),
        (r"docker compose ps jupyter\b", "docker compose ps doml"),
        (r"docker compose ps -q jupyter\b", "docker compose ps -q doml"),
        (r"docker compose cp (\S+) jupyter:", r"docker compose cp \1 doml:"),
        (r"grep -q jupyter\b", "grep -q doml"),
        (r"\n(\s*)jupyter \\\n", r"\n\1doml \\\n"),
        (r"/home/jovyan/work", "/project"),
        (r"[Jj]upyter container", "doml container"),
        (r"JupyterLab", "marimo"),
        (r"Jupyter notebook", "marimo notebook"),
        (r"`nbstripout` pre-commit hook is active — outputs stripped before git commit \(REPR-03\)",
         "Notebooks are plain-Python marimo files: outputs are never stored in git, only in `reports/*.html` (REPR-03)"),
        (r"display the nbconvert error output", "display the cell error output"),
        (r"display the nbconvert error", "display the cell error"),
        (r"the nbformat API", "a plain text edit of the marimo `.py` file (or `doml_nb.py append`)"),
        (r"nbformat", "doml_nb.py"),
    ]
    for a, b in subs:
        s = re.sub(a, b, s)
    path.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        migrate(Path(p))
        print("migrated", p)
