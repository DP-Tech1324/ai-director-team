import asyncio
from dashboard.orchestrator import run_agents

goal = "Build an AI dashboard with a login page and testing."

logs = asyncio.run(run_agents(goal))

for agent_name, response in logs.items():
    print(f"--- {agent_name} ---\n{response}\n")
