"""Invigilator allocation with a per-teacher duty cap and emergency (standby) cover.

Rules
- Every room in every session gets exactly one invigilator.
- A teacher holds at most one role (room or standby) per session.
- A teacher never exceeds `cap` duties in total (default 5).
- Each session also has `standby_per_session` standby (emergency) teachers.
  An unused standby slot counts as 0 duties; once activated it counts as exactly 1.
- Anyone named as standby is planned with at least 1 spare duty below the cap, so
  activating them can never push them over it.
- Room duties are spread as evenly as possible.
"""
import math
from ortools.sat.python import cp_model


def feasibility(teachers, rooms_per_session, cap=5, standby_per_session=1):
    """Check the arithmetic before solving. teachers: list of dicts with 'id'.
    Standby slots are not counted as duties, but they need spare capacity to be useful."""
    needed = sum(rooms_per_session.values())
    capacity = cap * len(teachers)
    headroom = capacity - needed
    return {
        "duties_needed": needed,
        "capacity": capacity,
        "min_teachers": math.ceil(needed / cap),
        "emergency_headroom": headroom,
        "ok": needed <= capacity,
        "standby_possible": headroom >= (standby_per_session > 0),
    }


def allocate(teachers, rooms_per_session, cap=5, standby_per_session=1, time_limit=20):
    """teachers: [{'id': 'T01', 'unavailable': {session,...}}].
    rooms_per_session: {session: number_of_rooms}.
    Returns {'rooms': {(session, room): teacher}, 'standby': {session: [teacher,...]}} or None."""
    ids = [t["id"] for t in teachers]
    unavail = {t["id"]: set(t.get("unavailable", ())) for t in teachers}
    sessions = list(rooms_per_session)
    m = cp_model.CpModel()

    y = {}  # y[t, s, r] : teacher t invigilates room r in session s
    z = {}  # z[t, s, k] : teacher t is standby slot k in session s
    for t in ids:
        for s in sessions:
            for r in range(rooms_per_session[s]):
                y[t, s, r] = m.NewBoolVar(f"y_{t}_{s}_{r}")
            for k in range(standby_per_session):
                z[t, s, k] = m.NewBoolVar(f"z_{t}_{s}_{k}")

    for s in sessions:
        for r in range(rooms_per_session[s]):
            m.AddExactlyOne(y[t, s, r] for t in ids)
        for k in range(standby_per_session):
            m.AddExactlyOne(z[t, s, k] for t in ids)
        for t in ids:
            roles = [y[t, s, r] for r in range(rooms_per_session[s])]
            roles += [z[t, s, k] for k in range(standby_per_session)]
            m.Add(sum(roles) <= 1)
            if s in unavail[t]:
                for v in roles:
                    m.Add(v == 0)

    room_total = {t: sum(y[t, s, r] for s in sessions for r in range(rooms_per_session[s])) for t in ids}
    is_standby = {t: m.NewBoolVar(f"sb_{t}") for t in ids}   # 1 if t is standby in any session
    for t in ids:
        for s in sessions:
            for k in range(standby_per_session):
                m.Add(z[t, s, k] <= is_standby[t])
        m.Add(room_total[t] + is_standby[t] <= cap)           # standby people keep 1 spare duty

    hi = m.NewIntVar(0, cap, "hi")
    lo = m.NewIntVar(0, cap, "lo")
    for t in ids:
        m.Add(room_total[t] <= hi)
        m.Add(room_total[t] >= lo)
    m.Minimize(hi - lo)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 4
    status = solver.Solve(m)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    rooms = {}
    standby = {s: [] for s in sessions}
    for s in sessions:
        for r in range(rooms_per_session[s]):
            rooms[s, r] = next(t for t in ids if solver.Value(y[t, s, r]))
        for k in range(standby_per_session):
            standby[s].append(next(t for t in ids if solver.Value(z[t, s, k])))
    return {"rooms": rooms, "standby": standby}


def duty_counts(plan, activated=()):
    """Actual duties per teacher = room duties + standby slots that were activated."""
    counts = {}
    for t in plan["rooms"].values():
        counts[t] = counts.get(t, 0) + 1
    return counts


def replace_absent(plan, teachers, absent, sessions=None, cap=5):
    """Fill the gaps left by an absent teacher. Returns (new_plan, log).

    Order of preference for each empty room:
      1. an unused standby teacher for that session
      2. any free, available teacher with the fewest duties and still under the cap
    If nobody qualifies the room is reported as UNFILLED so the coordinator can act."""
    unavail = {t["id"]: set(t.get("unavailable", ())) for t in teachers}
    rooms = dict(plan["rooms"])
    standby = {s: list(v) for s, v in plan["standby"].items()}
    log = []
    gaps = [(s, r) for (s, r), t in rooms.items() if t == absent and (sessions is None or s in sessions)]
    for (s, r) in sorted(gaps):
        counts = duty_counts({"rooms": rooms})
        counts[absent] = counts.get(absent, 0) - 1          # absent teacher does not serve this duty
        rooms.pop((s, r))
        busy = {t for (ss, _), t in rooms.items() if ss == s}
        chosen, source = None, None
        for t in standby.get(s, []):                          # 1. standby for this session
            if t != absent and t not in busy and counts.get(t, 0) < cap:
                chosen, source = t, "standby"
                standby[s].remove(t)
                break
        if chosen is None:                                    # 2. best available teacher
            standby_now = set(standby.get(s, []))
            pool = [t["id"] for t in teachers
                    if t["id"] != absent and t["id"] not in busy and t["id"] not in standby_now
                    and s not in unavail[t["id"]] and counts.get(t["id"], 0) < cap]
            if pool:
                chosen = min(pool, key=lambda t: (counts.get(t, 0), t))
                source = "reserve pool"
        if chosen is None:
            log.append({"session": s, "room": r, "replacement": None, "source": "UNFILLED"})
        else:
            rooms[s, r] = chosen
            log.append({"session": s, "room": r, "replacement": chosen, "source": source})
    return {"rooms": rooms, "standby": standby}, log
