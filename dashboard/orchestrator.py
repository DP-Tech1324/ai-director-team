import asyncio
from agents.director import director
from agents.planner import planner
from agents.coder import coder
from agents.researcher import researcher
from agents.scribe import scribe
from agents.designer import designer
from agents.qa import qa

# List of all agents except the Director
agents = [planner, coder, researcher, scribe, designer, qa]

async def run_agent(agent, message):
    # Await if generate_reply is async, else just call it
    if asyncio.iscoroutinefunction(agent.generate_reply):
        reply = await agent.generate_reply([{"role": "user", "content": message}])
    else:
        reply = agent.generate_reply([{"role": "user", "content": message}])
    return agent.name, reply

__all__ = ["run_agents"]

async def run_agents(goal):
    logs = {}

    # Step 1: Ask Director for subtasks
    if asyncio.iscoroutinefunction(director.generate_reply):
        director_reply = await director.generate_reply([{"role": "user", "content": goal}])
    else:
        director_reply = director.generate_reply([{"role": "user", "content": goal}])

    logs["Director"] = director_reply

    # Step 2: Extract subtasks by matching agent names in Director's reply
    director_reply_str = str(director_reply) if director_reply is not None else ""

    subtasks = []
    for line in director_reply_str.split("\n"):
        if any(agent.name in line for agent in agents):
            subtasks.append(line.strip())

    # Step 3: Assign subtasks to agents
    tasks = []
    for line in subtasks:
        for agent in agents:
            if agent.name in line:
                # Extract the instruction after ':' or ',' or fallback to whole line
                if ":" in line:
                    task_msg = line.split(":", 1)[1].strip()
                elif "," in line:
                    task_msg = line.split(",", 1)[1].strip()
                else:
                    task_msg = line.strip()
                tasks.append(run_agent(agent, task_msg))

    # Step 4: Run all agent tasks in parallel
    if tasks:
        results = await asyncio.gather(*tasks)
        for name, reply in results:
            logs[name] = reply
    else:
        logs["System"] = "⚠️ No subtasks were assigned. Check the Director's output format."

    return logs
