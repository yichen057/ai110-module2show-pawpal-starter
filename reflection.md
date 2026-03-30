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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
