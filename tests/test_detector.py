from app.db import connect, init_db
from app.detector import analyze, analyze_all
from app.models import CaseResult
from app.repository import add_results, add_run


def make_conn():
    conn = connect(":memory:")
    init_db(conn)
    return conn


def row(outcome, commit="a1", python="3.9", os_name="Windows"):
    return {
        "outcome": outcome,
        "commit_sha": commit,
        "python_version": python,
        "os": os_name,
    }


def test_same_conditions_different_results_is_flaky():
    rows = [row("passed"), row("failed"), row("passed"), row("passed"), row("failed")]
    finding = analyze("tests.test_a::test_x", rows)
    assert finding.verdict == "flaky"
    assert finding.inconsistent_groups == 1
    assert finding.failures == 2


def test_different_environments_are_not_counted_as_same_conditions():
    rows = [
        row("passed", python="3.9"),
        row("passed", python="3.9"),
        row("passed", python="3.9"),
        row("failed", python="3.10"),
        row("failed", python="3.10"),
    ]
    finding = analyze("tests.test_a::test_x", rows)
    assert finding.inconsistent_groups == 0
    assert finding.verdict != "flaky"


def test_all_passes_is_stable():
    finding = analyze("tests.test_a::test_x", [row("passed")] * 6)
    assert finding.verdict == "stable"


def test_all_failures_is_always_failing():
    finding = analyze("tests.test_a::test_x", [row("failed")] * 6)
    assert finding.verdict == "always_failing"


def test_fixed_by_a_later_commit_is_changed_once():
    rows = [row("failed", commit="a1")] + [row("passed", commit="b2")] * 5
    finding = analyze("tests.test_a::test_x", rows)
    assert finding.verdict == "changed_once"
    assert finding.transitions == 1


def test_alternating_across_commits_is_suspicious():
    rows = [
        row("passed", commit="a1"),
        row("failed", commit="b2"),
        row("passed", commit="c3"),
        row("failed", commit="d4"),
        row("passed", commit="e5"),
    ]
    finding = analyze("tests.test_a::test_x", rows)
    assert finding.verdict == "suspicious"
    assert finding.transitions == 4


def test_few_runs_is_not_enough_data():
    finding = analyze("tests.test_a::test_x", [row("passed"), row("passed")])
    assert finding.verdict == "not_enough_data"


def test_skipped_runs_are_ignored():
    rows = [row("passed")] * 3 + [row("skipped")] * 2
    finding = analyze("tests.test_a::test_x", rows)
    assert finding.runs == 3
    assert finding.verdict == "not_enough_data"


def test_errors_count_as_failures():
    finding = analyze("tests.test_a::test_x", [row("error")] * 5)
    assert finding.verdict == "always_failing"


def test_analyze_all_ranks_flaky_first():
    conn = make_conn()
    flaky_outcomes = ["passed", "failed", "passed", "failed", "passed"]
    for outcome in flaky_outcomes:
        run_id = add_run(conn, commit_sha="a1")
        add_results(
            conn,
            run_id,
            [
                CaseResult("tests.test_a", "test_stable", "passed", 0.01),
                CaseResult("tests.test_a", "test_flaky", outcome, 0.01),
            ],
        )
    findings = analyze_all(conn)
    assert [f.verdict for f in findings] == ["flaky", "stable"]
    assert findings[0].test_id == "tests.test_a::test_flaky"