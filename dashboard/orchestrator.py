import asyncio
import json

from agents.director import director
from agents.planner import planner
from agents.coder import coder
from agents.researcher import researcher
from agents.scribe import scribe
from agents.designer import designer
from agents.qa import qa

AGENT_MAP = {
    "Director": director,
    "Planner": planner,
    "Coder": coder,
    "Researcher": researcher,
    "Designer": designer,
    "Scribe": scribe,
    "QA": qa,
}

async def run_agent(agent, message: str):
    # Autogen agents are sync by default; run in thread to keep asyncio clean
    def _call():
        return agent.generate_reply([{"role": "user", "content": message}])
    reply = await asyncio.to_thread(_call)
    return agent.name, reply

async def run_agents(goal: str):
    logs = {}

    # 1) Director creates subtasks (JSON)
    director_reply = director.generate_reply([{"role": "user", "content": goal}])
    logs["Director"] = director_reply

    # 2) Parse JSON safely
    try:
        payload = json.loads(director_reply)
        subtasks = payload.get("subtasks", [])
    except Exception as e:
        logs["System"] = f"❌ Director output not valid JSON. Error: {e}\nOutput:\n{director_reply}"
        return logs

    # 3) Dispatch tasks (in parallel)
    tasks = []
    for s in subtasks:
        agent_name = (s.get("agent") or "").strip()
        task_msg = (s.get("task") or "").strip()
        agent = AGENT_MAP.get(agent_name)
        if not agent:
            logs[f"System:{agent_name}"] = f"⚠️ Unknown agent in subtasks: {agent_name}"
            continue
        tasks.append(run_agent(agent, task_msg))

    if tasks:
        results = await asyncio.gather(*tasks)
        for name, reply in results:
            logs[name] = reply
    else:
        logs["System"] = "⚠️ No subtasks dispatched."

    return logs
