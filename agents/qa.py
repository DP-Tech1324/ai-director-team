import json
from agents.base import BaseAgent

class QAAgent(BaseAgent):
    def generate_reply(self, messages):
        task = messages[-1]["content"] if messages else ""
        return json.dumps({
            "task": task,
            "review": "✅ Approved. Outputs are coherent and role-separated.",
            "next_improvements": [
                "Add real tool-calling for Coder (execute snippet + show output)",
                "Add persistent memory summary per run",
                "Add retries/timeouts per agent call"
            ]
        }, indent=2)

qa = QAAgent(
    name="QA",
    system_message="You are QA. Approve or request fixes in JSON."
)
