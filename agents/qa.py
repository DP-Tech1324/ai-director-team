from autogen import AssistantAgent
from config import CONFIG

qa = AssistantAgent(
    name="QA",
    system_message="You are the QA Engineer. Your job is to review outputs, catch errors, suggest improvements, and ensure quality before delivery.",
    llm_config=CONFIG["llm_config"]
)
