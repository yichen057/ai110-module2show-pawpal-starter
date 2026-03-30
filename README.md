# PawPal+

PawPal+ is a Streamlit app for planning daily pet care. It combines a simple UI with a scheduling engine that sorts tasks, respects time windows, warns about conflicts, and explains why each task was placed where it was.

## 📸 Demo

[View PawPal+ screenshots (PDF)](/course_images/ai110/PawPal+Screenshots.pdf)

## Overview

PawPal+ helps a pet owner organize care tasks such as walks, feeding, medication, grooming, and enrichment. The system models owners, pets, tasks, and schedules as separate classes, then uses a `Scheduler` to build a feasible day plan from those inputs.

## Features

- Priority-based scheduling so high-priority tasks are placed first.
- Optional time-based sorting to preview tasks in chronological order.
- Time window constraints with `earliest_start` and `latest_start`.
- Daily, weekly, and twice-daily recurrence support.
- Conflict detection for overlapping tasks.
- Exact-start conflict warnings for tasks that begin at the same time.
- Conflict resolution strategies: `priority`, `shortest`, and `reschedule`.
- Multi-criteria task filtering by pet, completion status, priority, and duration.
- Input validation on `Task`, `Pet`, and `Owner` to reject invalid data early.
- Reason strings on scheduled tasks so the UI can explain scheduler decisions.
- Streamlit schedule display with status blocks, warnings, and table-based output.

## System Architecture

The final implementation includes these core classes:

- `Owner`: stores pets, owner limits, and task filtering helpers.
- `Pet`: stores a pet profile and its task list.
- `Task`: stores task details, recurrence metadata, and completion state.
- `ScheduledTask`: links a task to a pet and a specific start/end time.
- `Schedule`: stores the generated plan, total duration, feasibility, and notes.
- `Scheduler`: contains the sorting, scheduling, recurrence expansion, conflict detection, feasibility checks, and conflict resolution logic.

Final UML files:

- [uml_final.mmd](./uml_final.mmd)
- [uml_final.png](./uml_final.png)

## Project Structure

```text
.
├── app.py
├── pawpal_system.py
├── test/test_pawpal.py
├── uml_final.mmd
├── uml_final.png
└── reflection.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The App

```bash
streamlit run app.py
```

## How To Use

1. Add one or more pets.
2. Add tasks with duration, priority, and optional time windows.
3. Review the task queue preview to see sorted and filtered tasks.
4. Generate the schedule.
5. Review the final plan, including warnings and schedule explanations.

## Scheduling Algorithms

### Sorting

- `sort_by_priority()` orders tasks by highest priority first, then by shortest duration.
- `sort_by_time()` orders tasks by earliest allowed start time, then priority.

### Slot Selection

- `_find_available_slot()` uses candidate start times and a 15-minute grid to find a valid gap.
- The scheduler exits early if total scheduled time would exceed `max_daily_time`.

### Recurrence

- `expand_recurring_tasks()` expands `twice_daily` tasks into morning and evening instances.
- Completing a daily or weekly task creates the next recurring instance automatically.

### Conflict Handling

- `detect_conflicts()` finds overlapping scheduled intervals.
- `detect_same_start_conflicts()` finds tasks with identical start times.
- `get_conflict_warning()` summarizes problems for the UI.
- `resolve_conflicts()` supports three recovery strategies.

## Testing

Run the full test suite with:

```bash
PYTHONPATH=. pytest test/test_pawpal.py -v
```

The project currently includes 60 passing tests covering:

- core class behavior
- schedule generation
- recurrence logic
- conflict detection
- input validation
- stress cases
- error handling
- conflict resolution strategies

## Key Files

- [app.py](/Users/yichen/Downloads/School/算法课/CodePath/AI110/Week4/ai110-module2show-pawpal-starter/app.py): Streamlit UI and schedule display.
- [pawpal_system.py](/Users/yichen/Downloads/School/算法课/CodePath/AI110/Week4/ai110-module2show-pawpal-starter/pawpal_system.py): domain model and scheduling logic.
- [test/test_pawpal.py](/Users/yichen/Downloads/School/算法课/CodePath/AI110/Week4/ai110-module2show-pawpal-starter/test/test_pawpal.py): automated tests.
- [reflection.md](/Users/yichen/Downloads/School/算法课/CodePath/AI110/Week4/ai110-module2show-pawpal-starter/reflection.md): project reflection.

## Notes

This project was built for the AI110 Module 2 PawPal+ assignment. The focus is on clear object-oriented design, algorithmic scheduling behavior, and transparent UI feedback.
