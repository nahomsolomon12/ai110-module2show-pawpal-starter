# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +float available_hours
        +List~Pet~ pets
        +preferences() dict
        +available_minutes() int
    }

    class Pet {
        +String name
        +String species
        +int age
    }

    class Task {
        +String name
        +int duration_minutes
        +String frequency
        +String priority
    }

    class Schedule {
        +Owner owner
        +Pet pet
        +List~Task~ tasks
        +generate() void
        +plan() List~dict~
        +excluded() List~dict~
        +summary() String
    }

    Owner "1" --> "many" Pet : owns
    Pet "1" --> "many" Task : has care tasks
    Schedule --> Owner : constrained by
    Schedule --> Pet : plans for
    Schedule --> "many" Task : uses
```

## Relationships

- **Owner → Pet** (1 to many): One owner can have multiple pets.
- **Pet → Task** (1 to many): One pet has multiple care tasks (feed, walk, meds, grooming, etc.)
- **Schedule → Owner**: The scheduler reads the owner's preferences (available hours) as constraints.
- **Schedule → Pet**: The schedule is generated for a specific pet belonging to the owner.
- **Schedule → Task**: The scheduler pulls from the pet's task list to build the plan.
