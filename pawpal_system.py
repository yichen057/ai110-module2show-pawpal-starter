from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from itertools import combinations
from typing import List, Optional, Dict, Tuple


@dataclass
class Task:
    """Represents a pet care task."""
    description: str
    duration: int  # in minutes
    priority: int  # 1-5 scale
    scheduled_time: Optional[datetime] = None
    earliest_start: Optional[time] = None  # Earliest time task can start (e.g., 8:00 AM)
    latest_start: Optional[time] = None    # Latest time task can start (e.g., 6:00 PM)
    frequency: str = "daily"  # e.g., "daily", "weekly", "once", "twice_daily"
    is_completed: bool = False  # Completion status for tracking task completion

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.is_completed = False

    def __hash__(self):
        """Return hash of task based on description, duration, and priority."""
        return hash((self.description, self.duration, self.priority))


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    type: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task as complete and handle recurrence for daily/weekly tasks."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.description}' not found for pet '{self.name}'.")
        
        task.mark_complete()  # Mark the original task complete
        
        # Handle recurrence
        if task.frequency in ["daily", "weekly"]:
            self._create_next_recurring_instance(task)

    def _create_next_recurring_instance(self, original_task: Task) -> None:
        """Create the next instance of a recurring task."""
        # Determine the base date
        if original_task.scheduled_time:
            base_date = original_task.scheduled_time.date()
            base_time = original_task.scheduled_time.time()
        else:
            # Use today's date and earliest_start time as base
            base_date = datetime.now().date()
            base_time = original_task.earliest_start if original_task.earliest_start else time(9, 0)
        
        # Calculate the next occurrence
        delta = timedelta(days=1) if original_task.frequency == "daily" else timedelta(days=7)
        next_date = base_date + delta
        
        # Create new task instance
        new_task = Task(
            description=original_task.description,  # Keep same description
            duration=original_task.duration,
            priority=original_task.priority,
            scheduled_time=datetime.combine(next_date, base_time),  # Always set scheduled_time
            earliest_start=original_task.earliest_start,  # Keep unchanged
            latest_start=original_task.latest_start,      # Keep unchanged
            frequency=original_task.frequency,  # Keep frequency for future recurrence
            is_completed=False  # Reset to incomplete
        )
        
        # Avoid duplicates: Check if a task with same desc and date exists
        existing_descriptions_and_dates = [
            (t.description, t.scheduled_time.date() if t.scheduled_time else None) for t in self.tasks
        ]
        new_desc_and_date = (new_task.description, new_task.scheduled_time.date())
        
        if new_desc_and_date not in existing_descriptions_and_dates:
            self.tasks.append(new_task)
        # Else: Skip silently to avoid duplicates


@dataclass
class Owner:
    """Represents a pet owner."""
    name: str
    pets: List[Pet] = field(default_factory=list)
    max_daily_time: int = 480  # in minutes, default 8 hours
    preferences: Dict[str, bool] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from all owned pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def filter_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Filter tasks by specific pet name."""
        return [task for pet in self.pets if pet.name == pet_name for task in pet.tasks]

    def filter_tasks_by_status(self, completed: bool) -> List[Task]:
        """Filter tasks by completion status."""
        return [task for task in self.get_all_tasks() if task.is_completed == completed]

    def filter_tasks(self, pet_names: Optional[List[str]] = None, completed: Optional[bool] = None, 
                     priority_min: Optional[int] = None, priority_max: Optional[int] = None, 
                     duration_max: Optional[int] = None) -> List[Task]:
        """Filter tasks based on multiple optional criteria.
        
        Args:
            pet_names: List of pet names to filter by (case-sensitive exact match)
            completed: Filter by completion status (True for completed, False for incomplete)
            priority_min: Minimum priority level (1-5)
            priority_max: Maximum priority level (1-5)  
            duration_max: Maximum duration in minutes
            
        Returns:
            List of tasks matching all specified criteria
        """
        tasks = self.get_all_tasks()
        filtered = tasks
        
        if pet_names:
            # Get tasks for specified pets
            pet_task_sets = []
            for pet_name in pet_names:
                pet_tasks = set(self.filter_tasks_by_pet(pet_name))
                if pet_tasks:  # Only add if pet exists
                    pet_task_sets.append(pet_tasks)
            if pet_task_sets:
                filtered = list(set.intersection(*pet_task_sets))
            else:
                return []  # No matching pets found
        
        if completed is not None:
            filtered = [t for t in filtered if t.is_completed == completed]
        
        if priority_min is not None:
            filtered = [t for t in filtered if t.priority >= priority_min]
        
        if priority_max is not None:
            filtered = [t for t in filtered if t.priority <= priority_max]
        
        if duration_max is not None:
            filtered = [t for t in filtered if t.duration <= duration_max]
        
        return filtered

    def mark_task_complete(self, task: Task, pet: Pet) -> None:
        """Mark a task complete for a specific pet, handling recurrence."""
        if pet not in self.pets:
            raise ValueError(f"Pet '{pet.name}' not found for owner '{self.name}'.")
        pet.mark_task_complete(task)


@dataclass
class ScheduledTask:
    """Represents a task scheduled at a specific time for a specific pet."""
    task: Task
    pet: Pet
    start_time: datetime
    end_time: datetime
    reason: str = ""  # Explanation for why this task was scheduled at this time


@dataclass
class Schedule:
    """Represents a generated daily schedule."""
    owner: Owner
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    total_duration: int = 0  # Total minutes scheduled
    is_feasible: bool = True  # Whether the schedule fits within constraints
    notes: str = ""  # Any notes or warnings about the schedule

    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task to the schedule."""
        self.scheduled_tasks.append(scheduled_task)
        self.total_duration += scheduled_task.task.duration

    def get_schedule_by_time(self) -> List[ScheduledTask]:
        """Return scheduled tasks sorted chronologically by start time."""
        return sorted(self.scheduled_tasks, key=lambda st: st.start_time)


class Scheduler:
    """Manages pet care schedule generation."""

    def generate_schedule(self, owner: Owner) -> Schedule:
        """Generate an optimized daily schedule for the owner's pets based on priorities and time windows."""
        schedule = Schedule(owner=owner)
        
        # Get all tasks and map them to their pets
        pet_task_map = {task: pet for pet in owner.pets for task in pet.tasks}
        all_tasks = owner.get_all_tasks()
        
        if not all_tasks:
            schedule.notes = "No tasks to schedule."
            return schedule
        
        # Expand recurring tasks
        expanded_tasks = self.expand_recurring_tasks(all_tasks)
        
        # Update pet_task_map for expanded tasks
        expanded_pet_task_map = {}
        for task in expanded_tasks:
            # Find original pet for this task (by description prefix)
            for orig_task, pet in pet_task_map.items():
                if task.description.startswith(orig_task.description):
                    expanded_pet_task_map[task] = pet
                    break
        
        # Sort tasks by priority
        sorted_tasks = self.sort_by_priority(expanded_tasks)
        
        # Attempt to schedule each task
        scheduled_tasks = []
        current_time = datetime.combine(datetime.now().date(), time(6, 0))  # Start at 6 AM
        
        for task in sorted_tasks:
            pet = expanded_pet_task_map[task]
            scheduled_task = self._find_available_slot(task, pet, scheduled_tasks, current_time, owner.max_daily_time)
            
            if scheduled_task:
                scheduled_tasks.append(scheduled_task)
                schedule.add_scheduled_task(scheduled_task)
            else:
                schedule.notes += f"Could not schedule task '{task.description}' for pet '{pet.name}'. "
        
        # Check feasibility
        conflicts = self.detect_conflicts(scheduled_tasks)
        same_start_conflicts = self.detect_same_start_conflicts(scheduled_tasks)

        schedule.is_feasible = len(conflicts) == 0 and len(same_start_conflicts) == 0 and schedule.total_duration <= owner.max_daily_time

        if conflicts:
            schedule.notes += f"Warning: {len(conflicts)} time conflict(s) detected. "
        if same_start_conflicts:
            schedule.notes += f"Warning: {len(same_start_conflicts)} exact-start task(s) detected. "

        if schedule.total_duration > owner.max_daily_time:
            schedule.notes += f"Warning: Total duration ({schedule.total_duration} min) exceeds max daily time ({owner.max_daily_time} min). "

        # Append lightweight summary
        warning_summary = self.get_conflict_warning(schedule)
        if warning_summary:
            schedule.notes += "Scheduler report: " + warning_summary

        return schedule

    def _find_available_slot(
        self, 
        task: Task, 
        pet: Pet, 
        scheduled_tasks: List[ScheduledTask], 
        start_time: datetime,
        max_daily_minutes: int
    ) -> Optional[ScheduledTask]:
        """Find an available time slot for a task that respects time windows and avoids conflicts."""
        earliest = task.earliest_start or time(6, 0)
        latest = task.latest_start or time(22, 0)
        current_time = start_time.replace(hour=earliest.hour, minute=earliest.minute)
        latest_time = start_time.replace(hour=latest.hour, minute=latest.minute)

        def _has_conflict(st_time: datetime, en_time: datetime) -> bool:
            return any(
                not (en_time <= st.start_time or st_time >= st.end_time)
                for st in scheduled_tasks
            )

        while current_time + timedelta(minutes=task.duration) <= latest_time:
            proposed_end = current_time + timedelta(minutes=task.duration)
            if not _has_conflict(current_time, proposed_end):
                total_with_this_task = sum(st.task.duration for st in scheduled_tasks) + task.duration
                if total_with_this_task <= max_daily_minutes:
                    reason = f"Scheduled within time window ({earliest.strftime('%H:%M')}-{latest.strftime('%H:%M')}) based on priority {task.priority}."
                    return ScheduledTask(task=task, pet=pet, start_time=current_time, end_time=proposed_end, reason=reason)
            current_time += timedelta(minutes=15)

        return None

    def optimize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (high→low) with secondary sort by duration (short→long)."""
        return self.sort_by_priority(tasks)

    def detect_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[Tuple[ScheduledTask, ScheduledTask]]:
        """Detect and return all pairs of tasks with overlapping time slots."""
        overlaps = [
            (st1, st2)
            for st1, st2 in combinations(scheduled_tasks, 2)
            if not (st1.end_time <= st2.start_time or st2.end_time <= st1.start_time)
        ]
        return overlaps

    def detect_same_start_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[Tuple[ScheduledTask, ScheduledTask]]:
        """Return pairs of tasks that share the exact same start time."""
        return [
            (st1, st2)
            for st1, st2 in combinations(scheduled_tasks, 2)
            if st1.start_time == st2.start_time
        ]

    def get_conflict_warning(self, schedule: Schedule) -> str:
        """Return a lightweight warning message when there are conflicts."""
        conflicts = self.detect_conflicts(schedule.scheduled_tasks)
        same_starts = self.detect_same_start_conflicts(schedule.scheduled_tasks)

        warnings = []
        if conflicts:
            warnings.append(f"{len(conflicts)} overlapping task pair(s) detected.")
        if same_starts:
            warnings.append(f"{len(same_starts)} exact-start task pair(s) detected.")

        return " ".join(warnings) if warnings else ""
    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (5→1) then by duration (shortest first)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by earliest start time, then by priority.

        For sorting time objects: uses (hour, minute) tuple comparison
        For sorting "HH:MM" strings: use key=lambda t: tuple(map(int, t.time_str.split(':')))
        """
        return sorted(tasks, key=lambda t: (t.earliest_start or time(23, 59), -t.priority))

    def sort_by_time_string(self, tasks: List[Task]) -> List[Task]:
        """Example: Sort tasks by time if stored as "HH:MM" strings.

        Uses lambda to parse "HH:MM" strings into comparable tuples.
        """
        # Assuming tasks had a time_str attribute like "08:30"
        # return sorted(tasks, key=lambda t: tuple(map(int, t.time_str.split(':'))))
        # For now, convert time objects to strings for demonstration
        return sorted(tasks, key=lambda t: tuple(map(int, (t.earliest_start or time(23, 59)).strftime("%H:%M").split(':'))))

    def expand_recurring_tasks(self, tasks: List[Task]) -> List[Task]:
        """Expand recurring tasks into multiple instances based on frequency."""
        expanded_tasks = []
        for task in tasks:
            if task.frequency == "daily":
                expanded_tasks.append(task)
            elif task.frequency == "twice_daily":
                # Create morning and evening instances
                morning_task = Task(
                    description=f"{task.description} (Morning)",
                    duration=task.duration,
                    priority=task.priority,
                    earliest_start=task.earliest_start,
                    latest_start=time(12, 0) if task.latest_start and task.latest_start > time(12, 0) else task.latest_start,
                    frequency="once",
                    is_completed=task.is_completed
                )
                evening_task = Task(
                    description=f"{task.description} (Evening)",
                    duration=task.duration,
                    priority=task.priority,
                    earliest_start=time(18, 0) if not task.earliest_start or task.earliest_start < time(18, 0) else task.earliest_start,
                    latest_start=task.latest_start,
                    frequency="once",
                    is_completed=task.is_completed
                )
                expanded_tasks.extend([morning_task, evening_task])
            elif task.frequency == "weekly":
                # For weekly, just add once for now (could be enhanced)
                expanded_tasks.append(task)
            else:  # "once" or unknown
                expanded_tasks.append(task)
        return expanded_tasks

    def is_feasible(self, owner: Owner, scheduled_tasks: List[ScheduledTask]) -> bool:
        """Check if schedule is feasible (no conflicts, within time limit, respects constraints)."""
        # Check for conflicts
        conflicts = self.detect_conflicts(scheduled_tasks)
        if conflicts:
            return False
        
        # Check total duration doesn't exceed max daily time
        total_duration = sum(st.task.duration for st in scheduled_tasks)
        if total_duration > owner.max_daily_time:
            return False
        
        return True

    def resolve_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[ScheduledTask]:
        """Remove lower-priority tasks from conflicting pairs to create a conflict-free schedule."""
        conflicts = self.detect_conflicts(scheduled_tasks)
        
        if not conflicts:
            return scheduled_tasks
        
        # Sort tasks by priority to identify which lower-priority task to reschedule
        resolved = scheduled_tasks[:]
        
        for st1, st2 in conflicts:
            # Reschedule the lower-priority task
            if st1.task.priority < st2.task.priority:
                # st1 is lower priority, so remove and try to reschedule later
                resolved.remove(st1)
            else:
                # st2 is lower priority
                resolved.remove(st2)
        
        return resolved
