"""Temporary testing ground: build a small household and exercise the Scheduler.

Prints the results of sorting, filtering, recurring tasks, and conflict
detection, then today's generated schedule.
"""

from datetime import date, datetime, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print one line per task: day and time, title, pet, and whether it's done."""
    print(f"\n{heading}")
    print("-" * 50)
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        when = f"{task.start_time:%a %H:%M}" if task.start_time else "--- --:--"
        status = "done" if task.is_done else "pending"
        due = f" due {task.due_date:%a %m/%d}" if task.due_date else ""
        print(f"  {when}  {task.title:<18} {task.pet.name:<6} [{status}]{due}")


def main() -> None:
    """Set up two pets with out-of-order and clashing tasks, then print each demo section."""
    owner = Owner(name="Mauricio", sex="M", contact_info="mauricio@example.com")

    mochi = Pet(name="Mochi", sex="M", species="Dog", breed="Shiba Inu",
                weight=22.5, birthday=date(2021, 4, 12))
    luna = Pet(name="Luna", sex="F", species="Cat", breed="Siamese",
               weight=9.0, birthday=date(2019, 8, 3))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()
    scheduler = Scheduler(owner=owner, day=today, available_minutes=120)

    def at(hour: int, minute: int = 0) -> datetime:
        """Return today's date at the given hour and minute."""
        return datetime.combine(today, time(hour, minute))

    # Added deliberately out of time order, one task left unscheduled.
    scheduler.add_task(mochi, Task("Evening walk", 30, Priority.HIGH, Frequency.DAILY, start_time=at(18)))
    scheduler.add_task(luna, Task("Clean litter box", 15, Priority.MEDIUM, Frequency.DAILY, start_time=at(12, 30)))
    scheduler.add_task(luna, Task("Vet checkup", 90, Priority.LOW))
    scheduler.add_task(mochi, Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY, start_time=at(7)))
    scheduler.add_task(luna, Task("Breakfast", 5, Priority.HIGH, Frequency.DAILY, start_time=at(7, 45)))
    scheduler.add_task(mochi, Task("Brush teeth", 10, Priority.MEDIUM, Frequency.DAILY, start_time=at(21)))

    # Deliberate clashes for the conflict check: one across pets, one same pet.
    scheduler.add_task(luna, Task("Dinner", 10, Priority.HIGH, Frequency.DAILY, start_time=at(18)))
    scheduler.add_task(mochi, Task("Medication", 5, Priority.HIGH, Frequency.DAILY, start_time=at(21)))

    # Finish a couple of daily tasks; each one spawns tomorrow's occurrence.
    next_occurrences = []
    for task in owner.get_all_tasks():
        if task.title in ("Morning walk", "Breakfast"):
            next_occurrences.append(task.mark_done(today))

    print("=" * 50)
    print("Sorting & Filtering Demo")
    print("=" * 50)

    print_tasks("Next occurrences created by mark_done()", next_occurrences)

    print_tasks("As stored (grouped by pet, not by time)", owner.get_all_tasks())
    print_tasks("Sorted by time", scheduler.sort_by_time())
    print_tasks("Only Luna's tasks", scheduler.filter_tasks(pet_name="luna"))
    print_tasks("Completed today", scheduler.filter_tasks(done=True))
    print_tasks("Still pending, sorted by time",
                scheduler.sort_by_time(scheduler.filter_tasks(done=False)))
    print_tasks("Mochi's pending tasks",
                scheduler.filter_tasks(pet_name="Mochi", done=False))

    print("\nConflict check")
    print("-" * 50)
    warnings = scheduler.conflict_warnings()
    for warning in warnings:
        print(f"  {warning}")
    if not warnings:
        print("  No conflicts.")

    # Build a plan for what's still pending (this reassigns start times).
    scheduler.generate_plan(start=time(8, 0))

    print()
    print("=" * 50)
    print("Today's Schedule")
    print("=" * 50)
    print(scheduler.display_schedule())
    print()
    print("Why this plan:")
    for reason in scheduler.explain_plan():
        print(f"  - {reason}")


if __name__ == "__main__":
    main()
