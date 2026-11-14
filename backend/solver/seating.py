import random
from ortools.sat.python import cp_model


def count_conflicts(grid):
    """grid: list of rows, each a list of subjects. Counts adjacent same-subject pairs."""
    n = 0
    for r, row in enumerate(grid):
        for c, s in enumerate(row):
            if c + 1 < len(row) and row[c + 1] == s:
                n += 1
            if r + 1 < len(grid) and grid[r + 1][c] == s:
                n += 1
    return n


def to_grid(subjects, rows, cols):
    return [subjects[r * cols:(r + 1) * cols] for r in range(rows)]


def baseline_random(students, rows, cols, seed=0):
    """students: list of (reg_no, subject). Returns list of (reg_no, subject) in seat order."""
    s = students[:]
    random.Random(seed).shuffle(s)
    return s[: rows * cols]


def solve_cpsat(students, rows, cols, time_limit=20):
    """Seat students so no two adjacent seats share a subject. Returns seat-ordered list or None."""
    n = rows * cols
    assert len(students) <= n, "Room too small"
    subjects = sorted({s for _, s in students})
    by_subj = {s: [r for r, sub in students if sub == s] for s in subjects}
    m = cp_model.CpModel()
    # x[s, i] = 1 if seat i holds a student of subject s; the last seats may stay empty
    x = {(s, i): m.NewBoolVar(f"x_{s}_{i}") for s in subjects for i in range(n)}
    empty = [m.NewBoolVar(f"e_{i}") for i in range(n)]
    for i in range(n):
        m.AddExactlyOne([x[s, i] for s in subjects] + [empty[i]])
    for s in subjects:
        m.Add(sum(x[s, i] for i in range(n)) == len(by_subj[s]))
    for i in range(n):
        r, c = divmod(i, cols)
        nbrs = []
        if c + 1 < cols:
            nbrs.append(i + 1)
        if r + 1 < rows:
            nbrs.append(i + cols)
        for j in nbrs:
            for s in subjects:
                m.Add(x[s, i] + x[s, j] <= 1)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(m)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    ptr = {s: 0 for s in subjects}
    out = []
    for i in range(n):
        placed = None
        for s in subjects:
            if solver.Value(x[s, i]):
                placed = (by_subj[s][ptr[s]], s)
                ptr[s] += 1
                break
        out.append(placed)
    return out
