---
name: doml-anomaly-detection
description: "Run optional anomaly detection after doml-data-understanding: generates notebooks/anomaly_detection.ipynb, reports/anomaly_report.html, and data/processed/anomaly_flags_{filename}.csv using Isolation Forest, LOF, and DBSCAN. Requires Docker to be running."
argument-hint: "[--file path/to/file] [--guidance \"analyst direction\"]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Run the DoML Anomaly Detection phase end-to-end:
1. Validate project state and read config.json
2. Parse optional --file (override default input) and --guidance (shapes narrative)
3. Run tidy data validation before any analysis (ANOM-02)
4. Copy the anomaly_detection.ipynb template and execute inside Docker
5. Write an anomaly detection executive narrative (findings + treatment recommendations)
6. Generate reports/anomaly_report.html with code hidden (ANOM-03)
7. Verify anomaly_flags_{filename}.csv was written to data/processed/ (ANOM-04)
</objective>

<execution_context>
@.claude/doml/workflows/anomaly-detection.md
</execution_context>

<context>
Arguments (optional): $ARGUMENTS
</context>

<process>
Execute the anomaly-detection workflow from @.claude/doml/workflows/anomaly-detection.md end-to-end.
</process>
