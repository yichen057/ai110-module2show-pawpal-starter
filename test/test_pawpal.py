"""
Unit tests for PawPal+ system
Tests for Task, Pet, Owner, and Scheduler classes
"""

import pytest
from datetime import datetime, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Schedule, ScheduledTask


class TestTask:
    """Test cases for Task class."""
    
    def test_task_creation(self):
        """Test that a task can be created with required attributes."""
        task = Task(
            description="Morning Walk",
            duration=30,
            priority=5,
            earliest_start=time(6, 0),
            latest_start=time(9, 0)
        )
        assert task.description == "Morning Walk"
        assert task.duration == 30
        assert task.priority == 5
        assert task.is_completed is False
    
    def test_task_mark_complete(self):
        """Test that calling mark_complete() changes the task's completion status."""
        task = Task(
            description="Feeding",
            duration=15,
            priority=5
        )
        assert task.is_completed is False, "Task should start incomplete"
        
        task.mark_complete()
        assert task.is_completed is True, "Task should be marked complete"
    
    def test_task_mark_incomplete(self):
        """Test that calling mark_incomplete() changes the task back to incomplete."""
        task = Task(
            description="Feeding",
            duration=15,
            priority=5,
            is_completed=True
        )
        assert task.is_completed is True, "Task should start complete"
        
        task.mark_incomplete()
        assert task.is_completed is False, "Task should be marked incomplete"
    
    def test_task_completion_toggle(self):
        """Test toggling task completion multiple times."""
        task = Task(description="Play", duration=30, priority=3)
        
        assert task.is_completed is False
        task.mark_complete()
        assert task.is_completed is True
        task.mark_incomplete()
        assert task.is_completed is False
        task.mark_complete()
        assert task.is_completed is True


class TestPet:
    """Test cases for Pet class."""
    
    def test_pet_creation(self):
        """Test that a pet can be created with name and type."""
        pet = Pet(name="Max", type="Dog")
        assert pet.name == "Max"
        assert pet.type == "Dog"
        assert pet.tasks == []
    
    def test_add_task_to_pet(self):
        """Test that adding a task to a Pet increases that pet's task count."""
        pet = Pet(name="Whiskers", type="Cat")
        assert len(pet.tasks) == 0, "Pet should have 0 tasks initially"
        
        task1 = Task(description="Feeding", duration=10, priority=5)
        pet.add_task(task1)
        assert len(pet.tasks) == 1, "Pet should have 1 task after adding"
        
        task2 = Task(description="Grooming", duration=20, priority=3)
        pet.add_task(task2)
        assert len(pet.tasks) == 2, "Pet should have 2 tasks after adding another"
    
    def test_add_multiple_tasks(self):
        """Test adding multiple tasks and verifying count."""
        pet = Pet(name="Buddy", type="Dog")
        
        for i in range(5):
            task = Task(description=f"Task {i}", duration=15, priority=3)
            pet.add_task(task)
        
        assert len(pet.tasks) == 5, "Pet should have 5 tasks"
    
    def test_pet_task_list_contains_added_tasks(self):
        """Test that added tasks are actually in the pet's task list."""
        pet = Pet(name="Max", type="Dog")
        task1 = Task(description="Morning Walk", duration=30, priority=5)
        task2 = Task(description="Evening Walk", duration=30, priority=5)
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        assert task1 in pet.tasks, "First task should be in pet's tasks"
        assert task2 in pet.tasks, "Second task should be in pet's tasks"
        assert len(pet.tasks) == 2


class TestOwner:
    """Test cases for Owner class."""
    
    def test_owner_creation(self):
        """Test that an owner can be created."""
        owner = Owner(name="Alice")
        assert owner.name == "Alice"
        assert owner.pets == []
        assert owner.max_daily_time == 480
    
    def test_add_pet_to_owner(self):
        """Test that adding a pet to an owner increases pet count."""
        owner = Owner(name="Bob")
        assert len(owner.pets) == 0, "Owner should have 0 pets initially"
        
        pet1 = Pet(name="Max", type="Dog")
        owner.add_pet(pet1)
        assert len(owner.pets) == 1, "Owner should have 1 pet after adding"
        
        pet2 = Pet(name="Whiskers", type="Cat")
        owner.add_pet(pet2)
        assert len(owner.pets) == 2, "Owner should have 2 pets after adding another"
    
    def test_get_all_tasks(self):
        """Test that owner can retrieve all tasks from all pets."""
        owner = Owner(name="Charlie")
        
        # Create and add first pet with tasks
        dog = Pet(name="Max", type="Dog")
        dog.add_task(Task(description="Walk", duration=30, priority=5))
        dog.add_task(Task(description="Feeding", duration=15, priority=5))
        owner.add_pet(dog)
        
        # Create and add second pet with tasks
        cat = Pet(name="Whiskers", type="Cat")
        cat.add_task(Task(description="Litter", duration=10, priority=4))
        owner.add_pet(cat)
        
        # Get all tasks
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 3, "Owner should have 3 total tasks"
    
    def test_get_all_tasks_empty(self):
        """Test that get_all_tasks returns empty list when no tasks."""
        owner = Owner(name="Diana")
        owner.add_pet(Pet(name="Pet1", type="Dog"))
        
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 0, "Should have no tasks"


class TestScheduler:
    """Test cases for Scheduler class."""
    
    def test_sort_by_priority(self):
        """Test that tasks are sorted by priority (highest first)."""
        scheduler = Scheduler()
        
        tasks = [
            Task(description="Low", duration=10, priority=1),
            Task(description="High", duration=10, priority=5),
            Task(description="Medium", duration=10, priority=3)
        ]
        
        sorted_tasks = scheduler.sort_by_priority(tasks)
        
        assert sorted_tasks[0].priority == 5, "Highest priority should be first"
        assert sorted_tasks[1].priority == 3, "Medium priority should be second"
        assert sorted_tasks[2].priority == 1, "Lowest priority should be last"
    
    def test_detect_conflicts(self):
        """Test that scheduler detects overlapping time slots."""
        scheduler = Scheduler()
        
        pet = Pet(name="Max", type="Dog")
        now = datetime.now()
        
        # Create two overlapping scheduled tasks
        task1 = Task(description="Task1", duration=30, priority=5)
        task2 = Task(description="Task2", duration=30, priority=4)
        
        st1 = ScheduledTask(
            task=task1,
            pet=pet,
            start_time=now,
            end_time=now + timedelta(minutes=30)
        )
        st2 = ScheduledTask(
            task=task2,
            pet=pet,
            start_time=now + timedelta(minutes=15),
            end_time=now + timedelta(minutes=45)
        )
        
        conflicts = scheduler.detect_conflicts([st1, st2])
        assert len(conflicts) == 1, "Should detect one conflict"
    
    def test_no_conflicts(self):
        """Test that scheduler detects no conflicts for non-overlapping tasks."""
        scheduler = Scheduler()
        
        pet = Pet(name="Max", type="Dog")
        now = datetime.now()
        
        # Create two non-overlapping scheduled tasks
        task1 = Task(description="Task1", duration=30, priority=5)
        task2 = Task(description="Task2", duration=30, priority=4)
        
        st1 = ScheduledTask(
            task=task1,
            pet=pet,
            start_time=now,
            end_time=now + timedelta(minutes=30)
        )
        st2 = ScheduledTask(
            task=task2,
            pet=pet,
            start_time=now + timedelta(minutes=30),
            end_time=now + timedelta(minutes=60)
        )
        
        conflicts = scheduler.detect_conflicts([st1, st2])
        assert len(conflicts) == 0, "Should detect no conflicts"
    
    def test_generate_schedule_feasible(self):
        """Test that scheduler generates a feasible schedule."""
        owner = Owner(name="Eve", max_daily_time=480)
        
        pet = Pet(name="Max", type="Dog")
        pet.add_task(Task(description="Walk", duration=30, priority=5, 
                         earliest_start=time(6, 0), latest_start=time(10, 0)))
        pet.add_task(Task(description="Feeding", duration=15, priority=5,
                         earliest_start=time(7, 0), latest_start=time(9, 0)))
        owner.add_pet(pet)
        
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        
        assert schedule.is_feasible is True, "Schedule should be feasible"
        assert len(schedule.scheduled_tasks) == 2, "Should have 2 scheduled tasks"


# Edge Case Tests (Phase 4 Critical Tests)
class TestSchedulerEdgeCases:
    """Edge case tests for scheduler sorting, time windows, and conflict detection."""
    
    # Edge Case #1: Back-to-Back Task Scheduling (Boundary Conflict Detection)
    def test_back_to_back_tasks_no_conflict(self):
        """Test that consecutive tasks (ending/starting at same time) are NOT flagged as conflicts.
        
        Scenario: Task A ends at 9:30, Task B starts at 9:30 (adjacent, not overlapping).
        Expected: No conflict detected, schedule.is_feasible = True
        """
        scheduler = Scheduler()
        pet = Pet(name="Max", type="Dog")
        
        now = datetime.combine(datetime.now().date(), time(6, 0))
        
        # Task A: 9:00-9:30
        task_a = Task(description="Morning Walk", duration=30, priority=5)
        st_a = ScheduledTask(
            task=task_a,
            pet=pet,
            start_time=now.replace(hour=9, minute=0),
            end_time=now.replace(hour=9, minute=30)
        )
        
        # Task B: 9:30-10:00 (starts exactly when A ends)
        task_b = Task(description="Feeding", duration=30, priority=5)
        st_b = ScheduledTask(
            task=task_b,
            pet=pet,
            start_time=now.replace(hour=9, minute=30),
            end_time=now.replace(hour=10, minute=0)
        )
        
        # Check conflicts
        conflicts = scheduler.detect_conflicts([st_a, st_b])
        assert len(conflicts) == 0, "Adjacent tasks should NOT conflict"
        
        # Verify schedule feasibility
        owner = Owner(name="Test", max_daily_time=480)
        owner.add_pet(pet)
        schedule = Schedule(owner=owner, scheduled_tasks=[st_a, st_b])
        assert scheduler.is_feasible(owner, [st_a, st_b]) is True, "Schedule with adjacent tasks should be feasible"
    
    # Edge Case #2: Task Duration Exceeds Available Time Window
    def test_task_too_long_for_time_window(self):
        """Test that a task requiring more time than the window permits is not scheduled.
        
        Scenario: 60-minute task with earliest_start=9:00, latest_start=9:30 (only 30 min available).
        Expected: _find_available_slot() returns None, task rejected from schedule
        """
        scheduler = Scheduler()
        owner = Owner(name="TestOwner", max_daily_time=480)
        
        pet = Pet(name="Max", type="Dog")
        # Task requires 60 minutes but window is only 9:00-9:30 (30 min max)
        task = Task(
            description="Long Grooming",
            duration=60,
            priority=5,
            earliest_start=time(9, 0),
            latest_start=time(9, 30)
        )
        pet.add_task(task)
        owner.add_pet(pet)
        
        # Try to find a slot for this task
        now = datetime.combine(datetime.now().date(), time(6, 0))
        scheduled_tasks = []
        slot = scheduler._find_available_slot(task, pet, scheduled_tasks, now, owner.max_daily_time)
        
        assert slot is None, "No slot should be found when task duration exceeds time window"
        
        # Verify full schedule generation rejects this task
        schedule = scheduler.generate_schedule(owner)
        assert len(schedule.scheduled_tasks) == 0, "Task should not be scheduled"
        assert "Could not schedule" in schedule.notes, "Notes should indicate scheduling failure"
        assert schedule.is_feasible is False or len(schedule.scheduled_tasks) == 0
    
    # Edge Case #3: Multiple High-Priority Tasks Exceeding Max Daily Time
    def test_capacity_overflow_with_high_priority_tasks(self):
        """Test that capacity constraint is enforced even with all high-priority tasks.
        
        Scenario: max_daily_time=120 min. Three priority-5 tasks (60, 60, 45 min).
        Expected: Only fit what's available (≤120 min), at least one task rejected with warning
        """
        scheduler = Scheduler()
        owner = Owner(name="BusyOwner", max_daily_time=120)  # Only 2 hours available
        
        pet = Pet(name="Max", type="Dog")
        
        # All high priority, but total > 120 min
        task1 = Task(description="Task1", duration=60, priority=5, 
                    earliest_start=time(6, 0), latest_start=time(22, 0))
        task2 = Task(description="Task2", duration=60, priority=5,
                    earliest_start=time(6, 0), latest_start=time(22, 0))
        task3 = Task(description="Task3", duration=45, priority=5,
                    earliest_start=time(6, 0), latest_start=time(22, 0))
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        schedule = scheduler.generate_schedule(owner)
        
        # Should have scheduled at most 120 minutes
        assert schedule.total_duration <= owner.max_daily_time, \
            f"Total duration {schedule.total_duration} should not exceed max {owner.max_daily_time}"
        # At least one task should fail to fit
        assert len(schedule.scheduled_tasks) < 3, \
            "Not all 3 tasks should be scheduled (165 min > 120 min constraint)"
        # At least one task should have failed scheduling
        assert "Could not schedule" in schedule.notes, \
            "Notes should indicate that at least one task couldn't be scheduled"
    
    # Edge Case #4: Twice-Daily Task Expansion with Time Window Constraints
    def test_twice_daily_task_expansion_respects_constraints(self):
        """Test that twice_daily tasks expand with correct morning/evening time constraints.
        
        Scenario: Task with frequency="twice_daily", earliest=8:00, latest=20:00.
        Morning instance should be ≤12:00, evening ≥18:00.
        Expected: Two expanded tasks with non-overlapping implicit time windows
        """
        scheduler = Scheduler()
        
        # Create a twice_daily task
        task = Task(
            description="Medication",
            duration=10,
            priority=4,
            earliest_start=time(8, 0),
            latest_start=time(20, 0),
            frequency="twice_daily"
        )
        
        expanded = scheduler.expand_recurring_tasks([task])
        
        assert len(expanded) == 2, "Should expand into 2 instances"
        assert "(Morning)" in expanded[0].description, "First should be morning instance"
        assert "(Evening)" in expanded[1].description, "Second should be evening instance"
        
        # Check morning constraint
        morning_task = expanded[0]
        if morning_task.latest_start:
            assert morning_task.latest_start <= time(12, 0), \
                f"Morning task latest_start {morning_task.latest_start} should be ≤ 12:00"
        
        # Check evening constraint
        evening_task = expanded[1]
        if evening_task.earliest_start:
            assert evening_task.earliest_start >= time(18, 0), \
                f"Evening task earliest_start {evening_task.earliest_start} should be ≥ 18:00"
    
    # Edge Case #5: Exact Start Time Conflicts (Same Pet, Different Tasks)
    def test_same_start_time_conflict_detection(self):
        """Test detection of tasks scheduled at the exact same start time.
        
        Scenario: Two tasks for same pet both scheduled at 9:00 AM (impossible simultaneously).
        Expected: detect_same_start_conflicts() returns pair, schedule.is_feasible=False
        """
        scheduler = Scheduler()
        pet = Pet(name="Max", type="Dog")
        
        now = datetime.combine(datetime.now().date(), time(6, 0))
        start_time = now.replace(hour=9, minute=0)
        
        # Task A: 9:00-9:30
        task_a = Task(description="Walk", duration=30, priority=5)
        st_a = ScheduledTask(
            task=task_a,
            pet=pet,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30)
        )
        
        # Task B: 9:00-9:20 (same start time!)
        task_b = Task(description="Feeding", duration=20, priority=4)
        st_b = ScheduledTask(
            task=task_b,
            pet=pet,
            start_time=start_time,  # SAME start time
            end_time=start_time + timedelta(minutes=20)
        )
        
        # Detect same-start conflicts
        same_start_conflicts = scheduler.detect_same_start_conflicts([st_a, st_b])
        assert len(same_start_conflicts) == 1, "Should detect one same-start conflict"
        assert (st_a, st_b) in same_start_conflicts or (st_b, st_a) in same_start_conflicts
        
        # Verify schedule flags this as infeasible
        owner = Owner(name="Test")
        owner.add_pet(pet)
        schedule = Schedule(owner=owner, scheduled_tasks=[st_a, st_b])
        conflicts = scheduler.detect_conflicts([st_a, st_b])
        same_starts = scheduler.detect_same_start_conflicts([st_a, st_b])
        
        # Schedule should mark infeasible if conflicts exist
        schedule.is_feasible = len(conflicts) == 0 and len(same_starts) == 0
        assert schedule.is_feasible is False, "Schedule with same-start conflicts should be infeasible"
        
        # Warning should be in notes
        warning = scheduler.get_conflict_warning(schedule)
        assert "exact-start task" in warning, "Warning should mention exact-start conflicts"


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_workflow(self):
        """Test a complete workflow: create owner, pets, tasks, and generate schedule."""
        # Setup
        owner = Owner(name="Tester", max_daily_time=480)
        
        dog = Pet(name="Max", type="Dog")
        dog.add_task(Task("Morning Walk", 30, 5, earliest_start=time(6, 0), latest_start=time(9, 0)))
        dog.add_task(Task("Feeding", 15, 5, earliest_start=time(7, 0), latest_start=time(9, 0)))
        owner.add_pet(dog)
        
        cat = Pet(name="Whiskers", type="Cat")
        cat.add_task(Task("Feeding", 10, 5, earliest_start=time(7, 0), latest_start=time(10, 0)))
        owner.add_pet(cat)
        
        # Verify all components
        assert len(owner.pets) == 2
        assert len(owner.get_all_tasks()) == 3
        
        # Generate schedule
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        
        # Verify schedule
        assert schedule.is_feasible is True
        assert len(schedule.scheduled_tasks) >= 2  # At least some tasks scheduled
        
        # Verify time sorting
        sorted_schedule = schedule.get_schedule_by_time()
        for i in range(len(sorted_schedule) - 1):
            assert sorted_schedule[i].start_time <= sorted_schedule[i + 1].start_time


# ============================================================================
# BEGINNER-FRIENDLY TESTS: Sorting, Recurrence, and Conflict Detection
# ============================================================================

class TestSortingCorrectness:
    """Test that tasks are sorted correctly by time (chronological order).
    
    CONCEPT: Sorting tasks by time helps the scheduler place activities 
    in the right order. These tests verify the scheduler sorts tasks 
    correctly before scheduling them.
    """
    
    def test_scheduled_tasks_are_in_chronological_order(self):
        """Verify that get_schedule_by_time() returns tasks in time order.
        
        WHAT WE'RE TESTING: 
        - Create 3 tasks scheduled at different times
        - Call get_schedule_by_time()
        - Verify they come back sorted from earliest to latest
        
        WHY THIS MATTERS:
        - A good schedule lists activities in order (6am, then 7am, then 8am)
        - This makes the schedule easy to read and follow
        """
        # SETUP: Create a schedule with tasks at different times
        owner = Owner(name="Alice")
        pet = Pet(name="Buddy", type="Dog")
        owner.add_pet(pet)
        
        now = datetime.combine(datetime.now().date(), time(6, 0))
        
        # Create 3 tasks at different times (OUT OF ORDER)
        early_task = Task(description="Early Walk", duration=30, priority=5)
        middle_task = Task(description="Lunch", duration=20, priority=5)
        late_task = Task(description="Evening Walk", duration=30, priority=5)
        
        # Schedule them intentionally out of order to test sorting
        st_late = ScheduledTask(
            task=late_task,
            pet=pet,
            start_time=now.replace(hour=17, minute=0),  # 5 PM (last)
            end_time=now.replace(hour=17, minute=30)
        )
        st_early = ScheduledTask(
            task=early_task,
            pet=pet,
            start_time=now.replace(hour=7, minute=0),   # 7 AM (first)
            end_time=now.replace(hour=7, minute=30)
        )
        st_middle = ScheduledTask(
            task=middle_task,
            pet=pet,
            start_time=now.replace(hour=12, minute=0),  # 12 PM (middle)
            end_time=now.replace(hour=12, minute=20)
        )
        
        # Add to schedule OUT OF ORDER
        schedule = Schedule(owner=owner, scheduled_tasks=[st_late, st_early, st_middle])
        
        # ACTION: Use get_schedule_by_time() to sort them
        sorted_tasks = schedule.get_schedule_by_time()
        
        # VERIFICATION: Check they're now in chronological order
        assert len(sorted_tasks) == 3, "Should have 3 tasks"
        assert sorted_tasks[0].start_time.hour == 7, "First task should be at 7 AM"
        assert sorted_tasks[1].start_time.hour == 12, "Second task should be at 12 PM"
        assert sorted_tasks[2].start_time.hour == 17, "Third task should be at 5 PM"
        
        # Extra verification: Each task starts after or at the same time as the previous
        for i in range(len(sorted_tasks) - 1):
            assert sorted_tasks[i].start_time <= sorted_tasks[i + 1].start_time, \
                "Tasks should be in chronological order"
    
    def test_sort_by_priority_highest_first(self):
        """Verify that sort_by_priority() puts high-priority tasks first.
        
        WHAT WE'RE TESTING:
        - Create tasks with different priorities (1=low, 5=high)
        - Call sort_by_priority()
        - Verify high-priority tasks come first
        
        WHY THIS MATTERS:
        - Important tasks (like feeding with priority 5) should be scheduled first
        - Less important tasks (like play time with priority 2) come later
        - This ensures urgent pet care is never forgotten
        """
        scheduler = Scheduler()
        
        # Create tasks with mixed priorities
        high_priority = Task(description="Medication", duration=5, priority=5)
        medium_priority = Task(description="Play", duration=30, priority=3)
        low_priority = Task(description="Nap time setup", duration=10, priority=1)
        
        tasks = [low_priority, high_priority, medium_priority]  # Random order
        
        # ACTION: Sort by priority
        sorted_tasks = scheduler.sort_by_priority(tasks)
        
        # VERIFICATION: High priority comes first
        assert sorted_tasks[0].priority == 5, "Highest priority (5) should be first"
        assert sorted_tasks[1].priority == 3, "Medium priority (3) should be second"
        assert sorted_tasks[2].priority == 1, "Lowest priority (1) should be last"


class TestRecurrenceLogic:
    """Test that daily tasks create new instances when completed.
    
    CONCEPT: A "daily" task like "Feed the dog" happens every day.
    When the owner marks today's feeding complete, the system should 
    automatically create tomorrow's feeding task.
    """
    
    def test_completing_daily_task_creates_next_day_task(self):
        """Verify completing a daily task creates a new task for tomorrow.
        
        WHAT WE'RE TESTING:
        - Create a pet with a daily task
        - Mark that task as complete
        - Check that a new identical task was created for the next day
        
        WHY THIS MATTERS:
        - The owner shouldn't have to manually recreate "Feed Buddy" every single day
        - The system should automatically schedule it again for tomorrow
        - This keeps the schedule always up-to-date
        """
        # SETUP: Create a pet with a daily task
        pet = Pet(name="Max", type="Dog")
        daily_task = Task(
            description="Morning Feed",
            duration=15,
            priority=5,
            frequency="daily"  # This is a DAILY task
        )
        pet.add_task(daily_task)
        
        # Verify we start with 1 task
        assert len(pet.tasks) == 1, "Pet should have 1 task initially"
        original_task = pet.tasks[0]
        
        # ACTION: Mark the task as complete
        pet.mark_task_complete(daily_task)
        
        # VERIFICATION: A new task should be created
        assert len(pet.tasks) == 2, "After completing daily task, should have 2 tasks (original + new)"
        
        # The original task should be marked complete
        assert original_task.is_completed is True, "Original task should be marked complete"
        
        # A new task should exist
        new_task = pet.tasks[1]
        assert new_task.is_completed is False, "New task should start incomplete"
        assert new_task.description == original_task.description, "New task should have same description"
        assert new_task.duration == original_task.duration, "New task should have same duration"
        assert new_task.priority == original_task.priority, "New task should have same priority"
    
    def test_weekly_task_creates_next_week_instance(self):
        """Verify completing a weekly task creates a new task for next week.
        
        WHAT WE'RE TESTING:
        - Create a weekly task (e.g., "Vet checkup")
        - Mark it as complete
        - Verify a new instance is created for 7 days later
        
        WHY THIS MATTERS:
        - Some tasks don't happen daily (weekly grooming, vet visits)
        - The system should handle these recurring schedules too
        """
        pet = Pet(name="Fluffy", type="Cat")
        weekly_task = Task(
            description="Weekly Grooming",
            duration=60,
            priority=4,
            frequency="weekly"  # This is a WEEKLY task
        )
        pet.add_task(weekly_task)
        
        # Mark complete
        pet.mark_task_complete(weekly_task)
        
        # Should have created a new instance
        assert len(pet.tasks) == 2, "Should have original + new instance"
        
        # The new task should be marked incomplete
        new_task = pet.tasks[1]
        assert new_task.is_completed is False, "New weekly task should be incomplete"
        assert new_task.frequency == "weekly", "New task should keep weekly frequency"


class TestConflictDetection:
    """Test that the scheduler correctly identifies scheduling conflicts.
    
    CONCEPT: A conflict happens when two tasks would need to happen 
    at the same time (impossible for one pet). The scheduler must catch 
    these and warn the owner.
    """
    
    def test_overlapping_tasks_are_detected_as_conflicts(self):
        """Verify that overlapping time slots are detected as conflicts.
        
        WHAT WE'RE TESTING:
        - Schedule Task A from 9:00-9:30
        - Schedule Task B from 9:15-9:45 (overlaps with A)
        - Call detect_conflicts()
        - Verify the overlap is detected
        
        WHY THIS MATTERS:
        - One pet can't do two things at once
        - If the scheduler accidentally books "Walk" and "Feeding" at the same time,
          it must flag this as a problem
        """
        scheduler = Scheduler()
        pet = Pet(name="Rex", type="Dog")
        
        now = datetime.combine(datetime.now().date(), time(6, 0))
        
        # Task A: 9:00-9:30
        task_a = Task(description="Walk", duration=30, priority=5)
        scheduled_a = ScheduledTask(
            task=task_a,
            pet=pet,
            start_time=now.replace(hour=9, minute=0),
            end_time=now.replace(hour=9, minute=30)
        )
        
        # Task B: 9:15-9:45 (OVERLAPS with A!)
        task_b = Task(description="Feeding", duration=30, priority=5)
        scheduled_b = ScheduledTask(
            task=task_b,
            pet=pet,
            start_time=now.replace(hour=9, minute=15),  # Starts while A is still running
            end_time=now.replace(hour=9, minute=45)
        )
        
        # ACTION: Detect conflicts
        conflicts = scheduler.detect_conflicts([scheduled_a, scheduled_b])
        
        # VERIFICATION: Should find exactly 1 conflict (the overlapping pair)
        assert len(conflicts) == 1, "Should detect exactly 1 conflict"
        conflict_pair = conflicts[0]
        assert (conflict_pair[0] == scheduled_a and conflict_pair[1] == scheduled_b) or \
               (conflict_pair[0] == scheduled_b and conflict_pair[1] == scheduled_a), \
               "Conflict should be between our two overlapping tasks"
    
    def test_non_overlapping_tasks_have_no_conflict(self):
        """Verify that non-overlapping tasks are NOT flagged as conflicts.
        
        WHAT WE'RE TESTING:
        - Schedule Task A from 9:00-9:30
        - Schedule Task B from 9:30-10:00 (no overlap, B starts when A ends)
        - Call detect_conflicts()
        - Verify NO conflict is detected
        
        WHY THIS MATTERS:
        - "Back-to-back" tasks are OK (feed at 9:00, walk at 9:30)
        - The system should only flag TRUE conflicts
        """
        scheduler = Scheduler()
        pet = Pet(name="Bella", type="Dog")
        
        now = datetime.combine(datetime.now().date(), time(6, 0))
        
        # Task A: 9:00-9:30
        task_a = Task(description="Feeding", duration=30, priority=5)
        scheduled_a = ScheduledTask(
            task=task_a,
            pet=pet,
            start_time=now.replace(hour=9, minute=0),
            end_time=now.replace(hour=9, minute=30)
        )
        
        # Task B: 9:30-10:00 (No overlap! B starts when A ends)
        task_b = Task(description="Walk", duration=30, priority=5)
        scheduled_b = ScheduledTask(
            task=task_b,
            pet=pet,
            start_time=now.replace(hour=9, minute=30),
            end_time=now.replace(hour=10, minute=0)
        )
        
        # ACTION: Detect conflicts
        conflicts = scheduler.detect_conflicts([scheduled_a, scheduled_b])
        
        # VERIFICATION: Should find NO conflicts
        assert len(conflicts) == 0, "Back-to-back tasks should NOT conflict"
    
    def test_full_schedule_feasibility_checks_conflicts(self):
        """Verify that is_feasible() correctly identifies infeasible schedules.
        
        WHAT WE'RE TESTING:
        - Create a schedule with 2 conflicting tasks
        - Call is_feasible()
        - Verify it returns False (schedule is not doable)
        
        WHY THIS MATTERS:
        - The scheduler should tell the owner "This schedule won't work!"
        - An infeasible schedule means tasks need to be rescheduled or removed
        """
        scheduler = Scheduler()
        owner = Owner(name="Owner", max_daily_time=480)
        pet = Pet(name="Dog", type="Dog")
        owner.add_pet(pet)
        
        now = datetime.combine(datetime.now().date(), time(6, 0))
        
        # Create two CONFLICTING scheduled tasks
        task1 = Task(description="Task1", duration=30, priority=5)
        task2 = Task(description="Task2", duration=30, priority=5)
        
        st1 = ScheduledTask(
            task=task1,
            pet=pet,
            start_time=now.replace(hour=9, minute=0),
            end_time=now.replace(hour=9, minute=30)
        )
        st2 = ScheduledTask(
            task=task2,
            pet=pet,
            start_time=now.replace(hour=9, minute=15),  # CONFLICTS with st1
            end_time=now.replace(hour=9, minute=45)
        )
        
        # ACTION: Check if this schedule is feasible
        is_feasible = scheduler.is_feasible(owner, [st1, st2])
        
        # VERIFICATION: Should be False (not feasible due to conflict)
        assert is_feasible is False, "Schedule with conflicts should not be feasible"


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidation:
    """Test that invalid inputs are properly rejected with clear error messages."""

    def test_empty_task_description_rejected(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            Task(description="", duration=10, priority=3)

    def test_whitespace_only_description_rejected(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            Task(description="   ", duration=10, priority=3)

    def test_zero_duration_rejected(self):
        with pytest.raises(ValueError, match="positive integer"):
            Task(description="Walk", duration=0, priority=3)

    def test_negative_duration_rejected(self):
        with pytest.raises(ValueError, match="positive integer"):
            Task(description="Walk", duration=-5, priority=3)

    def test_excessive_duration_rejected(self):
        with pytest.raises(ValueError, match="cannot exceed 1440"):
            Task(description="Walk", duration=1500, priority=3)

    def test_priority_below_range_rejected(self):
        with pytest.raises(ValueError, match="between 1 and 5"):
            Task(description="Walk", duration=10, priority=0)

    def test_priority_above_range_rejected(self):
        with pytest.raises(ValueError, match="between 1 and 5"):
            Task(description="Walk", duration=10, priority=6)

    def test_invalid_frequency_rejected(self):
        with pytest.raises(ValueError, match="Invalid frequency"):
            Task(description="Walk", duration=10, priority=3, frequency="monthly")

    def test_earliest_after_latest_rejected(self):
        with pytest.raises(ValueError, match="cannot be after"):
            Task(description="Walk", duration=10, priority=3,
                 earliest_start=time(18, 0), latest_start=time(8, 0))

    def test_empty_pet_name_rejected(self):
        with pytest.raises(ValueError, match="Pet name cannot be empty"):
            Pet(name="", type="Dog")

    def test_invalid_pet_type_rejected(self):
        with pytest.raises(ValueError, match="Invalid pet type"):
            Pet(name="Rex", type="Dinosaur")

    def test_empty_owner_name_rejected(self):
        with pytest.raises(ValueError, match="Owner name cannot be empty"):
            Owner(name="")

    def test_zero_max_daily_time_rejected(self):
        with pytest.raises(ValueError, match="positive integer"):
            Owner(name="Alice", max_daily_time=0)

    def test_excessive_max_daily_time_rejected(self):
        with pytest.raises(ValueError, match="cannot exceed 1440"):
            Owner(name="Alice", max_daily_time=2000)

    def test_duplicate_pet_name_rejected(self):
        owner = Owner(name="Alice")
        owner.add_pet(Pet(name="Max", type="Dog"))
        with pytest.raises(ValueError, match="already exists"):
            owner.add_pet(Pet(name="Max", type="Cat"))

    def test_description_whitespace_trimmed(self):
        task = Task(description="  Morning Walk  ", duration=30, priority=5)
        assert task.description == "Morning Walk"

    def test_valid_inputs_accepted(self):
        """Ensure valid inputs still work after adding validation."""
        task = Task(description="Walk", duration=30, priority=5,
                    earliest_start=time(6, 0), latest_start=time(10, 0),
                    frequency="daily")
        assert task.description == "Walk"
        pet = Pet(name="Max", type="Dog")
        assert pet.name == "Max"
        owner = Owner(name="Alice", max_daily_time=480)
        assert owner.name == "Alice"


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestStressAndPerformance:
    """Test system behavior with large numbers of tasks and pets."""

    def test_schedule_50_tasks(self):
        """Generate a schedule with 50 tasks across multiple pets."""
        owner = Owner(name="StressOwner", max_daily_time=1440)
        for i in range(5):
            pet = Pet(name=f"Pet{i}", type="Dog")
            for j in range(10):
                pet.add_task(Task(
                    description=f"Task-{i}-{j}",
                    duration=15,
                    priority=(j % 5) + 1,
                    earliest_start=time(6, 0),
                    latest_start=time(22, 0),
                ))
            owner.add_pet(pet)

        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        assert len(schedule.scheduled_tasks) > 0
        # No overlapping conflicts in the generated schedule
        conflicts = scheduler.detect_conflicts(schedule.scheduled_tasks)
        assert len(conflicts) == 0

    def test_schedule_100_tasks_performance(self):
        """Ensure scheduling 100 tasks completes without errors."""
        owner = Owner(name="PerfOwner", max_daily_time=1440)
        pet = Pet(name="Buddy", type="Dog")
        for i in range(100):
            pet.add_task(Task(
                description=f"Task{i}",
                duration=10,
                priority=(i % 5) + 1,
                earliest_start=time(6, 0),
                latest_start=time(22, 0),
            ))
        owner.add_pet(pet)

        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        # Should schedule as many as fit (960 min window / 10 min each = 96 max)
        assert len(schedule.scheduled_tasks) <= 96
        assert schedule.total_duration <= 1440

    def test_conflict_detection_many_tasks(self):
        """Detect conflicts efficiently with many scheduled tasks."""
        scheduler = Scheduler()
        pet = Pet(name="Rex", type="Dog")
        now = datetime.combine(datetime.now().date(), time(6, 0))

        tasks = []
        for i in range(50):
            t = Task(description=f"T{i}", duration=30, priority=3)
            st = ScheduledTask(
                task=t, pet=pet,
                start_time=now + timedelta(minutes=i * 30),
                end_time=now + timedelta(minutes=i * 30 + 30),
            )
            tasks.append(st)

        conflicts = scheduler.detect_conflicts(tasks)
        assert len(conflicts) == 0, "Non-overlapping tasks should have no conflicts"

    def test_many_pets_with_tasks(self):
        """Test owner with 20 pets, each having tasks."""
        owner = Owner(name="BigFamily", max_daily_time=1440)
        for i in range(20):
            pet = Pet(name=f"Pet{i}", type="Cat")
            pet.add_task(Task(
                description=f"Feed-{i}", duration=10, priority=5,
                earliest_start=time(6, 0), latest_start=time(22, 0),
            ))
            owner.add_pet(pet)

        assert len(owner.get_all_tasks()) == 20
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        assert len(schedule.scheduled_tasks) == 20


# ============================================================================
# ADVANCED ERROR HANDLING AND RECOVERY TESTS
# ============================================================================

class TestErrorHandlingAndRecovery:
    """Test graceful handling of edge cases and error recovery."""

    def test_schedule_with_no_pets(self):
        owner = Owner(name="NoPets")
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        assert schedule.is_feasible is True
        assert len(schedule.scheduled_tasks) == 0
        assert "No tasks" in schedule.notes

    def test_schedule_with_all_completed_tasks(self):
        owner = Owner(name="AllDone")
        pet = Pet(name="Max", type="Dog")
        t = Task(description="Walk", duration=30, priority=5,
                 earliest_start=time(6, 0), latest_start=time(10, 0),
                 is_completed=True)
        pet.add_task(t)
        owner.add_pet(pet)
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        # Completed tasks are still scheduled (status doesn't block scheduling)
        assert len(schedule.scheduled_tasks) >= 0

    def test_mark_nonexistent_task_raises_error(self):
        pet = Pet(name="Max", type="Dog")
        task = Task(description="Ghost Task", duration=10, priority=1)
        with pytest.raises(ValueError, match="not found"):
            pet.mark_task_complete(task)

    def test_mark_task_on_wrong_pet_raises_error(self):
        owner = Owner(name="Alice")
        pet1 = Pet(name="Max", type="Dog")
        pet2 = Pet(name="Luna", type="Cat")
        task = Task(description="Walk", duration=30, priority=5)
        pet1.add_task(task)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        with pytest.raises(ValueError, match="not found"):
            pet2.mark_task_complete(task)

    def test_owner_mark_task_unknown_pet_raises_error(self):
        owner = Owner(name="Bob")
        pet = Pet(name="Ghost", type="Dog")
        task = Task(description="Walk", duration=10, priority=1)
        pet.add_task(task)
        with pytest.raises(ValueError, match="not found"):
            owner.mark_task_complete(task, pet)

    def test_resolve_conflicts_invalid_strategy_raises(self):
        scheduler = Scheduler()
        with pytest.raises(ValueError, match="Unknown conflict resolution strategy"):
            scheduler.resolve_conflicts([], strategy="random")


# ============================================================================
# CONFLICT RESOLUTION STRATEGY TESTS
# ============================================================================

class TestConflictResolutionStrategies:
    """Test the different conflict resolution strategies."""

    def _make_conflicting_tasks(self):
        pet = Pet(name="Max", type="Dog")
        now = datetime.combine(datetime.now().date(), time(9, 0))
        t1 = Task(description="High Priority Long", duration=60, priority=5)
        t2 = Task(description="Low Priority Short", duration=20, priority=2)
        st1 = ScheduledTask(task=t1, pet=pet, start_time=now,
                            end_time=now + timedelta(minutes=60))
        st2 = ScheduledTask(task=t2, pet=pet, start_time=now + timedelta(minutes=30),
                            end_time=now + timedelta(minutes=50))
        return st1, st2

    def test_priority_strategy_keeps_higher_priority(self):
        st1, st2 = self._make_conflicting_tasks()
        scheduler = Scheduler()
        resolved = scheduler.resolve_conflicts([st1, st2], strategy="priority")
        assert st1 in resolved, "Higher priority task should be kept"
        assert st2 not in resolved, "Lower priority task should be removed"

    def test_shortest_strategy_keeps_shorter_task(self):
        st1, st2 = self._make_conflicting_tasks()
        scheduler = Scheduler()
        resolved = scheduler.resolve_conflicts([st1, st2], strategy="shortest")
        assert st2 in resolved, "Shorter task should be kept"
        assert st1 not in resolved, "Longer task should be removed"

    def test_reschedule_strategy_tries_to_move_task(self):
        pet = Pet(name="Max", type="Dog")
        now = datetime.combine(datetime.now().date(), time(9, 0))
        t1 = Task(description="Walk", duration=30, priority=5,
                  earliest_start=time(6, 0), latest_start=time(22, 0))
        t2 = Task(description="Feed", duration=15, priority=3,
                  earliest_start=time(6, 0), latest_start=time(22, 0))
        st1 = ScheduledTask(task=t1, pet=pet, start_time=now,
                            end_time=now + timedelta(minutes=30))
        st2 = ScheduledTask(task=t2, pet=pet, start_time=now + timedelta(minutes=15),
                            end_time=now + timedelta(minutes=30))
        scheduler = Scheduler()
        resolved = scheduler.resolve_conflicts([st1, st2], strategy="reschedule")
        # Both tasks should still be present (rescheduled, not dropped)
        assert len(resolved) == 2, "Reschedule strategy should keep both tasks"
        conflicts = scheduler.detect_conflicts(resolved)
        assert len(conflicts) == 0, "Resolved schedule should have no conflicts"

    def test_no_conflicts_returns_same_list(self):
        pet = Pet(name="Max", type="Dog")
        now = datetime.combine(datetime.now().date(), time(9, 0))
        t1 = Task(description="Walk", duration=30, priority=5)
        st1 = ScheduledTask(task=t1, pet=pet, start_time=now,
                            end_time=now + timedelta(minutes=30))
        scheduler = Scheduler()
        for strategy in ("priority", "shortest", "reschedule"):
            resolved = scheduler.resolve_conflicts([st1], strategy=strategy)
            assert resolved == [st1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
