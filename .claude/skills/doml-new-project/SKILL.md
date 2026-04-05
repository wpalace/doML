---
name: doml-new-project
description: "Start a new DoML analysis project: guided kickoff interview, Docker environment, and planning artifacts"
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
Guided kickoff for a new DoML analysis project.

Runs the kickoff interview to extract business context, validates the data folder, determines ML problem type, sets language preference, and generates all planning artifacts (PROJECT.md, ROADMAP.md, STATE.md, config.json).
</objective>

<execution_context>
@.claude/doml/workflows/new-project.md
</execution_context>

<context>
Phase number (optional): {{args}}
</context>

<process>
Execute the new-project workflow from @.claude/doml/workflows/new-project.md end-to-end.
</process>
