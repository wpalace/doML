# Notes

- does claud.md state that all ML must run in the container?
- new-project.md says to use duckdb schema introspection but no skill is defined for how to do this

mkdir -p ~/source/dtest/.claude && \
  cp -r /home/bill/source/DoML/.claude/doml ~/source/dtest/.claude/ && \
  cp -r /home/bill/source/DoML/.claude/skills/doml-new-project \
        /home/bill/source/DoML/.claude/skills/doml-plan-phase \
        /home/bill/source/DoML/.claude/skills/doml-execute-phase \
        /home/bill/source/DoML/.claude/skills/doml-progress \
        ~/source/dtest/.claude/skills/ 2>/dev/null || \
    (mkdir -p ~/source/dtest/.claude/skills && \
     cp -r /home/bill/source/DoML/.claude/skills/doml-* ~/source/dtest/.claude/skills/)
cp /home/bill/source/DoML/CLAUDE.md ~/source/dtest/

task: meta-prompt-framework-evaluation
description: |

  1. cd /app && make sure the meta-prompting framework is fully configured.
  2. Pull/load exactly these 3 Ollama models: model-a, model-b, model-c.
  3. For each of the 3 golden use cases (loaded from /app/golden-cases/*.json):
       - Run the meta-framework to generate the optimized prompt.
       - Execute that prompt on each of the 3 models.
       - After each run, ask the model itself to rate "ease of use" (1-10 JSON).
  4. For every output, run 3 independent judge calls (use the same 3 models or a dedicated judge model) using the scoring rubric in /app/judge-prompt.txt.
  5. Aggregate into a final score per model + per use case + overall delta vs baseline.
  6. Write full results to /app/results/eval-report.json and /app/results/summary.md.
  7. Exit cleanly with exit code 0 if all scores computed.

# Usability Enhancements

- EDA: The table above the correlation heatmap doesn't add much value as all the data is contained in the heatmap. Please remove it.
- modelling: add --guidance
- iterate: when iterating, the baseline model should not be the dummy model, but rather the all time leader prior to the iteration
- EDA: Add a section that explains why a particular metric was choosen as the evaluation criteria and why it was preferred over other similar metrics for this problem
- EAD and BU: For timeseries where there are many files (one for each time series) where the only real difference is the data and perhapse column names (but the struture is the same), only show a preview of the first two, followed by a note that the other files follow the same pattern. This will cut down on the clutter on the report.
