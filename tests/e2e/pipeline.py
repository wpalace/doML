"""End-to-end DoML pipeline test: scaffold a project and run every notebook path headlessly.

  python tests/e2e/pipeline.py scaffold KIND DIR   # host side: copy templates, data, planning files
  python tests/e2e/pipeline.py execute  KIND DIR   # run notebooks (inside Docker or a venv)

KIND: regression | classification | clustering | dimensionality_reduction | anomaly | forecasting
The sample data is small, synthetic-but-realistic, and seeded, so runs are repeatable.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
KINDS = ("regression", "classification", "clustering", "dimensionality_reduction", "anomaly", "forecasting")
SEED = 42


def sample_data(kind: str) -> tuple[pd.DataFrame, str | None]:
    rng = np.random.default_rng(SEED)
    n = 400
    if kind == "forecasting":
        idx = pd.date_range("2016-01-01", periods=96, freq="MS")
        t = np.arange(len(idx))
        y = 200 + 2.5 * t + 25 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 6, len(idx))
        promo = rng.integers(0, 2, len(idx))
        return pd.DataFrame({"date": idx, "sales": (y + 15 * promo).round(2), "promo": promo}), "sales"
    region = rng.choice(["north", "south", "east", "west"], n)
    x1, x2, x3 = rng.normal(50, 10, n), rng.gamma(2.0, 3.0, n), rng.uniform(0, 1, n)
    df = pd.DataFrame({"tenure_months": x1.round(1), "spend": x2.round(2), "score": x3.round(3), "region": region})
    if kind == "regression":
        df["revenue"] = (3 * x1 + 8 * x2 + 40 * x3 + (region == "west") * 20 + rng.normal(0, 10, n)).round(2)
        df.loc[rng.choice(n, 20, replace=False), "spend"] = np.nan
        return df, "revenue"
    if kind == "classification":
        logit = 0.08 * (x1 - 50) + 0.25 * (x2 - 6) + 2 * (x3 - 0.5)
        df["churned"] = (rng.uniform(0, 1, n) < 1 / (1 + np.exp(-logit))).astype(int)
        return df, "churned"
    if kind in ("clustering", "dimensionality_reduction"):
        centers = rng.normal(0, 4, (3, 8))
        lab = rng.integers(0, 3, n)
        X = centers[lab] + rng.normal(0, 1, (n, 8))
        out = pd.DataFrame(X.round(3), columns=[f"f{i}" for i in range(8)])
        out["segment_hint"] = np.where(lab == 0, "a", "b")
        return out, None
    if kind == "anomaly":
        X = rng.normal(0, 1, (n, 4))
        X[:12] += rng.normal(6, 1, (12, 4))
        return pd.DataFrame(X.round(3), columns=["temp", "pressure", "flow", "vibration"]), None
    raise ValueError(kind)


PROJECT_MD = """---
project: e2e-{kind}
created: 2026-10-25
last_updated: 2026-10-25
dataset: sample.csv
problem_type: {ptype}
---

# e2e-{kind}

## Business Context

**Business question:** Can we explain and predict the outcome for the {kind} test case?
**Stakeholder:** DoML maintainers
**Expected outcome:** Every notebook path runs end to end.

## Dataset

**Source:** data/raw/sample.csv
**Format:** CSV
**Description:** Seeded synthetic sample for the {kind} path
**Collection period:** 2016-2024
**Known biases or limitations:** Synthetic

## Problem Framing

**ML problem type:** {ptype}
**Target variable:** {target}
**Time factor:** {tf}
"""


def scaffold(kind: str, root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    tpl = REPO / ".claude" / "doml" / "templates"
    for sub in ("data/raw", "data/processed", "data/external", "notebooks", "reports", "models", "src", ".planning"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPO / ".claude" / "doml", root / ".claude" / "doml")
    for f in ("Dockerfile", "compose.yaml", "requirements.txt", "pyproject.toml", "uv.lock"):
        shutil.copy(tpl / f, root / f)
    df, target = sample_data(kind)
    df.to_csv(root / "data" / "raw" / "sample.csv", index=False)
    ptype = {"anomaly": "clustering", "forecasting": "time_series"}.get(kind, kind)
    cfg = json.loads((tpl / "config.json").read_text())
    cfg.update(problem_type=ptype, time_factor=kind == "forecasting", target_column=target)
    cfg["dataset"].update(path="data/raw/sample.csv", format="csv", target_column=target)
    (root / ".planning" / "config.json").write_text(json.dumps(cfg, indent=2))
    (root / ".planning" / "PROJECT.md").write_text(
        PROJECT_MD.format(kind=kind, ptype=ptype, target=target or "none", tf="Yes" if kind == "forecasting" else "No")
    )
    (root / ".planning" / "STATE.md").write_text((tpl / "STATE.md").read_text())
    print(f"scaffolded {kind} project at {root}")


def nb(root: Path, template: str, name: str) -> Path:
    dst = root / "notebooks" / name
    shutil.copy(root / ".claude" / "doml" / "templates" / "notebooks" / template, dst)
    return dst


def run(root: Path, notebook: Path, report: str, *args: str) -> None:
    tool = root / ".claude" / "doml" / "bin" / "doml_nb.py"
    cmd = [sys.executable, str(tool), "run", str(notebook.relative_to(root)), "--report", f"reports/{report}.html"]
    if args:
        cmd += ["--", *args]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=root, check=True, env={**os.environ, "PROJECT_ROOT": str(root)})
    html = (root / "reports" / f"{report}.html").read_text(encoding="utf-8")
    assert "MarimoExceptionRaisedError" not in html, f"{report}: a cell raised"
    assert "not causation" in html.lower() or report == "deployment_report", f"{report}: caveats missing"


def tool(root: Path, *args: str, stdin: str | None = None) -> None:
    t = root / ".claude" / "doml" / "bin" / "doml_nb.py"
    subprocess.run([sys.executable, str(t), *args], cwd=root, check=True, input=stdin, text=True)


def execute(kind: str, root: Path) -> None:
    # Raw data must be immutable inside the container (compose mounts it read-only).
    if os.environ.get("DOML_EXPECT_RO_RAW") == "1":
        try:
            (root / "data" / "raw" / "probe.txt").write_text("x")
        except OSError:
            print("OK: data/raw is read-only")
        else:
            raise AssertionError("data/raw is writable inside the container")

    b = nb(root, "business_understanding.py", "01_business_understanding.py")
    tool(root, "narrative", str(b.relative_to(root)), "summary", stdin="## Executive Summary\n\nE2E_SUMMARY_MARKER\n")
    run(root, b, "business_summary")
    assert "E2E_SUMMARY_MARKER" in (root / "reports" / "business_summary.html").read_text()
    run(root, nb(root, "data_understanding.py", "02_data_understanding.py"), "eda_report")
    assert list((root / "data" / "processed").glob("*.csv")), "EDA wrote no processed dataset"

    if kind in ("regression", "classification"):
        run(root, nb(root, "preprocessing.py", "03_preprocessing.py"), "preprocessing_report")
        assert list((root / "data" / "processed").glob("preprocessed_*")), "no preprocessed_* file"
        for v in (1, 2):
            m = nb(root, f"modelling_{kind}.py", f"04_modelling_{kind}_v{v}.py")
            if v == 2:  # the /doml-iterate path: direction note + code edit + param override
                rel = str(m.relative_to(root))
                tool(root, "narrative", rel, "direction", stdin="## Iteration Direction\n\nfocus on trials=3\n")
                tool(root, "sub", rel, r"n_trials\s*=\s*\d+", "n_trials=3")
                tool(root, "set-param", rel, "notebook_version", '"v2"')
            run(root, m, f"model_report_v{v}")
        lb = pd.read_csv(root / "models" / "leaderboard.csv")
        assert set(lb["notebook"]) == {f"04_modelling_{kind}_v1", f"04_modelling_{kind}_v2"}, lb["notebook"].unique()
        # Idempotent re-run: executing v1 again replaces its rows, it does not duplicate them.
        run(root, root / "notebooks" / f"04_modelling_{kind}_v1.py", "model_report_v1")
        lb2 = pd.read_csv(root / "models" / "leaderboard.csv")
        assert len(lb2) == len(lb), (len(lb), len(lb2))
        print(f"leaderboard rows: {len(lb)} (stable after re-run)")
        assert (root / "models" / "best_model.pkl").exists() or list((root / "models").glob("*.pkl"))
    elif kind in ("clustering", "dimensionality_reduction"):
        short = "clustering" if kind == "clustering" else "dimreduction"
        for v in (1, 2):
            run(root, nb(root, f"modelling_{short}.py", f"05_modelling_{kind}_v{v}.py"), f"{short}_report_v{v}")
        lb = pd.read_csv(root / "models" / "unsupervised_leaderboard.csv")
        assert sorted(lb["iteration"].unique()) == [1, 2] and set(lb["notebook_version"]) == {"v1", "v2"}
        run(root, root / "notebooks" / f"05_modelling_{kind}_v1.py", f"{short}_report_v1")
        lb2 = pd.read_csv(root / "models" / "unsupervised_leaderboard.csv")
        assert len(lb2) == len(lb) and sorted(lb2["iteration"].unique()) == [1, 2]
        print(f"unsupervised leaderboard rows: {len(lb)} (stable after re-run)")
    elif kind == "anomaly":
        run(root, nb(root, "anomaly_detection.py", "06_anomaly_detection.py"), "anomaly_report")
        assert list((root / "data" / "processed").glob("*anomal*")), "no anomaly flags written"
    elif kind == "forecasting":
        f = nb(root, "forecasting.py", "forecasting.py")
        rel = str(f.relative_to(root))
        tool(root, "set-param", rel, "HORIZON", "12")
        tool(root, "set-param", rel, "TARGET_COL", '"sales"')
        tool(root, "set-param", rel, "REGRESSORS", '"promo"')
        run(root, f, "forecast_report")
        assert (root / "models" / "forecast_leaderboard.csv").exists() or list((root / "models").glob("*leaderboard*"))
    print(f"PASS execute {kind}")


if __name__ == "__main__":
    action, kind, d = sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
    assert kind in KINDS, kind
    {"scaffold": scaffold, "execute": execute}[action](kind, d)
