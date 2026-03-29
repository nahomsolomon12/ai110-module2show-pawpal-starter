# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
 Pet → Task (1 to many)
A pet has multiple care tasks (feed, walk, meds, grooming)
Scheduler → Task (uses)
Scheduler takes tasks and organizes them
Scheduler → OwnerPreferences (depends on)
Scheduler respects constraints when building plans
- What classes did you include, and what responsibilities did you assign to each?
Pet: responsibilities - houses name species and age of each pet the end user wants to track, Tasks: responsibilities: name of task, duration, frequency and priorotization to work along with the schedule, Schedule: responsibilities - generates the order in which tasks are organized and outputs a plan, and Owner Preferences: responsibilities - provides constraints on the schedule class based on availablity of hours.
**b. Design changes**

- Did your design change during implementation?
Claude pointed out a few flaws in the UML one of which is Pet having no link to its Task list.

- If yes, describe at least one change and why you made it.
The UML shows Pet "1" --> "many" Task, but Pet holds no tasks attribute. Right now Schedule receives tasks as a loose list — there's no enforced connection between a pet and its tasks. A task list should live on Pet, and Schedule should pull from pet.tasks rather than accept an independent list.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The constraints implemented were primarily priority of tasks and time available by owner.
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
