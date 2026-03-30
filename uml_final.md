# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Task {
        +String name
        +int duration_minutes
        +String frequency
        +String priority
        +bool completed
        +date due_date
        +mark_complete() void
        +reset() void
        +reschedule() Task
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~Task~ tasks
        +add_task(task) void
        +get_tasks_by_priority() List~Task~
        +pending_tasks() List~Task~
        +complete_task(name) Task
    }

    class Owner {
        +String name
        +float available_hours
        +List~Pet~ pets
        +add_pet(pet) void
        +available_minutes() int
        +preferences() dict
        +get_all_tasks() dict
        +filter_tasks(completed, pet_name) dict
    }

    class Schedule {
        +Owner owner
        +Pet pet
        -List~dict~ _plan
        -List~dict~ _excluded
        -List~str~ _warnings
        -int _minutes_used
        -bool _generated
        +generate() void
        +plan() List~dict~
        +excluded() List~dict~
        +summary() String
    }

    class conflict_warnings {
        <<function>>
        +conflict_warnings(schedules) List~str~
    }

    Owner "1" --> "many" Pet : owns
    Pet "1" --> "many" Task : has care tasks
    Schedule --> Owner : constrained by
    Schedule --> Pet : plans for
    conflict_warnings ..> Schedule : reads _plan from
```

## Relationships

- **Owner → Pet** (1 to many): One owner can have multiple pets registered via `add_pet()`.
- **Pet → Task** (1 to many): Tasks live on the pet; `complete_task()` marks one done and appends a rescheduled copy.
- **Schedule → Owner**: `generate()` reads `owner.available_minutes()` as the time budget constraint.
- **Schedule → Pet**: The schedule is built exclusively from `pet.pending_tasks()` — it does not hold its own task list.
- **conflict_warnings → Schedule**: Module-level function that reads `_plan` entries (including `start_min`/`end_min`) from a list of schedules to detect time-window overlaps.

## Changes from Phase 1 UML

| What changed | Why |
|---|---|
| `Task` gained `completed`, `due_date`, and three methods | Needed for recurrence logic and `timedelta`-based rescheduling |
| `Pet` gained `tasks` attribute and three methods | Tasks must live on `Pet`, not float as a loose list passed to `Schedule` |
| `Owner` gained `add_pet()`, `get_all_tasks()`, `filter_tasks()` | Owner is the only class with visibility across all pets |
| `Schedule` lost `List~Task~ tasks` attribute | Schedule reads from `pet.tasks` directly — storing a separate copy would create drift |
| `Schedule` gained `_warnings`, `_minutes_used`, `_generated` | Internal state needed to support lazy generation and warning messages |
| `conflict_warnings` added as module-level function | Cross-schedule comparison does not belong to any single class |
