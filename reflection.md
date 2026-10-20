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

    I identified and implemented the four basic core classes Owner, Pet, Task, and Schedule into the initial UML design. Owner, Pet, Task, and Schedule. Owner can own many Pets. Each Pet has 1 Owner. Many Tasks can be assigned to a Pet. A Pet can have many tasks. A Schedule can contain many Tasks, and a Task is assigned to a Schedule.
- What classes did you include, and what responsibilities did you assign to each?

    Owner, Pet, Task, Schedule. Owner holds basic contact infor for the pet owner, has a list of Pets, and can add a Pet to their list. A Pet contains basic Pet info and the name of their Owner. A Task has basic info such as duration, priority, and Pet associated with it, and can mark itself done or reschedule its time. A Schedule has a list of Tasks and can add/remove Tasks, get a list of pending Tasks, get Tasks for a specific Pet, and display a schedule of Tasks.


**b. Design changes**

- Did your design change during implementation?

    Yes
- If yes, describe at least one change and why you made it.

    AI identified that a Pet does not point to its Owner, it only had a owner_name string but no Owner object. A Pet's owner_name: str is now owner: Owner. Schedule class was greatly expanded to now have an owner, a day, and available_minutes. generate_plan() was added to sort tasks by priority and fit them in available times. explain_plan() records why each task was kept or skipped.

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

    I used AI for every stage of the project. For design, I had it review my class skeletons against the UML. That review found the missing Pet -> Owner link (owner_name was just a string) and suggested replacing the done flag with last_done plus a Frequency enum so recurring tasks would work. For refactoring, it helped me turn priority from a plain string into a Priority IntEnum so tasks sort correctly, and it made age a computed property so it never goes stale. It also helped me implement generate_plan() and write the tests.
- What kinds of prompts or questions were most helpful?

    The most helpful prompts asked AI to review something specific, for example "review these skeletons against my UML and point out problems", instead of asking it to build everything from scratch in a single prompt. Keeping each logical task in its own chat window also helped in organizing myself and not being overwhelmed by everything being done in a single window.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    AI wanted to change the mark_done() method to mark_complete() to better match the project instructions but I ignored its suggestion as every student's UML will slightly vary with naming which is okay if the implementation fulfills the project requirements.
- How did you evaluate or verify what the AI suggested?

    I checked suggestions against my UML and the project requirements before accepting them, and I made sure each change still fit how the classes connect. For the logic, I verified behavior by running main.py to see a real generated schedule with its explanations and by running pytest tests manually. If I had any questions, I asked AI to explain itself and its changes.

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
