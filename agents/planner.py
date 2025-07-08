from agents.base import BaseAgent
import json

class PlannerAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            # Expect JSON input from Director
            last = messages[-1]["content"] if messages else ""
            data = json.loads(last) if last.strip().startswith("{") else {"goal": last}
            goal = data.get("goal", "")
            steps = [
                "Clarify requirements",
                "Design solution",
                "Implement code",
                "Test and review",
                "Document process"
            ]
            return json.dumps({"goal": goal, "steps": steps}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

planner = PlannerAgent(
    name="Planner",
    system_message="You are the Planner. Given a JSON goal, break it into specific steps and return as JSON."
).get_agent()