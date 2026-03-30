"""
PawPal+ Testing Script
Temporary testing ground to verify scheduling logic works correctly.
Tests: Owner, Pets, Tasks, and Scheduler with realistic scenarios.
"""

from datetime import datetime, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Schedule, ScheduledTask


def main():
    """Main testing function."""
    print("=" * 60)
    print("🐾 PawPal+ Scheduler Testing")
    print("=" * 60)
    print()
    
    # ===== SETUP: Create Owner =====
    owner = Owner(name="Alice", max_daily_time=480)  # 8 hours
    print(f"✓ Owner Created: {owner.name} (Max daily time: {owner.max_daily_time} minutes)")
    print()
    
    # ===== SETUP: Create Pets =====
    dog = Pet(name="Max", type="Dog")
    cat = Pet(name="Whiskers", type="Cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    print(f"✓ Pets Added: {[pet.name for pet in owner.pets]}")
    print()
    
    # ===== SETUP: Add Tasks for Dog (Max) =====
    print("Adding tasks for Max (Dog) - OUT OF ORDER:")
    
    # Add Play Time first (should be middle chronologically)
    task3 = Task(
        description="Play Time",
        duration=45,
        priority=3,
        earliest_start=time(14, 0),
        latest_start=time(17, 0),
        frequency="daily"
    )
    
    # Add Feeding second (should be early)
    task2 = Task(
        description="Feeding (Breakfast)",
        duration=15,
        priority=5,
        earliest_start=time(7, 0),
        latest_start=time(9, 0),
        frequency="daily"
    )
    
    # Add Morning Walk last (should be earliest)
    task1 = Task(
        description="Morning Walk",
        duration=30,
        priority=5,
        earliest_start=time(6, 0),
        latest_start=time(9, 0),
        frequency="daily"
    )
    
    dog.add_task(task3)  # Play Time first
    dog.add_task(task2)  # Feeding second  
    dog.add_task(task1)  # Morning Walk last
    print(f"  • Added: {[t.description for t in dog.tasks]} (Note: out of chronological order)")
    print()
    
    # ===== SETUP: Add Tasks for Cat (Whiskers) =====
    print("Adding tasks for Whiskers (Cat) - OUT OF ORDER:")
    
    # Add Evening Playtime first (should be latest)
    task6 = Task(
        description="Evening Playtime",
        duration=30,
        priority=2,
        earliest_start=time(18, 0),
        latest_start=time(20, 0),
        frequency="daily"
    )
    
    # Add Litter Box second (should be middle)
    task5 = Task(
        description="Litter Box Cleaning",
        duration=20,
        priority=4,
        earliest_start=time(10, 0),
        latest_start=time(12, 0),
        frequency="weekly"  # Changed to weekly for demonstration
    )
    
    # Add Feeding last (should be earliest)
    task4 = Task(
        description="Feeding (Breakfast)",
        duration=10,
        priority=5,
        earliest_start=time(7, 0),
        latest_start=time(10, 0),
        frequency="daily"
    )
    
    cat.add_task(task6)  # Evening Playtime first
    cat.add_task(task5)  # Litter Box second
    cat.add_task(task4)  # Feeding last
    print(f"  • Added: {[t.description for t in cat.tasks]} (Note: out of chronological order)")
    print()
    
    # ===== DEMO: New Features =====
    print("-" * 60)
    print("Demonstrating new features with OUT-OF-ORDER tasks:")
    
    scheduler = Scheduler()
    all_tasks = owner.get_all_tasks()
    
    print(f"✓ Tasks as added (unordered): {len(all_tasks)} total")
    for i, task in enumerate(all_tasks, 1):
        start = task.earliest_start.strftime("%H:%M") if task.earliest_start else "No time"
        print(f"  {i}. {task.description} (Start: {start}, Priority: {task.priority})")
    print()
    
    # Filter by pet
    max_tasks = owner.filter_tasks_by_pet("Max")
    print(f"✓ Tasks for Max: {len(max_tasks)}")
    for task in max_tasks:
        print(f"  • {task.description}")
    
    # Filter by status
    incomplete_tasks = owner.filter_tasks_by_status(False)
    print(f"✓ Incomplete tasks: {len(incomplete_tasks)}")
    
    # Advanced filtering with multiple criteria
    high_priority_incomplete = owner.filter_tasks(completed=False, priority_min=4)
    print(f"✓ High-priority incomplete tasks: {len(high_priority_incomplete)}")
    for task in high_priority_incomplete:
        print(f"  • {task.description} (Priority: {task.priority})")
    
    short_tasks = owner.filter_tasks(duration_max=20)
    print(f"✓ Short tasks (≤20 min): {len(short_tasks)}")
    for task in short_tasks:
        print(f"  • {task.description} ({task.duration} min)")
    
    # Sort by time
    time_sorted = scheduler.sort_by_time(all_tasks)
    print("✓ Tasks sorted by time (chronological order):")
    for task in time_sorted:
        start = task.earliest_start.strftime("%H:%M") if task.earliest_start else "No time"
        print(f"  • {task.description} (Start: {start})")
    print()
    
    # ===== GENERATE: Schedule =====
    print("-" * 60)
    print("Generating optimized schedule...")
    schedule = scheduler.generate_schedule(owner)
    print()
    
    # ===== DISPLAY: Today's Schedule =====
    print("=" * 60)
    print("📅 TODAY'S SCHEDULE FOR " + owner.name.upper())
    print("=" * 60)
    print()
    
    if not schedule.scheduled_tasks:
        print("❌ No tasks scheduled.")
    else:
        sorted_tasks = schedule.get_schedule_by_time()
        for i, scheduled_task in enumerate(sorted_tasks, 1):
            start = scheduled_task.start_time.strftime("%H:%M")
            end = scheduled_task.end_time.strftime("%H:%M")
            pet_name = scheduled_task.pet.name
            task_desc = scheduled_task.task.description
            priority = scheduled_task.task.priority
            duration = scheduled_task.task.duration
            
            print(f"{i}. [{start} - {end}] {task_desc}")
            print(f"   🐾 Pet: {pet_name} | Priority: {priority}/5 | Duration: {duration} min")

    print()
    print("-" * 60)
    print("⚠️ FORCED EXACT-TIME CONFLICT CHECK:")

    # Create an explicit conflict schedule to verify warning behavior
    conflict_schedule = Schedule(owner=owner)
    t0 = datetime.combine(datetime.now().date(), time(8, 0))
    task_a = ScheduledTask(task=Task(description="Conflict Check A", duration=30, priority=1, scheduled_time=t0), pet=dog, start_time=t0, end_time=t0 + timedelta(minutes=30))
    task_b = ScheduledTask(task=Task(description="Conflict Check B", duration=30, priority=1, scheduled_time=t0), pet=cat, start_time=t0, end_time=t0 + timedelta(minutes=30))
    conflict_schedule.add_scheduled_task(task_a)
    conflict_schedule.add_scheduled_task(task_b)

    exact_conflicts = scheduler.detect_same_start_conflicts(conflict_schedule.scheduled_tasks)
    if exact_conflicts:
        print(f"⚠️ WARNING: {len(exact_conflicts)} exact-start task conflict(s) detected.")
        for st1, st2 in exact_conflicts:
            print(f"  - {st1.task.description} ({st1.pet.name}) and {st2.task.description} ({st2.pet.name}) at {st1.start_time.strftime('%H:%M')}")
    else:
        print("✅ No exact-start conflicts detected (unexpected in forced case)")

    print()
    print("-" * 60)
    print("🔄 DEMONSTRATING TASK RECURRENCE:")
    
    # Mark a daily task complete to show recurrence
    morning_walk_task = None
    for task in dog.tasks:
        if task.description == "Morning Walk" and not task.is_completed:
            morning_walk_task = task
            break
    
    if morning_walk_task:
        print(f"Marking '{morning_walk_task.description}' (daily) as complete...")
        owner.mark_task_complete(morning_walk_task, dog)
        print(f"✓ Task marked complete. New recurring instance created!")
        print(f"✓ Dog now has {len(dog.tasks)} tasks")
        
        # Show the new task
        for task in dog.tasks:
            if not task.is_completed and task.description == "Morning Walk":
                scheduled_date = task.scheduled_time.strftime("%Y-%m-%d") if task.scheduled_time else "No date"
                print(f"  • New Morning Walk scheduled for: {scheduled_date}")
                break
    
    # Mark a weekly task complete
    litter_box_task = None
    for task in cat.tasks:
        if task.description == "Litter Box Cleaning" and not task.is_completed:
            litter_box_task = task
            break
    
    if litter_box_task:
        print(f"Marking '{litter_box_task.description}' (weekly) as complete...")
        owner.mark_task_complete(litter_box_task, cat)
        print(f"✓ Weekly task marked complete. New recurring instance created!")
        print(f"✓ Cat now has {len(cat.tasks)} tasks")
        
        # Show the new task
        for task in cat.tasks:
            if not task.is_completed and task.description == "Litter Box Cleaning":
                scheduled_date = task.scheduled_time.strftime("%Y-%m-%d") if task.scheduled_time else "No date"
                print(f"  • New Litter Box Cleaning scheduled for: {scheduled_date}")
                break
    
    print()
    print("=" * 60)
    print("📊 SCHEDULE SUMMARY")
    print("=" * 60)
    feasible_status = "✅ FEASIBLE" if schedule.is_feasible else "❌ NOT FEASIBLE"
    print(f"Status: {feasible_status}")
    print(f"Total Duration Scheduled: {schedule.total_duration} minutes")
    print(f"Max Daily Available Time: {owner.max_daily_time} minutes")
    print(f"Remaining Time: {owner.max_daily_time - schedule.total_duration} minutes")
    print()
    
    # Display any notes or warnings
    if schedule.notes:
        print("⚠️  NOTES:")
        print(schedule.notes)
        print()
    
    print("=" * 60)
    print("✓ Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()