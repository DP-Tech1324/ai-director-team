# dashboard/orchestrator.py
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

from agents.director import director
from agents.planner import planner
from agents.coder import coder
from agents.researcher import researcher
from agents.scribe import scribe
from agents.designer import designer
from agents.qa import qa

from core.run_context import RunContext, new_run_id
from core.contracts import normalize_output
from core.storage import ensure_dirs, save_run_context, save_agent_output


AGENTS = {
    "Planner": planner,
    "Researcher": researcher,
    "Coder": coder,
    "Designer": designer,
    "Scribe": scribe,
    "QA": qa,
}

ORDER = ["Director", "Planner", "Researcher", "Coder", "Designer", "Scribe", "QA", "System"]


# ----------------------------
# Intent Router (CRITICAL)
# ----------------------------
def _needs_code(goal: str) -> bool:
    g = (goal or "").lower()
    keywords = [
        "code", "script", "python", "streamlit", "html", "css", "javascript", "js",
        "react", "api", "bug", "error", "fix", "build", "implement", "template"
    ]
    return any(k in g for k in keywords)


def _needs_ui(goal: str) -> bool:
    g = (goal or "").lower()
    keywords = ["ui", "ux", "design", "layout", "page", "screen", "dashboard", "frontend"]
    return any(k in g for k in keywords)


def _is_simple_factual(goal: str) -> bool:
    g = (goal or "").strip().lower()
    if not g:
        return True

    # short/simple
    if len(g.split()) <= 6 and not _needs_code(g) and not _needs_ui(g):
        return True

    factual_triggers = [
        "days of week", "day of week",
        "capital of", "meaning of", "define", "definition",
        "what is", "who is", "list of", "tell me"
    ]
    return any(t in g for t in factual_triggers) and not _needs_code(g)


def build_subtasks(goal: str, mode: str) -> List[Dict[str, str]]:
    """
    Returns list of {"agent": "...", "task": "..."}.
    Ensures we do not run pointless agents for simple questions.
    """
    g = goal or ""

    # Fast mode: coder only
    if "fast" in (mode or "").lower():
        return [{"agent": "Coder", "task": g}]

    # Simple factual: answer directly, no code unless requested
    if _is_simple_factual(g):
        return [
            {"agent": "Planner", "task": f"Answer the user directly and clearly: {g}"},
            {"agent": "Researcher", "task": f"Add 2–4 helpful facts/examples ONLY if relevant: {g}"},
            {"agent": "Scribe", "task": f"Write the FINAL answer for the user. Put the direct answer first. Goal: {g}"},
            {"agent": "QA", "task": f"Check the final answer is correct and not generic. If wrong, correct it. Goal: {g}"},
        ]

    # Normal mode: structured + tips
    subtasks: List[Dict[str, str]] = [
        {"agent": "Planner", "task": f"Create a structured answer or plan for: {g}"},
        {"agent": "Researcher", "task": f"Add best practices, pitfalls, and tips for: {g}"},
    ]

    if _needs_code(g):
        subtasks.append({"agent": "Coder", "task": f"Provide working code/templates for: {g}. Return code where possible."})

    if _needs_ui(g):
        subtasks.append({"agent": "Designer", "task": f"Suggest UI/UX layout and components for: {g}."})

    subtasks.append({"agent": "Scribe", "task": f"Write the FINAL answer for the user. Put the answer first, then details. Goal: {g}"})
    subtasks.append({"agent": "QA", "task": f"Review outputs and final draft for: {g}. Correct mistakes and tighten."})
    return subtasks


# ----------------------------
# Helpers: Director parsing (optional)
# ----------------------------
def _extract_json_obj(s: str) -> Optional[Dict[str, Any]]:
    if not s:
        return None
    s = s.strip()

    # full JSON
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass

    # first {...}
    m = re.search(r"(\{[\s\S]*\})", s)
    if not m:
        return None
    try:
        obj = json.loads(m.group(1))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _extract_director_payload(director_reply: Any) -> Optional[Dict[str, Any]]:
    """
    If Director returns:
    {"goal": "...", "subtasks":[{"agent":"Planner","task":"..."}, ...]}
    we use it. Otherwise None.
    """
    if isinstance(director_reply, dict) and isinstance(director_reply.get("subtasks"), list):
        return director_reply

    if isinstance(director_reply, str):
        obj = _extract_json_obj(director_reply)
        if obj and isinstance(obj.get("subtasks"), list):
            return obj

    return None


async def _run_agent(agent_obj: Any, message: str) -> Tuple[str, Any]:
    if asyncio.iscoroutinefunction(agent_obj.generate_reply):
        reply = await agent_obj.generate_reply([{"role": "user", "content": message}])
    else:
        reply = agent_obj.generate_reply([{"role": "user", "content": message}])
    return agent_obj.name, reply


# ----------------------------
# Main Orchestrator
# ----------------------------
async def run_agents(
    goal: str,
    project: str = "general",
    mode: str = "Team Mode",
    model: str = "phi3:latest",
):
    """
    Returns: (ctx_dict, dirs_dict, logs_dict)
    logs_dict: {agent_name: normalized_output_dict, ...}
    """

    # 1) RunContext + dirs
    rid = new_run_id()
    ctx = RunContext(
        run_id=rid,
        project=project,
        goal=goal,
        mode=("fast" if "fast" in (mode or "").lower() else "team"),
        model=model,
        agents=["Director", "Planner", "Researcher", "Coder", "Designer", "Scribe", "QA"],
        start_time=datetime.now().isoformat(timespec="seconds"),
        status="running",
    )

    dirs = ensure_dirs(project=project, run_id=rid)
    save_run_context(dirs, ctx.to_dict())

    logs: Dict[str, Dict[str, Any]] = {}

    # 2) Director (kept for visibility, but NOT trusted blindly)
    try:
        director_reply = director.generate_reply([{"role": "user", "content": goal}])
    except Exception as e:
        director_reply = {"error": f"Director failed: {e}"}

    director_out = normalize_output("Director", director_reply, "Director Output", "director.json")
    save_agent_output(dirs, director_out.to_dict())
    logs["Director"] = director_out.to_dict()

    # 3) Decide subtasks
    director_payload = _extract_director_payload(director_reply)

    # If Director payload looks valid AND matches expected schema, we can use it.
    # BUT: We still protect against dumb subtasks by falling back when needed.
    subtasks: List[Dict[str, str]]
    if director_payload and isinstance(director_payload.get("subtasks"), list):
        # validate subtasks shape
        cleaned: List[Dict[str, str]] = []
        for stask in director_payload["subtasks"]:
            if not isinstance(stask, dict):
                continue
            a = str(stask.get("agent") or "").strip()
            t = str(stask.get("task") or "").strip()
            if a in AGENTS and t:
                cleaned.append({"agent": a, "task": t})
        # if director gave nonsense, fallback
        subtasks = cleaned if cleaned else build_subtasks(goal, mode)
    else:
        subtasks = build_subtasks(goal, mode)

    # 4) Run core agents (except Scribe/QA) in parallel
    core_names = [s["agent"] for s in subtasks if s["agent"] in ["Planner", "Researcher", "Coder", "Designer"]]
    core_names = list(dict.fromkeys(core_names))  # unique, preserve order

    tasks = []
    for agent_name in core_names:
        agent_obj = AGENTS[agent_name]
        # find the task text for that agent from subtasks
        msg = next((s["task"] for s in subtasks if s["agent"] == agent_name), goal)
        tasks.append(_run_agent(agent_obj, msg))

    results = await asyncio.gather(*tasks) if tasks else []

    for name, reply in results:
        default_file = {
            "Planner": "planner.json",
            "Researcher": "researcher.json",
            "Designer": "designer.json",
            "Coder": "coder_output.py",
        }.get(name, f"{name.lower()}.txt")

        out = normalize_output(name, reply, f"{name} Output", default_file)
        save_agent_output(dirs, out.to_dict())
        logs[name] = out.to_dict()

    # 5) Run Scribe AFTER core outputs (Scribe is deterministic in your file)
    scribe_input = f"GOAL:\n{goal}\n\nOUTPUTS:\n"
    for k in ["Planner", "Researcher", "Coder", "Designer"]:
        if k in logs:
            scribe_input += f"\n## {k}\n{logs[k].get('content','')}\n"

    scribe_reply = scribe.generate_reply([{"role": "user", "content": scribe_input}])
    scribe_out = normalize_output("Scribe", scribe_reply, "Final Summary", "scribe.md")
    save_agent_output(dirs, scribe_out.to_dict())
    logs["Scribe"] = scribe_out.to_dict()

    # 6) Run QA LAST (review scribe + everything)
    qa_input = f"GOAL:\n{goal}\n\nFINAL DRAFT:\n{logs['Scribe'].get('content','')}\n\nTEAM OUTPUTS:\n"
    for k in ["Planner", "Researcher", "Coder", "Designer"]:
        if k in logs:
            qa_input += f"\n## {k}\n{logs[k].get('content','')}\n"

    qa_reply = qa.generate_reply([{"role": "user", "content": qa_input}])
    qa_out = normalize_output("QA", qa_reply, "QA Review", "qa.json")
    save_agent_output(dirs, qa_out.to_dict())
    logs["QA"] = qa_out.to_dict()

    # 7) Mark complete
    ctx.status = "completed"
    save_run_context(dirs, ctx.to_dict())

    # Keep ordered logs for UI (optional)
    ordered_logs: Dict[str, Dict[str, Any]] = {}
    for k in ORDER:
        if k in logs:
            ordered_logs[k] = logs[k]
    for k, v in logs.items():
        if k not in ordered_logs:
            ordered_logs[k] = v

    return ctx.to_dict(), dirs, ordered_logs
