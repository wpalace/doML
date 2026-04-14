# Phase 14: CLI Binary Target — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 14-cli-binary-target
**Areas discussed:** Binary packaging, Input schema, --help example values, Classification output, Batch output format, Build container

---

## Binary Packaging (--onedir vs --onefile)

| Option | Description | Selected |
|--------|-------------|----------|
| --onedir | Produces dist/predict/ directory with predict executable inside. Faster startup, more reliable. Roadmap spec. | ✓ |
| --onefile | Single dist/predict executable. Simpler to share, ~2-5 second cold start from /tmp extraction. | |
| --onedir + zip step | Build --onedir, then zip dist/predict/ into dist/predict.tar.gz for distribution. | |

**User's choice:** --onedir
**Notes:** Success criteria SC-3 and SC-4 verify `dist/predict/predict` (the executable inside the directory, not just the directory itself).

---

## Input Schema

| Option | Description | Selected |
|--------|-------------|----------|
| Preprocessed schema | Accepts data matching preprocessed_* format. sklearn Pipeline handles encoding/scaling. | ✓ |
| Truly raw input | Accepts data/raw/ format. Binary must replicate Phase 2 cleaning steps. Significantly more complex. | |

**User's choice:** Preprocessed schema
**Notes:** User's initial instinct was "raw data as it came in." Discussion clarified the distinction between truly raw data (pre-EDA) and preprocessed data (post-cleaning, pre-sklearn encoding). Preprocessed-schema is what the sklearn Pipeline expects — simpler and reliable. Phase 2 cleaning is the user's responsibility before feeding new data to the binary.

---

## --help Example Values

| Option | Description | Selected |
|--------|-------------|----------|
| Embed at generation time | Read first row of preprocessed_*.csv when predict.py is generated; hardcode into argparse help. | ✓ |
| Read at runtime | Binary reads preprocessed_*.csv at runtime. Adds file dependency not present on target. | |
| Placeholder strings | Generic placeholders (e.g. 'example: 1.23'). No data dependency, less useful. | |

**User's choice:** Embed at generation time
**Notes:** Input schema decision (preprocessed) naturally resolved the example values source — first row of preprocessed_*.csv. Examples are hardcoded into predict.py at generation time so the binary is fully self-contained.

---

## Classification Output

| Option | Description | Selected |
|--------|-------------|----------|
| Label only | {"prediction": "class_a"}. Simple, consistent with regression/clustering. | |
| Label + probabilities | {"prediction": "class_a", "probabilities": {"class_a": 0.85, "class_b": 0.15}}. More useful for downstream thresholding. | ✓ |
| You decide | Claude picks label only unless calibration metadata signals otherwise. | |

**User's choice:** Label + probabilities
**Notes:** Uses both Pipeline.predict() and Pipeline.predict_proba(). Probabilities useful for calibration and downstream decision thresholding.

---

## Batch Output Format

| Option | Description | Selected |
|--------|-------------|----------|
| Input columns + prediction column | CSV mirrors input with prediction appended (+ prob_<class> columns for classification). | ✓ |
| Predictions only | Output file contains only prediction column. Harder to trace rows. | |
| JSON array | Array of {"prediction": ...} objects. Matches single-prediction JSON style. | |

**User's choice:** Input columns + prediction column (CSV)
**Notes:** For classification, one `prob_<class>` column per class is appended alongside the `prediction` column.

---

## Build Container

| Option | Description | Selected |
|--------|-------------|----------|
| Existing jupyter container | docker compose exec jupyter pyinstaller. sklearn/joblib already installed. No new image. | ✓ |
| Slim Python build image | Separate Dockerfile.build. Smaller binary but more build complexity. | |

**User's choice:** Existing jupyter container
**Notes:** Build invoked via `docker compose exec jupyter bash -c "cd src/<modelname>/vN && pyinstaller predict.spec"`. Binary targets Linux x86_64 matching the container.

---

## Claude's Discretion

- Exact argparse structure (subcommands vs flat flags)
- Help formatter class
- Error message wording for exit codes 1 and 2
- `--input` detection logic (json.loads() attempt vs file existence check)

## Deferred Ideas

- Windows/macOS binaries (out of scope for v1.4)
- `--onefile` packaging (decided against; can revisit if distribution simplicity becomes a priority)
