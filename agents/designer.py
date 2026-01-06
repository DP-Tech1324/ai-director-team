import json
from agents.base import BaseAgent

class DesignerAgent(BaseAgent):
    def generate_reply(self, messages):
        task = messages[-1]["content"] if messages else ""
        ui = {
            "layout": [
                "Header: Project/Goal + run button",
                "Left: Agent status (Director/Planner/etc.)",
                "Center: Conversation feed (role-colored bubbles)",
                "Right: Final Output + Copy button",
                "Bottom: Chat input (single line) + mode selector",
            ],
            "style": ["Dark theme", "Rounded cards", "Readable typography", "Compact spacing"]
        }
        return json.dumps({"task": task, "ui": ui}, indent=2)

designer = DesignerAgent(
    name="Designer",
    system_message="You are Designer. Return UI suggestions as JSON."
)
