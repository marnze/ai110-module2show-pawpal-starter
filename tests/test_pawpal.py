from datetime import date, datetime, time

import pytest

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

DAY = date(2026, 10, 20)


def make_pet() -> Pet:
    return Pet(name="Mochi", sex="F", species="dog", breed="Shiba", weight=10.0, birthday=date(2020, 1, 1))


def make_scheduler(available_minutes: int = 120) -> tuple[Scheduler, Pet]:
    """Owner with one pet, and a scheduler for DAY."""
    owner = Owner(name="Sam", sex="F", contact_info="sam@example.com")
    pet = make_pet()
    owner.add_pet(pet)
    return Scheduler(owner=owner, day=DAY, available_minutes=available_minutes), pet


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, 20, hour, minute)


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


# --- Sorting correctness ---


def test_sort_by_time_returns_chronological_order():
    scheduler, pet = make_scheduler()
    noon = Task("Play", 20, Priority.LOW, start_time=at(12))
    early = Task("Pill", 5, Priority.HIGH, start_time=at(6, 30))
    late = Task("Brush", 10, Priority.LOW, start_time=at(21))
    mid = Task("Walk", 30, Priority.HIGH, start_time=at(9, 15))
    for task in (noon, early, late, mid):
        scheduler.add_task(pet, task)

    result = scheduler.sort_by_time()

    assert result == [early, mid, noon, late]
    starts = [t.start_time for t in result]
    assert starts == sorted(starts)


def test_sort_by_time_keeps_insertion_order_for_ties():
    scheduler, pet = make_scheduler()
    first = Task("Feed", 5, Priority.HIGH, start_time=at(8))
    second = Task("Pill", 5, Priority.HIGH, start_time=at(8))
    first_unscheduled = Task("Vet", 60, Priority.LOW)
    second_unscheduled = Task("Bath", 20, Priority.LOW)
    for task in (first_unscheduled, first, second_unscheduled, second):
        scheduler.add_task(pet, task)

    assert scheduler.sort_by_time() == [first, second, first_unscheduled, second_unscheduled]


def test_sort_by_time_handles_empty_input():
    scheduler, _ = make_scheduler()

    assert scheduler.sort_by_time() == []
    assert scheduler.sort_by_time([]) == []


# --- Plan generation ---


def test_generate_plan_orders_by_priority_then_shorter_first():
    scheduler, pet = make_scheduler(available_minutes=120)
    low = Task("Brush", 10, Priority.LOW)
    long_high = Task("Walk", 30, Priority.HIGH)
    short_high = Task("Pill", 15, Priority.HIGH)
    medium = Task("Play", 20, Priority.MEDIUM)
    for task in (low, long_high, short_high, medium):
        scheduler.add_task(pet, task)

    plan = scheduler.generate_plan(time(8, 0))

    assert plan == [short_high, long_high, medium, low]
    assert [t.start_time for t in plan] == [at(8), at(8, 15), at(8, 45), at(9, 5)]
    assert scheduler.find_conflicts() == []


def test_generate_plan_skips_task_that_does_not_fit_but_keeps_going():
    scheduler, pet = make_scheduler(available_minutes=40)
    too_long = Task("Hike", 60, Priority.HIGH)
    fits = Task("Walk", 30, Priority.MEDIUM)
    exact_fit = Task("Brush", 10, Priority.LOW)  # uses exactly the last 10 min
    for task in (too_long, fits, exact_fit):
        scheduler.add_task(pet, task)

    plan = scheduler.generate_plan(time(8, 0))

    assert plan == [fits, exact_fit]
    assert too_long.start_time is None
    reasons = scheduler.explain_plan()
    assert len(reasons) == 3
    assert reasons[0].startswith("Skipped 'Hike'")
    assert reasons[2].startswith("Scheduled 'Brush'") and "(0 min left)" in reasons[2]


def test_generate_plan_with_zero_budget_schedules_nothing():
    scheduler, pet = make_scheduler(available_minutes=0)
    scheduler.add_task(pet, Task("Feed", 5, Priority.HIGH))

    assert scheduler.generate_plan(time(8, 0)) == []
    assert scheduler.get_scheduled_tasks() == []


def test_generate_plan_ignores_tasks_not_due_yet():
    scheduler, pet = make_scheduler()
    today = Task("Feed", 5, Priority.HIGH)
    tomorrow = Task("Bath", 20, Priority.HIGH, due_date=date(2026, 10, 21))
    overdue = Task("Nails", 15, Priority.LOW, due_date=date(2026, 10, 18))
    for task in (today, tomorrow, overdue):
        scheduler.add_task(pet, task)

    assert scheduler.generate_plan(time(8, 0)) == [today, overdue]
    assert tomorrow.start_time is None


# --- Recurrence logic ---


def test_daily_task_completion_adds_pending_task_for_next_day():
    scheduler, pet = make_scheduler()
    walk = Task("Walk", 30, Priority.HIGH, Frequency.DAILY, start_time=at(7))
    scheduler.add_task(pet, walk)

    next_walk = walk.mark_done(DAY)

    assert scheduler.get_pending_tasks() == []
    tomorrow = Scheduler(owner=scheduler.owner, day=date(2026, 10, 21), available_minutes=120)
    assert tomorrow.get_pending_tasks() == [next_walk]
    assert tomorrow.get_scheduled_tasks() == [next_walk]


def test_completing_daily_task_late_bases_next_due_on_completion_day():
    pet = make_pet()
    feed = Task("Feed", 5, Priority.HIGH, Frequency.DAILY, due_date=date(2026, 10, 20))
    pet.add_task(feed)

    next_feed = feed.mark_done(date(2026, 10, 22))

    assert next_feed.due_date == date(2026, 10, 23)


def test_daily_task_rolls_over_month_and_year():
    pet = make_pet()
    feed = Task("Feed", 5, Priority.HIGH, Frequency.DAILY, start_time=datetime(2026, 12, 31, 8, 0))
    pet.add_task(feed)

    next_feed = feed.mark_done(date(2026, 12, 31))

    assert next_feed.due_date == date(2027, 1, 1)
    assert next_feed.start_time == datetime(2027, 1, 1, 8, 0)


def test_recurring_task_without_pet_returns_unattached_next_occurrence():
    feed = Task("Feed", 5, Priority.HIGH, Frequency.DAILY)

    next_feed = feed.mark_done(DAY)

    assert next_feed is not None
    assert next_feed.pet is None
    assert next_feed.due_date == date(2026, 10, 21)


# --- Conflict detection ---


def test_find_conflicts_flags_tasks_at_duplicate_times():
    scheduler, pet = make_scheduler()
    feed = Task("Feed", 10, Priority.HIGH, start_time=at(8))
    pill = Task("Pill", 10, Priority.HIGH, start_time=at(8))
    scheduler.add_task(pet, feed)
    scheduler.add_task(pet, pill)

    assert scheduler.find_conflicts() == [(feed, pill)]
    warnings = scheduler.conflict_warnings()
    assert len(warnings) == 1
    assert "(08:00-08:10)" in warnings[0] and "both for Mochi" in warnings[0]


def test_find_conflicts_long_task_overlaps_several_later_tasks():
    scheduler, pet = make_scheduler()
    hike = Task("Hike", 120, Priority.HIGH, start_time=at(9))  # 9:00-11:00
    feed = Task("Feed", 30, Priority.HIGH, start_time=at(9, 30))  # 9:30-10:00
    pill = Task("Pill", 5, Priority.HIGH, start_time=at(10))  # starts as Feed ends
    brush = Task("Brush", 10, Priority.LOW, start_time=at(11))  # starts as Hike ends
    for task in (hike, feed, pill, brush):
        scheduler.add_task(pet, task)

    assert scheduler.find_conflicts() == [(hike, feed), (hike, pill)]


def test_find_conflicts_ignores_tasks_on_other_days():
    scheduler, pet = make_scheduler()
    scheduler.add_task(pet, Task("Feed", 10, Priority.HIGH, start_time=at(8)))
    scheduler.add_task(pet, Task("Pill", 10, Priority.HIGH, start_time=datetime(2026, 10, 21, 8, 0)))

    assert scheduler.find_conflicts() == []


def test_replanning_after_marking_task_done_does_not_create_conflict():
    scheduler, pet = make_scheduler()
    walk = Task("Walk", 30, Priority.HIGH)
    feed = Task("Feed", 10, Priority.MEDIUM)
    scheduler.add_task(pet, walk)
    scheduler.add_task(pet, feed)
    scheduler.generate_plan(time(8, 0))

    walk.mark_done(DAY)
    scheduler.generate_plan(time(8, 0))

    assert walk.start_time == at(8)
    assert feed.start_time == at(8, 30)
    assert scheduler.find_conflicts() == []


def test_generate_plan_fills_gaps_around_done_tasks():
    scheduler, pet = make_scheduler()
    vet = Task("Vet", 30, Priority.HIGH, start_time=at(9))  # 9:00-9:30, already done
    scheduler.add_task(pet, vet)
    vet.mark_done(DAY)
    feed = Task("Feed", 30, Priority.HIGH)
    walk = Task("Walk", 45, Priority.MEDIUM)
    pill = Task("Pill", 5, Priority.LOW)
    for task in (feed, walk, pill):
        scheduler.add_task(pet, task)

    plan = scheduler.generate_plan(time(8, 0))

    # Feed fits before the vet visit; Walk would cross it, so it moves after.
    assert [t.start_time for t in plan] == [at(8), at(9, 30), at(10, 15)]
    assert scheduler.find_conflicts() == []


def test_done_tasks_before_plan_start_do_not_delay_plan():
    scheduler, pet = make_scheduler()
    pill = Task("Pill", 5, Priority.HIGH, start_time=at(7))
    scheduler.add_task(pet, pill)
    pill.mark_done(DAY)
    feed = Task("Feed", 10, Priority.HIGH)
    scheduler.add_task(pet, feed)

    assert scheduler.generate_plan(time(8, 0)) == [feed]
    assert feed.start_time == at(8)


# --- Ownership and validation ---


def test_add_task_rejects_task_owned_by_another_pet():
    dog = make_pet()
    cat = Pet(name="Luna", sex="F", species="cat", breed="Siamese", weight=4.0, birthday=date(2019, 1, 1))
    feed = Task("Feed", 5, Priority.HIGH)
    dog.add_task(feed)
    dog.add_task(feed)  # adding again is a no-op

    with pytest.raises(ValueError):
        cat.add_task(feed)
    assert dog.tasks == [feed] and cat.tasks == []


def test_scheduler_rejects_pet_of_another_owner():
    scheduler, _ = make_scheduler()
    stranger = make_pet()

    with pytest.raises(ValueError):
        scheduler.add_task(stranger, Task("Feed", 5, Priority.HIGH))


@pytest.mark.parametrize("duration", [0, -5, 1.5])
def test_task_rejects_invalid_duration(duration):
    with pytest.raises(ValueError):
        Task("Feed", duration, Priority.HIGH)


def test_scheduler_rejects_negative_budget():
    owner = Owner(name="Sam", sex="F", contact_info="sam@example.com")

    with pytest.raises(ValueError):
        Scheduler(owner=owner, day=DAY, available_minutes=-1)
