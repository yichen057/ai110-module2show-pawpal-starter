import streamlit as st
from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler


def build_task_rows(tasks, owner):
    """Convert Task objects into table-friendly dictionaries."""
    pet_lookup = {}
    for pet in owner.pets:
        for task in pet.tasks:
            pet_lookup[id(task)] = pet.name

    rows = []
    for task in tasks:
        rows.append(
            {
                "Pet": pet_lookup.get(id(task), "Expanded task"),
                "Task": task.description,
                "Priority": task.priority,
                "Duration (min)": task.duration,
                "Window": (
                    f"{task.earliest_start.strftime('%H:%M') if task.earliest_start else '06:00'}"
                    f" - "
                    f"{task.latest_start.strftime('%H:%M') if task.latest_start else '22:00'}"
                ),
                "Completed": "Yes" if task.is_completed else "No",
            }
        )
    return rows


def build_schedule_rows(scheduled_tasks):
    """Convert ScheduledTask objects into table-friendly dictionaries."""
    rows = []
    for scheduled_task in scheduled_tasks:
        rows.append(
            {
                "Start": scheduled_task.start_time.strftime("%H:%M"),
                "End": scheduled_task.end_time.strftime("%H:%M"),
                "Pet": scheduled_task.pet.name,
                "Task": scheduled_task.task.description,
                "Priority": scheduled_task.task.priority,
                "Duration (min)": scheduled_task.task.duration,
                "Why it was placed here": scheduled_task.reason or "Scheduled by optimizer",
            }
        )
    return rows


def render_conflict_warning(scheduler, schedule):
    """Present conflict details in a clear, action-oriented format."""
    overlaps = scheduler.detect_conflicts(schedule.scheduled_tasks)
    same_start_conflicts = scheduler.detect_same_start_conflicts(schedule.scheduled_tasks)
    warning_summary = scheduler.get_conflict_warning(schedule)

    if not overlaps and not same_start_conflicts and schedule.total_duration <= schedule.owner.max_daily_time:
        st.success("No scheduling conflicts detected. This plan fits within your available care time.")
        return

    st.warning("Some tasks need attention before this plan is fully reliable.")

    if warning_summary:
        st.caption(warning_summary)

    if schedule.total_duration > schedule.owner.max_daily_time:
        overflow = schedule.total_duration - schedule.owner.max_daily_time
        st.error(
            f"The schedule is over your daily limit by {overflow} minutes. "
            "Consider shortening a task or lowering the number of tasks for today."
        )

    for first, second in overlaps:
        st.warning(
            f"Time overlap: {first.pet.name}'s '{first.task.description}' "
            f"({first.start_time.strftime('%H:%M')}-{first.end_time.strftime('%H:%M')}) overlaps with "
            f"'{second.task.description}' ({second.start_time.strftime('%H:%M')}-{second.end_time.strftime('%H:%M')})."
        )

    for first, second in same_start_conflicts:
        st.warning(
            f"Same start time: '{first.task.description}' and '{second.task.description}' both begin at "
            f"{first.start_time.strftime('%H:%M')}. A pet owner should do only one at a time."
        )


def display_schedule(schedule, scheduler):
    """Display a formatted schedule to the user."""
    chronological_tasks = schedule.get_schedule_by_time()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "Feasible" if schedule.is_feasible else "Needs review")
    with col2:
        st.metric("Total Time", f"{schedule.total_duration} min")
    with col3:
        remaining = schedule.owner.max_daily_time - schedule.total_duration
        st.metric("Time Left", f"{remaining} min")

    render_conflict_warning(scheduler, schedule)

    if chronological_tasks:
        st.write("**Today's Plan**")
        st.table(build_schedule_rows(chronological_tasks))

    if schedule.notes:
        st.info(schedule.notes)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ===== SESSION STATE MANAGEMENT =====
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Default Owner", max_daily_time=480)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

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

# ===== CURRENT OWNER STATUS =====
st.subheader("📊 Current Owner Status")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Owner", owner.name)

with col2:
    st.metric("Pets", len(owner.pets))

with col3:
    all_tasks = owner.get_all_tasks()
    st.metric("Total Tasks", len(all_tasks))

if owner.pets:
    st.write("**Pets:**")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.type}) - {len(pet.tasks)} tasks")
else:
    st.info("No pets added yet. Use the form below to add pets and tasks.")

st.divider()

# ===== ADD PET FORM =====
st.subheader("🐾 Add a New Pet")

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="pet_species")

    submitted_pet = st.form_submit_button("Add Pet")

    if submitted_pet:
        try:
            new_pet = Pet(name=pet_name, type=species)
            owner.add_pet(new_pet)
            st.success(f"Added pet: {pet_name} ({species})")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

# ===== ADD TASK FORM =====
st.subheader("📋 Add a Task")

if owner.pets:
    with st.form("add_task_form"):
        pet_options = [f"{pet.name} ({pet.type})" for pet in owner.pets]
        selected_pet_idx = st.selectbox(
            "Select pet for this task",
            range(len(pet_options)),
            format_func=lambda x: pet_options[x],
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task description", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        with col3:
            priority_options = {"Low": 1, "Medium": 3, "High": 5}
            priority_label = st.selectbox("Priority", list(priority_options.keys()), index=2)
            priority_value = priority_options[priority_label]

        with st.expander("Time Window (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                earliest_hour = st.number_input("Earliest hour", 0, 23, 6)
                earliest_minute = st.number_input("Earliest minute", 0, 59, 0)
            with col2:
                latest_hour = st.number_input("Latest hour", 0, 23, 22)
                latest_minute = st.number_input("Latest minute", 0, 59, 0)

            use_time_window = st.checkbox("Use time window", value=True)

        submitted_task = st.form_submit_button("Add Task")

        if submitted_task:
            try:
                earliest_start = None
                latest_start = None
                if use_time_window:
                    earliest_start = time(earliest_hour, earliest_minute)
                    latest_start = time(latest_hour, latest_minute)

                new_task = Task(
                    description=task_title,
                    duration=duration,
                    priority=priority_value,
                    earliest_start=earliest_start,
                    latest_start=latest_start,
                )

                selected_pet = owner.pets[selected_pet_idx]
                selected_pet.add_task(new_task)

                st.success(f"Added task '{task_title}' to {selected_pet.name}")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
else:
    st.warning("Please add a pet first before adding tasks.")

# ===== ALGORITHMIC TASK VIEW =====
st.divider()
st.subheader("🧠 Task Queue Preview")

if all_tasks:
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_pet_filter = st.selectbox("Pet filter", ["All pets"] + [pet.name for pet in owner.pets])
    with col2:
        priority_filter = st.selectbox("Minimum priority", [1, 2, 3, 4, 5], index=0)
    with col3:
        sort_mode = st.selectbox("Sort queue by", ["Priority", "Earliest time"])

    filtered_tasks = owner.filter_tasks(
        pet_names=None if selected_pet_filter == "All pets" else [selected_pet_filter],
        completed=False,
        priority_min=priority_filter,
    )

    if sort_mode == "Priority":
        preview_tasks = scheduler.sort_by_priority(filtered_tasks)
        st.success("Showing tasks in scheduler priority order.")
    else:
        preview_tasks = scheduler.sort_by_time(filtered_tasks)
        st.success("Showing tasks in chronological time-window order.")

    if preview_tasks:
        st.table(build_task_rows(preview_tasks, owner))
    else:
        st.warning("No tasks match the current filters.")
else:
    st.info("Add tasks to preview how the scheduler sorts and filters them.")

# ===== GENERATE SCHEDULE =====
st.divider()
st.subheader("📅 Generate Daily Schedule")

if owner.pets and owner.get_all_tasks():
    if st.button("Generate Schedule", type="primary"):
        with st.spinner("Generating optimized schedule..."):
            st.session_state.current_schedule = scheduler.generate_schedule(owner)

        if st.session_state.current_schedule.is_feasible:
            st.success("Schedule generated successfully.")
        else:
            st.warning("Schedule generated, but it includes issues that need review.")

    if "current_schedule" in st.session_state:
        st.divider()
        st.subheader("📋 Current Schedule")
        display_schedule(st.session_state.current_schedule, scheduler)
else:
    st.info("Add pets and tasks first, then generate a schedule.")
