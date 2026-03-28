"""
PawPal+ backend — skeleton classes based on UML design.
"""

from dataclasses import dataclass


@dataclass
class Pet:
    name: str
    species: str
    age: int


@dataclass
class Task:
    name: str
    duration_minutes: int
    frequency: str
    priority: str


class Owner:
    def __init__(self, name: str, available_hours: float):
        self.name = name
        self.available_hours = available_hours
        self.pets: list[Pet] = []

    def available_minutes(self) -> int:
        pass

    def preferences(self) -> dict:
        pass


class Schedule:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate(self) -> None:
        pass

    def plan(self) -> list:
        pass

    def excluded(self) -> list:
        pass

    def summary(self) -> str:
        pass
