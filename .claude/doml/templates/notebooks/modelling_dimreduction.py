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
    return NB_VERSION, narrative


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Dimensionality Reduction
    **DoML Phase 7 — Unsupervised: Dimensionality Reduction**
    Python-only template. Covers PCA (variance explained, biplot, loadings), UMAP (2D/3D/sensitivity), and t-SNE (perplexity sweep).
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

    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler, OrdinalEncoder
    from sklearn.manifold import TSNE
    import umap
    import plotly.express as px

    return (
        OrdinalEncoder,
        PCA,
        Path,
        SEED,
        StandardScaler,
        TSNE,
        date,
        json,
        np,
        os,
        pd,
        plt,
        px,
        umap,
    )


@app.cell
def _(Path, json, mo, os):
    with mo.redirect_stdout():
        PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', str(mo.notebook_dir().parent)))
        config_path = PROJECT_ROOT / '.planning' / 'config.json'
        config = json.load(open(config_path))
        problem_type = config.get('problem_type', 'dimensionality_reduction')
        assert problem_type == 'dimensionality_reduction', (
            f"Expected problem_type='dimensionality_reduction', got '{problem_type}'"
        )
        dataset_path = config.get('dataset', {}).get('path', '')
        print(f"Problem type: {problem_type}")
        print(f"Dataset: {dataset_path}")
    return PROJECT_ROOT, dataset_path


@app.cell
def _(PROJECT_ROOT, dataset_path, mo, pd):
    with mo.redirect_stdout():
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
        mo.output.append(df_raw.head())
    return (df_raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Preprocessing
    PCA and UMAP are variance/distance-based — scaling is mandatory. Categorical columns encoded with OrdinalEncoder for distance computation.
    """)
    return


@app.cell
def _(df_raw, mo):
    with mo.redirect_stdout():
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
        if cat_cols:
            enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            df[cat_cols] = enc.fit_transform(df[cat_cols])
            print(f"OrdinalEncoder applied to: {cat_cols}")
        else:
            print("No categorical columns to encode.")
    return


@app.cell
def _(StandardScaler, df, mo):
    with mo.redirect_stdout():
        # RobustScaler alternative if EDA flagged heavy outliers
        scaler = StandardScaler()
        # scaler = RobustScaler()  # uncomment if heavy outliers present

        X_scaled = scaler.fit_transform(df)
        feature_names = df.columns.tolist()
        print(f"Scaled features: {len(feature_names)}, shape: {X_scaled.shape}")
    return X_scaled, feature_names


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Principal Component Analysis (PCA)
    Scree plot shows explained variance per component and cumulative threshold annotations (80%, 90%, 95%).
    Biplot shows PC1/PC2 score scatter overlaid with feature loading arrows.
    Component loadings table shows top 5 features per principal component.
    """)
    return


@app.cell
def _(PCA, SEED, X_scaled, mo, np, plt):
    with mo.redirect_stdout():
        pca_full = PCA(random_state=SEED)
        pca_full.fit(X_scaled)

        evr = pca_full.explained_variance_ratio_
        cumulative = np.cumsum(evr)

        n_80 = int(np.argmax(cumulative >= 0.80)) + 1
        n_90 = int(np.argmax(cumulative >= 0.90)) + 1
        n_95 = int(np.argmax(cumulative >= 0.95)) + 1

        print(f"Components to reach 80% variance: {n_80}")
        print(f"Components to reach 90% variance: {n_90}")
        print(f"Components to reach 95% variance: {n_95}")

        n_plot = min(30, len(evr))
        _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        ax1.bar(range(1, n_plot + 1), evr[:n_plot])
        ax1.set_xlabel('Component'); ax1.set_ylabel('Explained Variance Ratio')
        ax1.set_title('PCA Scree Plot')

        ax2.plot(range(1, n_plot + 1), cumulative[:n_plot], 'b-o', markersize=4)
        ax2.axhline(0.80, color='orange', linestyle='--', label=f'80% ({n_80} components)')
        ax2.axhline(0.90, color='red', linestyle='--', label=f'90% ({n_90} components)')
        ax2.axhline(0.95, color='darkred', linestyle='--', label=f'95% ({n_95} components)')
        ax2.axvline(n_80, color='orange', linestyle=':', alpha=0.5)
        ax2.axvline(n_90, color='red', linestyle=':', alpha=0.5)
        ax2.axvline(n_95, color='darkred', linestyle=':', alpha=0.5)
        ax2.set_xlabel('Number of Components'); ax2.set_ylabel('Cumulative Explained Variance')
        ax2.set_title('Cumulative Variance Explained')
        ax2.legend(fontsize=9)
        ax2.set_ylim(0, 1.05)

        plt.tight_layout()
        mo.output.append(plt.gcf()); plt.close()
    return evr, n_80, n_90


@app.cell
def _(PCA, SEED, X_scaled, evr, feature_names, mo, np, plt):
    pca_2d = PCA(n_components=2, random_state=SEED)
    scores = pca_2d.fit_transform(X_scaled)
    loadings = pca_2d.components_  # shape (2, n_features)

    # Scale loading arrows to match score range (Pitfall 5: scale mismatch)
    scale = np.max(np.abs(scores)) / np.max(np.abs(loadings))

    _fig, _ax = plt.subplots(figsize=(10, 8))
    _ax.scatter(scores[:, 0], scores[:, 1], alpha=0.4, s=15, c='steelblue', label='Samples')

    for _i, _feat in enumerate(feature_names):
        _ax.arrow(0, 0, loadings[0, _i] * scale, loadings[1, _i] * scale,
                 head_width=0.05 * scale, head_length=0.05 * scale, fc='red', ec='red', alpha=0.7)
        _ax.text(loadings[0, _i] * scale * 1.1, loadings[1, _i] * scale * 1.1,
                _feat, color='red', fontsize=7)

    _ax.set_xlabel(f'PC1 ({evr[0]:.1%} variance)')
    _ax.set_ylabel(f'PC2 ({evr[1]:.1%} variance)')
    _ax.set_title('PCA Biplot — PC1 vs PC2 with Feature Loadings')
    plt.tight_layout()
    mo.output.append(plt.gcf()); plt.close()
    return


@app.cell
def _(PCA, SEED, X_scaled, evr, feature_names, mo, pd):
    with mo.redirect_stdout():
        # Top 5 features per component (by absolute loading weight)
        n_top = 5
        n_components_table = min(5, len(evr))
        loadings_full = PCA(n_components=n_components_table, random_state=SEED).fit(X_scaled).components_

        print(f"Top {n_top} feature loadings per principal component:\n")
        for i in range(n_components_table):
            comp_loadings = pd.Series(loadings_full[i], index=feature_names)
            top_features = comp_loadings.abs().nlargest(n_top)
            print(f"PC{i+1} ({evr[i]:.1%} variance):")
            for _feat in top_features.index:
                print(f"  {_feat:30s}  {comp_loadings[_feat]:+.4f}")
            print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## UMAP Embeddings
    UMAP (Uniform Manifold Approximation and Projection) preserves both local and global structure.
    Default: n_neighbors=15, min_dist=0.1. Sensitivity analysis shows effect of n_neighbors ∈ {5, 15, 30}.
    Note: UMAP embeddings are not pixel-reproducible across OS/hardware even with random_state set (numba JIT variation).
    """)
    return


@app.cell
def _(SEED, X_scaled, df_raw, mo, plt, umap):
    reducer_2d = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                            random_state=SEED, init='spectral')
    embedding_2d = reducer_2d.fit_transform(X_scaled)

    # Color by first categorical column if available, else uniform color
    label_col = None
    for _col in df_raw.select_dtypes(exclude='number').columns:
        label_col = _col
        break

    _fig, _ax = plt.subplots(figsize=(10, 8))
    if label_col is not None:
        labels = df_raw[label_col].astype('category')
        scatter = _ax.scatter(embedding_2d[:, 0], embedding_2d[:, 1],
                             c=labels.cat.codes, cmap='tab10', alpha=0.7, s=15)
        _ax.set_title(f'UMAP 2D (colored by {label_col})')
    else:
        _ax.scatter(embedding_2d[:, 0], embedding_2d[:, 1], alpha=0.7, s=15)
        _ax.set_title('UMAP 2D Embedding')
    _ax.set_xlabel('UMAP 1'); _ax.set_ylabel('UMAP 2')
    plt.tight_layout()
    mo.output.append(plt.gcf()); plt.close()
    return embedding_2d, label_col


@app.cell
def _(SEED, X_scaled, df_raw, label_col, mo, px, umap):
    reducer_3d = umap.UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=SEED)
    embedding_3d = reducer_3d.fit_transform(X_scaled)

    color_col = df_raw[label_col].astype(str) if label_col else None

    fig_3d = px.scatter_3d(
        x=embedding_3d[:, 0], y=embedding_3d[:, 1], z=embedding_3d[:, 2],
        color=color_col,
        labels={'x': 'UMAP 1', 'y': 'UMAP 2', 'z': 'UMAP 3', 'color': label_col or 'Point'},
        title='UMAP 3D Embedding (interactive)',
        opacity=0.7
    )
    fig_3d.update_traces(marker_size=3)
    mo.output.append(fig_3d)
    return


@app.cell
def _(SEED, X_scaled, mo, plt, umap):
    _fig, _axes = plt.subplots(1, 3, figsize=(18, 5))
    for _ax, n_nb in zip(_axes, [5, 15, 30]):
        reducer = umap.UMAP(n_components=2, n_neighbors=n_nb, min_dist=0.1,
                            random_state=SEED, init='spectral')
        _emb = reducer.fit_transform(X_scaled)
        _ax.scatter(_emb[:, 0], _emb[:, 1], alpha=0.5, s=8)
        _ax.set_title(f'UMAP n_neighbors={n_nb}')
        _ax.set_xlabel('UMAP 1'); _ax.set_ylabel('UMAP 2')
    plt.suptitle('UMAP n_neighbors Sensitivity', fontsize=13)
    plt.tight_layout()
    mo.output.append(plt.gcf()); plt.close()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## t-SNE Visualization
    t-SNE (t-Distributed Stochastic Neighbor Embedding) is a visualization technique.
    **Important limitation:** Inter-cluster distances in t-SNE are NOT meaningful — only within-cluster structure is interpretable.
    Perplexity sweep shows how cluster structure changes with perplexity ∈ {5, 30, 50}.
    For datasets with >50 features, PCA pre-reduction to 50 components is applied before t-SNE for speed.
    """)
    return


@app.cell
def _(PCA, SEED, TSNE, X_scaled, mo, plt):
    with mo.redirect_stdout():
        # Pre-reduce with PCA if n_features > 50 (Pitfall 6: t-SNE slow on high-dim data)
        if X_scaled.shape[1] > 50:
            print(f"n_features={X_scaled.shape[1]} > 50 — pre-reducing with PCA to 50 components before t-SNE")
            pca_pre = PCA(n_components=50, random_state=SEED)
            X_tsne_input = pca_pre.fit_transform(X_scaled)
        else:
            X_tsne_input = X_scaled
            print(f"n_features={X_scaled.shape[1]} — using scaled features directly for t-SNE")

        # NOTE: use max_iter=1000 (not n_iter — parameter renamed in sklearn 1.5; we're on 1.8.0)
        _fig, _axes = plt.subplots(1, 3, figsize=(18, 5))
        for _ax, perp in zip(_axes, [5, 30, 50]):
            tsne = TSNE(n_components=2, perplexity=perp, random_state=SEED,
                        learning_rate='auto', init='pca', max_iter=1000)
            _emb = tsne.fit_transform(X_tsne_input)
            _ax.scatter(_emb[:, 0], _emb[:, 1], alpha=0.5, s=8)
            _ax.set_title(f't-SNE perplexity={perp}')
            _ax.set_xlabel('t-SNE 1'); _ax.set_ylabel('t-SNE 2')
        plt.suptitle('t-SNE Perplexity Sweep — visualization only; inter-cluster distances not interpretable', fontsize=11)
        plt.tight_layout()
        mo.output.append(plt.gcf()); plt.close()
    return


@app.cell
def _(PCA, PROJECT_ROOT, SEED, X_scaled, embedding_2d, mo, n_90, pd):
    with mo.redirect_stdout():
        # Write PCA (n_90-dimensional) and UMAP 2D to data/processed/
        output_dir = PROJECT_ROOT / 'data' / 'processed'
        output_dir.mkdir(exist_ok=True)

        # PCA reduced to n_90 components
        pca_out = PCA(n_components=n_90, random_state=SEED)
        pca_scores = pca_out.fit_transform(X_scaled)
        pca_cols = [f'PC{i+1}' for i in range(n_90)]
        pca_df = pd.DataFrame(pca_scores, columns=pca_cols)
        pca_path = output_dir / f'pca_{n_90}d.csv'
        pca_df.to_csv(pca_path, index=False)
        print(f"PCA {n_90}D written to: {pca_path}")

        # UMAP 2D
        umap_df = pd.DataFrame(embedding_2d, columns=['UMAP_1', 'UMAP_2'])
        umap_path = output_dir / 'umap_2d.csv'
        umap_df.to_csv(umap_path, index=False)
        print(f"UMAP 2D written to: {umap_path}")
    return


@app.cell
def _(NB_VERSION, PROJECT_ROOT, date, evr, mo, n_80, n_90, pd):
    with mo.redirect_stdout():
        # Append PCA variance-explained summary to unsupervised_leaderboard.csv
        unsup_lb_path = PROJECT_ROOT / 'models' / 'unsupervised_leaderboard.csv'
        (PROJECT_ROOT / 'models').mkdir(exist_ok=True)

        new_rows = [
            {
                'iteration': 1,
                'problem_type': 'dimensionality_reduction',
                'method': 'PCA',
                'params': f'n_components_full={len(evr)}',
                'n_components': n_90,
                'variance_explained_80pct': n_80,
                'variance_explained_90pct': n_90,
                'notes': 'initial run — components to reach 80%/90% variance',
                'notebook_version': NB_VERSION,
                'run_date': str(date.today()),
            },
            {
                'iteration': 1,
                'problem_type': 'dimensionality_reduction',
                'method': 'UMAP',
                'params': 'n_neighbors=15,min_dist=0.1,n_components=2',
                'n_components': 2,
                'variance_explained_80pct': None,
                'variance_explained_90pct': None,
                'notes': '2D embedding; no variance metric applicable',
                'notebook_version': NB_VERSION,
                'run_date': str(date.today()),
            },
        ]

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
        print(combined[['method', 'n_components', 'variance_explained_80pct', 'variance_explained_90pct']].to_string(index=False))
    return


@app.cell(hide_code=True)
def _(narrative):
    narrative("interpretation", "")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Caveats

    - **Correlations are not causation.** Cluster structures and dimension-reduction patterns found may not generalize beyond this dataset.
    - **t-SNE is visualization-only.** Inter-cluster distances in t-SNE scatter plots are NOT interpretable — only within-cluster density structure is meaningful. Do not use t-SNE coordinates for downstream tasks.
    - **UMAP preserves more structure than t-SNE** but is still an approximation. Use UMAP embeddings for downstream tasks with caution.
    - **PCA component count is a modelling choice.** The 80%/90%/95% thresholds are heuristics — domain knowledge should inform the choice of final dimensionality.
    - **UMAP reproducibility.** UMAP uses numba JIT compilation with platform-specific variation. Exact embeddings may differ across machines even with random_state set.
    - **Scaling is mandatory** for distance-based methods (UMAP, t-SNE) and variance-based methods (PCA). If the preprocessing section is modified, ensure scaling remains.
    """)
    return


if __name__ == "__main__":
    app.run()
