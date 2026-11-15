import os
from dataclasses import asdict
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query

from app.db import connect, init_db
from app.detector import VERDICT_ORDER, analyze_all
from app.schemas import FindingOut

app = FastAPI(title="FlakeRadar")


def get_conn():
    path = os.environ.get("FLAKERADR_DB", "flakeradar.db")
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