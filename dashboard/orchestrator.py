import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autogen import GroupChat, GroupChatManager
from agents.director import director
from agents.planner import planner
from agents.coder import coder
from agents.researcher import researcher
from agents.scribe import scribe
from agents.designer import designer
from agents.qa import qa

def run_agents(goal):
    agents = [director, planner, coder, researcher, scribe, designer, qa]

    groupchat = GroupChat(
        agents=agents,
        messages=[],
        max_round=8
    )

    manager = GroupChatManager(groupchat=groupchat, llm_config=director.llm_config)
    logs = {}

    def capture(msgs):
        for m in msgs:
            logs.setdefault(m.sender.name, []).append(m.content)

    groupchat._post_process_message = capture
    director.initiate_chat(recipient=manager, message=goal)

    return logs