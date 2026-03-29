from pawpal_system import Owner, Pet, Task, Schedule, conflict_warnings

# --- Owner ---
jordan = Owner(name="Jordan", available_hours=2)

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Tasks for Mochi added OUT OF ORDER (low → medium → high) ---
mochi.add_task(Task(name="Grooming",      duration_minutes=20, frequency="weekly", priority="medium"))
mochi.add_task(Task(name="Feeding",       duration_minutes=10, frequency="daily",  priority="high"))
mochi.add_task(Task(name="Morning walk",  duration_minutes=30, frequency="daily",  priority="high"))
mochi.add_task(Task(name="Playtime",      duration_minutes=15, frequency="daily",  priority="low"))
mochi.add_task(Task(name="Training",      duration_minutes=10, frequency="daily",  priority="high"))

# --- Tasks for Luna added OUT OF ORDER (low → high → medium) ---
luna.add_task(Task(name="Vet check-up",     duration_minutes=60, frequency="weekly", priority="low"))
luna.add_task(Task(name="Feeding",          duration_minutes=10, frequency="daily",  priority="high"))
luna.add_task(Task(name="Litter box clean", duration_minutes=10, frequency="daily",  priority="medium"))
luna.add_task(Task(name="Brushing",         duration_minutes=10, frequency="daily",  priority="medium"))

# --- Register pets under owner ---
jordan.add_pet(mochi)
jordan.add_pet(luna)

# --- Generate schedules (marks tasks as scheduled, not completed) ---
print("=" * 55)
print("         TODAY'S SCHEDULE — PawPal+")
print("=" * 55)

for pet in jordan.pets:
    schedule = Schedule(owner=jordan, pet=pet)
    print()
    print(schedule.summary())
    print("-" * 55)

# --- Mark some tasks complete to demo filtering ---
mochi.tasks[1].mark_complete()  # Feeding
mochi.tasks[2].mark_complete()  # Morning walk
luna.tasks[1].mark_complete()   # Feeding

# --- Demo: filter_tasks ---
print()
print("=" * 55)
print("         FILTER DEMOS")
print("=" * 55)

# 1. All pending tasks across every pet
print("\n-- Pending tasks (all pets) --")
for pet_name, tasks in jordan.filter_tasks(completed=False).items():
    print(f"  {pet_name}:")
    for t in tasks:
        print(f"    {t}")

# 2. All completed tasks across every pet
print("\n-- Completed tasks (all pets) --")
for pet_name, tasks in jordan.filter_tasks(completed=True).items():
    print(f"  {pet_name}:")
    for t in tasks:
        print(f"    {t}")

# 3. All tasks for Mochi only (both statuses)
print("\n-- All tasks for Mochi only --")
for pet_name, tasks in jordan.filter_tasks(pet_name="Mochi").items():
    print(f"  {pet_name}:")
    for t in tasks:
        print(f"    {t}")

# 4. Only pending tasks for Luna
print("\n-- Pending tasks for Luna only --")
for pet_name, tasks in jordan.filter_tasks(completed=False, pet_name="Luna").items():
    print(f"  {pet_name}:")
    for t in tasks:
        print(f"    {t}")

# --- Reset all completions before reschedule demo ---
for t in mochi.tasks + luna.tasks:
    t.reset()

# --- Demo: complete_task auto-reschedule ---
print()
print("=" * 55)
print("         RESCHEDULE DEMO")
print("=" * 55)

print(f"\nMochi tasks before completing 'Feeding': {len(mochi.tasks)}")
next_feeding = mochi.complete_task("Feeding")
print(f"Mochi tasks after  completing 'Feeding': {len(mochi.tasks)}")
print(f"  Completed instance : {mochi.tasks[1]}")
print(f"  New queued instance: {next_feeding}")

print(f"\nLuna tasks before completing 'Litter box clean': {len(luna.tasks)}")
next_litter = luna.complete_task("Litter box clean")
print(f"Luna tasks after  completing 'Litter box clean': {len(luna.tasks)}")
print(f"  Completed instance : {luna.tasks[2]}")
print(f"  New queued instance: {next_litter}")

# --- Demo: sorting by priority + duration tiebreaker ---
print()
print("=" * 55)
print("         SORT DEMO — priority then shortest first")
print("=" * 55)

print("\n-- Mochi tasks sorted (get_tasks_by_priority) --")
for t in mochi.get_tasks_by_priority():
    print(f"  {t}")

print("\n-- Schedule sort: daily tasks before generate() --")
mochi_sorted_daily = sorted(
    [t for t in mochi.pending_tasks() if t.frequency == "daily"],
    key=lambda t: (-{"high": 3, "medium": 2, "low": 1}[t.priority], t.duration_minutes),
)
print("  Mochi daily tasks (high->low priority, shortest first on ties):")
for t in mochi_sorted_daily:
    print(f"    {t}")

# --- Demo: detect_overlaps across all pet schedules ---
print()
print("=" * 55)
print("         OVERLAP DETECTION DEMO")
print("=" * 55)

# Reset so all tasks are pending before building fresh schedules
for t in mochi.tasks + luna.tasks:
    t.reset()

mochi_schedule = Schedule(owner=jordan, pet=mochi)
luna_schedule  = Schedule(owner=jordan, pet=luna)
mochi_schedule.generate()
luna_schedule.generate()

print("\n-- Mochi scheduled windows --")
for entry in mochi_schedule.plan():
    print(f"  {entry['task']:20s}  min {entry['start_min']:>3}-{entry['end_min']:>3}")

print("\n-- Luna scheduled windows --")
for entry in luna_schedule.plan():
    print(f"  {entry['task']:20s}  min {entry['start_min']:>3}-{entry['end_min']:>3}")

warnings = conflict_warnings([mochi_schedule, luna_schedule])
print()
if warnings:
    print(f"  {len(warnings)} conflict(s) found:")
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found between schedules.")
