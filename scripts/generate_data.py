"""Create synthetic students.csv and rooms.csv for testing."""
import csv, random
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "sample"
OUT.mkdir(parents=True, exist_ok=True)

SUBJECTS = ["Maths", "Physics", "DBMS", "OS", "CN", "AI"]
N_STUDENTS = 120

with open(OUT / "students.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["reg_no", "dept", "subject"])
    for i in range(N_STUDENTS):
        w.writerow([f"22CS{i+1:03d}", "CSE", SUBJECTS[i % len(SUBJECTS)]])

with open(OUT / "rooms.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["room_id", "rows", "cols"])
    w.writerow(["A101", 6, 10])
    w.writerow(["A102", 6, 10])

print("Wrote", OUT)
