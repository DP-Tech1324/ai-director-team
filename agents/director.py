from agents.base import BaseAgent
import json

class DirectorAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            # Always output JSON with subtasks
            user_goal = messages[-1]["content"] if messages else ""
            subtasks = [
                {"agent": "Planner", "task": "Break the project into subtasks."},
                {"agent": "Researcher", "task": "Find the best way to accomplish the main goal."},
                {"agent": "Coder", "task": "Write the required code."},
                {"agent": "Designer", "task": "Suggest the UI layout."},
                {"agent": "Scribe", "task": "Document how to run the app."},
                {"agent": "QA", "task": "Review and approve final output."}
            ]
            return json.dumps({"goal": user_goal, "subtasks": subtasks}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

director = DirectorAgent(
    name="Director",
    system_message="You are the Director Agent. Always respond with a JSON object containing the goal and a list of subtasks, each with an agent and a task."
).get_agent()