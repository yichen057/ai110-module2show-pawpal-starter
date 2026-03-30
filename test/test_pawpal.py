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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
