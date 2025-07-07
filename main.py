from autogen import GroupChat, GroupChatManager
from agents.director import director
from agents.planner import planner
from agents.coder import coder
from agents.researcher import researcher
from agents.scribe import scribe
from agents.designer import designer
from agents.qa import qa

def run_ai_company():
    print("🎯 Welcome to your AI-Powered Company")
    goal = input("🗣 What would you like the team to accomplish?\n> ")

    agents = [director, planner, coder, researcher, scribe, designer, qa]

    groupchat = GroupChat(
        agents=agents,
        messages=[],
        max_round=10
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=director.llm_config,
        system_message="You are a GroupChatManager that routes messages to the right agents. Log all agent messages for debugging."
    )

    # 👇 Print everything that happens
    def log_messages(message):
        print("🗨️ Chat log:")
        for m in message:
            print(f"{m.sender.name} ➜ {m.content[:500]}\n{'-'*60}")

    # 👇 Hook into message events (basic logging)
    groupchat._post_process_message = log_messages

    # 👇 Start the session
    director.initiate_chat(recipient=manager, message=goal)

if __name__ == "__main__":
    run_ai_company()
