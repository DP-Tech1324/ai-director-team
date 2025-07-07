from autogen import AssistantAgent
from config import CONFIG

designer = AssistantAgent(
    name="Designer",
    system_message="You are the Designer. Generate UI/UX ideas, layout suggestions, visual themes, or design components. Return wireframes in text or code.",
    llm_config=CONFIG["llm_config"]
)
