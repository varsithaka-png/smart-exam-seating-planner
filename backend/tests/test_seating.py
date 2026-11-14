from backend.solver.seating import solve_cpsat, count_conflicts, to_grid


def make(n, k):
    return [(f"R{i:03d}", f"S{i % k}") for i in range(n)]


def test_no_conflicts_and_everyone_seated_once():
    students = make(40, 4)
    sol = solve_cpsat(students, 5, 8)
    assert sol is not None
    seated = [x[0] for x in sol if x]
    assert sorted(seated) == sorted(r for r, _ in students)
    grid = to_grid([x[1] if x else "-" for x in sol], 5, 8)
    assert count_conflicts(grid) == 0


def test_room_too_small():
    import pytest
    with pytest.raises(AssertionError):
        solve_cpsat(make(50, 4), 5, 8)
