"""Print the ```bash blocks of a DoML workflow, step by step, as one script.

Used by tests/e2e/deploy_paths.sh so the deploy tests run the exact commands that the
workflow Markdown tells the agent to run (no hand-copied duplicates).

Usage: extract_blocks.py WORKFLOW.md [--from STEP] [--to STEP] [--skip STEP ...]
"""

import argparse
import re
import sys
from pathlib import Path

STEP_RE = re.compile(r"^#{2,4} Step (\d+[a-z]?)\b")
FENCE_RE = re.compile(r"^(\s*)```(\w*)\s*$")


def step_num(label: str) -> int:
    return int(re.match(r"\d+", label).group())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workflow", type=Path)
    ap.add_argument("--from", dest="start", type=int, default=0)
    ap.add_argument("--to", dest="end", type=int, default=999)
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--drop", default="", help="comma-separated block indexes to leave out")
    ap.add_argument("--list", action="store_true", help="list bash blocks with their indexes")
    args = ap.parse_args()

    step = "0"
    out: list[str] = []
    in_block = False
    indent = ""
    keep = False
    index = -1
    drop = {int(i) for i in args.drop.split(",") if i}
    for line in args.workflow.read_text().splitlines():
        if not in_block and (m := STEP_RE.match(line)):
            step = m.group(1)
        fence = FENCE_RE.match(line)
        if fence and not in_block:
            in_block, indent = True, fence.group(1)
            if fence.group(2) == "bash":
                index += 1
            keep = (fence.group(2) == "bash" and index not in drop
                    and args.start <= step_num(step) <= args.end
                    and step not in args.skip and str(step_num(step)) not in args.skip)
            if keep:
                out.append(f"# ---- {args.workflow.name} Step {step} block {index}")
            continue
        if fence and in_block:
            in_block = False
            continue
        if in_block and keep:
            out.append(line[len(indent):] if line.startswith(indent) else line)
    if args.list:
        heads = [(l, out[i + 1] if i + 1 < len(out) else "") for i, l in enumerate(out) if l.startswith("# ---- ")]
        out = [f"{h}: {first[:70]}" for h, first in heads]
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
