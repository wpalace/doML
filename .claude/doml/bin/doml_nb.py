#!/usr/bin/env python3
"""doml_nb — small, stdlib-only helper the DoML workflows use to drive marimo notebooks.

It replaces the old nbformat / nbconvert snippets. Notebooks are plain Python, so edits
are text edits; outputs are never stored in the notebook, only in exported HTML reports.

Commands:
  run NOTEBOOK [--report PATH] [--with-code] [--timeout S] [-- ARGS...]
      Execute NOTEBOOK headlessly with `marimo export html`. Exit code 1 if any cell fails.
      Default report: reports/<notebook stem>.html (code hidden, stakeholder view).
  narrative NOTEBOOK SECTION [FILE|-]
      Write Markdown for a narrative cell (summary, direction, interpretation, performance)
      to notebooks/narratives/<stem>/<section>.md. The notebook renders it on the next run.
  set-param NOTEBOOK NAME JSON_VALUE
      Replace the first top-level `NAME = ...` assignment in NOTEBOOK with a JSON literal.
  append NOTEBOOK MARKER FILE|-
      Append code to the end of the cell that contains MARKER (before its `return`).
      Appending inside the defining cell keeps marimo's one-definition-per-name rule.
  sub NOTEBOOK PATTERN REPLACEMENT
      Regex substitution across the notebook text (first match only).
  next-version PATTERN
      Print max(N)+1 over files matching a glob that contains `_v*`, e.g.
      'notebooks/0*_modelling_regression_v*.py'. Prints 1 when nothing matches.
  check NOTEBOOK...
      `marimo check --strict`.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _marimo() -> list[str]:
    exe = shutil.which("marimo")
    return [exe] if exe else [sys.executable, "-m", "marimo"]


def _read(src: str) -> str:
    return sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")


def cmd_run(a: argparse.Namespace) -> int:
    nb = Path(a.notebook)
    report = Path(a.report) if a.report else Path("reports") / f"{nb.stem}.html"
    report.parent.mkdir(parents=True, exist_ok=True)
    cmd = [*_marimo(), "export", "html", str(nb), "-o", str(report), "--force"]
    cmd.append("--include-code" if a.with_code else "--no-include-code")
    if a.args:
        cmd += ["--", *a.args]
    try:
        proc = subprocess.run(cmd, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        print(f"ERROR: {nb} did not finish in {a.timeout}s", file=sys.stderr)
        return 124
    if proc.returncode != 0 or not report.exists():
        print(f"ERROR: {nb} failed (see the cell errors above)", file=sys.stderr)
        return 1
    print(f"OK: {nb} -> {report}")
    return 0


def cmd_narrative(a: argparse.Namespace) -> int:
    nb = Path(a.notebook)
    out = nb.parent / "narratives" / nb.stem / f"{a.section}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_read(a.file), encoding="utf-8")
    print(f"Narrative written: {out}")
    return 0


def cmd_set_param(a: argparse.Namespace) -> int:
    nb = Path(a.notebook)
    text = nb.read_text(encoding="utf-8")
    value = json.loads(a.value)
    literal = repr(value) if not isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    pat = re.compile(rf"^(?P<ind>[ \t]*){re.escape(a.name)}\s*=\s*[^#\n]*(?P<c>#.*)?$", re.M)
    new, n = pat.subn(lambda m: f"{m['ind']}{a.name} = {literal}" + (f"  {m['c']}" if m["c"] else ""), text, count=1)
    if not n:
        print(f"ERROR: no `{a.name} = ...` line in {nb}", file=sys.stderr)
        return 1
    nb.write_text(new, encoding="utf-8")
    print(f"{nb}: {a.name} = {literal}")
    return 0


def cmd_append(a: argparse.Namespace) -> int:
    nb = Path(a.notebook)
    text = nb.read_text(encoding="utf-8")
    cells = list(re.finditer(r"^@app\.cell.*?(?=^@app\.cell|^if __name__|\Z)", text, re.M | re.S))
    target = next((c for c in cells if a.marker in c.group(0)), None)
    if target is None:
        print(f"ERROR: no cell contains {a.marker!r}", file=sys.stderr)
        return 1
    body = target.group(0)
    ret = list(re.finditer(r"^    return\b.*$", body, re.M))
    if not ret:
        print("ERROR: target cell has no return statement", file=sys.stderr)
        return 1
    # Indent to the cell's body level; a `with mo.redirect_stdout():` cell needs 8 spaces.
    indent = "        " if re.search(r"^    with mo\.redirect_stdout\(\):", body, re.M) else "    "
    code = "".join(indent + ln if ln.strip() else "\n" for ln in _read(a.file).splitlines(keepends=True))
    if not code.endswith("\n"):
        code += "\n"
    at = ret[-1].start()
    body = body[:at] + code + body[at:]
    nb.write_text(text[: target.start()] + body + text[target.end():], encoding="utf-8")
    # Let marimo refresh the cell signatures (refs/defs) after the edit.
    subprocess.run([*_marimo(), "check", "--fix", str(nb)], capture_output=True)
    print(f"Appended code to the cell containing {a.marker!r} in {nb}")
    return 0


def cmd_sub(a: argparse.Namespace) -> int:
    nb = Path(a.notebook)
    text = nb.read_text(encoding="utf-8")
    new, n = re.subn(a.pattern, a.replacement, text, count=1)
    if not n:
        print(f"WARNING: pattern not found: {a.pattern}", file=sys.stderr)
        return 2
    nb.write_text(new, encoding="utf-8")
    return 0


def cmd_next_version(a: argparse.Namespace) -> int:
    vs = [int(m.group(1)) for f in glob.glob(a.pattern) if (m := re.search(r"_v(\d+)\.py$", f))]
    print(max(vs) + 1 if vs else 1)
    return 0


def cmd_check(a: argparse.Namespace) -> int:
    return subprocess.run([*_marimo(), "check", "--strict", *a.notebooks]).returncode


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="doml_nb", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("notebook")
    r.add_argument("--report")
    r.add_argument("--with-code", action="store_true")
    r.add_argument("--timeout", type=int, default=1800)
    n = sub.add_parser("narrative")
    n.add_argument("notebook")
    n.add_argument("section")
    n.add_argument("file", nargs="?", default="-")
    s = sub.add_parser("set-param")
    s.add_argument("notebook")
    s.add_argument("name")
    s.add_argument("value")
    ap = sub.add_parser("append")
    ap.add_argument("notebook")
    ap.add_argument("marker")
    ap.add_argument("file", nargs="?", default="-")
    sb = sub.add_parser("sub")
    sb.add_argument("notebook")
    sb.add_argument("pattern")
    sb.add_argument("replacement")
    nv = sub.add_parser("next-version")
    nv.add_argument("pattern")
    c = sub.add_parser("check")
    c.add_argument("notebooks", nargs="+")
    argv = list(sys.argv[1:] if argv is None else argv)
    extra: list[str] = []
    if "--" in argv:  # everything after `--` goes to the notebook (mo.cli_args())
        i = argv.index("--")
        argv, extra = argv[:i], argv[i + 1 :]
    a = p.parse_args(argv)
    a.args = extra
    return {
        "run": cmd_run, "narrative": cmd_narrative, "set-param": cmd_set_param,
        "append": cmd_append, "sub": cmd_sub, "next-version": cmd_next_version, "check": cmd_check,
    }[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
