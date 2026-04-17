---
phase: 18
slug: doml-iterate-deployment
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-17
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual CLI invocation + file existence checks (no test framework — skill/workflow files) |
| **Config file** | none |
| **Quick run command** | `ls .claude/skills/doml-iterate-deployment/SKILL.md .claude/doml/workflows/iterate-deployment.md` |
| **Full suite command** | See Per-Task Verification Map below |
| **Estimated runtime** | ~5 seconds (file existence + content grep checks) |

---

## Sampling Rate

- **After every task commit:** Run `ls .claude/skills/doml-iterate-deployment/SKILL.md .claude/doml/workflows/iterate-deployment.md`
- **After every plan wave:** Run full grep checks per Per-Task Verification Map
- **Before `/gsd-verify-work`:** All file-existence and content grep checks must pass
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | ITER-01 | — | N/A | file-exists | `ls .claude/skills/doml-iterate-deployment/SKILL.md` | ❌ W0 | ⬜ pending |
| 18-01-02 | 01 | 1 | ITER-01 | — | N/A | file-exists | `ls .claude/doml/workflows/iterate-deployment.md` | ❌ W0 | ⬜ pending |
| 18-01-03 | 01 | 1 | ITER-01 | — | N/A | content | `grep -q 'doml-iterate-deployment' .claude/skills/doml-iterate-deployment/SKILL.md` | ❌ W0 | ⬜ pending |
| 18-02-01 | 01 | 2 | ITER-02 | — | N/A | content | `grep -q 'v\${VERSION' .claude/doml/workflows/iterate-deployment.md` | ❌ W0 | ⬜ pending |
| 18-02-02 | 01 | 2 | ITER-03 | — | N/A | content | `grep -q 'newmodelname\|new_model\|v1/' .claude/doml/workflows/iterate-deployment.md` | ❌ W0 | ⬜ pending |
| 18-03-01 | 01 | 2 | ITER-04 | — | N/A | content | `grep -q '\-\-guidance' .claude/doml/workflows/iterate-deployment.md` | ❌ W0 | ⬜ pending |
| 18-04-01 | 01 | 3 | ITER-05 | — | N/A | content | `grep -q '\-\-target' .claude/doml/workflows/iterate-deployment.md` | ❌ W0 | ⬜ pending |
| 18-05-01 | 01 | 3 | ITER-01 | — | N/A | content | `grep -q 'deployment_report' .claude/doml/workflows/iterate-deployment.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- None — skill/workflow files are created from scratch; no pre-existing test stubs needed.

*Existing infrastructure: File-existence and grep checks are sufficient for workflow/skill artifacts.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `doml-iterate-deployment` is invokable in Claude Code | ITER-01 | Requires Claude Code runtime | Run `/doml-iterate-deployment` in a project with an existing deployment; confirm it starts the workflow |
| Leaderboard-match guard redirects correctly | ITER-01 | Requires a live leaderboard + deployment_metadata.json | Swap leaderboard leader, run command, confirm redirect message appears |
| `--guidance` shapes deployment config | ITER-04 | Requires Claude interpretation of freeform text | Run with `--guidance "optimize for low latency"` and confirm workflow references guidance text before deploying |
| Fresh deployment_report.html generated | ITER-01 | Requires Docker jupyter container | Run full iterate, confirm `reports/deployment_report.html` is regenerated with new version |
| No-new-model run completes | ITER-05 | Requires live deployment artifacts | Run without `--model` or `--guidance`, confirm new vN+1 directory is created |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
