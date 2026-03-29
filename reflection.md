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
Priority and available time were chosen as the primary constraints because they reflect the two most realistic limitations a pet owner faces daily: not every task is equally urgent, and there are only so many hours in a day. Priority ensures critical care (feeding, medication) is never bumped for lower-value tasks. Available time ensures the schedule is actually achievable rather than aspirational. A secondary sort by duration was added later so that when tasks share the same priority, shorter ones are scheduled first — this maximizes the number of tasks that fit within the time budget.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler uses a greedy algorithm: it processes tasks in priority order and adds each one only if it fits within the remaining available time. If a long high-priority task cannot fit, the scheduler stops adding high-priority tasks even if shorter lower-priority tasks could still fit.

- Why is that tradeoff reasonable for this scenario?
For a daily pet care app, simplicity and predictability matter more than an optimal mathematical solution. A greedy approach is easy to explain to the user ("high priority tasks come first"), runs instantly regardless of how many tasks exist, and produces sensible results in practice. A full knapsack optimization would be more accurate but significantly harder to implement and explain, and the benefit for a typical household with a handful of tasks would be negligible.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
AI was used throughout the project for design brainstorming (suggesting algorithm improvements and logic gaps), feature implementation (sorting by duration as a tiebreaker, the filter_tasks method on Owner, the complete_task auto-reschedule method on Pet), and debugging (catching the encoding error caused by the arrow character on Windows, and diagnosing the ValueError caused by completing a task before the reschedule demo ran).

- What kinds of prompts or questions were most helpful?
Specific, scoped prompts worked best — for example, asking for "a list of small algorithm improvements" produced concrete, actionable suggestions tied directly to the existing code. Prompts that referenced specific class names and described the desired behavior (e.g., "filter tasks by completion status or pet name") gave the AI enough context to place new methods in the right class with the right signature.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When the AI suggested implementing a knapsack or brute-force approach for small task sets to find a more optimal schedule, that suggestion was not implemented. The greedy approach was kept instead.

- How did you evaluate or verify what the AI suggested?
The knapsack suggestion was evaluated against the project's actual scope. For a household pet care app with a small number of tasks, the added complexity of a combinatorial algorithm would not produce a meaningfully better result for the user. Running main.py and reading the schedule output was sufficient to confirm the greedy approach produces correct, reasonable plans. The verification process was: run the code, read the output, confirm the ordering and totals match expectations.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Tasks were added in deliberately reversed priority order (low to high) to verify the sort puts them back in the correct order. The filter_tasks method was tested with all four combinations: pending only, completed only, one pet only, and pending + one pet. The complete_task reschedule was verified by checking that the task count increases by one after completion, that the original instance is marked done, and that the new instance is pending with a due_date advanced by one day (daily) or seven days (weekly).

- Why were these tests important?
These tests confirmed that the sorting, filtering, and rescheduling logic work correctly together — not just individually. The out-of-order insertion test is important because real users will not add tasks in priority order. The reschedule test is important because a bug there (e.g., advancing the wrong number of days, or accidentally completing the new copy instead of the original) would silently corrupt the task history.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Confident for the happy path — standard daily tasks with clear priorities and a reasonable time budget produce correct, well-ordered schedules. Less confident around edge cases that have not yet been exercised in testing.

- What edge cases would you test next if you had more time?
1. Owner available time of zero or less than the shortest task — does the schedule gracefully produce an empty plan?
2. All tasks sharing the same priority and duration — does the order remain stable?
3. Calling complete_task on a task that has already been completed — does it raise the correct ValueError?
4. A pet with only weekly tasks — does the schedule correctly defer all of them with no scheduled entries?
5. Rescheduling across a month boundary (e.g., March 31 + 1 day) — does timedelta correctly roll over to April 1?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The reschedule logic is the most satisfying part. The combination of Task.reschedule() using dataclasses.replace() and timedelta, and Pet.complete_task() orchestrating the completion and re-queuing, is clean and minimal. Each method has a single responsibility, and the due_date automatically advances the correct number of days based on frequency without any manual calendar math.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
The shared time budget across multiple pets would be the first redesign. Currently Owner.available_minutes() is used independently per pet, so an owner with 2 hours could theoretically end up scheduled for 2 hours per pet. A single running budget subtracted across all pets during schedule generation would make the planner realistic for multi-pet households. A persistent data layer (even a simple JSON file) would also be important so tasks and completion history survive between sessions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Ownership of data matters more than any individual algorithm. The most impactful design decisions in this project were about which class holds which data — tasks living on Pet rather than floating as a loose list, the reschedule copy being appended to pet.tasks rather than returned and discarded, and filter_tasks living on Owner because Owner is the only class with visibility across all pets. Getting those boundaries right made every subsequent feature easier to add. AI is most useful after those boundaries are established — it can suggest algorithms and methods quickly, but it cannot decide where data should live without understanding the project's goals.
