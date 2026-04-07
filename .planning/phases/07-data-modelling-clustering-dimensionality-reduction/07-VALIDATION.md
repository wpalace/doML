---
phase: 7
slug: data-modelling-clustering-dimensionality-reduction
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-07
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already in requirements.txt) + nbformat cell structure validation |
| **Config file** | none — validation is notebook structure inspection + file existence checks |
| **Quick run command** | `python -c "import nbformat; nb=nbformat.read('.claude/doml/templates/notebooks/modelling_clustering.ipynb',4); assert len(nb.cells)>0"` |
| **Full suite command** | `python -c "import nbformat; [nbformat.validate(nbformat.read(f,4)) for f in ['.claude/doml/templates/notebooks/modelling_clustering.ipynb','.claude/doml/templates/notebooks/modelling_dimreduction.ipynb']]"` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command (notebook valid JSON)
- **After every plan wave:** Run full suite command (both templates validate)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | MOD-03 | N/A | structure | `python -c "import nbformat; nb=nbformat.read('.claude/doml/templates/notebooks/modelling_clustering.ipynb',4); assert any('KMeans' in str(c) for c in nb.cells)"` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | MOD-03 | N/A | structure | `python -c "import nbformat; nb=nbformat.read('.claude/doml/templates/notebooks/modelling_clustering.ipynb',4); assert any('DBSCAN' in str(c) for c in nb.cells)"` | ❌ W0 | ⬜ pending |
| 07-01-03 | 01 | 1 | MOD-03 | N/A | structure | `python -c "import nbformat; nb=nbformat.read('.claude/doml/templates/notebooks/modelling_clustering.ipynb',4); assert any('silhouette' in str(c) for c in nb.cells)"` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 1 | MOD-05 | N/A | structure | `python -c "import nbformat; nb=nbformat.read('.claude/doml/templates/notebooks/modelling_dimreduction.ipynb',4); assert any('PCA' in str(c) for c in nb.cells)"` | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 1 | MOD-05 | N/A | structure | `python -c "import nbformat; nb=nbformat.read('.claude/doml/templates/notebooks/modelling_dimreduction.ipynb',4); assert any('UMAP' in str(c) for c in nb.cells)"` | ❌ W0 | ⬜ pending |
| 07-03-01 | 03 | 2 | MOD-03, MOD-05 | N/A | structure | `grep -q 'clustering\|dimensionality_reduction' .claude/doml/workflows/execute-phase.md` | ✅ | ⬜ pending |
| 07-04-01 | 04 | 2 | MOD-03 | N/A | existence | `test -f .claude/skills/doml-iterate-unsupervised/SKILL.md && test -f .claude/doml/workflows/iterate-unsupervised.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.claude/doml/templates/notebooks/modelling_clustering.ipynb` — created in Plan 07-01
- [ ] `.claude/doml/templates/notebooks/modelling_dimreduction.ipynb` — created in Plan 07-02
- [ ] `.claude/skills/doml-iterate-unsupervised/SKILL.md` — created in Plan 07-04
- [ ] `.claude/doml/workflows/iterate-unsupervised.md` — created in Plan 07-04

*These files are the primary artifacts — their creation IS the wave 0 deliverable.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Notebook executes end-to-end in Docker with a real dataset | MOD-03, MOD-05 | Requires Docker + dataset | `docker compose exec jupyter papermill notebooks/0N_modelling_clustering_v1.ipynb /dev/null` |
| UMAP 2D scatter shows cluster colors correctly | MOD-03 | Visual inspection | Run clustering notebook, view UMAP cell output |
| Dendrogram renders and hierarchical_k cell is editable | MOD-03 | Visual + interactive | Run clustering notebook through dendrogram cell |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
