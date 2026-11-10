import hashlib
import sqlite3
from pathlib import Path
from typing import Optional

from app.parser import parse_junit_xml
from app.repository import add_results, add_run, run_exists


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ingest_report(
        conn: sqlite3.Connection,
        path: Path,
        commit_sha: str,
        python_version: Optional[str] = None,
        os_name: Optional[str] = None,
        attempt: int = 1,
) -> Optional[int]:
    report_hash = file_hash(path)
    if run_exists(conn, report_hash):
        return None
    results = parse_junit_xml(str(path))
    run_id = add_run(
        conn,
        commit_sha=commit_sha,
        python_version=python_version,
        os_name=os_name,
        attempt=attempt,
        report_hash=report_hash,
    )
    add_results(conn, run_id, results)
    return run_id