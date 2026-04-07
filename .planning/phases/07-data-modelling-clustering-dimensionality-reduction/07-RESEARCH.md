# Phase 7: Data Modelling — Clustering & Dimensionality Reduction — Research

**Researched:** 2026-04-07
**Domain:** Unsupervised ML — clustering (KMeans, DBSCAN, hierarchical) + dimensionality reduction (PCA, UMAP, t-SNE)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Decision 1: Two Separate Notebook Templates**
Phase 7 produces two templates:
- `.claude/doml/templates/notebooks/modelling_clustering.ipynb`
- `.claude/doml/templates/notebooks/modelling_dimreduction.ipynb`
execute-phase routing: `"clustering"` → clustering template; `"dimensionality_reduction"` → dim reduction template.

**Decision 2: Dimensionality Reduction Serves Two Roles**
- `modelling_dimreduction.ipynb` = standalone PCA + UMAP + t-SNE analysis
- `modelling_clustering.ipynb` = ends with UMAP 2D visualization colored by cluster label
- Clustering notebook ordering: Preprocessing → KMeans → DBSCAN → Hierarchical → Internal metric comparison → UMAP 2D

**Decision 3: Self-Contained Scaling in Each Notebook**
Both notebooks include their own preprocessing section:
1. Load `data/processed/preprocessed_{filename}` or fall back to `data/raw/{filename}` with warning
2. Drop/median-fill remaining NaN
3. `StandardScaler` on all numeric columns (RobustScaler note for outlier-heavy datasets)
4. `OrdinalEncoder` for categorical columns (with Markdown note explaining distance-computation encoding)

**Decision 4: Clustering Notebook — Full Algorithm Coverage**
- KMeans: inertia elbow (k=2..12) + silhouette sweep (k=2..12); default to silhouette peak k
- DBSCAN: eps from 5th-percentile kNN distance; minPts ∈ {5, 10, 15} grid
- Hierarchical: Ward, full dendrogram truncated to last 30 merges; `hierarchical_k = 3` placeholder; analyst sets before running rest
- Internal metric comparison table (Silhouette ↑, Davies-Bouldin ↓, Calinski-Harabasz ↑) across all three methods
- Best-method cluster assignments written to `data/processed/cluster_assignments.csv`

**Decision 5: Dim Reduction Notebook — Algorithm Coverage**
- PCA: scree plot + cumulative variance; 80/90/95% component thresholds; biplot (PC1/PC2); top-5 loadings per component
- UMAP: 2D default (n_neighbors=15, min_dist=0.1); 3D interactive Plotly (fallback: static); n_neighbors ∈ {5,15,30} sensitivity side-by-side
- t-SNE: perplexity ∈ {5,30,50} side-by-side; visualization-only note
- Outputs: `data/processed/pca_{n}d.csv`, `umap_2d.csv`; `models/unsupervised_leaderboard.csv` PCA row

**Decision 6: Unsupervised Leaderboard — Separate File**
`models/unsupervised_leaderboard.csv` — separate from `models/leaderboard.csv`
- Clustering schema: `iteration, problem_type, method, params, n_clusters, silhouette, davies_bouldin, calinski_harabasz, notes, notebook_version, run_date`
- Dim reduction schema: `iteration, problem_type, method, params, n_components, variance_explained_80pct, variance_explained_90pct, notes, notebook_version, run_date`
- Append-only (same discipline as supervised leaderboard)

**Decision 7: `/doml-iterate-unsupervised` — Full Implementation**
Full (not stub) command: reads config.json, finds latest notebook, reads last Markdown cell + leaderboard, generates v{N+1} notebook, executes via nbconvert/papermill, appends to unsupervised_leaderboard.csv, writes interpretation cell.
Skill: `.claude/skills/doml-iterate-unsupervised/SKILL.md` + `.claude/doml/workflows/iterate-unsupervised.md`

**Decision 8: SHAP Not Applicable**
No SHAP in Phase 7. Feature importance via:
- KMeans: per-feature ANOVA F-statistic across clusters (scipy.stats.f_oneway)
- PCA: component loadings (already in Decision 5)
- UMAP/t-SNE: none — documented with Markdown explanation

### Claude's Discretion
None declared.

### Deferred Ideas (OUT OF SCOPE)
- SHAP for unsupervised
- R clustering (cluster, factoextra) — Milestone 3
- Interactive cluster exploration (Plotly/Dash)
- Gaussian Mixture Models (GMM)
- Spectral clustering
- Autoencoders — Milestone 2
- `reports/model_report.html` for unsupervised — Phase 9
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MOD-03 | Modelling notebook generated for clustering problems (KMeans, DBSCAN, hierarchical) | sklearn 1.8.0 clustering APIs verified; silhouette/DB/CH metrics verified; dendrogram pattern from AgglomerativeClustering confirmed |
| MOD-05 | Modelling notebook generated for dimensionality reduction (PCA, UMAP, t-SNE) | PCA sklearn API verified; umap-learn 0.5.11 API verified (stable across 0.5.x); TSNE sklearn API verified; Plotly 3D pattern confirmed |
</phase_requirements>

---

## Summary

Phase 7 produces two notebook templates for unsupervised ML analysis and a new `/doml-iterate-unsupervised` command. All required algorithms are available in the pinned environment: `scikit-learn==1.8.0` covers KMeans, DBSCAN, AgglomerativeClustering, PCA, and TSNE; `umap-learn==0.5.11` covers UMAP; `plotly==5.24.1` covers interactive 3D scatter. The internal metric APIs (silhouette_score, davies_bouldin_score, calinski_harabasz_score) are all in `sklearn.metrics` with stable signatures.

The primary structural challenge is the DBSCAN eps-selection step: the 5th-percentile kNN distance heuristic requires `NearestNeighbors` from sklearn (also available) and a sorted k-distance plot. The dendrogram pattern requires `distance_threshold=0, n_clusters=None` on `AgglomerativeClustering` to get the full linkage tree, then a helper function to build the scipy linkage matrix from `model.children_` and `model.distances_`. Both patterns are well-documented and verified.

The `/doml-iterate-unsupervised` workflow mirrors `/doml-iterate-model` in structure, with the key difference that direction parsing must handle both `problem_type: clustering` and `problem_type: dimensionality_reduction` — reading the correct template and leaderboard file in each case.

**Primary recommendation:** Follow Phase 6 cell structure conventions exactly — seeds at top, PROJECT_ROOT via env var, append-only leaderboard writes, interpretation cell appended last. The unsupervised leaderboard schema and execute-phase routing extension are the only net-new framework concerns; the algorithm code follows well-established sklearn/umap-learn patterns.

---

## Project Constraints (from CLAUDE.md)

| Directive | Enforcement |
|-----------|-------------|
| REPR-01: Random seeds (`SEED = 42`) at top of every notebook | Both templates open with seed block |
| REPR-02: Paths via `PROJECT_ROOT` env var — no hardcoded absolute paths | All file I/O uses `PROJECT_ROOT / ...` |
| INFR-05: `data/raw/` is immutable — never write there | Templates write only to `data/processed/` and `models/` |
| DuckDB first for tabular profiling on disk | Not applicable to this phase — data already loaded from preprocessed CSV; no disk-scan profiling needed |
| Tidy data before feature engineering | Preprocessing section in each notebook validates before algorithm sections |
| OUT-03: HTML reports include correlation-is-not-causation caveats | Caveats cell at end of each notebook |
| Python-only for modelling phases (Decision 7 from Phase 6 CONTEXT.md) | No R cells; both templates Python-only |
| Notebook outputs stripped on commit (REPR-03) via nbstripout | No action needed — hook already installed |

---

## Standard Stack

### Core (all pinned in requirements.txt)
[VERIFIED: /home/bill/source/DoML/requirements.txt]

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| scikit-learn | 1.8.0 | KMeans, DBSCAN, AgglomerativeClustering, PCA, TSNE, all metrics | The reference Python ML library; all clustering/decomp APIs here |
| umap-learn | 0.5.11 | UMAP 2D/3D embeddings | Standard UMAP implementation; pynndescent backend also pinned (0.6.0) |
| scipy | 1.16.3 | `dendrogram`, `linkage`, `f_oneway` (ANOVA) | Required for hierarchical dendrogram visualization; already a sklearn dependency |
| plotly | 5.24.1 | Interactive 3D scatter for UMAP 3D | Already in container; px.scatter_3d is the standard pattern |
| matplotlib | 3.10.0 | Elbow plot, silhouette sweeps, PCA scree/biplot, t-SNE scatter | Consistent with Phase 5/6 templates |
| seaborn | 0.13.2 | Heatmaps, styling | Consistent with Phase 5/6 templates |
| pandas | 2.3.3 | DataFrames, leaderboard CSV I/O | Standard throughout project |
| numpy | 2.3.5 | Numerical ops, percentile calculation | Standard throughout project |
| nbformat | 5.10.4 | Programmatic notebook cell insertion (interpretation cell, iterate-unsupervised) | Same pattern as Phase 6 execute-phase Step 3m |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sklearn.neighbors.NearestNeighbors | (in sklearn) | kNN distance for DBSCAN eps selection | Always — in DBSCAN preprocessing section |
| scipy.stats.f_oneway | (in scipy) | ANOVA F-statistic per feature across clusters | KMeans feature importance section |
| sklearn.preprocessing.StandardScaler, RobustScaler | (in sklearn) | Mandatory scaling before clustering/PCA | Top of both notebooks |
| sklearn.preprocessing.OrdinalEncoder | (in sklearn) | Encode categoricals for distance computation | Top of both notebooks |
| joblib | 1.5.3 | Unused in Phase 7 (no model serialization for unsupervised) | Not needed here |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| scipy dendrogram | plotly dendrogram | scipy is already a dependency and the standard approach; plotly dendrogram requires extra package patterns |
| plotly px.scatter_3d | matplotlib 3-angle subplots | plotly is already pinned; 3D interactive is clearly better for exploration; fallback to matplotlib only if plotly unavailable |
| ANOVA F-stat for cluster feature importance | Permutation importance with a surrogate model | ANOVA is simpler, directly interpretable, and requires no additional model; Decision 8 mandates ANOVA |

**Installation:** All packages already in requirements.txt. No new dependencies needed.

---

## Architecture Patterns

### Recommended Project Structure (Phase 7 outputs)
```
.claude/doml/
├── templates/notebooks/
│   ├── modelling_clustering.ipynb      # Plan 07-01
│   └── modelling_dimreduction.ipynb    # Plan 07-02
├── workflows/
│   ├── execute-phase.md                # Extended in Plan 07-03
│   └── iterate-unsupervised.md         # New in Plan 07-04
└── skills/
    └── doml-iterate-unsupervised/
        └── SKILL.md                    # New in Plan 07-04
data/processed/
├── cluster_assignments.csv             # Written by clustering notebook
├── pca_{n}d.csv                        # Written by dim reduction notebook
└── umap_2d.csv                         # Written by dim reduction notebook
models/
└── unsupervised_leaderboard.csv        # Written by both notebooks + iterate-unsupervised
```

### Pattern 1: Notebook Template Cell Structure (mirrors Phase 6)

All Phase 7 notebooks follow this structure:
```
Cell 0:  Markdown header + "Python-only" note
Cell 1:  Imports + seeds (REPR-01)
Cell 2:  PROJECT_ROOT + config.json read + problem_type guard (REPR-02)
Cell 3:  Data load (preprocessed_* or raw fallback)
Cell 4:  Markdown — preprocessing section header
Cells 5-8:  NaN fill, StandardScaler, OrdinalEncoder, shape report
[Algorithm cells...]
Last cell: Markdown — Caveats (OUT-03)
```

The interpretation cell is appended after execution by execute-phase.md or iterate-unsupervised.md (same pattern as Phase 6 Step 3m).

### Pattern 2: KMeans Elbow + Silhouette Sweep
[VERIFIED: scikit-learn.org/stable/modules/clustering.html]

```python
# Source: scikit-learn 1.8.0 docs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

inertias, silhouettes = [], []
K_RANGE = range(2, 13)

for k in K_RANGE:
    km = KMeans(n_clusters=k, init='k-means++', random_state=SEED, n_init='auto')
    km.fit(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, km.labels_))

# best k = argmax silhouette
best_k = K_RANGE[np.argmax(silhouettes)]

# Final fit
km_final = KMeans(n_clusters=best_k, init='k-means++', random_state=SEED, n_init='auto')
km_final.fit(X_scaled)
kmeans_labels = km_final.labels_
```

### Pattern 3: DBSCAN eps Selection via kNN Distance
[VERIFIED: sklearn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html, multiple community sources]

```python
from sklearn.neighbors import NearestNeighbors
import numpy as np

# 5th percentile of kNN distances as eps starting point
MIN_SAMPLES = 5
nn = NearestNeighbors(n_neighbors=MIN_SAMPLES)
nn.fit(X_scaled)
distances, _ = nn.kneighbors(X_scaled)
knn_dist = np.sort(distances[:, -1])  # distance to k-th neighbor, sorted

# eps starting point: 5th percentile of sorted distances
eps_start = np.percentile(knn_dist, 5)

# Grid search
eps_candidates = [eps_start * 0.5, eps_start, eps_start * 2.0]
minpts_candidates = [5, 10, 15]
```

Note: Context7 was not queried for these since sklearn is not in Context7; patterns are from [VERIFIED: official sklearn docs + community consensus].

### Pattern 4: Hierarchical Dendrogram from AgglomerativeClustering
[VERIFIED: scikit-learn.org/stable/auto_examples/cluster/plot_agglomerative_dendrogram.html]

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram
import numpy as np

# Must use distance_threshold=0, n_clusters=None to get full tree
model = AgglomerativeClustering(distance_threshold=0, n_clusters=None, linkage='ward')
model.fit(X_scaled)

def plot_dendrogram(model, **kwargs):
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count
    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)
    dendrogram(linkage_matrix, **kwargs)

# Truncated to last 30 merges for readability
plot_dendrogram(model, truncate_mode='lastp', p=30,
                leaf_rotation=90, leaf_font_size=8)
```

After analyst sets `hierarchical_k`, run final assignment:
```python
hierarchical_k = 3  # ANALYST: set this from dendrogram review
hc_final = AgglomerativeClustering(n_clusters=hierarchical_k, linkage='ward')
hierarchical_labels = hc_final.fit_predict(X_scaled)
```

### Pattern 5: Internal Metric Comparison Table
[VERIFIED: sklearn.org/stable/modules/generated/sklearn.metrics.*]

```python
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

def compute_metrics(X, labels, method_name, params_str):
    # Exclude noise points (-1) for silhouette/DB when computing DBSCAN metrics
    mask = labels != -1
    X_valid, labels_valid = X[mask], labels[mask]
    n_clusters = len(set(labels_valid))
    if n_clusters < 2:
        return {'method': method_name, 'params': params_str,
                'n_clusters': n_clusters, 'silhouette': None,
                'davies_bouldin': None, 'calinski_harabasz': None}
    return {
        'method':             method_name,
        'params':             params_str,
        'n_clusters':         n_clusters,
        'silhouette':         round(silhouette_score(X_valid, labels_valid), 4),
        'davies_bouldin':     round(davies_bouldin_score(X_valid, labels_valid), 4),
        'calinski_harabasz':  round(calinski_harabasz_score(X_valid, labels_valid), 2),
    }
```

Key interpretation:
- Silhouette: higher is better (range -1 to 1)
- Davies-Bouldin: lower is better (0 = optimal)
- Calinski-Harabasz: higher is better (no upper bound)

### Pattern 6: UMAP 2D + 3D with Plotly
[VERIFIED: plotly.com/python/t-sne-and-umap-projections/, umap-learn docs 0.5.8 — API consistent with 0.5.11]

```python
import umap

# 2D
reducer_2d = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=SEED)
embedding_2d = reducer_2d.fit_transform(X_scaled)

# 3D — interactive Plotly
reducer_3d = umap.UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=SEED)
embedding_3d = reducer_3d.fit_transform(X_scaled)

import plotly.express as px
fig_3d = px.scatter_3d(
    embedding_3d, x=0, y=1, z=2,
    color=cluster_labels.astype(str),
    labels={'color': 'Cluster'},
    title='UMAP 3D Embedding'
)
fig_3d.update_traces(marker_size=5)
fig_3d.show()

# Fallback for non-interactive output
# fig_3d.write_image('reports/umap_3d.png')  # requires kaleido
# Alternative fallback: 3-angle matplotlib subplots
```

Note on 3D fallback: `plotly==5.24.1` is pinned in requirements.txt; the container has it. The fallback to matplotlib 3-angle subplots is only for edge cases where plotly rendering fails (e.g., non-interactive HTML export without the plotly.js bundle).

### Pattern 7: PCA Scree Plot + Biplot
[VERIFIED: sklearn 1.4.2 on host, same API in 1.8.0]

```python
from sklearn.decomposition import PCA

pca = PCA(random_state=SEED)
pca.fit(X_scaled)

# Scree plot
evr = pca.explained_variance_ratio_
cumulative = np.cumsum(evr)

# Find 80/90/95% thresholds
n_80 = np.argmax(cumulative >= 0.80) + 1
n_90 = np.argmax(cumulative >= 0.90) + 1
n_95 = np.argmax(cumulative >= 0.95) + 1

# Biplot (PC1 + PC2 scores + loadings)
pca_2d = PCA(n_components=2, random_state=SEED)
scores = pca_2d.fit_transform(X_scaled)
loadings = pca_2d.components_  # shape (2, n_features)

fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(scores[:, 0], scores[:, 1], alpha=0.4, s=20)

# Feature arrows
scale = np.max(np.abs(scores)) / np.max(np.abs(loadings))
for i, feat in enumerate(feature_names):
    ax.arrow(0, 0, loadings[0, i] * scale, loadings[1, i] * scale,
             head_width=0.05, head_length=0.05, fc='red', ec='red')
    ax.text(loadings[0, i] * scale * 1.1, loadings[1, i] * scale * 1.1,
            feat, color='red', fontsize=8)
```

### Pattern 8: t-SNE Perplexity Sweep
[VERIFIED: sklearn 1.4.2 on host TSNE signature; same in 1.8.0]

```python
from sklearn.manifold import TSNE

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, perp in zip(axes, [5, 30, 50]):
    tsne = TSNE(n_components=2, perplexity=perp, random_state=SEED,
                learning_rate='auto', init='pca')
    emb = tsne.fit_transform(X_scaled)
    ax.scatter(emb[:, 0], emb[:, 1], alpha=0.5, s=10)
    ax.set_title(f't-SNE perplexity={perp}')
```

Note: `learning_rate='auto'` and `init='pca'` are the sklearn-recommended defaults since 1.2 (more stable than fixed learning_rate + random init). [VERIFIED: sklearn docs]

### Pattern 9: ANOVA Feature Importance for Clusters
[VERIFIED: scipy 1.16.3 in requirements.txt; f_oneway is a stable scipy.stats function]

```python
from scipy.stats import f_oneway
import pandas as pd

df_with_labels = X_df.copy()
df_with_labels['cluster'] = best_labels

f_stats = {}
for col in X_df.columns:
    groups = [group[col].values for _, group in df_with_labels.groupby('cluster')]
    f_val, p_val = f_oneway(*groups)
    f_stats[col] = {'f_statistic': f_val, 'p_value': p_val}

feature_importance = (pd.DataFrame(f_stats).T
                        .sort_values('f_statistic', ascending=False)
                        .reset_index()
                        .rename(columns={'index': 'feature'}))
```

### Pattern 10: Unsupervised Leaderboard Append
[VERIFIED: mirrors Phase 6 leaderboard pattern from modelling_regression.ipynb]

```python
from pathlib import Path
from datetime import date
import pandas as pd

unsup_lb_path = PROJECT_ROOT / 'models' / 'unsupervised_leaderboard.csv'

new_rows = [
    {
        'iteration': 1,
        'problem_type': 'clustering',
        'method': 'KMeans',
        'params': f'k={best_k}',
        'n_clusters': best_k,
        'silhouette': kmeans_metrics['silhouette'],
        'davies_bouldin': kmeans_metrics['davies_bouldin'],
        'calinski_harabasz': kmeans_metrics['calinski_harabasz'],
        'notes': 'initial run',
        'notebook_version': 'v1',
        'run_date': str(date.today()),
    },
    # ... DBSCAN, Hierarchical rows
]

new_df = pd.DataFrame(new_rows)

if unsup_lb_path.exists():
    existing = pd.read_csv(unsup_lb_path)
    # Resolve iteration number
    next_iter = existing['iteration'].max() + 1
    new_df['iteration'] = next_iter
    combined = pd.concat([existing, new_df], ignore_index=True)
else:
    combined = new_df

(PROJECT_ROOT / 'models').mkdir(exist_ok=True)
combined.to_csv(unsup_lb_path, index=False)
```

### Pattern 11: iterate-unsupervised Workflow Structure
(mirrors iterate-model.md planned steps — Decision 7 requires full implementation)

```
Step 1: Read config.json → problem_type (clustering or dimensionality_reduction)
Step 2: Find most recent notebook: notebooks/0{N}_modelling_{type}_v{M}.ipynb (highest M)
Step 3: Read last Markdown cell (interpretation) + unsupervised_leaderboard.csv
Step 4: Resolve next version → v{M+1}
Step 5: Copy template (.claude/doml/templates/notebooks/modelling_{type}.ipynb)
Step 6: Modify notebook cells based on direction string
         - Clustering direction: adjust k range / eps values / minPts / select algorithm
         - Dim reduction direction: adjust n_neighbors / n_components / perplexity
Step 7: Execute via nbconvert (timeout 900s — no Optuna, shorter than supervised)
Step 8: Append results to unsupervised_leaderboard.csv
Step 9: Read leaderboard, write interpretation cell comparing v{M+1} vs v{M}
Step 10: Display summary (prior best vs new best, delta metrics)
```

### Anti-Patterns to Avoid

- **Using accuracy/F1/RMSE for clustering:** These require a ground truth label. Use only silhouette, Davies-Bouldin, Calinski-Harabasz for model selection.
- **Including noise points (-1) in silhouette/DB metrics for DBSCAN:** DBSCAN labels noise as -1. silhouette_score requires ≥2 clusters and will crash if passed a single cluster or noise-only labels. Always mask `-1` rows before calling metric functions.
- **Using t-SNE for downstream tasks:** t-SNE is visualization-only. Inter-cluster distances are not meaningful. UMAP preserves more global structure and can be used for downstream tasks.
- **Computing UMAP on unscaled data:** UMAP is distance-based; unscaled features with different units dominate the embedding. Always scale before UMAP.
- **Hardcoding `n_iter=1000` for t-SNE on large datasets:** Default is 1000; may need to increase for n_samples > 10,000. Add a note in the template.
- **`AgglomerativeClustering` without `distance_threshold=0` for dendrogram:** Fitting with `n_clusters=N` does not store `distances_` attribute required for dendrogram construction. Must use `distance_threshold=0, n_clusters=None`.
- **Overwriting unsupervised_leaderboard.csv:** Must be append-only. Use `pd.concat` pattern, not direct write.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Elbow method for KMeans | Custom inertia-diff heuristic | KMeans.inertia_ + matplotlib plot; analyst visually selects | The "elbow" is subjective; present both elbow + silhouette, let analyst decide |
| DBSCAN eps selection | Arbitrary eps grid | NearestNeighbors kNN distance plot; 5th-percentile starting point | Data-driven starting point; avoids all-noise or all-one-cluster failure |
| Hierarchical dendrogram | Custom merge visualization | scipy.cluster.hierarchy.dendrogram with AgglomerativeClustering linkage matrix | scipy's implementation handles all edge cases and truncation modes |
| Cluster validity index | Custom distance computations | silhouette_score, davies_bouldin_score, calinski_harabasz_score from sklearn.metrics | Well-defined, parallelized, edge-case-safe implementations |
| UMAP from scratch | Manual manifold approximation | umap-learn | Months of research; pynndescent acceleration already in requirements.txt |
| Interactive 3D scatter | Custom WebGL/matplotlib3d | plotly.express.scatter_3d | Already in requirements.txt; single function call; produces HTML-embeddable output |

---

## Common Pitfalls

### Pitfall 1: DBSCAN Produces All-Noise or All-One-Cluster Result
**What goes wrong:** Silhouette score crashes with `Number of labels is 1` or all points labeled -1.
**Why it happens:** eps too small → every point is noise; eps too large → one cluster.
**How to avoid:** Always validate after DBSCAN fit: `n_clusters = len(set(labels)) - (1 if -1 in labels else 0)`. Skip metric computation if `n_clusters < 2`. Report noise percentage in grid table. Include this guard in compute_metrics() helper.
**Warning signs:** `n_clusters = 0` or `noise_pct > 80%` in grid output.

### Pitfall 2: silhouette_score on DBSCAN Including Noise Points
**What goes wrong:** silhouette_score(-1 labels) raises ValueError or returns misleadingly low score.
**Why it happens:** sklearn silhouette_score does not handle -1 labels as "unassigned" — it treats them as a cluster label.
**How to avoid:** Always mask: `mask = labels != -1; score = silhouette_score(X[mask], labels[mask])`. Document this in a Markdown cell.

### Pitfall 3: AgglomerativeClustering Missing distances_ Attribute
**What goes wrong:** `AttributeError: 'AgglomerativeClustering' object has no attribute 'distances_'`
**Why it happens:** Fitting with `n_clusters=N` (the normal usage) does not store the merge distances.
**How to avoid:** For dendrogram, always fit with `distance_threshold=0, n_clusters=None`. For final assignment with chosen `hierarchical_k`, fit a second instance with `n_clusters=hierarchical_k`.

### Pitfall 4: UMAP random_state Producing Different Results Across OS
**What goes wrong:** UMAP embedding differs across platforms even with `random_state=SEED`.
**Why it happens:** UMAP uses numba-JIT code paths that can vary by platform/OS. [VERIFIED: github.com/lmcinnes/umap/issues/153]
**How to avoid:** Document this limitation in a Markdown cell. Set `random_state=SEED` for best-effort reproducibility. Do not rely on pixel-exact embedding reproducibility across different machines.

### Pitfall 5: PCA Biplot Scale Mismatch
**What goes wrong:** Loading arrows are invisible (too small) or overlap with scores.
**Why it happens:** Score coordinates are in the hundreds; loading values are in [-1, 1].
**How to avoid:** Scale loadings by `np.max(np.abs(scores)) / np.max(np.abs(loadings))` before drawing arrows. See Pattern 7 above.

### Pitfall 6: t-SNE on High-Dimensional Data Without PCA Pre-reduction
**What goes wrong:** t-SNE is extremely slow on datasets with > 50 features.
**Why it happens:** t-SNE's O(n²) pairwise distance computation scales with both n_samples and n_features.
**How to avoid:** If `n_features > 50`, pre-reduce with PCA to 50 components before t-SNE. Add a conditional check in the template. [ASSUMED] (well-established community practice; not verified against specific sklearn docs version)

### Pitfall 7: Unsupervised Leaderboard Iteration Counter
**What goes wrong:** All runs write `iteration=1` — no comparison across iterations.
**Why it happens:** Naive append without reading the existing max iteration.
**How to avoid:** Before appending, check `existing['iteration'].max()` if the file exists. See Pattern 10 above.

### Pitfall 8: execute-phase.md Step 3g Routing — Existing Guard Blocks Phase 7
**What goes wrong:** Current `execute-phase.md` Step 3g stops execution with "Use /doml-execute-phase 7 for these problem types" when clustering/dim_reduction is detected.
**Why it happens:** The Phase 6 executor was written to redirect; Phase 7 adds the actual executor for these types.
**How to avoid:** Plan 07-03 must extend execute-phase.md to add a new `| 7 — Clustering/Dim Reduction |` row in the routing table and implement the Phase 7 executor steps. The Step 3g redirect message should be updated to be a fallback only when Phase 7 executor steps are absent.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| KMeans with random init | KMeans with k-means++ + `n_init='auto'` | sklearn 1.2 | More stable; `n_init='auto'` runs 10 inits by default |
| t-SNE random init + fixed learning_rate | t-SNE `init='pca'` + `learning_rate='auto'` | sklearn 1.2 | Better convergence; PCA init gives more stable orientation |
| Manual linkage matrix construction from scratch | Build from `model.children_` + `model.distances_` | sklearn example pattern | Cleaner; no need to call scipy's linkage() separately on data |
| UMAP with no random_state (non-reproducible) | UMAP with `random_state=SEED` | umap-learn 0.4+ | Best-effort reproducibility; numba JIT still causes cross-OS variation |

**Deprecated/Outdated:**
- `sklearn.manifold.TSNE(n_iter=...)` parameter: renamed to `max_iter` in sklearn 1.5. Using `n_iter` will raise deprecation warning in 1.8. [VERIFIED: sklearn 1.8.0 docs via WebFetch]. Use `max_iter=1000` (but since the pinned version is 1.8.0, use `max_iter`).
- `KMeans(n_init=10)` hardcoded: replaced by `n_init='auto'` in sklearn 1.4+. [VERIFIED: sklearn 1.8.0 docs]

---

## execute-phase.md Extension Pattern

Phase 07-03 needs to add a Phase 7 routing block to execute-phase.md. The pattern to follow:

**Current Step 3g (Phase 6):** Redirects clustering/dim_reduction to Phase 7
**Required addition:** A new Phase 7 executor block parallel to the Phase 3 block

The routing table in Step 3 should gain a new row:
```
| 7 — Clustering/Dim Reduction | Phase 7 executor (Steps 3n–3t) | notebooks/0{N}_modelling_{type}_v{M}.ipynb | — (no HTML report until Phase 9) |
```

The Phase 7 executor steps follow the same pattern as Phase 3 (Steps 3g–3m):
1. Read `problem_type` from config.json → route to clustering or dim reduction template
2. Resolve next version number
3. Copy template to `notebooks/0{N}_modelling_{type}_v{M}.ipynb`
4. Execute via nbconvert (timeout 900s — no Optuna tuning in unsupervised)
5. Verify notebook output + verify `models/unsupervised_leaderboard.csv` written
6. Write Claude interpretation cell comparing metrics to prior run (if v>1)
7. No HTML report step — deferred to Phase 9

Note: The notebook number for Phase 7 modelling starts at 05 (03=preprocessing, 04=supervised modelling_v1). If the user runs both supervised (Phase 6) and unsupervised (Phase 7), unsupervised notebooks would be `notebooks/05_modelling_clustering_v1.ipynb`. The execute-phase executor should use the next available notebook number, not hardcode 05. [ASSUMED — verify the numbering convention matches what Phase 6 established]

---

## Environment Availability

All dependencies are pre-installed in the container via requirements.txt. No external services needed.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| scikit-learn | KMeans, DBSCAN, PCA, TSNE, metrics | ✓ | 1.8.0 (pinned) | — |
| umap-learn | UMAP 2D/3D | ✓ | 0.5.11 (pinned) | — |
| pynndescent | umap-learn backend | ✓ | 0.6.0 (pinned) | — |
| plotly | UMAP 3D interactive | ✓ | 5.24.1 (pinned) | matplotlib 3-angle static subplots |
| scipy | dendrogram, f_oneway | ✓ | 1.16.3 (pinned) | — |
| numba | umap-learn JIT compilation | ✓ | 0.62.1 (pinned) | — |
| Docker container running | notebook execution | Assumed running | — | User must start with `docker compose up` |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:**
- plotly interactive 3D: plotly available in container; if rendering fails in HTML export, fallback to 3-angle matplotlib subplot.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 (pinned in requirements.txt) |
| Config file | None detected — pytest.ini/pyproject.toml not found |
| Quick run command | `pytest .claude/doml/ -x -q` |
| Full suite command | `pytest .claude/doml/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MOD-03 | Clustering notebook template exists and is valid nbformat | smoke | `python3 -c "import nbformat; nbformat.read(open('.claude/doml/templates/notebooks/modelling_clustering.ipynb'), as_version=4)"` | ❌ Wave 0 |
| MOD-05 | Dim reduction notebook template exists and is valid nbformat | smoke | `python3 -c "import nbformat; nbformat.read(open('.claude/doml/templates/notebooks/modelling_dimreduction.ipynb'), as_version=4)"` | ❌ Wave 0 |
| MOD-03 | execute-phase.md routes clustering to correct template | manual | Review execute-phase.md Step 3n conditional | ❌ Wave 0 |
| MOD-05 | execute-phase.md routes dimensionality_reduction to correct template | manual | Review execute-phase.md Step 3n conditional | ❌ Wave 0 |
| MOD-03 | Clustering notebook contains silhouette/DB/CH metrics — no accuracy metric | smoke | `grep -c "accuracy\|f1_score\|roc_auc" .claude/doml/templates/notebooks/modelling_clustering.ipynb` (expect 0) | ❌ Wave 0 |
| Decision 7 | iterate-unsupervised SKILL.md exists and is parseable | smoke | `cat .claude/skills/doml-iterate-unsupervised/SKILL.md` (expect non-empty) | ❌ Wave 0 |
| Decision 6 | unsupervised_leaderboard.csv schema matches spec | unit | `pytest .claude/doml/tests/test_unsupervised_leaderboard.py` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -c "import nbformat; nbformat.read(open('...'), as_version=4)"` for each new template
- **Per wave merge:** `pytest .claude/doml/ -q` (if tests exist)
- **Phase gate:** Both templates validate as nbformat v4 + no accuracy metrics in clustering template

### Wave 0 Gaps
- [ ] Notebook validation: smoke test for both templates (nbformat.read)
- [ ] Clustering template metric check: grep-based assertion that accuracy/f1/roc_auc absent
- [ ] SKILL.md existence check for doml-iterate-unsupervised

Note: Phase 6 used a pattern of verification via one-liner python3 commands inline in execute-phase.md rather than pytest test files. Phase 7 should follow the same convention for consistency. No separate test files are required — verification is embedded in workflow steps.

---

## Security Domain

This phase generates data analysis notebook templates and workflow files. No authentication, user input processing, session management, or cryptographic operations are involved.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | — |
| V3 Session Management | No | — |
| V4 Access Control | No | — |
| V5 Input Validation | Minimal | `direction` argument string in iterate-unsupervised is used for cell generation only; no shell injection risk if handled in Python string operations (not shell commands) |
| V6 Cryptography | No | — |

**Notable:** The `/doml-iterate-unsupervised` direction string is used to generate notebook cells programmatically (Python nbformat API). It is NOT passed to shell commands, so injection risk is negligible. The direction string should be treated as analyst-supplied text, not executable code.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | t-SNE on >50 features should be pre-reduced with PCA to 50 components first | Pitfall 6 | If dataset has <50 features this is moot; if >50 and pre-reduction not done, notebook is just slow, not incorrect |
| A2 | Notebook numbering for Phase 7 starts at 05 (after 03_preprocessing + 04_modelling_supervised) | execute-phase Extension Pattern | If a project skips Phase 6, numbering would be different; executor should auto-detect next available number |
| A3 | UMAP `init='random'` (as seen in plotly docs example) is used for 3D; `init='pca'` may be preferable for reproducibility | Architecture Pattern 6 | Using `init='random'` with `random_state=SEED` should be fine; `init='pca'` (default in newer versions) is more stable but may not be default in 0.5.11 |

---

## Open Questions

1. **UMAP default `init` in 0.5.11**
   - What we know: The plotly docs example uses `init='random'`; newer umap-learn may default to `spectral` or `pca`
   - What's unclear: Whether `init` default changed between 0.5.8 and 0.5.11
   - Recommendation: Explicitly set `init='spectral'` (the umap-learn default) for 2D, `init='random'` for 3D (spectral init has issues with >2 components in some builds). [ASSUMED]

2. **Notebook file number for Phase 7 outputs**
   - What we know: Phase 6 produces `03_preprocessing.ipynb` and `04_modelling_{type}_v{N}.ipynb`
   - What's unclear: If a project runs Phase 7 without Phase 6 (dim reduction as first modelling phase), what number is correct?
   - Recommendation: execute-phase.md Phase 7 executor should glob `notebooks/0*_modelling_*.ipynb` and auto-detect the next available number, just as Phase 6 does for version numbers.

3. **Plotly HTML embedding in nbconvert output (Phase 9 concern)**
   - What we know: plotly figures render interactively in JupyterLab; nbconvert may or may not embed plotly.js
   - What's unclear: Whether `jupyter nbconvert --to html` correctly embeds plotly interactive charts without extra configuration
   - Recommendation: This is a Phase 9 concern (HTML reports). For Phase 7, just `fig.show()` in the notebook. Flag for Phase 9 research.

---

## Sources

### Primary (HIGH confidence)
- `/home/bill/source/DoML/requirements.txt` — confirmed package versions: scikit-learn 1.8.0, umap-learn 0.5.11, plotly 5.24.1, scipy 1.16.3, pandas 2.3.3, numpy 2.3.5
- `/home/bill/source/DoML/.claude/doml/templates/notebooks/modelling_regression.ipynb` — Phase 6 cell structure pattern
- `/home/bill/source/DoML/.claude/doml/workflows/execute-phase.md` — executor pattern, routing table
- `/home/bill/source/DoML/.claude/skills/doml-iterate-model/SKILL.md` — iterate command structure to mirror
- [scikit-learn 1.8.0 clustering docs](https://scikit-learn.org/stable/modules/clustering.html) — KMeans, DBSCAN, AgglomerativeClustering APIs
- [scikit-learn 1.8.0 dendrogram example](https://scikit-learn.org/stable/auto_examples/cluster/plot_agglomerative_dendrogram.html) — linkage matrix construction pattern
- [plotly UMAP/t-SNE projections](https://plotly.com/python/t-sne-and-umap-projections/) — px.scatter_3d and px.scatter patterns
- Python introspection via Bash: KMeans, DBSCAN, PCA, TSNE, silhouette_score, davies_bouldin_score, calinski_harabasz_score, NearestNeighbors signatures confirmed on host sklearn 1.4.2 (consistent with 1.8.0)

### Secondary (MEDIUM confidence)
- [umap-learn 0.5.8 docs](https://umap-learn.readthedocs.io/en/latest/basic_usage.html) — API parameters (0.5.8 docs; 0.5.11 API is consistent based on PyPI changelog pattern)
- [umap-learn 0.5.8 parameters](https://umap-learn.readthedocs.io/en/latest/parameters.html) — n_neighbors, min_dist guidance
- WebSearch: DBSCAN eps kNN heuristic — multiple community sources confirm NearestNeighbors + 5th-percentile pattern

### Tertiary (LOW confidence)
- [umap random_state OS variation](https://github.com/lmcinnes/umap/issues/153) — Pitfall 4 (GitHub issue, older; behavior may have improved in 0.5.11)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified in requirements.txt
- Architecture patterns: HIGH — verified against sklearn 1.8.0 docs + Phase 6 existing code
- UMAP API: MEDIUM — verified against 0.5.8 docs; 0.5.11 should be consistent (minor version bump)
- Pitfalls: HIGH for sklearn-specific; MEDIUM for UMAP cross-OS reproducibility
- iterate-unsupervised workflow: HIGH — direct mirror of iterate-model stub structure

**Research date:** 2026-04-07
**Valid until:** 2026-05-07 (stable libraries; 30-day window)
