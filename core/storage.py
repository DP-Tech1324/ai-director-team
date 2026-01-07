# core/storage.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any

from core.run_context import slugify


def ensure_dirs(project: str, run_id: str) -> Dict[str, Path]:
    project_slug = slugify(project)
    base = Path("projects") / project_slug
    runs = base / "runs" / run_id
    memory = base / "memory"
    versions = base / "versions"
    generated = Path("generated") / run_id

    for p in [runs, memory, versions, generated]:
        p.mkdir(parents=True, exist_ok=True)

    return {
        "project_base": base,
        "runs": runs,
        "memory": memory,
        "versions": versions,
        "generated": generated,
    }


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8")


def save_run_context(dirs: Dict[str, Path], run_context: Dict[str, Any]) -> None:
    write_json(dirs["runs"] / "run_context.json", run_context)


def save_agent_output(dirs: Dict[str, Path], agent_output: Dict[str, Any]) -> Path:
    filename = agent_output.get("save_as", "output.txt")
    content = agent_output.get("content", "")
    out_path = dirs["runs"] / filename
    write_text(out_path, content)
    return out_path
