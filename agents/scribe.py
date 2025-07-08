from agents.base import BaseAgent
from tools import save_file
import json
import datetime

class ScribeAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            last = messages[-1]["content"] if messages else ""
            # Log to markdown file in logs/
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"logs/scribe_log_{now}.md"
            content = f"# Scribe Log\n\n## Message\n{last}\n"
            save_file(filename, content)
            return f"📝 Scribe log saved to {filename}"
        except Exception as e:
            return f"❌ Error: {e}"

scribe = ScribeAgent(
    name="Scribe",
    system_message="You are a technical writer. Document the project clearly. Auto-log agent actions in markdown files under logs/. Use tools to save files like README.md."
).get_agent()