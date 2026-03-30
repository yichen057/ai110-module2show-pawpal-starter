import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler

# ===== SESSION STATE MANAGEMENT =====
# Check if Owner exists in session state, create if not
if 'owner' not in st.session_state:
    st.session_state.owner = Owner(name="Default Owner", max_daily_time=480)
    print("✓ Created new Owner in session state")

# Access the persistent Owner object
owner = st.session_state.owner

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
        # Create new Pet object and add to owner
        new_pet = Pet(name=pet_name, type=species)
        owner.add_pet(new_pet)
        st.success(f"✓ Added pet: {pet_name} ({species})")
        st.rerun()  # Refresh the page to update the UI

# ===== ADD TASK FORM =====
st.subheader("📋 Add a Task")

if owner.pets:
    with st.form("add_task_form"):
        # Pet selector
        pet_options = [f"{pet.name} ({pet.type})" for pet in owner.pets]
        selected_pet_idx = st.selectbox(
            "Select pet for this task", 
            range(len(pet_options)), 
            format_func=lambda x: pet_options[x]
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
        
        # Optional time window inputs
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
            # Create time objects if time window is used
            earliest_start = None
            latest_start = None
            if use_time_window:
                earliest_start = time(earliest_hour, earliest_minute)
                latest_start = time(latest_hour, latest_minute)
            
            # Create new Task object
            new_task = Task(
                description=task_title,
                duration=duration,
                priority=priority_value,
                earliest_start=earliest_start,
                latest_start=latest_start
            )
            
            # Add task to selected pet
            selected_pet = owner.pets[selected_pet_idx]
            selected_pet.add_task(new_task)
            
            st.success(f"✓ Added task '{task_title}' to {selected_pet.name}")
            st.rerun()  # Refresh the page to update the UI
else:
    st.warning("Please add a pet first before adding tasks.")

# ===== GENERATE SCHEDULE =====
st.subheader("📅 Generate Daily Schedule")

if owner.pets and owner.get_all_tasks():
    if st.button("Generate Schedule", type="primary"):
        with st.spinner("Generating optimized schedule..."):
            # Create scheduler and generate schedule
            scheduler = Scheduler()
            schedule = scheduler.generate_schedule(owner)
            
            # Store schedule in session state for display
            st.session_state.current_schedule = schedule
        
        st.success("✓ Schedule generated!")
        
        # Display schedule results
        if st.session_state.current_schedule:
            display_schedule(st.session_state.current_schedule)
    
    # Display current schedule if it exists
    if 'current_schedule' in st.session_state:
        st.divider()
        st.subheader("📋 Current Schedule")
        display_schedule(st.session_state.current_schedule)
        
else:
    st.info("Add pets and tasks first, then generate a schedule.")

# ===== SCHEDULE DISPLAY FUNCTION =====
def display_schedule(schedule):
    """Display a formatted schedule to the user."""
    # Schedule header
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "✅ Feasible" if schedule.is_feasible else "❌ Issues")
    with col2:
        st.metric("Total Time", f"{schedule.total_duration} min")
    with col3:
        remaining = schedule.owner.max_daily_time - schedule.total_duration
        st.metric("Time Left", f"{remaining} min")
    
    # Schedule details
    if schedule.scheduled_tasks:
        st.write("**Scheduled Tasks:**")
        
        # Group by pet for better organization
        pet_groups = {}
        for stask in schedule.scheduled_tasks:
            pet_name = stask.pet.name
            if pet_name not in pet_groups:
                pet_groups[pet_name] = []
            pet_groups[pet_name].append(stask)
        
        # Display tasks grouped by pet
        for pet_name, tasks in pet_groups.items():
            with st.expander(f"🐾 {pet_name} ({len(tasks)} tasks)", expanded=True):
                for i, stask in enumerate(sorted(tasks, key=lambda x: x.start_time), 1):
                    start_time = stask.start_time.strftime("%H:%M")
                    end_time = stask.end_time.strftime("%H:%M")
                    duration = stask.task.duration
                    priority = stask.task.priority
                    description = stask.task.description
                    
                    st.write(f"**{i}.** [{start_time} - {end_time}] {description}")
                    st.caption(f"Duration: {duration} min | Priority: {priority}/5")
                    if stask.reason:
                        st.caption(f"💡 {stask.reason}")
    
    # Display any notes or warnings
    if schedule.notes:
        st.warning(f"**Notes:** {schedule.notes}")
    
    # Feasibility check
    if not schedule.is_feasible:
        st.error("⚠️ Schedule has conflicts or exceeds time limits. Consider adjusting priorities or time constraints.")
