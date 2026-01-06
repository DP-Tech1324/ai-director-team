import json
from agents.base import BaseAgent

class ResearcherAgent(BaseAgent):
    def generate_reply(self, messages):
        task = messages[-1]["content"] if messages else ""

        if "login" in task.lower() and "streamlit" in task.lower():
            tips = [
                "Use st.session_state to remember login state across reruns",
                "Never hardcode real passwords in production; use hashed passwords + secrets",
                "Add rate limiting / lockouts if exposed publicly",
                "Prefer OAuth/Supabase/Auth0 for real apps"
            ]
        else:
            tips = [
                "Keep scope small; build MVP first",
                "Avoid premature optimization; measure before tuning",
                "Write clear docstrings and a short README/runbook",
                "Add basic error handling and input validation"
            ]

        return json.dumps({"task": task, "tips": tips}, indent=2)

researcher = ResearcherAgent(
    name="Researcher",
    system_message="You are Researcher. Return ONLY research tips as JSON."
)
