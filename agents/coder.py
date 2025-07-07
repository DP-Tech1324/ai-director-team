from autogen import AssistantAgent
from config import CONFIG

coder = AssistantAgent(
    name="Coder",
    system_message="You are the Coder. Write efficient, clean code based on the subtask you are given. Use best practices and proper structure.",
    llm_config=CONFIG["llm_config"]
)
