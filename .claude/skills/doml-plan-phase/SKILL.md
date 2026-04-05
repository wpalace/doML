---
name: doml-plan-phase
description: "Create a detailed analysis phase plan (PLAN.md) for a DoML project phase"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

<objective>
Create an executable analysis phase plan for a DoML project phase.

Reads the project's ROADMAP.md and STATE.md to determine the next unplanned phase, then produces a PLAN.md file that an executor agent can run to produce reproducible analysis notebooks.
</objective>

<execution_context>
@.claude/doml/workflows/plan-phase.md
</execution_context>

<context>
Phase number (optional): {{args}}
</context>

<process>
Execute the plan-phase workflow from @.claude/doml/workflows/plan-phase.md end-to-end.
</process>
