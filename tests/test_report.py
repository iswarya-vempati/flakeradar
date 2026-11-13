from app.db import connect, init_db
from app.detector import Finding, analyze_all
from app.models import CaseResult
from app.report import format_report
from app.repository import add_results, add_run


def make_finding(test_id, verdict, failures=2, runs=5, transitions=3):
    return Finding(
        test_id=test_id,
        runs=runs,
        failures=failures,
        transitions=transitions,
        inconsistent_groups=1 if verdict == "flaky" else 0,
        verdict=verdict,
        evidence=f"evidence for {test_id}",
    )


def test_default_report_hides_stable_tests():
    findings = [
        make_finding("t::flaky_one", "flaky"),
        make_finding("t::stable_one", "stable", failures=0, transitions=0),
    ]
    text = format_report(findings)
    assert "t::flaky_one" in text
    assert "t::stable_one" not in text


def test_show_all_includes_stable_tests():
    findings = [
        make_finding("t::flaky_one", "flaky"),
        make_finding("t::stable_one", "stable", failures=0, transitions=0),
    ]
    text = format_report(findings, show_all=True)
    assert "t::stable_one" in text


def test_top_limits_how_many_tests_are_shown():
    findings = [
        make_finding("t::flaky_a", "flaky"),
        make_finding("t::flaky_b", "flaky"),
        make_finding("t::flaky_c", "flaky"),
    ]
    text = format_report(findings, top=2)
    assert "t::flaky_a" in text
    assert "t::flaky_c" not in text
    assert "and 1 more" in text


def test_empty_database_gives_a_clear_message():
    assert "No test results" in format_report([])


def test_report_shows_numbers_and_evidence():
    findings = [
        make_finding("t::flaky_one", "flaky"),
        make_finding("t::stable_one", "stable", failures=0, transition=0),
    ]
    text = format_report(findings)
    assert "Tests analyzed: 2" in text
    assert "Failed 2 of 5 runs" in text
    assert "evidence for t::flaky_one" in text


def test_report_from_a_real_database():
    conn = connect(":memory:")
    init_db(conn)
    for outcome in ["passed", "failed", "passed", "failed", "passed"]:
        run_id = add_run(conn, commit_sha="a1")
        case = CaseResult("tests.test_a","test_x", outcome, 0.01)
        add_results(conn, run_id, [case])
    text = format_report(analyze_all(conn))
    assert "[FLAKY] tests.test_a::test_x" in text