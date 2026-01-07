# core/contracts.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, cast
import json
import re


OutputType = Literal["code", "markdown", "json", "text"]
Lang = Literal["python", "html", "json", "md", "text"]


def _as_dict(x: Any) -> Dict[str, Any]:
    if isinstance(x, dict):
        return x
    return {}


def _coerce_type(value: Any) -> OutputType:
    v = str(value or "").lower().strip()

    if v in ("code", "python", "py", "html", "javascript", "js"):
        return "code"
    if v in ("markdown", "md"):
        return "markdown"
    if v in ("json",):
        return "json"
    return "text"


def _coerce_lang(value: Any) -> Lang:
    v = str(value or "").lower().strip()

    if v in ("py", "python"):
        return "python"
    if v in ("html", "htm"):
        return "html"
    if v in ("json",):
        return "json"
    if v in ("md", "markdown"):
        return "md"
    return "text"


def _extract_json_obj(s: str) -> Optional[Dict[str, Any]]:
    """
    Tries to find and parse the first JSON object in a string.
    Returns dict or None.
    """
    if not s:
        return None

    s = s.strip()

    # If the whole thing is JSON
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass

    # Try to extract first {...} block
    m = re.search(r"(\{[\s\S]*\})", s)
    if not m:
        return None

    try:
        obj = json.loads(m.group(1))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


@dataclass
class AgentOutput:
    agent: str
    type: OutputType = "text"
    title: str = ""
    language: Lang = "text"
    content: str = ""
    save_as: str = ""
    runnable: bool = False
    previewable: bool = False
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "type": self.type,
            "title": self.title,
            "language": self.language,
            "content": self.content,
            "save_as": self.save_as,
            "runnable": self.runnable,
            "previewable": self.previewable,
            "meta": self.meta,
        }


def normalize_output(agent: str, reply: Any, title: str, default_save_as: str) -> AgentOutput:
    """
    Accepts anything (dict / string / None) and returns a consistent AgentOutput object.
    This prevents agents from breaking the UI and fixes Pylance type complaints.
    """

    # None -> empty text output
    if reply is None:
        return AgentOutput(
            agent=agent,
            type="text",
            title=title,
            language="text",
            content="",
            save_as=default_save_as,
            runnable=False,
            previewable=False,
            meta={},
        )

    # If reply is already dict-like and follows schema
    if isinstance(reply, dict):
        t = _coerce_type(reply.get("type"))
        lang = _coerce_lang(reply.get("language"))

        return AgentOutput(
            agent=str(reply.get("agent") or agent),
            type=cast(OutputType, t),
            title=str(reply.get("title") or title),
            language=cast(Lang, lang),
            content=str(reply.get("content") or ""),
            save_as=str(reply.get("save_as") or default_save_as),
            runnable=bool(reply.get("runnable") or False),
            previewable=bool(reply.get("previewable") or False),
            meta=_as_dict(reply.get("meta")),
        )

    # If it’s a string, try to parse JSON schema first
    s = str(reply)
    maybe = _extract_json_obj(s)
    if maybe and ("content" in maybe or "type" in maybe):
        # treat as schema object
        return normalize_output(agent, maybe, title, default_save_as)

    # Otherwise treat as plain text; attempt to detect code fences
    lower = s.lower()
    is_code = "```" in s
    is_html = "<html" in lower or "<!doctype html" in lower
    inferred_type: OutputType = "code" if is_code else ("code" if is_html else "text")
    inferred_lang: Lang = "html" if is_html else ("text")

    return AgentOutput(
        agent=agent,
        type=inferred_type,
        title=title,
        language=inferred_lang,
        content=s,
        save_as=default_save_as,
        runnable=(inferred_lang == "python"),
        previewable=(inferred_lang in ("html",)),
        meta={},
    )
