---
project: PROJECT_NAME
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
dataset: DATASET_FILE_OR_FOLDER
problem_type: unknown
language: python
---

# PROJECT_NAME

## Business Context

**Business question:**
[What decision or action will this analysis inform?]

**Stakeholder:**
[Who will act on the findings from this analysis?]

**Expected outcome:**
[What does success look like? What will the stakeholder do differently after seeing results?]

## Dataset

**Source:** data/raw/DATASET_FILE
**Format:** CSV / Parquet / Excel
**Description:** [Brief description of what the data represents]
**Collection period:** [Date range or recency of data]
**Known biases or limitations:** [Any known issues with data quality, coverage, or representativeness]

## Problem Framing

**ML problem type:** [regression / classification / clustering / time_series / dimensionality_reduction]
**Target variable:** [Column name, or "none" for unsupervised]
**Key features:** [List of columns expected to be predictive, if known]
**Time factor:** [Yes / No — Is time a relevant dimension in this dataset?]

**Decision framing:**
> We are trying to [decision] using [metric/outcome column] as a proxy.

## Language Preference

**Analysis language:** Python (default) / R (opt-in)
**Reason:** [Why this preference was selected, if non-default]

## Analysis Scope

**In scope:**
- [ ] Business Understanding notebook
- [ ] Data Understanding EDA notebook
- [ ] Stakeholder HTML reports

**Out of scope for this analysis:**
- [List any exclusions agreed with stakeholder]

## Assumptions and Constraints

- [List assumptions made about the data, problem, or domain]
- [List constraints: time, resources, stakeholder requirements]

## Caveats

- Correlation is not causation — all findings are observational unless a controlled experiment was run
- [Add domain-specific caveats here]
