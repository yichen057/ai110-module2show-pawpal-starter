# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Initial design description:
I designed a modular, object-oriented system to handle pet care management. The architecture is split into four primary classes to ensure a clear separation of concerns:

Pet Class: Responsible for storing individual pet profiles, including their specific needs and a collection of their assigned tasks.

Task Class: A data-holding class that defines a single activity, including its priority, duration, and time_slot.

Owner Class: Acts as the primary data controller, managing a list of Pet objects and coordinating user-level settings.

Scheduler Class: The "brain" of the system. It contains the logic for sorting tasks, detecting time conflicts, and generating the optimized daily itinerary.

**b. Core User Actions**

The system enables three primary user actions:

1. **Add/Edit Pet Information**: Users can register a new pet into the system or modify existing pet details (name, type, age, preferences, special needs). This action forms the foundation of the system, as all scheduling and task management revolves around the pet's profile and individual characteristics.

2. **Add/Edit Tasks**: Users can create and manage daily tasks or activities for their pet (e.g., feeding, walks, grooming, playtime, medication). Each task can have associated properties like duration, priority level, time windows, and any special requirements. This gives users fine-grained control over what needs to be scheduled.

3. **Generate Daily Plan with Reasoning**: The system produces an optimized daily schedule based on pet constraints (available time, pet energy levels, preferences) and task requirements. Importantly, the system provides detailed reasoning for its scheduling decisions—explaining *why* tasks are placed at certain times, how constraints were balanced, and what tradeoffs were made. This transparency helps users understand and trust the scheduling logic.

**c. Design changes**

- Did your design change during implementation? Yes
- If yes, describe at least one change and why you made it.
Based on AI feedback, I realized my initial Scheduler was too simplistic and lacked a way to store the final output. I added a ScheduledTask dataclass and a structured Schedule class. This change is crucial because it allows the system to link a specific Pet to a Task at a specific datetime, making it much easier to detect time conflicts and display a clear itinerary in the UI later. I also added time window constraints to the Task class to ensure activities like "Feeding" happen at appropriate times.

Additionally, I added a `get_all_tasks()` method to the Owner class to follow the **encapsulation principle**. This method allows the Scheduler to retrieve all tasks from all pets without directly traversing the data structure. This improves maintainability—if the internal data structure changes, only the Owner class needs to be updated, not the Scheduler.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers the following constraints in order of importance:
1. **Input validation**: All data is validated at creation time (Task, Pet, Owner) — invalid durations, out-of-range priorities, empty names, unsupported frequencies, and reversed time windows are rejected immediately with clear error messages.
2. **Time window constraints**: Each task has an earliest/latest start time; the scheduler only places tasks within their allowed window.
3. **Priority**: Higher-priority tasks (5) are scheduled first, ensuring critical care (feeding, medication) is never missed.
4. **Capacity**: Total scheduled minutes cannot exceed the owner’s `max_daily_time`.
5. **Conflict avoidance**: The scheduler checks for overlapping time slots and same-start conflicts before finalizing.

Priority and time windows were chosen as the most important constraints because missing a high-priority task like medication could harm the pet, and time windows reflect real-world biological needs (e.g., feeding at appropriate hours).

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Tradeoff 1: The scheduler supports both true overlap detection (`detect_conflicts`) and exact-start collision detection (`detect_same_start_conflicts`), but it chooses to present a lightweight warning for exact start conflicts in the normal flow. This means that the system will explicitly warn about task pairs that begin at the same time, while the full interval-overlap resolution path is simplified for readability and speed. The tradeoff is that it is easier to implement and safer for small-scope pet scheduling, but it does not provide advanced backtracking and reallocation for every partial overlap interval that a full constraint solver would.

Tradeoff 2: The conflict resolution system offers three strategies (`"priority"`, `"shortest"`, `"reschedule"`) rather than a single optimal solver. The `"reschedule"` strategy attempts to move conflicting tasks to new time slots before dropping them, which preserves more tasks but is greedier than a full backtracking solver. This is reasonable because pet care schedules are typically small enough (under 100 tasks) that a greedy approach produces good results without the complexity of a constraint satisfaction solver.

Rationale: For a family-pet planner, avoiding crashes and giving actionable warnings is more useful than aggressively resolving every edge-case overlap. The modular strategy design allows future growth to add robust interval solver algorithms if the product’s scope requires it.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The test suite (60 tests) covers the following behaviors:

1. **Core functionality** (12 tests): Task creation/completion, pet management, owner operations, basic scheduling — these verify the foundation works.
2. **Edge cases** (5 tests): Back-to-back tasks, time window overflow, capacity limits, twice-daily expansion, same-start conflicts — these catch subtle bugs at boundaries.
3. **Sorting & recurrence** (4 tests): Chronological ordering, priority sorting, daily/weekly auto-creation — these ensure the scheduler produces correct output order.
4. **Conflict detection** (4 tests): Overlapping vs. adjacent tasks, feasibility checking, integration workflow — these verify the system correctly identifies problems.
5. **Input validation** (17 tests): Empty descriptions, invalid durations/priorities/frequencies, reversed time windows, invalid pet types, duplicate pet names, whitespace trimming — these ensure bad data is rejected before it causes downstream errors.
6. **Stress testing** (4 tests): 50-task scheduling, 100-task scheduling, bulk conflict detection, 20-pet scheduling — these confirm the system handles realistic and large workloads.
7. **Error handling** (6 tests): No pets, completed tasks, non-existent tasks, wrong pet, unknown pet, invalid strategy — these verify graceful failure with clear messages.
8. **Conflict resolution strategies** (4 tests): Priority, shortest, reschedule strategies, and no-conflict passthrough — these verify all three resolution approaches work correctly.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence: 5/5 stars. The 60-test suite covers core logic, edge cases, input validation, stress scenarios, error recovery, and all three conflict resolution strategies. Every test passes, and the scheduler produces conflict-free schedules even with 100 tasks.

If I had more time, I would test:
- Concurrent modification scenarios (marking tasks complete while generating a schedule)
- Timezone-aware scheduling across different time zones
- Property-based / fuzz testing with randomized task parameters
- UI integration tests verifying the Streamlit app correctly renders schedules

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the layered approach to robustness. The system now validates data at the boundary (input validation on Task, Pet, Owner), handles errors gracefully in the middle layer (scheduler edge cases), and provides multiple resolution strategies at the output layer (priority, shortest, reschedule). This defense-in-depth approach means bugs are caught early and the scheduler never crashes on bad input. The stress tests confirming 50-100 tasks schedule correctly also gave me confidence that the performance optimizations (candidate-based slot finding, early capacity exit) were worthwhile.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign the conflict resolution to use a proper constraint satisfaction approach (e.g., interval scheduling with backtracking) instead of the current greedy strategies. I would also add a notification/alert system so owners get reminders before tasks are due, and implement a persistence layer (database or file-based) so schedules survive between sessions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important lesson was that **validation and error handling are not afterthoughts — they are part of the design**. Adding `__post_init__` validation to dataclasses caught entire categories of bugs that would have silently propagated through the scheduler. Working with AI helped me identify these gaps systematically: by listing "areas for future enhancement" and then addressing each one with targeted code and tests, I turned vague improvement ideas into concrete, testable changes. The process of writing tests first (for validation, stress, error recovery) also clarified what the code actually needed to do before I wrote it.
