from typing import Optional

from pydantic import BaseModel


class FindingOut(BaseModel):
    test_id: str
    runs: int
    failures: int
    transitions: int
    inconsistent_groups: int
    verdict: str
    evidence: str


class HistoryItem(BaseModel):
    outcome: str
    duration: float
    commit_sha: str
    python_version: Optional[str] = None
    os: Optional[str] = None
    created_at: str


class FindingDetail(FindingOut):
    history: list[HistoryItem]