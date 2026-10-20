"""PawPal system classes, generated from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Pet:
    name: str
    sex: str
    species: str
    breed: str
    age: int
    weight: float
    birthday: date
    owner_name: str


@dataclass
class Owner:
    name: str
    sex: str
    contact_info: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        pass

    def list_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        pass


@dataclass
class Task:
    title: str
    duration: int  # minutes
    priority: str
    pet: Pet
    done: bool = False

    def mark_done(self) -> None:
        """Mark this task as completed."""
        pass

    def reschedule(self, new_time: datetime) -> None:
        """Move this task to a new time."""
        pass


@dataclass
class Schedule:
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from the schedule."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet done."""
        pass

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to the given pet."""
        pass

    def display_schedule(self) -> None:
        """Print the schedule in a readable format."""
        pass
