import sqlite3

import pytest

from app.db import connect, init_db
from app.models import CaseResult
from app.repository import add_results, add_run, get_history, list_test_ids


def make_conn():
    conn = connect(":memory:")
    init_db(conn)
    return conn


def test_add_run_returns_an_id():
    conn = make_conn()
    run_id = add_run(conn, commit_sha="a1")
    assert run_id == 1


def test_result_needs_an_existing_run():
    conn = make_conn()
    case = CaseResult("tests.test_a", "test_x", "passed", 0.01)
    with pytest.raises(sqlite3.IntegrityError):
        add_results(conn, 999, [case])


def test_results_can_be_read_back_as_history():
    conn = make_conn()
    run_id = add_run(
        conn, commit_sha="a1", python_version="3.9.6", os_name="Windows"
    )
    case = CaseResult("tests.test_a", "test_ok", "passed", 0.01)
    add_results(conn, run_id, [case])
    history = get_history(conn, "tests.test_a::test_ok")
    assert len(history) == 1
    assert history[0]["outcome"] == "passed"
    assert history[0]["commit_sha"] == "a1"
    assert history[0]["python_version"] == "3.9.6"
    assert history[0]["os"] == "Windows"


def test_history_is_in_run_order():
    conn = make_conn()
    first = add_run(conn, commit_sha="a1")
    second = add_run(conn, commit_sha="b2")
    add_results(
        conn, first, [CaseResult("tests.test_a", "test_x", "passed", 0.01)]
    )
    add_results(
        conn,
        second,
        [CaseResult("tests.test_a", "test_x", "failed", 0.01, "boom")],
    )
    rows = get_history(conn, "tests.test_a::test_x")
    assert [row["outcome"] for row in rows] == ["passed", "failed"]


def test_report_hash_must_be_unique():
    conn = make_conn()
    add_run(conn, commit_sha="a1", report_hash="abc")
    with pytest.raises(sqlite3.IntegrityError):
        add_run(conn, commit_sha="a1", report_hash="abc")


def test_list_ids_returns_each_test_once():
    conn = make_conn()
    for _ in range(2):
        run_id = add_run(conn, commit_sha="a1")
        case = CaseResult("tests.test_a", "test_x", "passed", 0.01)
        add_results(conn, run_id, [case])
    assert list_test_ids(conn) == ["tests.test_a::test_x"]