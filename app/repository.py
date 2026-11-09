import sqlite3
from typing import Optional

from app.models import CaseResult

def add_run(
    conn: sqlite3.Connection,
    commit_sha: str,
    python_version: Optional[str] = None,
    os_name: Optional[str] = None,
    attempt: int = 1,
) -> int:
    cursor = conn.execute(
        "INSERT INTO runs (commit_sha, python_version, os, attempt) "
        "VALUES (?, ?, ?, ?)",
        (commit_sha, python_version, os_name, attempt),  
    )
    conn.commit()
    return cursor.lastrowid


def add_results(
        conn: sqlite3.Connection, run_id: int, results: list[CaseResult]
) -> None:
    rows = [
        (
            run_id,
            r.test_id,
            r.classname,
            r.name,
            r.outcome,
            r.duration,
            r.message,
        )
        for r in results
    ]
    conn.executemany(
        "INSERT INTO results "
        "(run_id, test_id, classname, name, outcome, duration, message) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()