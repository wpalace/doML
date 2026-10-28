"""Summary tables in static HTML reports embed every row in a vertically scrollable table.

marimo's default table embeds only its first page (10 rows) in `marimo export html`.
Each DoML template defines `table()` in its narrative-helper cell; this checks that the
helper exists in every template and that an exported report holds all rows of a table.
"""

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / ".claude/doml/templates/notebooks"
NOTEBOOKS = sorted(TEMPLATES.glob("*.py"))


def _helper_source(nb: Path) -> str:
    tree = ast.parse(nb.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "table":
            return ast.get_source_segment(nb.read_text(encoding="utf-8"), node)
    raise AssertionError(f"{nb.name}: no table() helper")


@pytest.mark.parametrize("nb", NOTEBOOKS, ids=lambda p: p.name)
def test_every_template_defines_and_exports_table(nb: Path) -> None:
    src = nb.read_text(encoding="utf-8")
    _helper_source(nb)
    tree = ast.parse(src)
    exported = [
        ast.unparse(fn.body[-1].value)
        for fn in tree.body
        if isinstance(fn, ast.FunctionDef) and any(
            isinstance(n, ast.FunctionDef) and n.name == "table" for n in fn.body)
    ]
    assert exported and "table" in exported[0], f"{nb.name}: table() not exported from helper cell"


@pytest.mark.parametrize("nb", NOTEBOOKS, ids=lambda p: p.name)
def test_dataframe_outputs_go_through_table(nb: Path) -> None:
    # Bare DataFrame-like outputs (a name or subscript passed to mo.output.append) must be wrapped.
    tree = ast.parse(nb.read_text(encoding="utf-8"))
    bad = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and ast.unparse(node.func) == "mo.output.append"
                and node.args and isinstance(node.args[0], ast.Name | ast.Subscript)
                and not ast.unparse(node.args[0]).startswith("fig")):
            bad.append(f"line {node.lineno}: {ast.unparse(node.args[0])}")
    assert not bad, f"{nb.name}: unwrapped table outputs: {bad}"


def _export(tmp_path: Path, nrows: int, max_rows: int = 200) -> str:
    helper = _helper_source(TEMPLATES / "data_understanding.py")
    body = "\n".join("    " + line[4:] if line.startswith("    ") else "    " + line
                     for line in helper.splitlines())
    nb = tmp_path / "nb.py"
    nb.write_text(f'''import marimo
app = marimo.App()

@app.cell
def _():
    import marimo as mo
    import pandas as pd
{body}
    df = pd.DataFrame({{"row_id": [f"ROWMARK{{i:04d}}" for i in range({nrows})], "v": range({nrows})}})
    mo.output.append(table(df, max_rows={max_rows}))
    return

if __name__ == "__main__":
    app.run()
''', encoding="utf-8")
    out = tmp_path / "nb.html"
    marimo = shutil.which("marimo") or str(Path(sys.executable).with_name("marimo"))
    subprocess.run([marimo, "export", "html", str(nb), "-o", str(out), "--no-include-code"],
                   check=True, capture_output=True, timeout=300)
    return out.read_text(encoding="utf-8")


@pytest.mark.skipif(not (shutil.which("marimo") or Path(sys.executable).with_name("marimo").exists()),
                    reason="marimo not installed")
def test_export_embeds_all_rows_scrollable(tmp_path: Path) -> None:
    html = _export(tmp_path, 27)
    for i in range(27):
        assert f"ROWMARK{i:04d}" in html, f"row {i} missing from export"
    assert "Showing the first 10" not in html
    assert "max-height" in html or "&quot;max-height&quot;" in html


@pytest.mark.skipif(not (shutil.which("marimo") or Path(sys.executable).with_name("marimo").exists()),
                    reason="marimo not installed")
def test_export_caps_huge_tables(tmp_path: Path) -> None:
    html = _export(tmp_path, 60, max_rows=25)
    assert "ROWMARK0024" in html and "ROWMARK0025" not in html
    assert "Showing the first 25 of 60 rows" in html
    # The note is above the table.
    assert html.index("Showing the first 25") < html.index("ROWMARK0000")


@pytest.mark.skipif(not (shutil.which("marimo") or Path(sys.executable).with_name("marimo").exists()),
                    reason="marimo not installed")
def test_export_respects_marimo_page_size_cap(tmp_path: Path) -> None:
    # marimo rejects page_size > 200; a larger max_rows is clamped to 200.
    html = _export(tmp_path, 250, max_rows=1000)
    assert "ROWMARK0199" in html and "ROWMARK0200" not in html
    assert "Showing the first 200 of 250 rows" in html


def test_helper_default_and_cap_are_200() -> None:
    for nb in NOTEBOOKS:
        src = _helper_source(nb)
        assert "max_rows=200" in src and "min(int(max_rows), 200)" in src, nb.name
