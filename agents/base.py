from autogen import AssistantAgent
from config import CONFIG
from typing import Optional

class BaseAgent:
    def __init__(self, name: str, system_message: str, tools: Optional[dict] = None):
        self.name = name
        self.system_message = system_message
        kwargs = {
            "name": name,
            "system_message": system_message,
            "llm_config": CONFIG["llm_config"]
        }
        # 'tools' argument removed for compatibility with current autogen version

        self.agent = AssistantAgent(**kwargs)

    def get_agent(self):
        return self.agent

    def __repr__(self):
        return f"<BaseAgent name={self.name}>"