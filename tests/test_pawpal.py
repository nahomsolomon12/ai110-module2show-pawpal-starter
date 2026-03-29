import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Schedule, conflict_warnings


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration_minutes=30, frequency="daily", priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Grooming", duration_minutes=20, frequency="weekly", priority="medium"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_schedule_sorts_high_priority_before_low():
    """Tasks added in reverse priority order must be scheduled high before low."""
    owner = Owner(name="Alex", available_hours=2)
    pet = Pet(name="Biscuit", species="dog", age=2)
    pet.add_task(Task(name="Playtime",     duration_minutes=15, frequency="daily", priority="low"))
    pet.add_task(Task(name="Morning walk", duration_minutes=30, frequency="daily", priority="high"))
    owner.add_pet(pet)

    schedule = Schedule(owner=owner, pet=pet)
    plan = schedule.plan()

    assert plan[0]["task"] == "Morning walk"
    assert plan[1]["task"] == "Playtime"


def test_schedule_sorts_shortest_first_on_priority_tie():
    """When two tasks share the same priority, the shorter one is scheduled first."""
    owner = Owner(name="Alex", available_hours=2)
    pet = Pet(name="Biscuit", species="dog", age=2)
    pet.add_task(Task(name="Long walk",  duration_minutes=45, frequency="daily", priority="high"))
    pet.add_task(Task(name="Feeding",    duration_minutes=10, frequency="daily", priority="high"))
    owner.add_pet(pet)

    schedule = Schedule(owner=owner, pet=pet)
    plan = schedule.plan()

    assert plan[0]["task"] == "Feeding"
    assert plan[1]["task"] == "Long walk"


def test_schedule_start_times_are_chronological():
    """Each scheduled task's start_min must equal the previous task's end_min."""
    owner = Owner(name="Alex", available_hours=2)
    pet = Pet(name="Biscuit", species="dog", age=2)
    pet.add_task(Task(name="Feeding",     duration_minutes=10, frequency="daily", priority="high"))
    pet.add_task(Task(name="Training",    duration_minutes=15, frequency="daily", priority="high"))
    pet.add_task(Task(name="Morning walk",duration_minutes=30, frequency="daily", priority="high"))
    owner.add_pet(pet)

    schedule = Schedule(owner=owner, pet=pet)
    plan = schedule.plan()

    for i in range(1, len(plan)):
        assert plan[i]["start_min"] == plan[i - 1]["end_min"], (
            f"Gap or overlap between '{plan[i-1]['task']}' and '{plan[i]['task']}'"
        )


def test_schedule_excludes_task_that_exceeds_budget():
    """A task longer than the entire available window must land in excluded(), not plan()."""
    owner = Owner(name="Alex", available_hours=0.5)   # 30 min
    pet = Pet(name="Biscuit", species="dog", age=2)
    pet.add_task(Task(name="Vet visit", duration_minutes=60, frequency="daily", priority="high"))
    owner.add_pet(pet)

    schedule = Schedule(owner=owner, pet=pet)
    assert schedule.plan() == []
    assert any(e["task"] == "Vet visit" for e in schedule.excluded())


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_complete_task_creates_new_pending_instance():
    """After complete_task(), the pet should have one more task than before."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))
    original_count = len(pet.tasks)

    pet.complete_task("Feeding")

    assert len(pet.tasks) == original_count + 1


def test_complete_task_marks_original_done():
    """The original task instance must be marked complete after complete_task()."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))

    pet.complete_task("Feeding")

    assert pet.tasks[0].completed is True


def test_complete_daily_task_advances_due_date_by_one_day():
    """Rescheduled daily task due_date must be exactly one day after the original."""
    today = date.today()
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high",
                      due_date=today))

    next_task = pet.complete_task("Feeding")

    assert next_task.due_date == today + timedelta(days=1)


def test_complete_weekly_task_advances_due_date_by_seven_days():
    """Rescheduled weekly task due_date must be exactly seven days after the original."""
    today = date.today()
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(name="Grooming", duration_minutes=20, frequency="weekly", priority="medium",
                      due_date=today))

    next_task = pet.complete_task("Grooming")

    assert next_task.due_date == today + timedelta(days=7)


def test_complete_task_raises_if_already_completed():
    """Calling complete_task() when the only matching task is already done must raise ValueError."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high")
    pet.add_task(task)
    task.mark_complete()   # mark done directly — no rescheduled copy is created

    with pytest.raises(ValueError):
        pet.complete_task("Feeding")   # no pending instance exists, must raise


def test_rescheduled_task_appears_in_next_generate():
    """After complete_task(), a fresh generate() should schedule the new pending instance."""
    owner = Owner(name="Alex", available_hours=2)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))
    owner.add_pet(pet)

    pet.complete_task("Feeding")

    schedule = Schedule(owner=owner, pet=pet)
    plan = schedule.plan()

    scheduled_names = [e["task"] for e in plan]
    assert "Feeding" in scheduled_names


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_warnings_detects_overlapping_schedules():
    """Two pets sharing the same owner both start at minute 0, so their tasks overlap."""
    owner = Owner(name="Alex", available_hours=2)

    mochi = Pet(name="Mochi", species="dog", age=3)
    mochi.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))

    luna = Pet(name="Luna", species="cat", age=5)
    luna.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    s1 = Schedule(owner=owner, pet=mochi)
    s2 = Schedule(owner=owner, pet=luna)

    warnings = conflict_warnings([s1, s2])

    assert len(warnings) > 0
    assert any("Mochi" in w and "Luna" in w for w in warnings)


def test_conflict_warnings_returns_empty_for_single_schedule():
    """A single schedule has no other schedule to conflict with."""
    owner = Owner(name="Alex", available_hours=2)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))
    owner.add_pet(pet)

    warnings = conflict_warnings([Schedule(owner=owner, pet=pet)])

    assert warnings == []


def test_conflict_warnings_returns_empty_for_empty_input():
    """Passing an empty list must never raise and must return []."""
    assert conflict_warnings([]) == []


def test_conflict_warnings_no_overlap_when_sequential():
    """Tasks that run back-to-back (not simultaneously) must not be flagged."""
    owner = Owner(name="Alex", available_hours=2)

    mochi = Pet(name="Mochi", species="dog", age=3)
    mochi.add_task(Task(name="Walk", duration_minutes=30, frequency="daily", priority="high"))

    luna = Pet(name="Luna", species="cat", age=5)
    luna.add_task(Task(name="Feeding", duration_minutes=10, frequency="daily", priority="high"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Force non-overlapping windows by manipulating start times directly
    s1 = Schedule(owner=owner, pet=mochi)
    s2 = Schedule(owner=owner, pet=luna)
    s1.generate()
    s2.generate()

    # Manually shift Luna's window to start after Mochi finishes (min 30)
    for entry in s2._plan:
        entry["start_min"] += 30
        entry["end_min"]   += 30

    warnings = conflict_warnings([s1, s2])
    assert warnings == []
