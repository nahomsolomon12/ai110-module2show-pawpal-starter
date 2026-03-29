from pawpal_system import Owner, Pet, Task, Schedule

import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialization — guard pattern so objects survive reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------
st.header("Owner Setup")

with st.form("owner_form"):
    owner_name      = st.text_input("Your name", value="Jordan")
    available_hours = st.number_input("Available hours today", min_value=0.5, max_value=24.0, value=2.0, step=0.5)
    owner_submitted = st.form_submit_button("Save Owner")

if owner_submitted:
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name, available_hours=available_hours)
    else:
        st.session_state.owner.name            = owner_name
        st.session_state.owner.available_hours = available_hours
    st.success(f"Owner set: {st.session_state.owner}")

# ---------------------------------------------------------------------------
# Section 2: Add a Pet
# ---------------------------------------------------------------------------
if st.session_state.owner:
    st.divider()
    st.header("Add a Pet")

    with st.form("pet_form"):
        pet_name    = st.text_input("Pet name", value="Mochi")
        species     = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        age         = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        pet_submitted = st.form_submit_button("Add Pet")

    if pet_submitted:
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added: {new_pet}")

    if st.session_state.owner.pets:
        st.write("**Current pets:**", [str(p) for p in st.session_state.owner.pets])

# ---------------------------------------------------------------------------
# Section 3: Add a Task to a Pet
# ---------------------------------------------------------------------------
if st.session_state.owner and st.session_state.owner.pets:
    st.divider()
    st.header("Add a Task")

    pet_names    = [p.name for p in st.session_state.owner.pets]
    target_name  = st.selectbox("Select pet", pet_names, key="task_target")
    target_pet   = next(p for p in st.session_state.owner.pets if p.name == target_name)

    with st.form("task_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_name = st.text_input("Task name", value="Morning walk")
        with col2:
            duration  = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            frequency = st.selectbox("Frequency", ["daily", "weekly"])
        with col4:
            priority  = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        task_submitted = st.form_submit_button("Add Task")

    if task_submitted:
        new_task = Task(
            name=task_name,
            duration_minutes=int(duration),
            frequency=frequency,
            priority=priority,
        )
        target_pet.add_task(new_task)
        st.success(f"Task added to {target_pet.name}: {new_task}")

    if target_pet.tasks:
        st.write(f"**Tasks for {target_pet.name}:**")
        st.table([
            {
                "Task":     t.name,
                "Duration": f"{t.duration_minutes} min",
                "Frequency": t.frequency,
                "Priority": t.priority,
                "Done":     t.completed,
            }
            for t in target_pet.tasks
        ])

# ---------------------------------------------------------------------------
# Section 4: Generate Schedule
# ---------------------------------------------------------------------------
if st.session_state.owner and st.session_state.owner.pets:
    st.divider()
    st.header("Today's Schedule")

    if st.button("Generate Schedule"):
        for pet in st.session_state.owner.pets:
            if not pet.tasks:
                st.info(f"{pet.name} has no tasks yet.")
                continue
            schedule = Schedule(owner=st.session_state.owner, pet=pet)
            st.subheader(f"{pet.name}")
            st.text(schedule.summary())
