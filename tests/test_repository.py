from app.db import connect, init_db
from app.repository import add_run


def make_conn():
    conn = connect(":memory:")
    init_db(conn)
    return conn

def test_add_run_returns_an_id():
    conn = make_conn()
    run_id = add_run(conn, commit_sha="a1")
    assert run_id == 1