from agents.base import BaseAgent

scribe = BaseAgent(
    name="Scribe",
    system_message="You are the Scribe. Turn task results into well-written documentation, blog posts, summaries, or copywriting."
).get_agent()