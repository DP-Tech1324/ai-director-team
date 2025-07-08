from agents.base import BaseAgent

researcher = BaseAgent(
    name="Researcher",
    system_message=(
        "You are the Researcher. Search or simulate finding insights, trends, "
        "and supporting information for a task. Return summaries, examples, or data."
    )
).get_agent()