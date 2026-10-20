"""PawPal system classes, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
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
    # Set by Owner.add_pet() -- always add pets through that method.
    # Hidden from repr to avoid printing in a loop.
    owner: Owner | None = field(default=None, repr=False)

    @property
    def age(self) -> int:
        """Age in whole years, computed from birthday so it never goes stale."""
        pass


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
        pass

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        pass


# eq=False: two tasks with the same details are still different tasks.
@dataclass(eq=False)
class Task:
    title: str
    duration: int  # minutes
    priority: Priority
    pet: Pet
    frequency: Frequency = Frequency.ONCE
    start_time: datetime | None = None  # filled in when the plan is built
    last_done: date | None = None  # replaces a plain done flag, so repeats work

    def __post_init__(self) -> None:
        """Raise ValueError if duration is not a positive number of minutes."""
        pass

    def mark_done(self, on: date) -> None:
        """Record that this task was completed on the given day."""
        pass

    def is_due(self, on: date) -> bool:
        """Return True if this task still needs doing on the given day.

        ONCE: due until it has ever been done.
        DAILY: due unless it was done on that day.
        WEEKLY: due if never done or last done 7+ days earlier.
        """
        pass

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new start time."""
        pass

    def end_time(self) -> datetime | None:
        """Return start_time + duration, or None if not scheduled yet."""
        pass

    def overlaps(self, other: Task) -> bool:
        """Return True if both tasks are scheduled and their time slots overlap."""
        pass


@dataclass
class Schedule:
    owner: Owner
    day: date
    available_minutes: int  # owner's time budget for this day
    tasks: list[Task] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)  # filled by generate_plan()

    def __post_init__(self) -> None:
        """Raise ValueError if available_minutes is negative."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule.

        Ignore it if it's already there. Raise ValueError if the task's pet
        doesn't belong to this schedule's owner.
        """
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are due on self.day (see Task.is_due)."""
        pass

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to the given pet."""
        pass

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
        pass

    def find_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of scheduled tasks whose time slots overlap.

        generate_plan() never creates overlaps, but reschedule() can.
        """
        pass

    def explain_plan(self) -> list[str]:
        """Return the reasons recorded by the last generate_plan() call."""
        pass

    def display_schedule(self) -> str:
        """Return the plan as readable text (the UI decides how to show it)."""
        pass
