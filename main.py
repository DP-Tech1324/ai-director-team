import asyncio
from dashboard.orchestrator import run_agents

def run_cli():
    print("🎯 Welcome to AI Director Team (Fast Orchestrator Mode)")
    goal = input("🗣 Goal:\n> ").strip()

    logs = asyncio.run(run_agents(goal))

    print("\n==================== RESULTS ====================")
    for name, reply in logs.items():
        print(f"\n--- {name} ---")
        print(reply)

if __name__ == "__main__":
    run_cli()
