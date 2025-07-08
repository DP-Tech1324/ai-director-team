from agents.base import BaseAgent

coder = BaseAgent(
    name="Coder",
    system_message="You are the Coder. Write efficient, clean code based on the subtask you are given. Use best practices and proper structure."
).get_agent()