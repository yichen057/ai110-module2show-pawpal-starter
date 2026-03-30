"""
PawPal+ Testing Script
Temporary testing ground to verify scheduling logic works correctly.
Tests: Owner, Pets, Tasks, and Scheduler with realistic scenarios.
"""

from datetime import datetime, time
from pawpal_system import Owner, Pet, Task, Scheduler


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
    print("Adding tasks for Max (Dog):")
    task1 = Task(
        description="Morning Walk",
        duration=30,
        priority=5,
        earliest_start=time(6, 0),
        latest_start=time(9, 0),
        frequency="daily"
    )
    task2 = Task(
        description="Feeding (Breakfast)",
        duration=15,
        priority=5,
        earliest_start=time(7, 0),
        latest_start=time(9, 0),
        frequency="daily"
    )
    task3 = Task(
        description="Play Time",
        duration=45,
        priority=3,
        earliest_start=time(14, 0),
        latest_start=time(17, 0),
        frequency="daily"
    )
    
    dog.add_task(task1)
    dog.add_task(task2)
    dog.add_task(task3)
    print(f"  • {[t.description for t in dog.tasks]}")
    print()
    
    # ===== SETUP: Add Tasks for Cat (Whiskers) =====
    print("Adding tasks for Whiskers (Cat):")
    task4 = Task(
        description="Feeding (Breakfast)",
        duration=10,
        priority=5,
        earliest_start=time(7, 0),
        latest_start=time(10, 0),
        frequency="daily"
    )
    task5 = Task(
        description="Litter Box Cleaning",
        duration=20,
        priority=4,
        earliest_start=time(10, 0),
        latest_start=time(12, 0),
        frequency="daily"
    )
    task6 = Task(
        description="Evening Playtime",
        duration=30,
        priority=2,
        earliest_start=time(18, 0),
        latest_start=time(20, 0),
        frequency="daily"
    )
    
    cat.add_task(task4)
    cat.add_task(task5)
    cat.add_task(task6)
    print(f"  • {[t.description for t in cat.tasks]}")
    print()
    
    # ===== VERIFY: Owner retrieves all tasks =====
    print("-" * 60)
    all_tasks = owner.get_all_tasks()
    print(f"✓ Tasks Retrieved from Owner: {len(all_tasks)} total")
    for i, task in enumerate(all_tasks, 1):
        print(f"  {i}. {task.description} (Priority: {task.priority})")
    print()
    
    # ===== GENERATE: Schedule =====
    print("-" * 60)
    print("Generating optimized schedule...")
    scheduler = Scheduler()
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