from agents.base import BaseAgent
from tools import run_python_code, save_file
import json

class CoderAgent(BaseAgent):
    def generate_reply(self, messages):
        try:
            last = messages[-1]["content"] if messages else ""
            data = json.loads(last) if last.strip().startswith("{") else {"task": last}
            # Simulate code generation
            code = f"# Code for: {data.get('task', '')}\nprint('Hello from Coder!')"
            return code
        except Exception as e:
            return f"❌ Error: {e}"

coder = CoderAgent(
    name="Coder",
    system_message="You are a Python developer. Write clean, working code. Use tools to run or save code if needed."
).get_agent()