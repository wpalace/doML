# DoML Iterate Model Workflow

## Purpose

Generate a new modelling iteration notebook incorporating analyst-supplied direction. Reads the most recent executed modelling notebook and its interpretation cell, creates a v{N+1} notebook with the specified focus, runs the full CV + leaderboard + SHAP + Optuna pipeline, and appends results to `models/leaderboard.csv` for cross-iteration comparison.

## Invoked by: /doml-iterate-model [optional direction string]

## Implementation Status

| Step | Implemented | Phase |
|------|-------------|-------|
| Read prior notebook + interpretation cell | Stub | Phase 6b |
| Generate next version notebook | Stub | Phase 6b |
| Run CV + leaderboard + SHAP + Optuna | Stub | Phase 6b |
| Append results to leaderboard.csv | Stub | Phase 6b |
| Write new interpretation cell | Stub | Phase 6b |

---

## ⚠️ Stub — Full Implementation Deferred to Phase 6b Planning

This workflow documents planned behavior. The command is registered but not yet fully executable. See the **Manual Workaround** section at the bottom for how to iterate now.

---

## Planned Workflow

### Planned Step 1 — Identify prior notebook

Find the most recent executed modelling notebook in `notebooks/`:

```
notebooks/0{N}_modelling_{problem_type}_v{M}.ipynb   (highest M)
```

Read the final Markdown cell — this is the Claude interpretation cell written by `execute-phase.md` Step 3m. Extract:
- Top model name and CV score
- Any anomalies flagged
- Suggested next steps

### Planned Step 2 — Resolve next version number

Increment M → M+1. New notebook path:

```
notebooks/0{N}_modelling_{problem_type}_v{M+1}.ipynb
```

Version resolution glob:
```bash
python3 -c "
import glob, re
existing = glob.glob('notebooks/0*_modelling_*_v*.ipynb')
versions = [int(re.search(r'_v(\d+)\.ipynb', f).group(1)) for f in existing if re.search(r'_v(\d+)\.ipynb', f)]
print(max(versions) + 1 if versions else 1)
"
```

### Planned Step 3 — Generate modified notebook

Copy the template for the `problem_type` from `.planning/config.json` (regression or classification).

Incorporate the direction argument:
- If direction mentions **specific model names** → focus the `models` dict on those models, remove others
- If direction mentions **feature engineering** → insert new cells before the CV loop with the specified engineering steps
- If direction mentions **hyperparameter focus** → widen the Optuna search space for that model (e.g., deeper `max_depth` range for XGBoost)
- If direction is empty → copy template as-is (same as initial run)

### Planned Step 4 — Execute the new iteration notebook

Same execution pattern as `execute-phase.md` Step 3k:

```bash
docker compose exec jupyter jupyter nbconvert \
  --execute \
  --to notebook \
  --inplace \
  notebooks/0{N}_modelling_{problem_type}_v{M+1}.ipynb \
  --ExecutePreprocessor.timeout=1200
```

Timeout: 1200s (20 min) — Optuna adds execution time.

### Planned Step 5 — Append results to leaderboard.csv

The modelling notebook handles append-only leaderboard writes automatically. After execution, display a cross-iteration leaderboard summary:

```
All models across all iterations, sorted by primary metric:

  model                      version  cv_primary_mean  cv_primary_std
  XGBRegressor (tuned)       v2       11.23            0.31
  XGBRegressor               v2       13.45            0.42
  XGBRegressor (tuned)       v1       12.34            0.45
  ...

Full leaderboard: models/leaderboard.csv ({N} total entries)
```

### Planned Step 6 — Write Claude interpretation

Same as `execute-phase.md` Step 3m — append an interpretation cell to the new notebook.

Compare v{M+1} results to v{M} and note:
- Whether the direction improved performance
- The delta in primary metric vs. prior best
- Suggested next step (iterate again, proceed to reports, or flag concerns)

### Planned Step 7 — Display summary

```
Previous best (v{M}):   {model_name}   CV {metric} = {score}
New best (v{M+1}):      {model_name}   CV {metric} = {score}
Delta: {+/-X.XXXX}

Full leaderboard: models/leaderboard.csv ({N} total entries)

Next: Run /doml-iterate-model "your next direction" to continue, or
      /doml-progress to review overall project status.
```

---

## Manual Workaround

Until Phase 6b implements this workflow, analysts can iterate manually:

1. **Copy the prior notebook:**
   ```bash
   cp notebooks/04_modelling_{type}_v1.ipynb notebooks/04_modelling_{type}_v2.ipynb
   ```

2. **Edit the notebook in JupyterLab:**
   - Modify the `models` dict to focus on promising models
   - Add feature engineering cells before the CV loop
   - Adjust Optuna search spaces for specific models

3. **Re-run the notebook:**
   ```bash
   docker compose exec jupyter jupyter nbconvert \
     --execute --to notebook --inplace \
     notebooks/04_modelling_{type}_v2.ipynb \
     --ExecutePreprocessor.timeout=1200
   ```

4. **Leaderboard auto-appends:** The notebook's leaderboard write is append-only — all iterations accumulate in `models/leaderboard.csv`.

---

## Implementation Note

Full implementation requires:

1. **Direction string parsing** — identify model/feature/hyperparameter focus from natural language
2. **Dynamic notebook cell modification** — insert feature engineering cells, modify `models` dict based on direction
3. **Cross-iteration leaderboard summary display** — aggregate `leaderboard.csv` across all version notebooks

Planned for Phase 6b. The key technical challenge is step 2 — injecting cells into an existing notebook template programmatically while keeping the cell structure coherent.
