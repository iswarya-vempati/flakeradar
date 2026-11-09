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
    