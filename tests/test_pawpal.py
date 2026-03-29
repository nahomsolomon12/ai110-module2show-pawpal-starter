import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
