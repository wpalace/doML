---
name: doml-progress
description: "Display current DoML project status, completed phases, and next recommended action"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

<objective>
Show current DoML analysis project status at a glance.

Reads .planning/STATE.md and .planning/ROADMAP.md to display: current phase, completed phases, next recommended action, and key decisions made so far.
</objective>

<execution_context>
@.claude/doml/workflows/progress.md
</execution_context>

<process>
Execute the progress workflow from @.claude/doml/workflows/progress.md end-to-end.
</process>
