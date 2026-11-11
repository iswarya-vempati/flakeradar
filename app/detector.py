import sqlite3
from dataclasses import dataclass

from app.repository import get_history, list_test_ids

MIN_RUNS = 5
FAIL_OUTCOMES = {"failed", "error"}
VERDICT_ORDER = {
    "flaky": 0,
    "suspicious": 1,
    "changed_once": 2,
    "always_failing": 3,
    "not_enough_data": 4,
    "stable": 5,
}


@dataclass
class Finding:
    test_id: str
    runs: int
    failures: int
    transitions: int
    inconsistent_groups: int
    verdict: str
    evidence: str


def analyze(test_id: str, rows: list) -> Finding:
    executed = [row for row in rows if row["outcome"] != "skipped"]
    failed_flags = [row["outcome"] in FAIL_OUTCOMES for row in executed]
    runs = len(executed)
    failures = sum(failed_flags)
    transitions = sum(
        1 for before, after in zip(failed_flags, failed_flags[1:]) if before != after
    )

    seen_by_conditions = {}
    for row, failed in zip(executed, failed_flags):
        conditions = (row["commit_sha"], row["python_version"], row["os"])
        seen_by_conditions.setdefault(conditions, set()).add(failed)
    inconsistent = sum(1 for seen in seen_by_conditions.values() if len(seen) == 2)

    if inconsistent > 0:
        verdict = "flaky"
        evidence = (
            "Passed and failed under identical conditions" 
            f"(same commit, Python version and OS) in {inconsistent} group(s)."
        )
    elif runs < MIN_RUNS:
        verdict = "not_enough_data"
        evidence = f"Only {runs} run(s) so far. At least {MIN_RUNS} are needed."
    elif failures == 0:
        verdict = "stable"
        evidence = f"Passed in a;; {runs} runs."
    elif failures == runs:
        verdict = "always_failing"
        evidence = f"Failed in all {runs} runs, so it looks broken, not flaky."
    elif transitions >= 2:
        verdict = "suspicious"
        evidence = (
            f"Result changed {transitions} times in {runs} runs, but never under "
            "identical conditions. This could be real bugs coming and going."
        )
    else:
        verdict = "changed_once"
        evidence = "Result changed once, which looks like a real fix or a real break."

    return Finding(
        test_id=test_id,
        runs=runs,
        failures=failures,
        transitions=transitions,
        inconsistent_froups=inconsistent,
        verdict=verdict,
        evidence=evidence,
    )