import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


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

    # Notebook identity: tags leaderboard rows so a re-run replaces its own rows.
    import re as _re

    NB_STEM = _Path(__file__).stem
    _m = _re.search(r"_(v\d+)$", NB_STEM)
    NB_VERSION = _m.group(1) if _m else "v1"
    # Scrollable tables: marimo embeds only the first page (10 rows) of a table in
    # static HTML exports. table() embeds up to max_rows rows in a vertically
    # scrollable box; horizontal scrolling still works. marimo caps page_size at
    # 200, so at most 200 rows are embedded; a note above the table says so.
    def table(obj, max_rows=200, max_height=480):
        try:
            import pandas as _pd
        except ImportError:
            return obj
        if type(obj).__name__ == "Styler":
            obj = obj.data
        if isinstance(obj, _pd.Series):
            obj = obj.to_frame()
        if not isinstance(obj, _pd.DataFrame):
            return obj
        _n = len(obj)
        max_rows = max(1, min(int(max_rows), 200))  # marimo: page_size <= 200
        _shown = obj.head(max_rows)
        _t = mo.ui.table(
            _shown,
            pagination=False,
            page_size=max(len(_shown), 1),
            selection=None,
            max_height=max_height,
        )
        if _n > max_rows:
            return mo.vstack([
                mo.md(f"*Showing the first {max_rows:,} of {_n:,} rows. "
                      f"The full data is in the source file; it is not embedded in this report.*"),
                _t,
            ])
        return _t

    return (NB_VERSION, narrative, table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Clustering Modelling
    **DoML Phase 7 — Unsupervised: Clustering**
    Python-only template. Covers KMeans, DBSCAN, and hierarchical clustering with internal evaluation metrics and UMAP visualization.
    """)
    return


@app.cell(hide_code=True)
def _(narrative):
    narrative("summary", "")
    return


@app.cell(hide_code=True)
def _(narrative):
    narrative("direction", "")
    return


@app.cell
def _():
    import os, random
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import json
    from pathlib import Path
    from datetime import date

    # Reproducibility (REPR-01)
    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)

    # scikit-learn
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler, OrdinalEncoder
    from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
    from sklearn.neighbors import NearestNeighbors

    # scipy
    from scipy.cluster.hierarchy import dendrogram
    from scipy.stats import f_oneway

    # umap
    import umap

    return (
        AgglomerativeClustering,
        DBSCAN,
        KMeans,
        NearestNeighbors,
        OrdinalEncoder,
        Path,
        SEED,
        StandardScaler,
        calinski_harabasz_score,
        date,
        davies_bouldin_score,
        dendrogram,
        f_oneway,
        json,
        np,
        os,
        pd,
        plt,
        silhouette_score,
        umap,
    )


@app.cell
def _(Path, json, mo, os):
    with mo.redirect_stdout():
        PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', str(mo.notebook_dir().parent)))
        config_path = PROJECT_ROOT / '.planning' / 'config.json'
        config = json.load(open(config_path))
        problem_type = config.get('problem_type', 'clustering')
        assert problem_type == 'clustering', f"Expected problem_type='clustering', got '{problem_type}'"
        dataset_path = config.get('dataset', {}).get('path', '')
        print(f"Problem type: {problem_type}")
        print(f"Dataset: {dataset_path}")
    return PROJECT_ROOT, dataset_path


@app.cell
def _(PROJECT_ROOT, dataset_path, mo, pd, table):
    with mo.redirect_stdout():
        # Load preprocessed data (output of Phase 6a preprocessing notebook)
        # Falls back to raw data with a warning if preprocessed file not found
        import glob

        preprocessed_pattern = str(PROJECT_ROOT / 'data' / 'processed' / 'preprocessed_*')
        preprocessed_files = glob.glob(preprocessed_pattern)

        if preprocessed_files:
            data_path = preprocessed_files[0]
            print(f"Loading preprocessed data: {data_path}")
            df_raw = pd.read_csv(data_path)
        else:
            raw_path = PROJECT_ROOT / dataset_path  # dataset.path is project-relative, e.g. data/raw/x.csv
            if not raw_path.is_file():
                raw_path = PROJECT_ROOT / 'data' / 'raw' / dataset_path
            print(f"WARNING: No preprocessed_* file found. Loading raw data: {raw_path}")
            print("Consider running Phase 6a (preprocessing) first for better results.")
            df_raw = pd.read_csv(raw_path)

        print(f"Shape: {df_raw.shape}")
        mo.output.append(table(df_raw.head()))
    return (df_raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Preprocessing
    Clustering and distance-based algorithms require scaled features. Categorical columns are encoded with OrdinalEncoder for distance computation (not model interpretation).
    """)
    return


@app.cell
def _(df_raw, mo):
    with mo.redirect_stdout():
        # Fill remaining NaN with column median (numeric) or mode (categorical)
        numeric_cols = df_raw.select_dtypes(include='number').columns.tolist()
        cat_cols = df_raw.select_dtypes(exclude='number').columns.tolist()

        df = df_raw.copy()
        for _col in numeric_cols:
            if df[_col].isna().any():
                df[_col].fillna(df[_col].median(), inplace=True)
        for _col in cat_cols:
            if df[_col].isna().any():
                df[_col].fillna(df[_col].mode()[0], inplace=True)

        print(f"NaN remaining: {df.isna().sum().sum()}")
    return cat_cols, df


@app.cell
def _(OrdinalEncoder, cat_cols, df, mo):
    with mo.redirect_stdout():
        # Encode categorical columns for distance computation
        # Note: OrdinalEncoder is used here for distance/variance computation, not model interpretation.
        # For interpretation, refer back to the original column values.
        if cat_cols:
            enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            df[cat_cols] = enc.fit_transform(df[cat_cols])
            print(f"OrdinalEncoder applied to: {cat_cols}")
        else:
            print("No categorical columns to encode.")
    return


@app.cell
def _(StandardScaler, df, mo, pd):
    with mo.redirect_stdout():
        # Scale all features to zero mean, unit variance
        # RobustScaler is recommended if EDA flagged heavy outliers — change `scaler` variable below
        scaler = StandardScaler()
        # scaler = RobustScaler()  # uncomment if heavy outliers present

        X_scaled = scaler.fit_transform(df)
        X_df = pd.DataFrame(X_scaled, columns=df.columns)
        feature_names = df.columns.tolist()
        print(f"Scaled features: {len(feature_names)}")
        print(f"X_scaled shape: {X_scaled.shape}")
    return X_df, X_scaled, feature_names


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## KMeans Clustering
    Elbow method (inertia vs k) and silhouette sweep (k=2..12). Select optimal k from both plots.
    Default: k from silhouette peak (argmax). Review the elbow plot to confirm.
    """)
    return


@app.cell
def _(KMeans, SEED, X_scaled, mo, np, plt, silhouette_score):
    with mo.redirect_stdout():
        K_RANGE = range(2, 13)
        inertias, silhouettes = [], []

        for k in K_RANGE:
            km = KMeans(n_clusters=k, init='k-means++', random_state=SEED, n_init='auto')
            km.fit(X_scaled)
            inertias.append(km.inertia_)
            silhouettes.append(silhouette_score(X_scaled, km.labels_))

        # Best k from silhouette peak
        best_k = list(K_RANGE)[np.argmax(silhouettes)]
        print(f"Best k (silhouette peak): {best_k}")

        _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        ax1.plot(list(K_RANGE), inertias, 'bo-')
        ax1.set_xlabel('k'); ax1.set_ylabel('Inertia')
        ax1.set_title('Elbow Method — KMeans Inertia')
        ax1.axvline(best_k, color='red', linestyle='--', label=f'Silhouette peak k={best_k}')
        ax1.legend()

        ax2.plot(list(K_RANGE), silhouettes, 'gs-')
        ax2.set_xlabel('k'); ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Silhouette Score vs k')
        ax2.axvline(best_k, color='red', linestyle='--', label=f'Peak k={best_k}')
        ax2.legend()

        plt.tight_layout()
        mo.output.append(plt.gcf()); plt.close()
    return (best_k,)


@app.cell
def _(KMeans, SEED, X_scaled, best_k, mo, pd):
    with mo.redirect_stdout():
        km_final = KMeans(n_clusters=best_k, init='k-means++', random_state=SEED, n_init='auto')
        km_final.fit(X_scaled)
        kmeans_labels = km_final.labels_
        print(f"KMeans final: k={best_k}, cluster sizes: {pd.Series(kmeans_labels).value_counts().to_dict()}")
    return (kmeans_labels,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## DBSCAN Clustering
    eps starting point: 5th percentile of kNN distances. Grid search over eps × minPts {5, 10, 15}.
    Silhouette, Davies-Bouldin, and Calinski-Harabasz computed excluding noise points (label=-1).
    """)
    return


@app.cell
def _(
    DBSCAN,
    NearestNeighbors,
    X_scaled,
    calinski_harabasz_score,
    davies_bouldin_score,
    mo,
    np,
    pd,
    silhouette_score,
):
    with mo.redirect_stdout():
        # Compute eps starting point from 5th-percentile kNN distance
        MIN_SAMPLES_REF = 5
        nn = NearestNeighbors(n_neighbors=MIN_SAMPLES_REF)
        nn.fit(X_scaled)
        distances, _ = nn.kneighbors(X_scaled)
        knn_dist = np.sort(distances[:, -1])
        eps_start = float(np.percentile(knn_dist, 5))
        print(f"eps starting point (5th percentile kNN dist): {eps_start:.4f}")

        eps_candidates = [round(eps_start * 0.5, 4), round(eps_start, 4), round(eps_start * 2.0, 4)]
        minpts_candidates = [5, 10, 15]

        dbscan_results = []
        for eps in eps_candidates:
            for minpts in minpts_candidates:
                db = DBSCAN(eps=eps, min_samples=minpts)
                labels = db.fit_predict(X_scaled)
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                noise_pct = round(100 * (labels == -1).sum() / len(labels), 1)
                mask = labels != -1
                if n_clusters >= 2 and mask.sum() > n_clusters:
                    sil = round(silhouette_score(X_scaled[mask], labels[mask]), 4)
                    db_score = round(davies_bouldin_score(X_scaled[mask], labels[mask]), 4)
                    ch_score = round(calinski_harabasz_score(X_scaled[mask], labels[mask]), 2)
                else:
                    sil = db_score = ch_score = None
                dbscan_results.append({
                    'eps': eps, 'min_samples': minpts,
                    'n_clusters': n_clusters, 'noise_pct': noise_pct,
                    'silhouette': sil, 'davies_bouldin': db_score, 'calinski_harabasz': ch_score
                })

        dbscan_df = pd.DataFrame(dbscan_results)
        print(dbscan_df.to_string(index=False))
    return dbscan_df, eps_start


@app.cell
def _(DBSCAN, X_scaled, dbscan_df, eps_start, kmeans_labels, mo, pd):
    with mo.redirect_stdout():
        # Select best DBSCAN config: highest silhouette (excluding None)
        valid_dbscan = dbscan_df[dbscan_df['silhouette'].notna()].copy()
        if len(valid_dbscan) > 0:
            best_dbscan_row = valid_dbscan.loc[valid_dbscan['silhouette'].idxmax()]
            best_eps = best_dbscan_row['eps']
            best_minpts = int(best_dbscan_row['min_samples'])
            print(f"Best DBSCAN: eps={best_eps}, min_samples={best_minpts}")
            db_best = DBSCAN(eps=best_eps, min_samples=best_minpts)
            dbscan_labels = db_best.fit_predict(X_scaled)
        else:
            print("WARNING: No valid DBSCAN config found (all produced < 2 clusters). Using kmeans_labels as fallback.")
            dbscan_labels = kmeans_labels
            best_eps, best_minpts = eps_start, 5
        print(f"DBSCAN cluster sizes: {pd.Series(dbscan_labels).value_counts().to_dict()}")
    return best_eps, best_minpts, dbscan_labels


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Hierarchical Clustering (Ward Linkage)
    Dendrogram shows the full merge tree truncated to last 30 merges.
    Review the dendrogram and set `hierarchical_k` in the next cell to your chosen cluster count.
    """)
    return


@app.cell
def _(AgglomerativeClustering, X_scaled, dendrogram, mo, np, plt):
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

    # Must use distance_threshold=0, n_clusters=None to get distances_ attribute
    hc_tree = AgglomerativeClustering(distance_threshold=0, n_clusters=None, linkage='ward')
    hc_tree.fit(X_scaled)

    _fig, _ax = plt.subplots(figsize=(14, 6))
    plot_dendrogram(hc_tree, truncate_mode='lastp', p=30,
                    leaf_rotation=90, leaf_font_size=8, ax=_ax)
    _ax.set_title('Hierarchical Clustering Dendrogram (Ward, last 30 merges)')
    _ax.set_xlabel('Sample index or cluster size')
    _ax.set_ylabel('Distance')
    plt.tight_layout()
    mo.output.append(plt.gcf()); plt.close()
    return


@app.cell
def _(mo):
    with mo.redirect_stdout():
        # ANALYST: Review the dendrogram above and set your chosen cluster count below
        hierarchical_k = 3  # <-- CHANGE THIS based on dendrogram review
        print(f"hierarchical_k set to: {hierarchical_k}")
    return (hierarchical_k,)


@app.cell
def _(AgglomerativeClustering, X_scaled, hierarchical_k, mo, pd):
    with mo.redirect_stdout():
        # Second instance with n_clusters=hierarchical_k for final assignments
        hc_final = AgglomerativeClustering(n_clusters=hierarchical_k, linkage='ward')
        hierarchical_labels = hc_final.fit_predict(X_scaled)
        print(f"Hierarchical cluster sizes: {pd.Series(hierarchical_labels).value_counts().to_dict()}")
    return (hierarchical_labels,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Internal Metric Comparison
    Silhouette ↑ (higher is better), Davies-Bouldin ↓ (lower is better), Calinski-Harabasz ↑ (higher is better).
    Metrics computed on valid (non-noise) points only. Best method highlighted.
    """)
    return


@app.cell
def _(
    X_scaled,
    best_eps,
    best_k,
    best_minpts,
    calinski_harabasz_score,
    davies_bouldin_score,
    dbscan_labels,
    hierarchical_k,
    hierarchical_labels,
    kmeans_labels,
    mo,
    pd,
    silhouette_score,
):
    with mo.redirect_stdout():
        def compute_metrics(X, labels, method_name, params_str):
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

        metrics_rows = [
            compute_metrics(X_scaled, kmeans_labels, 'KMeans', f'k={best_k}'),
            compute_metrics(X_scaled, dbscan_labels, 'DBSCAN', f'eps={best_eps},min_samples={best_minpts}'),
            compute_metrics(X_scaled, hierarchical_labels, 'Hierarchical', f'Ward,k={hierarchical_k}'),
        ]

        metrics_df = pd.DataFrame(metrics_rows)
        print(metrics_df.to_string(index=False))

        # Identify best method by silhouette
        valid_metrics = metrics_df[metrics_df['silhouette'].notna()]
        best_method_row = valid_metrics.loc[valid_metrics['silhouette'].idxmax()]
        best_method = best_method_row['method']
        print(f"\nBest method (highest silhouette): {best_method}")

        # Assign best_labels for downstream use
        if best_method == 'KMeans':
            best_labels = kmeans_labels
        elif best_method == 'DBSCAN':
            best_labels = dbscan_labels
        else:
            best_labels = hierarchical_labels
    return best_labels, best_method, metrics_rows


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cluster Feature Importance (ANOVA F-Statistic)
    Per-feature ANOVA F-statistic across clusters. High F = feature strongly separates clusters.
    Note: This is NOT SHAP — SHAP requires a supervised target variable and does not apply to clustering.
    """)
    return


@app.cell
def _(X_df, best_labels, f_oneway, feature_names, mo, pd):
    with mo.redirect_stdout():
        # Use best_labels for feature importance (non-noise only)
        mask_best = best_labels != -1
        df_valid = X_df[mask_best].copy()
        df_valid['cluster'] = best_labels[mask_best]

        f_stats = {}
        for _col in feature_names:
            groups = [group[_col].values for _, group in df_valid.groupby('cluster')]
            if len(groups) >= 2:
                f_val, p_val = f_oneway(*groups)
                f_stats[_col] = {'f_statistic': round(float(f_val), 4), 'p_value': round(float(p_val), 6)}
            else:
                f_stats[_col] = {'f_statistic': None, 'p_value': None}

        feature_importance_df = (pd.DataFrame(f_stats).T
                                  .sort_values('f_statistic', ascending=False)
                                  .reset_index()
                                  .rename(columns={'index': 'feature'}))
        print("Top features driving cluster separation:")
        print(feature_importance_df.head(20).to_string(index=False))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## UMAP 2D Visualization
    UMAP preserves local and global structure. Points colored by best-method cluster assignment.
    Note: UMAP is distance-based — always scale features before embedding (done above).
    Cross-OS UMAP reproducibility may vary even with random_state set (numba JIT variation).
    """)
    return


@app.cell
def _(SEED, X_scaled, best_labels, best_method, mo, plt, umap):
    reducer_2d = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                            random_state=SEED, init='spectral')
    embedding_2d = reducer_2d.fit_transform(X_scaled)

    _fig, _ax = plt.subplots(figsize=(10, 8))
    scatter = _ax.scatter(embedding_2d[:, 0], embedding_2d[:, 1],
                         c=best_labels, cmap='tab10', alpha=0.7, s=15)
    plt.colorbar(scatter, ax=_ax, label='Cluster')
    _ax.set_title(f'UMAP 2D — {best_method} cluster assignments')
    _ax.set_xlabel('UMAP 1'); _ax.set_ylabel('UMAP 2')
    plt.tight_layout()
    mo.output.append(plt.gcf()); plt.close()
    return


@app.cell
def _(
    PROJECT_ROOT,
    best_labels,
    best_method,
    dbscan_labels,
    hierarchical_k,
    hierarchical_labels,
    kmeans_labels,
    mo,
    pd,
):
    with mo.redirect_stdout():
        # Write cluster assignments to data/processed/
        output_dir = PROJECT_ROOT / 'data' / 'processed'
        output_dir.mkdir(exist_ok=True)

        cluster_out = pd.DataFrame({
            'cluster_kmeans': kmeans_labels,
            'cluster_dbscan': dbscan_labels,
            f'cluster_hierarchical_k{hierarchical_k}': hierarchical_labels,
            'cluster_best': best_labels,
            'best_method': best_method,
        })
        cluster_path = output_dir / 'cluster_assignments.csv'
        cluster_out.to_csv(cluster_path, index=False)
        print(f"Cluster assignments written to: {cluster_path}")
    return


@app.cell
def _(NB_VERSION, PROJECT_ROOT, date, metrics_rows, mo, pd):
    with mo.redirect_stdout():
        # Append results to models/unsupervised_leaderboard.csv (append-only — do not overwrite)
        unsup_lb_path = PROJECT_ROOT / 'models' / 'unsupervised_leaderboard.csv'
        (PROJECT_ROOT / 'models').mkdir(exist_ok=True)

        new_rows = []
        for row in metrics_rows:
            if row['silhouette'] is not None:
                new_rows.append({
                    'iteration': 1,
                    'problem_type': 'clustering',
                    'method': row['method'],
                    'params': row['params'],
                    'n_clusters': row['n_clusters'],
                    'silhouette': row['silhouette'],
                    'davies_bouldin': row['davies_bouldin'],
                    'calinski_harabasz': row['calinski_harabasz'],
                    'notes': 'initial run',
                    'notebook_version': NB_VERSION,
                    'run_date': str(date.today()),
                })

        new_df = pd.DataFrame(new_rows)
        if unsup_lb_path.exists():
            existing = pd.read_csv(unsup_lb_path)
            # A re-run of the same notebook replaces its own rows and keeps its iteration number.
            _mine = existing['notebook_version'] == new_df['notebook_version'].iloc[0] if 'notebook_version' in existing.columns else existing['iteration'] < 0
            next_iter = int(existing.loc[_mine, 'iteration'].iloc[0]) if _mine.any() else (int(existing['iteration'].max()) + 1 if len(existing) else 1)
            existing = existing[~_mine]
            new_df['iteration'] = next_iter
            combined = pd.concat([existing, new_df], ignore_index=True)
        else:
            combined = new_df

        combined.to_csv(unsup_lb_path, index=False)
        print(f"Unsupervised leaderboard updated: {unsup_lb_path}")
        print(combined[['method', 'n_clusters', 'silhouette', 'davies_bouldin', 'calinski_harabasz']].to_string(index=False))
    return


@app.cell(hide_code=True)
def _(narrative):
    narrative("interpretation", "")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Caveats

    - **Correlations are not causation.** Cluster structures found may not generalize beyond this dataset.
    - **Internal metrics are unsupervised.** Silhouette, Davies-Bouldin, and Calinski-Harabasz do not measure predictive validity — they measure structural quality within this dataset.
    - **Cluster count is a modelling choice.** The "best k" from silhouette is a heuristic starting point. Domain knowledge should inform the final choice.
    - **DBSCAN is sensitive to eps and min_samples.** The kNN 5th-percentile heuristic is a starting point — explore the grid table before selecting a final configuration.
    - **UMAP reproducibility.** UMAP uses numba JIT compilation with platform-specific variation. Exact embeddings may differ across machines even with random_state set.
    """)
    return


if __name__ == "__main__":
    app.run()
