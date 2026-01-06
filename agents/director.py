import json
from agents.base import BaseAgent

class DirectorAgent(BaseAgent):
    def generate_reply(self, messages):
        user_goal = messages[-1]["content"] if messages else ""
        subtasks = [
            {"agent": "Planner", "task": f"Create a tight 3–5 step plan for: {user_goal}"},
            {"agent": "Researcher", "task": f"Provide key tips/best practices for: {user_goal}"},
            {"agent": "Coder", "task": f"Create a simple working template or snippet for: {user_goal}"},
            {"agent": "Designer", "task": f"Suggest UI/UX layout ideas for: {user_goal}"},
            {"agent": "Scribe", "task": f"Write concise runbook/summary for: {user_goal}"},
            {"agent": "QA", "task": f"Review outputs for: {user_goal} and approve or request fixes."},
        ]
        return json.dumps({"goal": user_goal, "subtasks": subtasks}, indent=2)

director = DirectorAgent(
    name="Director",
    system_message="You are the Director. Output ONLY valid JSON with keys: goal, subtasks[]."
)
