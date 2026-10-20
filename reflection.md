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

    The scheduler considers 4 constraints. Time: the owner sets available_minutes for the day, and generate_plan() only schedules tasks that still fit in what's left of that budget. Priority: every task is LOW, MEDIUM, or HIGH, and higher priority tasks are placed first, with shorter tasks first when priorities tie. Due dates and recurrence: only tasks that are due that day are planned, so completed tasks are left out, and a DAILY or WEEKLY task that is marked done creates its next occurrence for tomorrow or next week instead of showing up again today. Time conflicts: since the owner can't do two things at once, conflict_warnings() flags any tasks whose time slots overlap, whether they are for the same pet or different pets.
- How did you decide which constraints mattered most?

    I ranked them by what would hurt a pet the most if it went wrong. Priority matters most because missing a feeding or a medication is much worse than skipping a grooming session, so the scheduler always places HIGH tasks first. Time comes next because a plan that doesn't fit into the owner's actual day isn't useful, which is why tasks that don't fit are skipped and explained instead of squeezed in. Due dates keep the plan focused on what actually needs doing today, and conflicts are reported as warnings instead of errors so the owner stays in control and can decide how to fix them. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    generate_plan() uses a greedy approach instead of searching for the best possible combination of tasks. It sorts pending tasks by priority (highest first, shorter task first on ties) and walks the list once, scheduling each task that still fits in the remaining available_minutes. This means it doesn't always use the time budget as well as it could. For example, with 60 minutes left, one 50 minute HIGH task is scheduled first and then two 30 minute MEDIUM tasks no longer fit, even though some owners might prefer getting both MEDIUM tasks done. A "knapsack" style algorithm could find the combination with the most total value, but it's more complex to write, test, and explain.
- Why is that tradeoff reasonable for this scenario?

    For a pet owner, the most important tasks (feeding, medication, walks) should always come first, even if that leaves a few minutes unused. The greedy approach guarantees that a HIGH priority task is never dropped to make room for lower priority ones, which matches how a real owner would think about their day. It's also easy to explain: every decision is recorded in explain_plan(), so the owner can see exactly why a task was scheduled or skipped. With only around 10-20 tasks a day, the small amount of time it might waste matters much less than having a plan that is predictable and easy to understand.

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

    The suite has 33 tests covering six areas. Sorting: sort_by_time() returns tasks in time order, keeps the order tasks were added when two have the same time, puts unscheduled tasks last, and handles empty lists. Plan generation: generate_plan() puts higher priority first, puts the shorter task first when priorities tie, and skips a task that doesn't fit the budget while still scheduling later tasks that do. It also handles a task that exactly fills the remaining time, a zero budget, and tasks that are not due yet or are overdue. Recurring tasks: finishing a DAILY or WEEKLY task creates the next occurrence 1 or 7 days later at the same time. One-time tasks don't repeat, and marking a task done twice doesn't create a duplicate. I also tested finishing a task late and a date rolling over from Dec 31 to Jan 1. Conflict detection: tasks at the same time, overlaps between different pets, and one long task that overlaps several shorter ones are all flagged. Back-to-back tasks and tasks on other days are not. Replanning: building the plan again after finishing a task keeps the finished task in its slot and doesn't create overlaps. Filtering and validation: filtering by pet name and done status, rejecting a task or pet that already belongs to someone else, and rejecting invalid durations and negative budgets.
- Why were these tests important?

    These are the behaviors the whole app depends on. If sorting or priority order is wrong, the owner could get a plan where a medication is skipped for a grooming session. The edge cases mattered most because that's where small mistakes hide, like using `<=` instead of `<` when checking whether two tasks overlap. The tests also found a real bug. If I built the plan, marked the 8:00 walk done, and built the plan again, the next task was also placed at 8:00, because generate_plan() ignored the time slots already used by finished tasks. Running main.py by hand never showed this, because it only builds the plan once. After the fix, that test passes and protects against the bug coming back.

**b. Confidence**

- How confident are you that your scheduler works correctly?

    4 out of 5. All 33 tests pass, and they cover the main scheduling behavior and the edge cases most likely to break. I'm not at 5 because a few areas are still untested or need a design decision, and the Streamlit UI has no automated tests, so I've only checked it by hand.
- What edge cases would you test next if you had more time?

    First, plans that run past midnight, for example starting at 23:30 with a 60 minute task. get_scheduled_tasks() only looks at the date a task starts on, so a task that ends the next day may be missed or cause strange conflicts. Second, whether finished tasks should count against available_minutes when the plan is rebuilt. Right now a finished 30 minute walk doesn't reduce the budget, so I'd decide which behavior is right and test it. Third, finishing a recurring task early, before its due date, and leap-year dates like Feb 28/29. Finally, I'd add tests for the Streamlit app to make sure session_state keeps pets and tasks between page reruns.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    I'm most satisfied that the scheduler explains itself and that the tests back it up. Every task generate_plan() schedules or skips gets a reason, so the owner never has to guess why "Vet checkup" didn't make it into the day. The same reasons show up in main.py and in the "Why this plan?" section of the Streamlit app. 
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    First, I'd make the Streamlit app do everything the backend can. Right now you can't mark a task done, edit it, or delete it from the UI, so recurring tasks only show up in main.py and the tests. Second, I'd add owner preferences, which the scenario mentions but I didn't build. For example, a task could have a preferred time window like "walks in the morning" or "meds at 9:00," and the planner would try to place it there. Third, I'd save pets and tasks to a file so they survive a page refresh, because session_state is lost when the browser tab closes. Finally, I'd settle the open design questions from my testing section: plans that run past midnight, and whether finished tasks should use up the day's available minutes.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    The UML is just a starting point. My first design had Schedule holding its own list of tasks, but once I started building, it made more sense for each Pet to own its tasks and for the Scheduler to read them through the Owner. Updating the diagram at the end showed how much the design changed. I also learned that AI is most useful as a reviewer when I give it something specific to check, like my skeletons against my UML, and less useful when I ask it to build everything at once. Either way, I still have to verify its work. The tests and running the app myself were how I knew the code actually did what the AI said it did.
