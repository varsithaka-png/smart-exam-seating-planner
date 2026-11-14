
import sys
sys.path.insert(0, ".")

from backend.solver.invigilation import (
    allocate,
    replace_absent,
    duty_counts,
    feasibility
)

# Create 20 teachers
teachers = [{"id": f"T{i:02d}"} for i in range(20)]

# 12 sessions, each having 6 rooms
rooms_per_session = {f"S{i}": 6 for i in range(12)}

# Check whether allocation is possible
print("Feasibility:", feasibility(teachers, rooms_per_session))

# Allocate invigilators
plan = allocate(teachers, rooms_per_session)

# Display duties assigned to teachers
print("Duties per teacher:", duty_counts(plan))

# Test absent teacher replacement
absent = plan["rooms"]["S0", 0]

new_plan, log = replace_absent(
    plan,
    teachers,
    absent,
    sessions={"S0"}
)

print("Absent:", absent, "->", log)
