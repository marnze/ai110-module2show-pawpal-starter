# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

The scheduling logic lives in `pawpal_system.py` and is built from four classes plus two enums:

- **`Owner`** holds contact info and a list of `Pet`s. `add_pet()` links each pet back to its owner, and `get_all_tasks()` gathers every task across all pets.
- **`Pet`** stores profile details (species, breed, weight, birthday; `age` is computed from the birthday) and its own list of `Task`s. `add_task()` links each task back to its pet and stops one task from belonging to two pets.
- **`Task`** is a single care item: title, duration in minutes, `Priority` (LOW/MEDIUM/HIGH) and `Frequency` (ONCE/DAILY/WEEKLY). Each `Task` is one occurrence with an optional `due_date`; `mark_done()` records `last_done` and, for repeating tasks, creates the next occurrence. Once a task is scheduled it has a `start_time`, and `overlaps()` checks whether it clashes with another task.
- **`Scheduler`** plans one day for one owner within a time budget (`available_minutes`). `generate_plan()` gets the pending tasks and sorts them by priority (highest first, shorter task wins a tie). It then gives each task that still fits the next free time slot and skips any task that doesn't. It records a reason for every task it schedules or skips. `explain_plan()` returns those reasons, `sort_by_time()` and `filter_tasks()` organize the task list, `conflict_warnings()` reports overlapping tasks, and `display_schedule()` formats the day as text (see Smarter Scheduling below).

The flow goes **Owner → Pets → Tasks**, and the **Scheduler** reads that structure through the owner to build the day's plan and explain it.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==================================================
Today's Schedule
==================================================
Schedule for Mauricio on Tuesday, October 20:
  07:00-07:05  Breakfast (Luna) [HIGH, pending]
  07:05-07:35  Morning walk (Mochi) [HIGH, pending]
  07:35-07:45  Brush teeth (Mochi) [MEDIUM, pending]
  07:45-08:00  Clean litter box (Luna) [MEDIUM, pending]

Why this plan:
  - Scheduled 'Breakfast' for Luna at 07:00: HIGH priority, 5 min fits (115 min left).
  - Scheduled 'Morning walk' for Mochi at 07:05: HIGH priority, 30 min fits (85 min left).
  - Scheduled 'Brush teeth' for Mochi at 07:35: MEDIUM priority, 10 min fits (75 min left).
  - Scheduled 'Clean litter box' for Luna at 07:45: MEDIUM priority, 15 min fits (60 min left).
  - Skipped 'Vet checkup' for Luna: needs 90 min but only 60 min left.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.generate_plan()` | By start time (unscheduled last); the planner orders by priority, then shortest duration |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_pending_tasks()` | By pet name and/or completion status; the planner skips tasks that don't fit the time left |
| Conflict handling | `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()`, `Task.overlaps()` | Overlapping time slots, same pet or different pets; returns warnings instead of raising |
| Recurring tasks | `Task.mark_done()`, `Task.is_due()`, `Task.is_done` | Completing a DAILY task creates tomorrow's copy; WEEKLY creates one 7 days out |

### Sorting — `Scheduler.sort_by_time(tasks=None)`

Returns tasks ordered by `start_time`, earliest first. Tasks with no start time go at the end in their original order. It uses `sorted()` with the key `(start_time is None, start_time or datetime.max)`, so `None` is never compared to a `datetime`. Pass in any list (for example, the result of `filter_tasks()`) or leave it out to sort all of the owner's tasks. `get_scheduled_tasks()` and `display_schedule()` use it to list the day in time order.

`generate_plan()` uses a separate order to decide *what to schedule first*: highest `Priority` first, shorter task first when priorities tie.

### Filtering — `Scheduler.filter_tasks(pet_name=None, done=None)`

Returns the owner's tasks that match every filter given; leaving an argument as `None` skips that filter, so the filters can be combined or used alone.

- `pet_name="luna"` keeps only that pet's tasks (case-insensitive).
- `done=True` keeps completed tasks (`Task.is_done`).
- `done=False` keeps tasks due on the scheduler's day (`Task.is_due()`). Future occurrences of recurring tasks match neither status.

Filter and sort together: `scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna", done=False))`.

### Conflict detection — `Scheduler.find_conflicts()` and `Scheduler.conflict_warnings()`

`find_conflicts()` returns every pair of tasks on the scheduler's day whose time slots overlap, whether they belong to the same pet or different pets (the owner can't do two things at once). It catches partial overlaps (18:00–18:30 vs. 18:15), not only exact time matches, while back-to-back tasks (one ends at 07:15, the next starts at 07:15) are not conflicts. Because the tasks are sorted by start time, each task is only compared with the ones that start before it ends, so the loop stops early instead of checking every pair.

`conflict_warnings()` turns each pair into a readable message and never raises, so the program shows the warnings and keeps running:

```
WARNING: 'Evening walk' (18:00-18:30) overlaps 'Dinner' (18:00-18:10), Mochi and Luna.
WARNING: 'Brush teeth' (21:00-21:10) overlaps 'Medication' (21:00-21:05), both for Mochi.
```

### Recurring tasks — `Task.mark_done(on)`

Each `Task` object is one occurrence with an optional `due_date`. When a DAILY or WEEKLY task is marked done, `mark_done()`:

1. Records `last_done = on`.
2. Creates a copy due `on + 1 day` (DAILY) or `on + 7 days` (WEEKLY), keeping the title, duration, priority, and time of day.
3. Adds the copy to the same pet and returns it.

ONCE tasks return `None`, and marking a task done twice never creates a duplicate. `Task.is_due(day)` is true once a task's `due_date` arrives and stays true until it's done, so a completed task never comes back; its next occurrence takes its place.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
