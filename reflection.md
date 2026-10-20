# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Brainstorming (step 1 and step 2 of Phase 1):
Three core actions a user should be able to perform:
1. Add a pet. This should also include the pet's info and owner's basic info
2. Schedule a task. Could be a walk, feeding, medicine, enrichment, grooming, etc. Be able to edit the tasks' duration and priority
3. View a schedule of the day's tasks. The plan/schedule should take into account the tasks' contraints and priorities

Main objects needed for this system:
* Pet 
    - attributes: name, sex, species, breed (if applicable), age, weight, birthday, owner_name
    - methods: getters and setters for each attribute, although I'm not sure if Python needs this
* Owner 
    - attributes: name, sex, contact_info (phone number and/or email), pets (list or whichever collection type makes sense)
    - methods: add_pet, list_pets
* Task
    - attributes: title (description of task e.g. "morning walk"), duration (how long task will take), priority (low, medium, high), done (bool for if task has been completed), pet (which pet is assigned to the task)
    - methods: mark_done (sets done to true), reschedule (updates time)
* Schedule (not sure if should be its own class or just a list of tasks? or some other structure)
    - attributes: tasks (list of Task instances)
    - methods: add_task, remove_task, get_pending_tasks (tasks where done is False), get_tasks_for_pet (returns tasks assigned to specific Pet), display_schedule (some kind of clean way to display the schedule of tasks for the day)

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
