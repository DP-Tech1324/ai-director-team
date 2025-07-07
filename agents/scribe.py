from autogen import AssistantAgent
from config import CONFIG

scribe = AssistantAgent(
    name="Scribe",
    system_message="You are the Scribe. Turn task results into well-written documentation, blog posts, summaries, or copywriting.",
    llm_config=CONFIG["llm_config"]
)
