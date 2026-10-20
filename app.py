from datetime import date, time

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

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.table(
            [
                {
                    "Pet": t.pet.name,
                    "Task": t.title,
                    "Minutes": t.duration,
                    "Priority": t.priority.name.title(),
                    "Frequency": t.frequency.value.title(),
                }
                for t in all_tasks
            ]
        )
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

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner, day=plan_day, available_minutes=int(available))
    plan = scheduler.generate_plan(start_at)
    if plan:
        st.table(
            [
                {
                    "Start": f"{t.start_time:%H:%M}",
                    "End": f"{t.end_time():%H:%M}",
                    "Pet": t.pet.name,
                    "Task": t.title,
                    "Priority": t.priority.name.title(),
                }
                for t in plan
            ]
        )
    else:
        st.warning("Nothing could be scheduled. Add tasks or increase the available minutes.")

    with st.expander("Why this plan?", expanded=True):
        for reason in scheduler.explain_plan():
            st.markdown(f"- {reason}")

    for a, b in scheduler.find_conflicts():
        st.error(f"Conflict: '{a.title}' overlaps '{b.title}'.")
