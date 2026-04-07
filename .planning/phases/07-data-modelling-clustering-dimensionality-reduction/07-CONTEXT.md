# Phase 7 Context: Data Modelling — Clustering & Dimensionality Reduction

**Phase:** 07 — Data Modelling — Clustering & Dimensionality Reduction
**Goal:** Implement modelling notebooks for unsupervised problems (clustering and dimensionality reduction) with internal evaluation metrics, UMAP/t-SNE cluster visualization, and a fully implemented `/doml-iterate-unsupervised` command.
**Requirements:** MOD-03, MOD-05

---

## Prior Phase Outputs (Carrying Forward)

From Phase 6:
- `.claude/doml/templates/notebooks/preprocessing.ipynb` — preprocessing template; Phase 7 notebooks load `data/processed/preprocessed_{filename}` as starting point
- `.claude/doml/templates/notebooks/modelling_regression.ipynb` + `modelling_classification.ipynb` — reference patterns for cell structure, leaderboard design, and execute-phase routing
- `/doml-iterate-model` stub registered (SKILL.md + iterate-model.md) — supervised-only; remains as-is; Phase 7 adds a parallel `/doml-iterate-unsupervised` command
- `models/leaderboard.csv` — supervised results; Phase 7 writes to a separate `models/unsupervised_leaderboard.csv`

Decision 7 (Phase 6 CONTEXT.md): Python-only for all modelling phases — applies here without re-discussion.
Decision 2 (Phase 6 CONTEXT.md): Version-numbered notebooks (`notebooks/0{N}_modelling_{problem_type}_v{iteration}.ipynb`) — applies here without re-discussion.

Packages available (requirements.txt — pinned):
- `scikit-learn`, `umap-learn`, `shap`, `optuna`
- `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`
- `nbformat==5.10.4`, `nbconvert==7.16.4`, `papermill==2.6.0`
- `duckdb==1.5.1`

---

<decisions>

## Decision 1: Two Separate Notebook Templates

**Resolved:** Phase 7 produces two separate notebook templates:
- `.claude/doml/templates/notebooks/modelling_clustering.ipynb`
- `.claude/doml/templates/notebooks/modelling_dimreduction.ipynb`

**Why:** Mirrors Phase 6's regression/classification split. A user running a pure dimensionality reduction analysis should not be forced through a clustering notebook, and vice versa. `config.json` `problem_type` routes to the correct template at execute time.

**execute-phase routing:** If `problem_type` is `"clustering"` → copy `modelling_clustering.ipynb`. If `problem_type` is `"dimensionality_reduction"` → copy `modelling_dimreduction.ipynb`. Both templates are always generated (they're framework assets, not analysis artifacts).

**How to apply:** Plan 07-01 implements the clustering template; Plan 07-02 implements the dim reduction template. execute-phase.md routing added in Plan 07-03.

---

## Decision 2: Dimensionality Reduction Serves Two Roles

**Resolved:** PCA/UMAP/t-SNE serve both roles in Phase 7:

1. **Standalone analysis** — `modelling_dimreduction.ipynb` performs PCA (variance explained, scree plot, component loadings), UMAP (2D + 3D embeddings, nearest-neighbor structure), and t-SNE (2D, perplexity sweep) as first-class analysis goals
2. **Cluster visualization** — `modelling_clustering.ipynb` includes a dim reduction section at the end: after cluster assignments are produced, UMAP 2D scatter is generated with points colored by cluster label

**Notebook ordering in clustering notebook:**
1. Preprocessing (scale)
2. KMeans (elbow + silhouette sweep)
3. DBSCAN (eps/minPts grid)
4. Hierarchical (dendrogram → analyst cuts)
5. Internal metric comparison (silhouette, Davies-Bouldin, Calinski-Harabasz) across all methods
6. UMAP 2D visualization colored by best-method cluster assignments

**How to apply:** The clustering notebook always includes UMAP visualization as its final section. The dim reduction notebook is a standalone analysis with no dependency on clustering.

---

## Decision 3: Preprocessing — Self-Contained Scaling in Each Notebook

**Resolved:** Each Phase 7 notebook includes its own preprocessing section at the top — not dependent on the Phase 6 supervised preprocessing notebook.

**Why:** Unsupervised preprocessing has different requirements: scaling is mandatory (KMeans and PCA are distance/variance-based), but encoding for clustering differs from supervised encoding (no target leakage concern). Including scaling inline makes notebooks self-contained and runnable independently.

**Preprocessing section contents (both notebooks):**
1. Load `data/processed/preprocessed_{filename}` if it exists (output of Phase 6a) — else load `data/raw/{filename}` with a warning Markdown cell
2. Drop or impute any remaining NaN (simple median fill — document in Markdown cell)
3. Apply `StandardScaler` to all numeric columns (default)
4. Include a note: "RobustScaler recommended if EDA flagged heavy outliers — change `scaler` variable"
5. Categorical columns: encoded inline using `OrdinalEncoder` with a Markdown note explaining this is for distance computation, not model interpretation

**How to apply:** Plans 07-01 and 07-02 both open with this ~4-cell preprocessing section before their respective algorithm sections.

---

## Decision 4: Clustering Notebook — Algorithm Coverage and k Selection

**Resolved:**

### KMeans
- Elbow method: inertia vs. k (k=2..12), plot with annotated "elbow" suggestion
- Silhouette sweep: silhouette score vs. k (k=2..12), plot
- Analyst selects final k from both plots; selected k used for final cluster assignments
- Default starting point: k from silhouette peak (argmax)

### DBSCAN
- Grid search over `eps` (5th percentile of nearest-neighbor distances as starting point) and `minPts` (5, 10, 15)
- Report: number of clusters found, noise point percentage, silhouette (excluding noise)
- Analyst selects final eps/minPts from the grid summary table

### Hierarchical
- Ward linkage dendrogram plotted (truncated to last 30 merges for readability)
- Notebook stops with a Markdown cell: "Review the dendrogram above. Set `hierarchical_k` in the next cell to your chosen cluster count."
- `hierarchical_k` variable cell follows — analyst sets it, then runs the rest of the notebook
- Default: `hierarchical_k = 3` (placeholder; clearly labeled as needing review)

### Internal metric comparison table
After all three methods run, a summary DataFrame is built:

| Method | n_clusters | Silhouette ↑ | Davies-Bouldin ↓ | Calinski-Harabasz ↑ |
|--------|-----------|--------------|-----------------|---------------------|
| KMeans(k=4) | 4 | 0.42 | 0.89 | 312.4 |
| DBSCAN | 3 | 0.38 | 1.02 | 287.1 |
| Hierarchical(k=4) | 4 | 0.41 | 0.91 | 309.2 |

Best method highlighted. Cluster assignments for the best method written to `data/processed/cluster_assignments.csv`.

**How to apply:** Plan 07-01 implements this full sequence.

---

## Decision 5: Dim Reduction Notebook — Algorithm Coverage

**Resolved:**

### PCA
- Scree plot: explained variance ratio per component + cumulative
- Annotation: number of components to reach 80%, 90%, 95% explained variance
- Biplot (first 2 components): feature loading vectors overlaid on score scatter
- Component loadings table: top 5 features per component with their weights

### UMAP
- 2D embedding (default: `n_neighbors=15`, `min_dist=0.1`) — scatter plot
- 3D embedding — interactive plotly scatter (if plotly available, else static 3-angle matplotlib)
- Parameter sensitivity: run 2D UMAP with `n_neighbors` ∈ {5, 15, 30} — 3 plots side-by-side
- Color points by any available categorical label in the dataset (or "no label" if none)

### t-SNE
- 2D embedding with perplexity sweep: `perplexity` ∈ {5, 30, 50} — 3 plots side-by-side
- Note: t-SNE is for visualization only — distances between clusters are not interpretable

### Output
- Reduced-dimension representations written to `data/processed/pca_{n}d.csv`, `umap_2d.csv` for downstream use
- `models/unsupervised_leaderboard.csv` updated with PCA variance-explained summary row

**How to apply:** Plan 07-02 implements this sequence.

---

## Decision 6: Unsupervised Leaderboard — Separate File

**Resolved:** Unsupervised results are written to `models/unsupervised_leaderboard.csv` — separate from `models/leaderboard.csv` (supervised).

**Why:** Internal metrics (silhouette, Davies-Bouldin, Calinski-Harabasz) are incompatible with supervised metrics (RMSE, ROC-AUC). Mixing them in one file creates confusion.

**Schema:**
```
iteration, problem_type, method, params, n_clusters, silhouette, davies_bouldin, calinski_harabasz, notes, notebook_version, run_date
```

For dim reduction rows:
```
iteration, problem_type, method, params, n_components, variance_explained_80pct, variance_explained_90pct, notes, notebook_version, run_date
```

**Append-not-overwrite:** Same discipline as supervised leaderboard — each run appends rows. All iteration results remain visible for comparison.

**How to apply:** Plans 07-01, 07-02, and 07-04 all write to this file. The `/doml-iterate-unsupervised` command also appends to it.

---

## Decision 7: New `/doml-iterate-unsupervised` Command — Full Implementation

**Resolved:** Phase 7 implements `/doml-iterate-unsupervised` in full — not a stub. This is a new, parallel command to the existing `/doml-iterate-model` (supervised-only).

**Command signature:**
```
/doml-iterate-unsupervised "direction"
```

Examples:
- `/doml-iterate-unsupervised "try DBSCAN with finer eps grid around 0.3"`
- `/doml-iterate-unsupervised "focus on PCA — explore 5-component solution"`
- `/doml-iterate-unsupervised "apply UMAP with n_neighbors=5 to capture local structure"`

**Workflow steps:**
1. Read `config.json` to determine `problem_type` (clustering vs. dimensionality_reduction)
2. Find the most recent modelling notebook for that type (`notebooks/0{N}_modelling_{type}_v{N}.ipynb`)
3. Read its interpretation cell (last Markdown cell) + `models/unsupervised_leaderboard.csv`
4. Generate a new iteration notebook (next version number) incorporating the analyst's direction
5. Execute the notebook (nbconvert/papermill) inside Docker
6. Append results to `models/unsupervised_leaderboard.csv`
7. Write an interpretation Markdown cell at the end of the new notebook
8. Report to analyst: what changed, new metrics vs. prior iteration

**Skill registration:** `.claude/skills/doml-iterate-unsupervised/SKILL.md` + `.claude/doml/workflows/iterate-unsupervised.md`

**How to apply:** Plan 07-04 implements this command (skill file + full workflow).

---

## Decision 8: SHAP for Unsupervised — Not Applicable

**Resolved:** SHAP is not applied in Phase 7.

**Why:** SHAP requires a supervised model with a target variable. Unsupervised methods produce cluster assignments or embeddings — SHAP's Shapley value framework does not apply.

**Instead:** Feature importance for clustering is handled via:
- **KMeans:** Feature contribution to cluster separation — compute per-feature ANOVA F-statistic across clusters (high F = feature drives cluster separation)
- **PCA:** Component loadings (already in Decision 5)
- **UMAP/t-SNE:** No feature importance — purely structural visualization; documented in a Markdown cell

**How to apply:** Plans 07-01 and 07-02 include feature contribution sections using the above methods, clearly labeled as "Cluster Feature Importance (not SHAP)".

</decisions>

---

<canonical_refs>
- `.planning/config.json` — `problem_type`, `analysis_language`, `dataset.path`
- `.planning/PROJECT.md` — business context, target variable (or absence of one for unsupervised)
- `.planning/phases/06-data-modelling-regression-classification/06-CONTEXT.md` — Decision 2 (versioning), Decision 7 (Python-only), Decision 8 (/doml-iterate-model stub)
- `data/processed/preprocessed_{filename}` — preferred input; falls back to `data/raw/{filename}`
- `.claude/doml/templates/notebooks/modelling_regression.ipynb` — reference for cell structure, leaderboard patterns
- `.claude/doml/workflows/execute-phase.md` — Phase 3 executor (patterns to follow for Phase 7 executor extension)
- `.claude/skills/doml-iterate-model/SKILL.md` — reference for `/doml-iterate-unsupervised` SKILL.md structure
- `CLAUDE.md` — REPR-01 (seeds), REPR-02 (PROJECT_ROOT), OUT-03 (caveats)
- `REQUIREMENTS.md` — MOD-03, MOD-05 definitions
</canonical_refs>

---

<deferred>
## Deferred to Later Phases

- SHAP for unsupervised — not applicable; feature contribution via ANOVA F-stat instead (documented in Decision 8)
- R clustering (cluster package, factoextra) — Milestone 3
- Interactive cluster exploration (Plotly/Dash) — out of scope; HTML reports are the delivery format
- Gaussian Mixture Models (GMM) — soft clustering; can be added in a future iterate-unsupervised call
- Spectral clustering — deferred; dependency on affinity matrix tuning adds complexity
- Autoencoders for dim reduction — Milestone 2 (deep learning milestone)

## Phase 9 Dependency

- `reports/model_report.html` for unsupervised phases — Phase 9 handles all modelling HTML reports including clustering/dim reduction results, cluster visualizations, and unsupervised leaderboard display
</deferred>
