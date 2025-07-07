from autogen import AssistantAgent
from config import CONFIG

planner = AssistantAgent(
    name="Planner",
    system_message="You are the Planner. Given a goal, break it into specific steps.",
    llm_config=CONFIG["llm_config"]
)