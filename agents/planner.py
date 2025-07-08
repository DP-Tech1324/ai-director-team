from agents.base import BaseAgent

planner = BaseAgent(
    name="Planner",
    system_message="You are the Planner. Given a goal, break it into specific steps."
).get_agent()