from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
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
        
        # Sort tasks by priority
        sorted_tasks = self.sort_by_priority(all_tasks)
        
        # Attempt to schedule each task
        scheduled_tasks = []
        current_time = datetime.combine(datetime.now().date(), time(6, 0))  # Start at 6 AM
        
        for task in sorted_tasks:
            pet = pet_task_map[task]
            scheduled_task = self._find_available_slot(task, pet, scheduled_tasks, current_time, owner.max_daily_time)
            
            if scheduled_task:
                scheduled_tasks.append(scheduled_task)
                schedule.add_scheduled_task(scheduled_task)
            else:
                schedule.notes += f"Could not schedule task '{task.description}' for pet '{pet.name}'. "
        
        # Check feasibility
        conflicts = self.detect_conflicts(scheduled_tasks)
        schedule.is_feasible = len(conflicts) == 0 and schedule.total_duration <= owner.max_daily_time
        
        if conflicts:
            schedule.notes += f"Warning: {len(conflicts)} time conflict(s) detected. "
        
        if schedule.total_duration > owner.max_daily_time:
            schedule.notes += f"Warning: Total duration ({schedule.total_duration} min) exceeds max daily time ({owner.max_daily_time} min). "
        
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
        # Define default time window if not specified
        earliest = task.earliest_start if task.earliest_start else time(6, 0)
        latest = task.latest_start if task.latest_start else time(22, 0)
        
        current_time = start_time.replace(hour=earliest.hour, minute=earliest.minute)
        latest_time = start_time.replace(hour=latest.hour, minute=latest.minute)
        
        # Try to find an available slot
        while current_time + timedelta(minutes=task.duration) <= latest_time:
            # Check if this slot conflicts with any scheduled task
            proposed_end = current_time + timedelta(minutes=task.duration)
            has_conflict = False
            
            for st in scheduled_tasks:
                if not (proposed_end <= st.start_time or current_time >= st.end_time):
                    has_conflict = True
                    break
            
            if not has_conflict:
                # Check if total time doesn't exceed max daily time
                total_with_this_task = sum(st.task.duration for st in scheduled_tasks) + task.duration
                if total_with_this_task <= max_daily_minutes:
                    reason = f"Scheduled within time window ({earliest.strftime('%H:%M')}-{latest.strftime('%H:%M')}) based on priority {task.priority}."
                    return ScheduledTask(
                        task=task,
                        pet=pet,
                        start_time=current_time,
                        end_time=proposed_end,
                        reason=reason
                    )
            
            # Move to next 15-minute slot
            current_time += timedelta(minutes=15)
        
        return None

    def optimize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (high→low) with secondary sort by duration (short→long)."""
        return self.sort_by_priority(tasks)

    def detect_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[Tuple[ScheduledTask, ScheduledTask]]:
        """Detect and return all pairs of tasks with overlapping time slots."""
        conflicts = []
        for i in range(len(scheduled_tasks)):
            for j in range(i + 1, len(scheduled_tasks)):
                st1 = scheduled_tasks[i]
                st2 = scheduled_tasks[j]
                # Check if time ranges overlap
                if not (st1.end_time <= st2.start_time or st2.end_time <= st1.start_time):
                    conflicts.append((st1, st2))
        return conflicts

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (5→1) then by duration (shortest first)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration))

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
