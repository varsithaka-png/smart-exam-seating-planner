import csv, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.solver.seating import baseline_random, solve_cpsat, count_conflicts, to_grid

DATA = Path(__file__).resolve().parent.parent / "data" / "sample"
students = [(r["reg_no"], r["subject"]) for r in csv.DictReader(open(DATA / "students.csv"))]
room = next(csv.DictReader(open(DATA / "rooms.csv")))
rows, cols = int(room["rows"]), int(room["cols"])
students = students[: rows * cols]

base = baseline_random(students, rows, cols)
print("Random baseline conflicts:", count_conflicts(to_grid([s for _, s in base], rows, cols)))

t = time.perf_counter()
sol = solve_cpsat(students, rows, cols)
dt = time.perf_counter() - t
grid = to_grid([x[1] if x else "-" for x in sol], rows, cols)
print(f"CP-SAT conflicts: {count_conflicts(grid)}  (time {dt:.2f}s)")
