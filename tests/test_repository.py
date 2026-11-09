import sqlite3

import pytest

from app.db import connect, init_db
from app.models import CaseResult
from app.repository import add_results, add_run


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