---
name: doml-iterate-unsupervised
description: "Generate a new unsupervised modelling iteration notebook with analyst-supplied direction, run the full clustering or dimensionality reduction pipeline, and append results to models/unsupervised_leaderboard.csv for cross-iteration comparison"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

<objective>
Generate a new unsupervised modelling iteration notebook incorporating analyst-supplied direction.

Reads the most recent clustering or dimensionality reduction notebook and its Claude interpretation cell, generates a new version notebook (v{N+1}) with the specified focus, runs the full pipeline, and appends all results to `models/unsupervised_leaderboard.csv` for cross-iteration comparison.

Works for both problem types:
- `clustering`: KMeans, DBSCAN, hierarchical with internal metrics (silhouette, Davies-Bouldin, Calinski-Harabasz)
- `dimensionality_reduction`: PCA, UMAP, t-SNE with variance explained and structural analysis
</objective>

<arguments>
- **direction** (optional): A quoted string describing the analysis focus for this iteration.
  - If omitted: defaults to re-running the same pipeline with the same settings
  - Examples:
    - `/doml-iterate-unsupervised` — re-run baseline pipeline
    - `/doml-iterate-unsupervised "try DBSCAN with finer eps grid around 0.3"`
    - `/doml-iterate-unsupervised "focus on PCA — explore 5-component solution"`
    - `/doml-iterate-unsupervised "apply UMAP with n_neighbors=5 to capture local structure"`
    - `/doml-iterate-unsupervised "try k=6 for KMeans based on domain knowledge"`
    - `/doml-iterate-unsupervised "increase t-SNE perplexity range to 10-100"`
</arguments>

<execution_context>
@.claude/doml/workflows/iterate-unsupervised.md
</execution_context>

<context>
Direction (optional): {{args}}
</context>

<process>
Execute the iterate-unsupervised workflow from @.claude/doml/workflows/iterate-unsupervised.md.
</process>
