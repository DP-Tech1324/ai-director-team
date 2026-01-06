import datetime
from agents.base import BaseAgent
from tools import save_file

class ScribeAgent(BaseAgent):
    def generate_reply(self, messages):
        task = messages[-1]["content"] if messages else ""
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"memory/scribe_log_{now}.md"
        content = f"""# Scribe Summary

## Task
{task}

## Runbook
1. Run: `python main.py`
2. Or run UI: `streamlit run dashboard/app.py`
3. Outputs are saved in `memory/`

"""
        save_result = save_file(filename, content)
        return f"📝 {save_result}"

scribe = ScribeAgent(
    name="Scribe",
    system_message="You are Scribe. Save concise summaries to memory/."
)
