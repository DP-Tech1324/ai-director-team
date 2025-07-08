from agents.base import BaseAgent
from tools import run_python_code, save_file

coder = BaseAgent(
    name="Coder",
    system_message="You are a Python developer. Write clean, working code. Use tools to run or save code if needed.",
    tools={
        "run_python_code": run_python_code,
        "save_file": save_file
    }
).get_agent()