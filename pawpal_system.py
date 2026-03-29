"""
PawPal+ backend — full implementation of four core classes.
"""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Literal

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity with scheduling metadata."""
    name: str
    duration_minutes: int
    frequency: Literal["daily", "weekly"]
    priority: Literal["low", "medium", "high"]
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as done for the current period."""
        self.completed = True

    def reset(self) -> None:
        """Reset completion status for a new scheduling period."""
        self.completed = False

    def reschedule(self) -> "Task":
        """Return a fresh copy of this task reset for its next occurrence.

        Due date is advanced by 1 day for daily tasks, 7 days for weekly tasks,
        calculated from the current due_date using timedelta.
        """
        interval = timedelta(days=1 if self.frequency == "daily" else 7)
        return replace(self, completed=False, due_date=self.due_date + interval)

    def __str__(self) -> str:
        """Return a readable string showing task name, time, frequency, priority, and status."""
        status = "done" if self.completed else "pending"
        return (
            f"{self.name} ({self.duration_minutes} min | "
            f"{self.frequency} | {self.priority} priority | "
            f"due {self.due_date} | {status})"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet and the care tasks associated with it."""
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted highest to lowest priority."""
        return sorted(self.tasks, key=lambda t: PRIORITY_RANK[t.priority], reverse=True)

    def pending_tasks(self) -> list[Task]:
        """Return only tasks not yet marked complete."""
        return [t for t in self.tasks if not t.completed]

    def complete_task(self, name: str) -> Task:
        """Mark a pending task complete and append a fresh copy for its next occurrence.

        For daily tasks the new instance is ready for tomorrow;
        for weekly tasks it is ready for next week.

        Returns the newly queued Task instance.
        Raises ValueError if no pending task with that name exists.
        """
        for task in self.tasks:
            if task.name == name and not task.completed:
                task.mark_complete()
                next_task = task.reschedule()
                self.tasks.append(next_task)
                return next_task
        raise ValueError(f"No pending task '{name}' found for {self.name}")

    def __str__(self) -> str:
        """Return a readable string showing pet name, species, age, and task count."""
        return f"{self.name} ({self.species}, age {self.age}) — {len(self.tasks)} task(s)"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """
    An owner manages one or more pets and provides scheduling constraints
    through their available daily hours.
    """

    def __init__(self, name: str, available_hours: float):
        """Initialize an owner with a name and their daily available hours."""
        if available_hours <= 0:
            raise ValueError("available_hours must be greater than 0")
        self.name = name
        self.available_hours = available_hours
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def available_minutes(self) -> int:
        """Convert available hours to minutes for scheduling math."""
        return int(self.available_hours * 60)

    def preferences(self) -> dict:
        """Return a summary of owner scheduling constraints."""
        return {
            "owner_name": self.name,
            "available_hours": self.available_hours,
            "available_minutes": self.available_minutes(),
        }

    def get_all_tasks(self) -> dict[str, list[Task]]:
        """Return all tasks grouped by pet name across every owned pet."""
        return {pet.name: pet.tasks for pet in self.pets}

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> dict[str, list[Task]]:
        """Return tasks filtered by completion status, pet name, or both.

        Args:
            completed: If True, return only completed tasks. If False, return
                       only pending tasks. If None, include both.
            pet_name:  If provided, return tasks for that pet only.
                       If None, include all pets.

        Returns:
            A dict mapping pet name → filtered task list. Pets with no
            matching tasks are omitted from the result.
        """
        pets = self.pets
        if pet_name is not None:
            pets = [p for p in pets if p.name == pet_name]

        result = {}
        for pet in pets:
            tasks = pet.tasks
            if completed is not None:
                tasks = [t for t in tasks if t.completed == completed]
            if tasks:
                result[pet.name] = tasks
        return result

    def __str__(self) -> str:
        """Return a readable string showing owner name, available hours, and pet count."""
        return (
            f"Owner: {self.name} | {self.available_hours}h available | "
            f"{len(self.pets)} pet(s)"
        )


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

class Schedule:
    """
    The scheduling brain.

    Retrieves tasks from a pet, applies owner constraints, and produces an
    ordered daily care plan.

    Algorithm:
      1. Pull pending daily tasks from the pet; note weekly tasks as deferred.
      2. Sort daily tasks by priority (high → medium → low), then by duration (shortest first) as a tiebreaker.
      3. Greedily add tasks until the owner's available minutes are used up.
      4. Store results internally; expose via plan(), excluded(), summary().
    """

    def __init__(self, owner: Owner, pet: Pet):
        """Initialize a schedule for one pet, validated against the owner's registered pets."""
        if pet not in owner.pets:
            raise ValueError(f"{pet.name} is not registered under {owner.name}")
        self.owner = owner
        self.pet = pet
        self._plan: list[dict] = []
        self._excluded: list[dict] = []
        self._minutes_used: int = 0
        self._generated: bool = False
        self._warnings: list[str] = []

    def generate(self) -> None:
        """Build the schedule. Must be called before plan(), excluded(), or summary()."""
        self._plan = []
        self._excluded = []
        self._minutes_used = 0
        self._warnings = []

        available = self.owner.available_minutes()
        daily = [t for t in self.pet.pending_tasks() if t.frequency == "daily"]
        weekly = [t for t in self.pet.pending_tasks() if t.frequency == "weekly"]

        sorted_daily = sorted(daily, key=lambda t: (-PRIORITY_RANK[t.priority], t.duration_minutes))

        for task in sorted_daily:
            if self._minutes_used + task.duration_minutes <= available:
                start = self._minutes_used
                end   = start + task.duration_minutes
                self._plan.append({
                    "task": task.name,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "start_min": start,
                    "end_min": end,
                    "reason": (
                        f"Scheduled — {task.priority} priority, "
                        f"fits within available time."
                    ),
                })
                self._minutes_used += task.duration_minutes
            else:
                remaining = available - self._minutes_used
                self._excluded.append({
                    "task": task.name,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "reason": (
                        f"Skipped — {remaining} min remaining, "
                        f"task needs {task.duration_minutes} min."
                    ),
                })

        for task in weekly:
            self._excluded.append({
                "task": task.name,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "reason": "Deferred — weekly task, not scheduled today.",
            })

        if not self._plan:
            self._warnings.append(
                f"WARNING: No tasks could be scheduled for {self.pet.name}. "
                f"All daily tasks may exceed the available {available} min."
            )
        elif len(self._excluded) > len(weekly):
            skipped_count = len(self._excluded) - len(weekly)
            self._warnings.append(
                f"WARNING: {skipped_count} task(s) for {self.pet.name} were skipped "
                f"due to insufficient time. Consider increasing available hours."
            )

        self._generated = True

    def plan(self) -> list[dict]:
        """Return the list of scheduled tasks. Calls generate() if not yet run."""
        if not self._generated:
            self.generate()
        return self._plan

    def excluded(self) -> list[dict]:
        """Return tasks that were skipped or deferred. Calls generate() if not yet run."""
        if not self._generated:
            self.generate()
        return self._excluded

    def summary(self) -> str:
        """Return a human-readable plan with explanations for every task decision."""
        if not self._generated:
            self.generate()

        prefs = self.owner.preferences()
        lines = [
            f"Daily care plan for {self.pet.name} ({self.pet.species}, age {self.pet.age})",
            f"Owner: {prefs['owner_name']} | Available: {prefs['available_hours']}h "
            f"({prefs['available_minutes']} min) | Scheduled: {self._minutes_used} min",
            "",
            "=== Scheduled Tasks ===",
        ]

        if self._plan:
            for i, entry in enumerate(self._plan, 1):
                lines.append(
                    f"  {i}. {entry['task']} — {entry['duration_minutes']} min "
                    f"[{entry['priority']}]"
                )
                lines.append(f"     {entry['reason']}")
        else:
            lines.append("  (No tasks could be scheduled.)")

        if self._excluded:
            lines += ["", "=== Not Scheduled ==="]
            for entry in self._excluded:
                lines.append(
                    f"  - {entry['task']} ({entry['duration_minutes']} min): {entry['reason']}"
                )

        if self._warnings:
            lines += ["", "=== Warnings ==="]
            for w in self._warnings:
                lines.append(f"  ! {w}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Lightweight conflict detection
# ---------------------------------------------------------------------------

def conflict_warnings(schedules: list[Schedule]) -> list[str]:
    """Return plain-English warning strings for any time-window overlaps across schedules.

    Two tasks conflict when their windows intersect:
        A.start_min < B.end_min  AND  B.start_min < A.end_min

    This is intentionally lightweight — it never raises an exception. If the
    input is empty or all schedules have no planned tasks, it returns [].

    Args:
        schedules: Any list of Schedule objects (generated or not).

    Returns:
        A list of human-readable warning strings. Empty list means no conflicts.
    """
    if not schedules:
        return []

    all_entries: list[tuple[str, dict]] = []
    for sched in schedules:
        if not sched._generated:
            sched.generate()
        for entry in sched._plan:
            all_entries.append((sched.pet.name, entry))

    warnings = []
    for i in range(len(all_entries)):
        for j in range(i + 1, len(all_entries)):
            pet_a, a = all_entries[i]
            pet_b, b = all_entries[j]
            if a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"]:
                warnings.append(
                    f"WARNING: [{pet_a}] '{a['task']}' (min {a['start_min']}-{a['end_min']}) "
                    f"overlaps [{pet_b}] '{b['task']}' (min {b['start_min']}-{b['end_min']})"
                )
    return warnings
