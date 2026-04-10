# DoML Progress Workflow

## Purpose
Display current DoML analysis project status, completed phases, and recommended next action.

## Invoked by: /doml-progress

---

## Workflow

### Step 1 — Read project state

Read `.planning/STATE.md`. If it does not exist, display:

```
No DoML project found in this directory.

Run /doml-new-project to start a new analysis project.
```

Then stop.

### Step 2 — Read roadmap

Read `.planning/ROADMAP.md` to get the phase list and completion status.

### Step 3 — Read config (optional)

Read `.planning/config.json` if it exists. Extract `language` preference (default: Python) and `problem_type` if set.

### Step 4 — Display progress report

Output a progress report in this format:

```
DoML Project: [project_name from PROJECT.md or STATE.md]
Dataset: [dataset from config.json or STATE.md, or "not yet configured"]
Problem type: [problem_type from config.json, or "not yet determined"]
Language: [language from config.json, default Python]

Progress: [progress bar] [percent]%

Phases:
  ✅ Phase 1: [name] — [completion date if known]
  🚧 Phase 2: [name] — IN PROGRESS
  ⬜ Phase 3: [name]
  ...

Current focus: [current_focus from STATE.md]
Last activity: [last_activity from STATE.md]

Next action: [determined in Step 5]
```

Build the progress bar from `progress.percent` in STATE.md frontmatter:
- Each █ = 10%. Fill remainder with ░.
- Example: 40% → [████░░░░░░] 40%

### Step 5 — Determine next action

Route based on STATE.md `status` and phase/plan state:

| Condition | Next action message |
|-----------|---------------------|
| No phases started | Run `/doml-new-project` to begin the kickoff interview |
| Interview complete, BU not run | Run `/doml-business-understanding` to generate the Business Understanding notebook and report |
| BU complete, EDA not run | Run `/doml-data-understanding` to generate the EDA notebook and report |
| EDA complete, modelling not run | Run `/doml-modelling` to run preprocessing and modelling for your problem type |
| Modelling complete | Run `/doml-iterate-model "direction"` or `/doml-iterate-unsupervised "direction"` to refine |
| Phase in progress | Continue with the current phase — check STATE.md `stopped_at` |
| All phases complete | Run `/doml-progress` to review status, or check `reports/` for stakeholder outputs |

### Step 6 — Show key decisions (if any)

If STATE.md has a Decisions section with entries, display the last 3–5 decisions under a **Key decisions** heading.
