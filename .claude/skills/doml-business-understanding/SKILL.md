---
name: doml-business-understanding
description: "Run the Business Understanding phase end-to-end: generates notebooks/01_business_understanding.ipynb and reports/business_summary.html. Requires /doml-new-project to have been run first and Docker to be running."
argument-hint: "[--guidance \"analyst direction\"]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Run the DoML Business Understanding phase end-to-end:
1. Copy the BU notebook template to notebooks/01_business_understanding.ipynb
2. Check for headerless CSVs and prompt for column names if needed
3. Execute the notebook inside Docker
4. Write an executive narrative as the first cell
5. Generate reports/business_summary.html with code hidden

Optional: pass --guidance "your direction" to provide analyst context that shapes
the interpretation cell written after execution.
</objective>

<execution_context>
@.claude/doml/workflows/business-understanding.md
</execution_context>

<context>
Guidance (optional): $ARGUMENTS
</context>

<process>
Execute the business-understanding workflow from @.claude/doml/workflows/business-understanding.md end-to-end.
</process>
