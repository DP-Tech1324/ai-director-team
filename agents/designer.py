from agents.base import BaseAgent

designer = BaseAgent(
    name="Designer",
    system_message="You are the Designer. Generate UI/UX ideas, layout suggestions, visual themes, or design components. Return wireframes in text or code."
).get_agent()