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
- **`Task`** is a single care item: title, duration in minutes, `Priority` (LOW/MEDIUM/HIGH) and `Frequency` (ONCE/DAILY/WEEKLY). It records `last_done` instead of a done flag, so `is_due()` can tell whether a repeating task needs doing again. Once a task is scheduled it has a `start_time`, and `overlaps()` checks whether it clashes with another task.
- **`Scheduler`** plans one day for one owner within a time budget (`available_minutes`). `generate_plan()` gets the pending tasks and sorts them by priority (highest first, shorter task wins a tie). It then gives each task that still fits the next free time slot and skips any task that doesn't. It records a reason for every task it schedules or skips. `explain_plan()` returns those reasons, `find_conflicts()` reports overlaps caused by manual `reschedule()` calls, and `display_schedule()` formats the day as text.

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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
