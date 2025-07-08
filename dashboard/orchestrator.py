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

# Run a single agent with a given message
async def run_agent(agent, message):
    return agent.name, agent.generate_reply([{"role": "user", "content": message}])

# Main function to coordinate the AI team
async def run_agents(goal):
    logs = {}

    # Step 1: Ask the Director to break down the goal
    director_reply = director.generate_reply([{"role": "user", "content": goal}])
    logs["Director"] = director_reply

    # Step 2: Parse subtasks by matching agent names in the Director's reply
    director_reply_str = str(director_reply) if director_reply is not None else ""
    subtasks = [line for line in director_reply_str.split("\n") if any(agent.name in line for agent in agents)]

    # Step 3: Assign subtasks to agents
    tasks = []
    for line in subtasks:
        for agent in agents:
            if agent.name in line:
                # Extract the instruction after a colon or comma
                if ":" in line:
                    task_msg = line.split(":", 1)[-1].strip()
                elif "," in line:
                    task_msg = line.split(",", 1)[-1].strip()
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