from autogen import AssistantAgent
from config import CONFIG
from tools import save_file

scribe = AssistantAgent(
    name="Scribe",
    system_message="You are a technical writer. Document the project clearly. Use tools to save files like README.md.",
    llm_config=CONFIG["llm_config"],
    tools={
        "save_file": save_file
    }
)