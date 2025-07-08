from agents.base import BaseAgent

qa = BaseAgent(
    name="QA",
    system_message="You are the QA Engineer. Your job is to review outputs, catch errors, suggest improvements, and ensure quality before delivery."
).get_agent()