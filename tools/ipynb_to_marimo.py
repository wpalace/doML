"""One-off migration tool: convert DoML Jupyter templates (.ipynb) to marimo (.py).

Kept in the repo for provenance (branch `marimo`). It is not used at runtime.

Steps per notebook:
1. Rewrite each Python code cell so it renders in marimo exports:
   - drop IPython.display imports
   - display(Markdown(x)) -> mo.output.append(mo.md(x)); display(x) -> mo.output.append(x)
   - IPyImage(path) -> mo.image(src=path)
   - plt.show() -> append the current figure, then close it; fig.show() -> append fig
   - a trailing bare expression -> mo.output.append(expr)
   - cells that print are wrapped in `with mo.redirect_stdout():` so stdout lands
     in the cell output (and therefore in the exported HTML report)
   - PROJECT_ROOT falls back to the notebook's parent directory, not /home/jovyan/work
2. Run `marimo convert` (it resolves cell refs/defs and makes loop variables cell-private).
3. Add narrative cells (executive summary, iteration direction, interpretation) that
   read Markdown sidecar files written by the DoML workflows.
"""

from __future__ import annotations

import ast
import io
import json
import re
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

OLD_ROOT = re.compile(r"""os\.environ\.get\((['"])PROJECT_ROOT\1,\s*(['"])/home/jovyan/work\2\)""")
NEW_ROOT = "os.environ.get('PROJECT_ROOT', str(mo.notebook_dir().parent))"


def _string_continuation_lines(src: str) -> set[int]:
    """Return 1-based line numbers that sit inside a multi-line string (after its first line)."""
    inside: set[int] = set()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.STRING, getattr(tokenize, "FSTRING_MIDDLE", -1), getattr(tokenize, "FSTRING_END", -1)):
            start, end = tok.start[0], tok.end[0]
            inside.update(range(start + 1, end + 1))
    return inside


def _is_output_call(node: ast.expr) -> bool:
    if not isinstance(node, ast.Call):
        return False
    text = ast.unparse(node.func)
    return text in {"print", "mo.output.append", "mo.output.replace"} or text.startswith(("plt.", "warnings."))


def transform_code(src: str) -> str:
    # R support is removed: no `language` setting remains in config.json.
    src = re.sub(r"^[^\n]*config\.get\('language'[^\n]*\n?", "", src, flags=re.M)
    src = re.sub(r"^[ \t]*from IPython\.display import [^\n]*\n?", "", src, flags=re.M)
    src = re.sub(r"^[ \t]*import IPython[^\n]*\n?", "", src, flags=re.M)
    src = OLD_ROOT.sub(NEW_ROOT, src)
    src = src.replace("display(Markdown(", "mo.output.append(mo.md(")
    src = src.replace("display(HTML(", "mo.output.append(mo.Html(")
    src = re.sub(r"IPyImage\(", "mo.image(src=", src)
    src = re.sub(r"(?<![\w.])display\(", "mo.output.append(", src)
    src = re.sub(r"(?<![\w.])plt\.show\(\)", "mo.output.append(plt.gcf()); plt.close()", src)
    src = re.sub(r"(?<![\w.])(\w+)\.show\(\)", r"mo.output.append(\1)", src)

    tree = ast.parse(src)
    if tree.body and isinstance(tree.body[-1], ast.Expr) and not _is_output_call(tree.body[-1].value):
        last = tree.body[-1]
        lines = src.splitlines()
        seg = "\n".join(lines[last.lineno - 1 : last.end_lineno])
        lines[last.lineno - 1 : last.end_lineno] = [f"mo.output.append({seg.strip()})"]
        src = "\n".join(lines)

    if re.search(r"(?<![\w.])print\(", src):
        keep = _string_continuation_lines(src)
        body = [
            line if (i in keep or not line.strip()) else "    " + line
            for i, line in enumerate(src.splitlines(), start=1)
        ]
        src = "with mo.redirect_stdout():\n" + "\n".join(body)
    ast.parse(src)  # fail fast on a bad rewrite
    return src


NARRATIVE_HELPER = '''

@app.cell(hide_code=True)
def _(mo):
    # DoML narrative sidecars: notebooks/narratives/<notebook stem>/<section>.md
    # The DoML workflows write these files (executive summary, interpretation, ...).
    # Editing a sidecar never changes code, so the analysis stays reproducible.
    from pathlib import Path as _Path

    def narrative(section, placeholder=""):
        _p = mo.notebook_dir() / "narratives" / _Path(__file__).stem / f"{section}.md"
        if _p.exists():
            return mo.md(_p.read_text(encoding="utf-8"))
        return mo.md(placeholder) if placeholder else mo.md("")

    return (narrative,)
'''


def narrative_cell(section: str, placeholder: str = "") -> str:
    ph = json.dumps(placeholder, ensure_ascii=False)
    return f'''

@app.cell(hide_code=True)
def _(narrative):
    narrative("{section}", {ph})
    return
'''


def postprocess(py: str, name: str, md_cells: list[str]) -> str:
    cells = re.split(r"\n(?=\n@app\.cell)", py)
    # cells[0] is the header (import marimo / app = ...); cells[1] is `import marimo as mo`
    out: list[str] = [cells[0], cells[1], NARRATIVE_HELPER.rstrip("\n")]
    is_modelling = name.startswith(("modelling_", "anomaly", "forecasting"))
    placed_interp = False
    for i, cell in enumerate(cells[2:]):
        if "## Interpretation & Recommendations" in cell or "## Performance Summary" in cell:
            section = "performance" if "Performance Summary" in cell else "interpretation"
            text = next((m for m in md_cells if m.lstrip().startswith(("## Interpretation", "## Performance Summary"))), "")
            out.append(narrative_cell(section, text).rstrip("\n"))
            placed_interp = True
            continue
        out.append(cell)
        if i == 0:  # title cell -> summary (+ direction) directly below
            out.append(narrative_cell("summary").rstrip("\n"))
            if is_modelling:
                out.append(narrative_cell("direction").rstrip("\n"))
    if not placed_interp:
        tail = out.pop()  # keep the `if __name__` footer last
        out.append(narrative_cell("interpretation").rstrip("\n"))
        out.append(tail)
    return "\n".join(out) + ("\n" if not out[-1].endswith("\n") else "")


class _Scope(ast.NodeVisitor):
    """Collect cell-global defs and every Name occurrence (position, is_load)."""

    def __init__(self) -> None:
        self.defs: set[str] = set()
        self.names: list[tuple[int, int, str, bool]] = []
        self._depth = 0

    def _bind(self, name: str) -> None:
        if self._depth == 0:
            self.defs.add(name)

    def visit_Name(self, node: ast.Name) -> None:
        load = isinstance(node.ctx, ast.Load)
        self.names.append((node.lineno, node.col_offset, node.id, load))
        if not load:
            self._bind(node.id)

    def visit_Assign(self, node: ast.Assign) -> None:
        # Evaluation order: the right-hand side is read before the targets are bound.
        self.visit(node.value)
        for t in node.targets:
            self.visit(t)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name):
            self.names.append((node.target.lineno, node.target.col_offset, node.target.id, True))
            self._bind(node.target.id)
        self.visit(node.value)

    def visit_Import(self, node: ast.Import | ast.ImportFrom) -> None:
        for a in node.names:
            self._bind((a.asname or a.name).split(".")[0])

    visit_ImportFrom = visit_Import

    def _scoped(self, node: ast.AST) -> None:
        name = getattr(node, "name", None)
        if name:
            self._bind(name)
            self.names.append((node.lineno, node.col_offset, name, False))
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = visit_Lambda = _scoped
    visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = _scoped


def _scan(src: str) -> _Scope:
    sc = _Scope()
    sc.visit(ast.parse(src))  # names stay in evaluation order
    return sc


def _rename_tokens(src: str, old: str, new: str) -> str:
    """Rename a variable at token level so comments and layout are preserved."""
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    lines = src.splitlines(keepends=True)
    edits = []
    depth = 0
    for i, t in enumerate(toks):
        if t.type == tokenize.OP and t.string in "([{":
            depth += 1
        elif t.type == tokenize.OP and t.string in ")]}":
            depth -= 1
        if t.type != tokenize.NAME or t.string != old:
            continue
        prev = toks[i - 1].string if i else ""
        nxt = toks[i + 1].string if i + 1 < len(toks) else ""
        if prev == "." or (depth > 0 and nxt == "=" and prev in {"(", ","}):
            continue
        edits.append(t.start)
    for row, col in reversed(edits):
        line = lines[row - 1]
        lines[row - 1] = line[:col] + new + line[col + len(old):]
    return "".join(lines)


def privatize_locals(sources: list[str]) -> list[str]:
    """Make re-defined, cell-local names private (`_x`) the way marimo expects.

    marimo forbids defining one global name in two cells. In Jupyter that is common
    (loop variables, fig/ax, temporaries). When no other cell reads a cell's
    definition, renaming it to `_name` inside that cell is behaviour-preserving.
    Remaining true conflicts are left for `marimo convert`.
    """
    scans = [_scan(s) for s in sources]
    defs_by_cell = [sc.defs for sc in scans]
    out = list(sources)
    all_names = set().union(*defs_by_cell) if defs_by_cell else set()
    for var in sorted(all_names):
        cells = [i for i, d in enumerate(defs_by_cell) if var in d]
        if len(cells) < 2:
            continue
        for k, c in enumerate(cells):
            nxt = cells[k + 1] if k + 1 < len(cells) else len(sources)
            read_later = any(
                any(n == var and load for _, _, n, load in scans[j].names) for j in range(c + 1, nxt)
            )
            occ = [o for o in scans[c].names if o[2] == var]
            reads_outer = bool(occ) and occ[0][3]
            if not read_later and not reads_outer:
                out[c] = _rename_tokens(out[c], var, "_" + var)
    return out


def convert(src: Path, dst: Path) -> None:
    nb = json.loads(src.read_text(encoding="utf-8"))
    md_cells = []
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    for c, new in zip(code, privatize_locals(["".join(c["source"]) for c in code])):
        c["source"] = new
    for cell in nb["cells"]:
        text = "".join(cell["source"])
        if cell["cell_type"] == "code":
            cell["source"] = transform_code(text)
        else:
            text = re.sub(r"^> \*\*Note:\*\* This notebook uses Python regardless[^\n]*\n(> [^\n]*R equivalents\.\n?)?", "", text, flags=re.M)
            cell["source"] = text
            md_cells.append(text)
        cell.pop("outputs", None) if cell["cell_type"] != "code" else cell.update(outputs=[], execution_count=None)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_nb = Path(tmp) / src.name
        tmp_nb.write_text(json.dumps(nb), encoding="utf-8")
        subprocess.run(["marimo", "convert", str(tmp_nb), "-o", str(dst)], check=True, capture_output=True)
    py = dst.read_text(encoding="utf-8")
    py = py.replace("app = marimo.App()", 'app = marimo.App(width="medium")')
    dst.write_text(postprocess(py, src.stem, md_cells), encoding="utf-8")
    subprocess.run(["marimo", "check", "--fix", str(dst)], check=False, capture_output=True)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        out = p.with_name(p.stem.removesuffix("_python") + ".py")
        convert(p, out)
        print(f"converted {p} -> {out}")
