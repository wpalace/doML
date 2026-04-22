---
phase: 21
slug: copilot-support-target-flag
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-22
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash (manual shell tests) |
| **Config file** | none — shell script testing |
| **Quick run command** | `bash install.sh --help` |
| **Full suite command** | `bash install.sh --target both --dry-run 2>/dev/null || bash install.sh --version` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bash install.sh --help`
- **After every plan wave:** Run full smoke test for both targets
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | COP-01 | — | N/A | unit | `test -f AGENTS.md && echo OK` | ❌ W0 | ⬜ pending |
| 21-01-02 | 01 | 1 | COP-02 | — | N/A | unit | `test -f .github/copilot-instructions.md && echo OK` | ❌ W0 | ⬜ pending |
| 21-01-03 | 01 | 1 | COP-03/04 | — | N/A | unit | `ls .github/skills/doml-*/SKILL.md 2>/dev/null | wc -l` | ❌ W0 | ⬜ pending |
| 21-02-01 | 02 | 2 | INST-07 | — | N/A | integration | `bash install.sh --target claude --help` | ✅ | ⬜ pending |
| 21-02-02 | 02 | 2 | INST-08 | — | N/A | integration | `bash install.sh --target copilot --help` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing `install.sh` and `install.ps1` are the test harness — no new test framework needed

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Copilot prompts invocable via `#doml-new-project` in VS Code | COP-04 | Requires VS Code + GitHub Copilot Chat extension | Open VS Code, type `#doml-new-project` in Copilot Chat, verify skill resolves |
| `--target copilot` generates `.github/skills/` structure | COP-04 | Requires archive download or dry-run | Run `bash install.sh --target copilot` in a temp dir and inspect output |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
