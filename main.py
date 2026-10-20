"""Temporary testing ground: build a small household and print today's schedule."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    owner = Owner(name="Mauricio", sex="M", contact_info="mauricio@example.com")

    mochi = Pet(name="Mochi", sex="M", species="Dog", breed="Shiba Inu",
                weight=22.5, birthday=date(2021, 4, 12))
    luna = Pet(name="Luna", sex="F", species="Cat", breed="Siamese",
               weight=9.0, birthday=date(2019, 8, 3))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()
    scheduler = Scheduler(owner=owner, day=today, available_minutes=120)

    scheduler.add_task(mochi, Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY))
    scheduler.add_task(mochi, Task("Brush teeth", 10, Priority.MEDIUM, Frequency.DAILY))
    scheduler.add_task(luna, Task("Breakfast", 5, Priority.HIGH, Frequency.DAILY))
    scheduler.add_task(luna, Task("Clean litter box", 15, Priority.MEDIUM, Frequency.DAILY))
    scheduler.add_task(luna, Task("Vet checkup", 90, Priority.LOW))

    scheduler.generate_plan(start=time(7, 0))

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
