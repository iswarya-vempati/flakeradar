from app.db import connect, init_db


def test_init_db_creates_tables():
    conn = connect(":memory:")
    init_db(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    names = {row["name"] for row in rows}
    assert {"runs", "results"} <= names