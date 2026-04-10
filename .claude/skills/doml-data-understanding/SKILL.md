---
name: doml-data-understanding
description: "Run the Data Understanding (EDA) phase end-to-end: generates notebooks/02_data_understanding.ipynb and reports/eda_report.html. Requires /doml-business-understanding to have been run first and Docker to be running."
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
Run the DoML Data Understanding (EDA) phase end-to-end:
1. Detect language (Python/R) from config.json
2. Check for headerless CSVs and prompt for column names if needed
3. Copy the appropriate EDA notebook template
4. Execute the notebook inside Docker
5. Write an EDA executive narrative as the first cell
6. Generate reports/eda_report.html with code hidden

Optional: pass --guidance "your direction" to provide analyst context that shapes
the EDA interpretation cell written after execution.
</objective>

<execution_context>
@.claude/doml/workflows/data-understanding.md
</execution_context>

<context>
Guidance (optional): $ARGUMENTS
</context>

<process>
Execute the data-understanding workflow from @.claude/doml/workflows/data-understanding.md end-to-end.
</process>
