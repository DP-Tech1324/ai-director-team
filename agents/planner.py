import json
from agents.base import BaseAgent

class PlannerAgent(BaseAgent):
    def generate_reply(self, messages):
        task = messages[-1]["content"] if messages else ""

        # Simple task-aware template (still deterministic)
        if "login" in task.lower() and "streamlit" in task.lower():
            steps = [
                "Create UI: username + password inputs and a Login button",
                "Validate: check credentials (hardcoded for now) and show success/error",
                "Persist session: store logged_in in st.session_state and show protected page",
                "Add logout + basic security notes (never store plain passwords)"
            ]
        else:
            steps = [
                "Clarify requirements and expected output",
                "Draft a minimal plan (3–6 steps)",
                "Implement the simplest working version",
                "Test edge cases and refine",
                "Document how to run it"
            ]

        return json.dumps({"task": task, "steps": steps}, indent=2)

planner = PlannerAgent(
    name="Planner",
    system_message="You are Planner. Return ONLY planning steps as JSON."
)
