from agents.base import BaseAgent
import json

class ResearcherAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            last = messages[-1]["content"] if messages else ""
            # Simulate research
            return json.dumps({"insight": f"Research completed for: {last}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

researcher = ResearcherAgent(
    name="Researcher",
    system_message="You are the Researcher. Search or simulate finding insights, trends, and supporting information for a task. Return summaries, examples, or data."
).get_agent()