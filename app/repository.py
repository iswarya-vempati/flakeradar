import sqlite3
from typing import Optional

from app.models import CaseResult


def add_run(
    conn: sqlite3.Connection,
    commit_sha: str,
    python_version: Optional[str] = None,
    os_name: Optional[str] = None,
    attempt: int = 1,
    report_hash: Optional[str] = None,
) -> int:
    cursor = conn.execute(
        "INSERT INTO runs (commit_sha, python_version, os, attempt, report_hash) "
        "VALUES (?, ?, ?, ?, ?)",
        (commit_sha, python_version, os_name, attempt, report_hash),  
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

def get_history(conn: sqlite3.Connection, test_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT results.outcome, results.duration,
               runs.commit_sha, runs.created_at
        FROM results
        JOIN runs ON runs.id = results.run_id
        WHERE results.test_id = ?
        ORDER BY runs.id
        """,
        (test_id,),
    ).fetchall()


def run_exists(conn: sqlite3.Connection, report_hash: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM runs WHERE report_hash = ?", (report_hash,)
    ).fetchone()
    return row is not None