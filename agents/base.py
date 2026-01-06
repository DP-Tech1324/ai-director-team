from autogen import AssistantAgent
from config import CONFIG

class BaseAgent(AssistantAgent):
    def __init__(self, name: str, system_message: str):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=CONFIG["llm_config"],
        )
