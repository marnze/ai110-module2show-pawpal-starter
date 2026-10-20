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

## ✨ Features

- **Priority-first planning:** `generate_plan()` puts the most important tasks first (HIGH → LOW). When two tasks have the same priority, the shorter one goes first, so more tasks fit.
- **Time-budget fitting:** Tasks are added one after another until the owner's available minutes run out. A task that doesn't fit is skipped, but the planner keeps checking the rest, because a shorter task later in the list may still fit.
- **Working around finished tasks:** When the plan is rebuilt, tasks already done today keep their time slots. New tasks fill the gaps between them (`_next_free_slot()`), so replanning never creates overlaps.
- **Sorting by time:** `sort_by_time()` lists tasks earliest first, with unscheduled tasks at the end. Tasks with the same start time keep the order they were added in.
- **Filtering:** `filter_tasks()` narrows the list by pet name (case-insensitive), by status (done / due today), or both.
- **Conflict warnings:** `find_conflicts()` finds tasks whose time slots overlap, for the same pet or different pets. Because the tasks are sorted by time first, each task is only compared with the ones that start before it ends. Back-to-back tasks are not conflicts. `conflict_warnings()` turns each overlap into a readable message instead of raising an error.
- **Daily and weekly recurrence:** Marking a DAILY or WEEKLY task done creates the next one, due 1 or 7 days later at the same time of day. Marking a task done twice never creates a duplicate, and ONCE tasks don't repeat.
- **Due dates:** A task is due once its `due_date` arrives and stays due until it's done, so an overdue task is never dropped. Future occurrences stay hidden until their day.
- **Plan explanations:** Every scheduled or skipped task gets a reason (priority, minutes used, minutes left), which `explain_plan()` returns.
- **Data checks:** A pet or task can't belong to two owners or pets. Durations must be positive whole minutes, and the time budget can't be negative.

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

Run the full test suite from the project root:

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover the scheduling logic in `pawpal_system.py`:

- **Sorting:** tasks come back in time order. Tasks with the same time keep the order they were added in, unscheduled tasks go last, and empty lists work.
- **Plan generation:** higher priority goes first, with the shorter task first on a tie. A task that doesn't fit the time budget is skipped while later tasks can still fit. Also covers a task that exactly fills the budget, a zero budget, tasks not due yet, and tasks overdue.
- **Recurring tasks:** finishing a daily or weekly task creates the next one 1 or 7 days later at the same time. Marking a task done twice doesn't duplicate it, and one-time tasks don't repeat. Also covers finishing a task late, rolling over from Dec 31 to Jan 1, and a recurring task with no pet.
- **Conflict detection:** catches tasks at the same time and overlaps across different pets. Back-to-back tasks and tasks on other days are not flagged, and a long task that overlaps several later ones is reported against each of them.
- **Replanning:** building the plan again after finishing tasks keeps finished tasks in their time slots. It fills the gaps around them without creating overlaps.
- **Filtering and validation:** filtering by pet name and done status. Rejects tasks or pets that already belong to someone else, invalid durations, and negative budgets.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\nunez\Desktop\AI110\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 33 items

tests\test_pawpal.py .................................                   [100%]

============================= 33 passed in 0.04s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

All 33 tests pass. They cover the main scheduling behavior and the edge cases most likely to break: ties, boundaries, budget limits, date rollover and replanning. Writing them also uncovered a real bug, overlapping time slots after replanning, which is now fixed. It's not 5 stars because a few cases are still untested or open design decisions:

- Plans that run past midnight.
- Whether finished tasks should count against the day's time budget when the plan is rebuilt.
- The Streamlit UI, which has no automated tests.

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

Run the app with `streamlit run app.py`.

### Main UI features

| Section | What you can do |
|---------|-----------------|
| **Owner** | Enter the owner's name and contact info. |
| **Add a Pet** | Add a pet with name, species, breed, sex, weight and birthday. A table lists every pet with its age and task count. |
| **Add a Task** | Give a pet a task with a title, duration, priority and frequency (once, daily or weekly). The task table can be filtered by pet and by status (All / Due today / Done) and is sorted by time. |
| **Build Schedule** | Pick the day, a start time and how many minutes you have, then click **Generate schedule**. |
| **Schedule results** | A green banner if there are no conflicts or a yellow warning if there are, three summary numbers (tasks, planned minutes, minutes free), the schedule table, a list of tasks that didn't fit, and a "Why this plan?" section. |
| **Move a task to a fixed time** | Set a task to a specific time, such as a vet appointment. |

### Example workflow

1. Enter your name in the **Owner** section.
2. Add two pets, for example **Mochi** (dog) and **Luna** (cat).
3. Add tasks: *Morning walk* for Mochi (30 min, High, Daily), *Breakfast* for Luna (5 min, High, Daily), *Brush teeth* for Mochi (10 min, Medium) and *Vet checkup* for Luna (90 min, Low).
4. Set the task filter to **Luna** to see only her tasks, then back to **All pets**.
5. In **Build Schedule**, set the start time to 07:00 and available minutes to 60, then click **Generate schedule**.
6. Read the result:
   - The two High-priority tasks come first, with the shorter *Breakfast* ahead of *Morning walk*.
   - *Brush teeth* fills the next slot.
   - *Vet checkup* is listed under "Didn't fit today" because only 15 minutes are left.
   - The green banner confirms there are no conflicts.
7. Open **Move a task to a fixed time** and move *Brush teeth* to 07:10. A yellow warning appears above the table. It names both overlapping tasks, their pets and time slots, and suggests a time that frees up the slot. The rows involved are marked ⚠️ in the table.
8. Click **Generate schedule** again to replace the manual time and clear the conflict.

### Scheduler behaviors shown

- **Priority sorting with a tie-breaker:** highest priority first, then the shorter task first (step 6).
- **Time-budget fitting:** a task that doesn't fit is skipped and explained, and the rest are still scheduled (step 6).
- **Filtering and sorting by time:** the task table uses `filter_tasks()` and `sort_by_time()` (step 4).
- **Conflict warnings:** `find_conflicts()` catches the overlap after a manual move (step 7).
- **Plan explanations:** "Why this plan?" shows the reasons from `explain_plan()` (step 6).

### Sample CLI output

`python main.py` builds a sample owner with two pets. It marks two daily tasks done, sorts and filters the task list, checks for conflicts, and generates the day's plan. Here is part of its output:

```
Sorted by time
--------------------------------------------------
  Tue 07:00  Morning walk       Mochi  [done]
  Tue 07:45  Breakfast          Luna   [done]
  Tue 12:30  Clean litter box   Luna   [pending]
  Tue 18:00  Evening walk       Mochi  [pending]
  Tue 18:00  Dinner             Luna   [pending]
  Tue 21:00  Brush teeth        Mochi  [pending]
  Tue 21:00  Medication         Mochi  [pending]
  Wed 07:00  Morning walk       Mochi  [pending] due Wed 10/21
  Wed 07:45  Breakfast          Luna   [pending] due Wed 10/21
  --- --:--  Vet checkup        Luna   [pending]

Conflict check
--------------------------------------------------
  WARNING: 'Evening walk' (18:00-18:30) overlaps 'Dinner' (18:00-18:10), Mochi and Luna.
  WARNING: 'Brush teeth' (21:00-21:10) overlaps 'Medication' (21:00-21:05), both for Mochi.

==================================================
Today's Schedule
==================================================
Schedule for Mauricio on Tuesday, October 20:
  07:00-07:30  Morning walk (Mochi) [HIGH, done]
  07:45-07:50  Breakfast (Luna) [HIGH, done]
  08:00-08:05  Medication (Mochi) [HIGH, pending]
  08:05-08:15  Dinner (Luna) [HIGH, pending]
  08:15-08:45  Evening walk (Mochi) [HIGH, pending]
  08:45-08:55  Brush teeth (Mochi) [MEDIUM, pending]
  08:55-09:10  Clean litter box (Luna) [MEDIUM, pending]

Why this plan:
  - Scheduled 'Medication' for Mochi at 08:00: HIGH priority, 5 min fits (115 min left).
  - Scheduled 'Dinner' for Luna at 08:05: HIGH priority, 10 min fits (105 min left).
  - Scheduled 'Evening walk' for Mochi at 08:15: HIGH priority, 30 min fits (75 min left).
  - Scheduled 'Brush teeth' for Mochi at 08:45: MEDIUM priority, 10 min fits (65 min left).
  - Scheduled 'Clean litter box' for Luna at 08:55: MEDIUM priority, 15 min fits (50 min left).
  - Skipped 'Vet checkup' for Luna: needs 90 min but only 50 min left.
```

In this output:
- Tomorrow's *Morning walk* and *Breakfast* were created automatically when today's were marked done.
- The two conflicts come from fixed times set in the demo.
- The plan skips the finished 07:00 and 07:45 tasks and starts the remaining ones at 08:00, so nothing overlaps.
