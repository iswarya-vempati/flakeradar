import os
from dataclasses import asdict
from typing import Optional
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.db import connect, init_db
from app.repository import get_history
from app.detector import VERDICT_ORDER, analyze, analyze_all
from app.schemas import FindingDetail, FindingOut
from app.report import format_report

app = FastAPI(title="FlakeRadar")


def get_conn():
    path = os.environ.get("FLAKERADAR_DB", "flakeradar.db")
    if not Path(path).exists():
        raise HTTPException(status_code=503, detail=f"Database file not found: {path}")
    conn = connect(path)
    try:
        init_db(conn)
        yield conn
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tests", response_model=list[FindingOut])
def list_tests(
    verdict: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    conn=Depends(get_conn),
):
    if verdict is not None and verdict not in VERDICT_ORDER:
        raise HTTPException(status_code=422, detail=f"Unknown verdict: {verdict}")
    findings = analyze_all(conn)
    if verdict is not None:
        findings = [f for f in findings if f.verdict == verdict]
    return [asdict(f) for f in findings[:limit]]


@app.get("/tests/{test_id:path}", response_model=FindingDetail)
def get_test(test_id: str, conn=Depends(get_conn)):
    rows = get_history(conn, test_id)
    if not rows:
        raise HTTPException(status_code=404, detail=f"No results for test: {test_id}")
    finding = analyze(test_id, rows)
    history = [dict(row) for row in rows]
    return {**asdict(finding), "history": history}


@app.get("/report", response_class=PlainTextResponse)
def report(
    top: int = Query(10, ge=1, le=500),
    show_all: bool = False,
    conn=Depends(get_conn),
):
    return format_report(analyze_all(conn), top=top, show_all=show_all)