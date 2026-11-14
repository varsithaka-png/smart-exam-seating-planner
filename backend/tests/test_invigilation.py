from backend.solver.invigilation import allocate, feasibility, replace_absent, duty_counts

CAP = 5


def make(n_teachers=20, sessions=12, rooms=6):
    teachers = [{"id": f"T{i:02d}"} for i in range(n_teachers)]
    return teachers, {f"S{i}": rooms for i in range(sessions)}


def test_cap_and_no_double_booking():
    teachers, rps = make()
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=1)
    assert plan is not None
    for s, n in rps.items():
        assigned = [plan["rooms"][s, r] for r in range(n)] + plan["standby"][s]
        assert len(assigned) == len(set(assigned))            # nobody twice in a session
    assert max(duty_counts(plan).values()) <= CAP


def test_standby_fills_absent_teacher():
    teachers, rps = make()
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=1)
    absent = plan["rooms"]["S0", 0]
    new, log = replace_absent(plan, teachers, absent, sessions={"S0"}, cap=CAP)
    assert log[0]["source"] == "standby"
    assert new["rooms"]["S0", 0] != absent
    assert len(new["rooms"]) == len(plan["rooms"])


def test_cap_still_respected_after_replacement():
    teachers, rps = make()
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=1)
    absent = plan["rooms"]["S3", 2]
    new, _ = replace_absent(plan, teachers, absent, cap=CAP)
    assert max(duty_counts(new).values()) <= CAP


def test_infeasible_is_reported_before_solving():
    teachers, rps = make(n_teachers=10, sessions=12, rooms=6)   # 72 duties > 10 x 5
    info = feasibility(teachers, rps, cap=CAP, standby_per_session=1)
    assert not info["ok"] and info["min_teachers"] == 15
    assert allocate(teachers, rps, cap=CAP, standby_per_session=1) is None


def test_unfilled_when_nobody_available():
    teachers = [{"id": "A"}, {"id": "B"}]
    rps = {"S0": 2}
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=0)
    new, log = replace_absent(plan, teachers, "A", cap=CAP)
    assert log[0]["source"] == "UNFILLED"


def test_unused_standby_counts_as_zero_duties():
    teachers, rps = make()
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=1)
    counts = duty_counts(plan)
    assert sum(counts.values()) == sum(rps.values())            # 72 room duties, standby not added


def test_standby_always_has_spare_duty():
    teachers, rps = make()
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=1)
    counts = duty_counts(plan)
    for s, people in plan["standby"].items():
        for t in people:
            assert counts.get(t, 0) <= CAP - 1


def test_activated_standby_counts_as_exactly_one():
    teachers, rps = make()
    plan = allocate(teachers, rps, cap=CAP, standby_per_session=1)
    before = duty_counts(plan)
    absent = plan["rooms"]["S0", 0]
    cover = plan["standby"]["S0"][0]
    new, log = replace_absent(plan, teachers, absent, sessions={"S0"}, cap=CAP)
    after = duty_counts(new)
    assert log[0]["replacement"] == cover
    assert after.get(cover, 0) == before.get(cover, 0) + 1
    assert after[absent] == before[absent] - 1
    assert max(after.values()) <= CAP
