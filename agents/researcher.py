from autogen import AssistantAgent
from config import CONFIG

researcher = AssistantAgent(
    name="Researcher",
    system_message="You are the Researcher. Search or simulate finding insights, trends, and supporting information for a task. Return summaries, examples, or data.",
    llm_config=CONFIG["llm_config"]
)
