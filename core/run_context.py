# core/run_context.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
import re
from typing import List, Literal, Dict, Any


Status = Literal["running", "completed", "failed"]
Mode = Literal["team", "fast"]


def slugify(name: str) -> str:
    name = (name or "").strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name or "default"


def new_run_id(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


@dataclass
class RunContext:
    run_id: str
    project: str
    goal: str
    mode: Mode
    model: str
    agents: List[str]
    start_time: str
    status: Status = "running"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
