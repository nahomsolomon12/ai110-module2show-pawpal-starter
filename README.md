# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Three enhancements were added to `pawpal_system.py` to make the scheduler more useful and reliable.

### Sort by priority and duration

`Schedule.generate()` now sorts daily tasks by priority first (high → medium → low), then by duration as a tiebreaker — shortest task first when two tasks share the same priority. This maximizes the number of tasks that fit within the owner's available time window, rather than stopping early because a long task blocked a short one.

### Filter tasks by status or pet

`Owner.filter_tasks(completed, pet_name)` returns tasks filtered by completion status, pet name, or both. All parameters are optional, so any combination works:

```python
owner.filter_tasks(completed=False)              # all pending tasks across every pet
owner.filter_tasks(completed=True)               # all completed tasks
owner.filter_tasks(pet_name="Mochi")             # all tasks for one pet
owner.filter_tasks(completed=False, pet_name="Mochi")  # pending tasks for one pet
```

Pets with no matching tasks are omitted from the result.

### Lightweight conflict detection

`conflict_warnings(schedules)` checks all scheduled task pairs across multiple schedules for time-window overlaps and returns a plain list of warning strings — it never raises an exception. Because each pet's schedule independently starts from minute 0, an owner with multiple pets can be double-booked if both schedules are treated as running concurrently. The function surfaces those conflicts as readable messages:

```
WARNING: [Mochi] 'Feeding' (min 0-10) overlaps [Luna] 'Feeding' (min 0-10)
```

Each `Schedule` also tracks its own `_warnings` list, populated during `generate()` when no tasks could be scheduled or tasks were skipped due to time constraints. These warnings appear automatically at the bottom of `schedule.summary()`.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
