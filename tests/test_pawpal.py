from datetime import date, datetime

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


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


def test_sort_by_time_orders_earliest_first_and_unscheduled_last():
    owner = Owner(name="Sam", sex="F", contact_info="sam@example.com")
    pet = make_pet()
    owner.add_pet(pet)
    day = date(2026, 10, 20)
    scheduler = Scheduler(owner=owner, day=day, available_minutes=120)

    evening = Task("Dinner", 10, Priority.HIGH, start_time=datetime(2026, 10, 20, 18, 0))
    unscheduled = Task("Brush", 10, Priority.LOW)
    morning = Task("Walk", 30, Priority.HIGH, start_time=datetime(2026, 10, 20, 7, 0))
    for task in (evening, unscheduled, morning):
        scheduler.add_task(pet, task)

    assert scheduler.sort_by_time() == [morning, evening, unscheduled]


def test_filter_tasks_by_pet_name_and_completion():
    owner = Owner(name="Sam", sex="F", contact_info="sam@example.com")
    dog = make_pet()
    cat = Pet(name="Luna", sex="F", species="cat", breed="Siamese", weight=4.0, birthday=date(2019, 1, 1))
    owner.add_pet(dog)
    owner.add_pet(cat)
    day = date(2026, 10, 20)
    scheduler = Scheduler(owner=owner, day=day, available_minutes=120)

    walk = Task("Walk", 30, Priority.HIGH)
    feed_cat = Task("Feed", 5, Priority.HIGH)
    litter = Task("Litter", 15, Priority.MEDIUM)
    scheduler.add_task(dog, walk)
    scheduler.add_task(cat, feed_cat)
    scheduler.add_task(cat, litter)
    feed_cat.mark_done(day)

    assert scheduler.filter_tasks(pet_name="luna") == [feed_cat, litter]
    assert scheduler.filter_tasks(done=True) == [feed_cat]
    assert scheduler.filter_tasks(done=False) == [walk, litter]
    assert scheduler.filter_tasks(pet_name="Luna", done=False) == [litter]
    assert scheduler.filter_tasks(pet_name="Rex") == []
    assert scheduler.filter_tasks() == [walk, feed_cat, litter]


def test_completing_daily_task_creates_next_occurrence_tomorrow():
    pet = make_pet()
    day = date(2026, 10, 20)
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY, start_time=datetime(2026, 10, 20, 7, 0))
    pet.add_task(walk)

    next_walk = walk.mark_done(day)

    assert next_walk is not None and next_walk is not walk
    assert pet.tasks == [walk, next_walk]
    assert next_walk.pet is pet
    assert next_walk.due_date == date(2026, 10, 21)
    assert next_walk.start_time == datetime(2026, 10, 21, 7, 0)
    assert (next_walk.title, next_walk.duration, next_walk.priority) == ("Walk", 30, Priority.HIGH)
    assert not next_walk.is_done
    # Completed one is finished for good; the new one isn't due until tomorrow.
    assert not walk.is_due(day) and not walk.is_due(date(2026, 10, 21))
    assert not next_walk.is_due(day)
    assert next_walk.is_due(date(2026, 10, 21))


def test_completing_weekly_task_creates_next_occurrence_in_seven_days():
    pet = make_pet()
    bath = Task("Bath", 20, Priority.MEDIUM, Frequency.WEEKLY)
    pet.add_task(bath)

    next_bath = bath.mark_done(date(2026, 10, 20))

    assert next_bath.due_date == date(2026, 10, 27)
    assert next_bath.start_time is None
    assert not next_bath.is_due(date(2026, 10, 26))
    assert next_bath.is_due(date(2026, 10, 27))


def test_completing_once_task_creates_nothing():
    pet = make_pet()
    vet = Task("Vet", 60, Priority.LOW)
    pet.add_task(vet)

    assert vet.mark_done(date(2026, 10, 20)) is None
    assert pet.tasks == [vet]


def test_marking_done_twice_does_not_duplicate():
    pet = make_pet()
    feed = Task("Feed", 5, Priority.HIGH, Frequency.DAILY)
    pet.add_task(feed)

    feed.mark_done(date(2026, 10, 20))
    assert feed.mark_done(date(2026, 10, 20)) is None
    assert len(pet.tasks) == 2


def test_conflict_warnings_for_same_pet_and_different_pets():
    owner = Owner(name="Sam", sex="F", contact_info="sam@example.com")
    dog = make_pet()
    cat = Pet(name="Luna", sex="F", species="cat", breed="Siamese", weight=4.0, birthday=date(2019, 1, 1))
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner=owner, day=date(2026, 10, 20), available_minutes=120)

    def at(hour: int, minute: int = 0) -> datetime:
        return datetime(2026, 10, 20, hour, minute)

    scheduler.add_task(dog, Task("Walk", 30, Priority.HIGH, start_time=at(18)))
    scheduler.add_task(cat, Task("Dinner", 10, Priority.HIGH, start_time=at(18, 15)))
    scheduler.add_task(dog, Task("Brush", 10, Priority.LOW, start_time=at(21)))
    scheduler.add_task(dog, Task("Pill", 5, Priority.HIGH, start_time=at(21)))
    scheduler.add_task(cat, Task("Litter", 15, Priority.MEDIUM, start_time=at(7)))
    scheduler.add_task(cat, Task("Play", 10, Priority.LOW, start_time=at(7, 15)))  # starts as Litter ends
    scheduler.add_task(dog, Task("Vet", 60, Priority.LOW))  # unscheduled

    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 2
    assert "'Walk'" in warnings[0] and "'Dinner'" in warnings[0] and "Mochi and Luna" in warnings[0]
    assert "'Brush'" in warnings[1] and "'Pill'" in warnings[1] and "both for Mochi" in warnings[1]


def test_conflict_warnings_empty_when_no_overlap():
    owner = Owner(name="Sam", sex="F", contact_info="sam@example.com")
    pet = make_pet()
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, day=date(2026, 10, 20), available_minutes=120)
    scheduler.add_task(pet, Task("Walk", 30, Priority.HIGH, start_time=datetime(2026, 10, 20, 7, 0)))
    scheduler.add_task(pet, Task("Feed", 5, Priority.HIGH, start_time=datetime(2026, 10, 20, 7, 30)))

    assert scheduler.conflict_warnings() == []
