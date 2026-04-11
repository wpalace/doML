---
name: doml-get-data
description: "Download datasets from Kaggle or direct URLs into data/raw/. Run standalone or invoked automatically by doml-new-project when data/raw/ is empty. Requires Docker to be running."
argument-hint: "kaggle owner/dataset-name | url https://example.com/data.csv"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Acquire a dataset into data/raw/ from Kaggle or a direct URL:
1. Parse the source type from arguments: kaggle or url
2. Check that Docker is running
3. For Kaggle: verify credentials, download + extract inside container, docker cp to host data/raw/
4. For URL: curl download to data/raw/.stage/, extract if ZIP, move supported formats to data/raw/
5. Set up Git LFS tracking for data files (graceful degrade if git-lfs not installed)
6. Compute SHA-256 hashes and file sizes, append provenance block to data/raw/README.md
7. Display download summary
</objective>

<execution_context>
@.claude/doml/workflows/get-data.md
</execution_context>

<context>
Arguments: $ARGUMENTS
</context>

<process>
Execute the get-data workflow from @.claude/doml/workflows/get-data.md end-to-end.
</process>
