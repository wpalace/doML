---
name: doml-execute-phase
description: "Execute a planned DoML analysis phase and produce Jupyter notebooks and stakeholder HTML reports"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - NotebookEdit
---

<objective>
Execute a planned DoML analysis phase end-to-end.

Reads the phase PLAN.md, runs each analysis task in order, produces reproducible Jupyter notebooks in /notebooks/, and generates stakeholder HTML reports in /reports/ via nbconvert.
</objective>

<execution_context>
@.claude/doml/workflows/execute-phase.md
</execution_context>

<context>
Phase number (optional): {{args}}
</context>

<process>
Execute the execute-phase workflow from @.claude/doml/workflows/execute-phase.md end-to-end.
</process>
