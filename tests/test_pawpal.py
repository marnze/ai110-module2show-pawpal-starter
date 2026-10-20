from datetime import date

from pawpal_system import Pet, Priority, Task


def make_pet() -> Pet:
    return Pet(name="Mochi", sex="F", species="dog", breed="Shiba", weight=10.0, birthday=date(2020, 1, 1))


def test_mark_done_changes_task_status():
    task = Task(title="Walk", duration=30, priority=Priority.HIGH)
    today = date(2026, 10, 20)
    assert task.is_due(today)

    task.mark_done(today)

    assert task.last_done == today
    assert not task.is_due(today)


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Feed", duration=10, priority=Priority.MEDIUM))

    assert len(pet.tasks) == 1
