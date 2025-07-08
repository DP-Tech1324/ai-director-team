from agents.base import BaseAgent
import json

class DesignerAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            last = messages[-1]["content"] if messages else ""
            # Simulate design suggestion
            return json.dumps({"ui": f"Suggested UI for: {last}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

designer = DesignerAgent(
    name="Designer",
    system_message="You are the Designer. Generate UI/UX ideas, layout suggestions, visual themes, or design components. Return wireframes in text or code."
).get_agent()