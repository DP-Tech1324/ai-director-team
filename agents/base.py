from autogen import AssistantAgent
from config import CONFIG

class BaseAgent:
    def __init__(self, name: str, system_message: str):
        self.name = name
        self.system_message = system_message
        self.agent = AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config=CONFIG["llm_config"]
        )

    def get_agent(self):
        return self.agent