"""PawPal system classes, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum


class Priority(IntEnum):
    """Task priority. Higher number = more important, so sorting works."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task repeats."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# eq=False: two tasks with the same details are still different tasks.
@dataclass(eq=False)
class Task:
    title: str
    duration: int  # minutes
    priority: Priority
    frequency: Frequency = Frequency.ONCE
    start_time: datetime | None = None  # filled in when the plan is built
    last_done: date | None = None  # replaces a plain done flag, so repeats work
    # Set by Pet.add_task() -- always add tasks through that method.
    # Hidden from repr to avoid printing in a loop.
    pet: Pet | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Raise ValueError if duration is not a positive number of minutes."""
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError(f"duration must be a positive number of minutes, got {self.duration!r}")

    def mark_done(self, on: date) -> None:
        """Record that this task was completed on the given day."""
        self.last_done = on

    def is_due(self, on: date) -> bool:
        """Return True if this task still needs doing on the given day.

        ONCE: due until it has ever been done.
        DAILY: due unless it was done on that day.
        WEEKLY: due if never done or last done 7+ days earlier.
        """
        if self.last_done is None:
            return True
        if self.frequency is Frequency.ONCE:
            return False
        if self.frequency is Frequency.DAILY:
            return self.last_done != on
        return (on - self.last_done).days >= 7

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new start time."""
        self.start_time = new_time

    def end_time(self) -> datetime | None:
        """Return start_time + duration, or None if not scheduled yet."""
        if self.start_time is None:
            return None
        return self.start_time + timedelta(minutes=self.duration)

    def overlaps(self, other: Task) -> bool:
        """Return True if both tasks are scheduled and their time slots overlap."""
        if other is self or self.start_time is None or other.start_time is None:
            return False
        return self.start_time < other.end_time() and other.start_time < self.end_time()


# eq=False: two pets are only "equal" if they are the same object,
# so two identical-looking pets never get mixed up.
@dataclass(eq=False)
class Pet:
    name: str
    sex: str
    species: str
    breed: str
    weight: float
    birthday: date
    tasks: list[Task] = field(default_factory=list)
    # Set by Owner.add_pet() -- always add pets through that method.
    # Hidden from repr to avoid printing in a loop.
    owner: Owner | None = field(default=None, repr=False)

    @property
    def age(self) -> int:
        """Age in whole years, computed from birthday so it never goes stale."""
        today = date.today()
        had_birthday = (today.month, today.day) >= (self.birthday.month, self.birthday.day)
        return today.year - self.birthday.year - (0 if had_birthday else 1)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's list and set task.pet to this pet.

        Ignore the task if it's already in the list. Raise ValueError if the
        task already belongs to a different pet.
        """
        if task.pet is not None and task.pet is not self:
            raise ValueError(f"Task '{task.title}' already belongs to {task.pet.name}")
        if task not in self.tasks:
            self.tasks.append(task)
        task.pet = self

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's list. Ignore it if it isn't there."""
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet = None


@dataclass
class Owner:
    name: str
    sex: str
    contact_info: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list and set pet.owner to this owner.

        Ignore the pet if it's already in the list. Raise ValueError if the
        pet already belongs to a different owner.
        """
        if pet.owner is not None and pet.owner is not self:
            raise ValueError(f"{pet.name} already belongs to {pet.owner.name}")
        if pet not in self.pets:
            self.pets.append(pet)
        pet.owner = self

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets, in one list."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Scheduler:
    owner: Owner
    day: date
    available_minutes: int  # owner's time budget for this day
    reasons: list[str] = field(default_factory=list)  # filled by generate_plan()

    def __post_init__(self) -> None:
        """Raise ValueError if available_minutes is negative."""
        if self.available_minutes < 0:
            raise ValueError(f"available_minutes cannot be negative, got {self.available_minutes}")

    def add_task(self, pet: Pet, task: Task) -> None:
        """Assign a task to one of the owner's pets.

        Raise ValueError if the pet doesn't belong to this scheduler's owner.
        """
        if pet.owner is not self.owner:
            raise ValueError(f"{pet.name} does not belong to {self.owner.name}")
        pet.add_task(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from whichever pet it is assigned to."""
        if task.pet is not None:
            task.pet.remove_task(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks across all pets that are due on self.day (see Task.is_due)."""
        return [task for task in self.owner.get_all_tasks() if task.is_due(self.day)]

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to the given pet."""
        return [task for task in self.owner.get_all_tasks() if task.pet is pet]

    def get_scheduled_tasks(self) -> list[Task]:
        """Return tasks that have a start time on self.day, in time order."""
        scheduled = [
            task for task in self.owner.get_all_tasks()
            if task.start_time is not None and task.start_time.date() == self.day
        ]
        return sorted(scheduled, key=lambda task: task.start_time)

    def generate_plan(self, start: time) -> list[Task]:
        """Build the day's plan, starting at `start` on self.day.

        1. Take the pending tasks and sort them by priority (highest first),
           breaking ties with the shorter task first.
        2. Walk the list, giving each task that still fits in the remaining
           available_minutes a start_time right after the previous one.
           A task that doesn't fit is skipped, but keep checking the rest,
           since a shorter task later in the list may still fit.
        3. Clear self.reasons, then record why each task was kept or skipped.
        Return the scheduled tasks in time order.
        """
        pending = sorted(self.get_pending_tasks(), key=lambda t: (-t.priority, t.duration))
        self.reasons = []
        current = datetime.combine(self.day, start)
        remaining = self.available_minutes
        plan: list[Task] = []

        for task in pending:
            label = f"'{task.title}' for {task.pet.name}"
            if task.duration <= remaining:
                task.start_time = current
                current = task.end_time()
                remaining -= task.duration
                plan.append(task)
                self.reasons.append(
                    f"Scheduled {label} at {task.start_time:%H:%M}: "
                    f"{task.priority.name} priority, {task.duration} min fits "
                    f"({remaining} min left)."
                )
            else:
                task.start_time = None
                self.reasons.append(
                    f"Skipped {label}: needs {task.duration} min but only "
                    f"{remaining} min left."
                )
        return plan

    def find_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of scheduled tasks whose time slots overlap.

        generate_plan() never creates overlaps, but reschedule() can.
        """
        scheduled = self.get_scheduled_tasks()
        return [
            (a, b)
            for i, a in enumerate(scheduled)
            for b in scheduled[i + 1:]
            if a.overlaps(b)
        ]

    def explain_plan(self) -> list[str]:
        """Return the reasons recorded by the last generate_plan() call."""
        return list(self.reasons)

    def display_schedule(self) -> str:
        """Return the plan as readable text (the UI decides how to show it)."""
        scheduled = self.get_scheduled_tasks()
        if not scheduled:
            return f"No tasks scheduled for {self.day:%A, %B %d}."
        lines = [f"Schedule for {self.owner.name} on {self.day:%A, %B %d}:"]
        for task in scheduled:
            status = "done" if task.last_done == self.day else "pending"
            lines.append(
                f"  {task.start_time:%H:%M}-{task.end_time():%H:%M}  {task.title} "
                f"({task.pet.name}) [{task.priority.name}, {status}]"
            )
        return "\n".join(lines)
