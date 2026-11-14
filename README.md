# Smart Exam Seating and Invigilation Planner

Automated, rule-based exam planning using constraint optimization (Google OR-Tools CP-SAT).

## Quick start
    python -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python scripts/generate_data.py
    python scripts/run_demo.py
    python -m pytest -q backend/tests

## Structure
- backend/solver/   seating logic (baseline + CP-SAT)
- backend/tests/    unit tests
- scripts/          data generator and demo runner
- data/sample/      synthetic CSV files
- docs/             requirements, diagrams, progress log
