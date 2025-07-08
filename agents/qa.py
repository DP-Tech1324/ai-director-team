from agents.base import BaseAgent
import json

class QAAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            last = messages[-1]["content"] if messages else ""
            # Simulate QA review
            if "error" in last.lower():
                return json.dumps({"review": "❌ Issues found. Please fix errors."})
            return json.dumps({"review": "✅ Output looks good!"})
        except Exception as e:
            return json.dumps({"error": str(e)})

qa = QAAgent(
    name="QA",
    system_message="You are the QA Engineer. Your job is to review outputs, catch errors, suggest improvements, and ensure quality before delivery."
).get_agent()