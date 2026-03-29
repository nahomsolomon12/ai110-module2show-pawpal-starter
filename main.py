from pawpal_system import Owner, Pet, Task, Schedule

# --- Owner ---
jordan = Owner(name="Jordan", available_hours=2)

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Tasks for Mochi (dog) ---
mochi.add_task(Task(name="Morning walk",    duration_minutes=30, frequency="daily",  priority="high"))
mochi.add_task(Task(name="Feeding",         duration_minutes=10, frequency="daily",  priority="high"))
mochi.add_task(Task(name="Grooming",        duration_minutes=20, frequency="weekly", priority="medium"))

# --- Tasks for Luna (cat) ---
luna.add_task(Task(name="Feeding",          duration_minutes=10, frequency="daily",  priority="high"))
luna.add_task(Task(name="Litter box clean", duration_minutes=10, frequency="daily",  priority="medium"))
luna.add_task(Task(name="Vet check-up",     duration_minutes=60, frequency="weekly", priority="low"))

# --- Register pets under owner ---
jordan.add_pet(mochi)
jordan.add_pet(luna)

# --- Generate and print schedules ---
print("=" * 50)
print("         TODAY'S SCHEDULE — PawPal+")
print("=" * 50)

for pet in jordan.pets:
    schedule = Schedule(owner=jordan, pet=pet)
    print()
    print(schedule.summary())
    print("-" * 50)
