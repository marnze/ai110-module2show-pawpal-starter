from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit reruns this file on every interaction, so keep one Owner in
# session_state and build everything else from it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", sex="", contact_info="")
owner: Owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.contact_info = st.text_input("Contact info", value=owner.contact_info)

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        breed = st.text_input("Breed")
    with col2:
        sex = st.selectbox("Sex", ["female", "male", "unknown"])
        weight = st.number_input("Weight (lbs)", min_value=0.0, value=10.0, step=0.5)
        birthday = st.date_input("Birthday", value=date(2020, 1, 1), max_value=date.today())
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(
                Pet(
                    name=pet_name.strip(),
                    sex=sex,
                    species=species,
                    breed=breed,
                    weight=weight,
                    birthday=birthday,
                )
            )
            st.success(f"Added {pet_name.strip()}.")
        else:
            st.error("Pet name is required.")

if owner.pets:
    st.table(
        [
            {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.age, "Tasks": len(p.tasks)}
            for p in owner.list_pets()
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        # Pick by index so two pets with the same name stay distinct.
        pet_index = st.selectbox(
            "Pet",
            range(len(owner.pets)),
            format_func=lambda i: f"{owner.pets[i].name} ({owner.pets[i].species})",
        )
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", list(Priority), index=2, format_func=lambda p: p.name.title())
            frequency = st.selectbox("Frequency", list(Frequency), format_func=lambda f: f.value.title())
        if st.form_submit_button("Add task"):
            pet = owner.pets[pet_index]
            pet.add_task(
                Task(title=task_title, duration=int(duration), priority=priority, frequency=frequency)
            )
            st.success(f"Added '{task_title}' for {pet.name}.")

    if owner.get_all_tasks():
        # Filtering only needs the day, not a time budget.
        view = Scheduler(owner=owner, day=date.today(), available_minutes=0)
        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox("Show pet", ["All pets"] + sorted({p.name for p in owner.pets}))
        with col2:
            status_filter = st.selectbox("Show status", ["All", "Due today", "Done"])
        tasks = view.sort_by_time(
            view.filter_tasks(
                pet_name=None if pet_filter == "All pets" else pet_filter,
                done={"All": None, "Due today": False, "Done": True}[status_filter],
            )
        )
        if tasks:
            st.table(
                [
                    {
                        "Time": f"{t.start_time:%H:%M}" if t.start_time else "—",
                        "Pet": t.pet.name,
                        "Task": t.title,
                        "Minutes": t.duration,
                        "Priority": t.priority.name.title(),
                        "Frequency": t.frequency.value.title(),
                        "Status": "✅ Done" if t.is_done else ("Due" if t.is_due(view.day) else "Upcoming"),
                    }
                    for t in tasks
                ]
            )
        else:
            st.info("No tasks match these filters.")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
col1, col2, col3 = st.columns(3)
with col1:
    plan_day = st.date_input("Day", value=date.today())
with col2:
    start_at = st.time_input("Start time", value=time(8, 0))
with col3:
    available = st.number_input("Available minutes", min_value=0, max_value=1440, value=120)

scheduler = Scheduler(owner=owner, day=plan_day, available_minutes=int(available))
if st.button("Generate schedule", type="primary"):
    scheduler.generate_plan(start_at)
    # Start times live on the tasks, but the reasons only live on this
    # Scheduler, so keep them for the reruns that follow.
    st.session_state.plan_reasons = (plan_day, scheduler.explain_plan())

# Render from the tasks themselves so the schedule survives reruns
# (changing a filter, moving a task, etc.).
scheduled = scheduler.get_scheduled_tasks()
if not scheduled:
    st.info(f"Nothing scheduled for {plan_day:%A, %B %d} yet. Click **Generate schedule**.")
else:
    conflicts = scheduler.find_conflicts()
    if conflicts:
        lines = [
            f"**⚠️ {len(conflicts)} time conflict{'s' if len(conflicts) > 1 else ''}** — "
            "you can't be in two places at once:"
        ]
        for a, b in conflicts:
            lines.append(
                f"- **{a.title}** for {a.pet.name} ({a.start_time:%H:%M}–{a.end_time():%H:%M}) overlaps "
                f"**{b.title}** for {b.pet.name} ({b.start_time:%H:%M}–{b.end_time():%H:%M}). "
                f"Try moving *{b.title}* to {a.end_time():%H:%M} or later."
            )
        st.warning("\n".join(lines))
    else:
        st.success(f"✅ {len(scheduled)} task(s) planned for {plan_day:%A, %B %d} with no time conflicts.")

    planned = sum(t.duration for t in scheduled)
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks", len(scheduled))
    col2.metric("Planned minutes", planned)
    col3.metric("Minutes free", int(available) - planned)

    conflicting = {t for pair in conflicts for t in pair}
    st.table(
        [
            {
                "": "⚠️" if t in conflicting else "",
                "Start": f"{t.start_time:%H:%M}",
                "End": f"{t.end_time():%H:%M}",
                "Pet": t.pet.name,
                "Task": t.title,
                "Priority": t.priority.name.title(),
                "Status": "✅ Done" if t.is_done else "Pending",
            }
            for t in scheduled
        ]
    )

    skipped = [t for t in scheduler.get_pending_tasks() if t.start_time is None]
    if skipped:
        st.warning(
            "Didn't fit today: "
            + ", ".join(f"**{t.title}** ({t.pet.name}, {t.duration} min)" for t in skipped)
            + ". Free up more minutes or lower another task's priority."
        )

    saved = st.session_state.get("plan_reasons")
    if saved and saved[0] == plan_day:
        with st.expander("Why this plan?"):
            for reason in saved[1]:
                st.markdown(f"- {reason}")

    pending = [t for t in scheduled if not t.is_done]
    if pending:
        with st.expander("Move a task to a fixed time"):
            st.caption("For things like a vet appointment. Generating the schedule again will replace this.")
            with st.form("reschedule"):
                idx = st.selectbox(
                    "Task",
                    range(len(pending)),
                    format_func=lambda i: f"{pending[i].title} ({pending[i].pet.name}, {pending[i].start_time:%H:%M})",
                )
                new_start = st.time_input("New start time", value=time(9, 0))
                if st.form_submit_button("Move task"):
                    pending[idx].reschedule(datetime.combine(plan_day, new_start))
                    st.rerun()
