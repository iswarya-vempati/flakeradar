from dataclasses import dataclass
from typing import Optional


@dataclass
class CaseResult:
    classname: str
    name: str
    outcome: str
    duration: float
    message: Optional[str] = None

    @property
    def test_id(self) -> str:
        return f"{self.classname}::{self.name}"