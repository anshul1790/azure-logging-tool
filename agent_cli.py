# agent_cli.py
from src.agent.azure_logging_agent import AzureHubLoggingAgent
def main():
    agent = AzureHubLoggingAgent(thread_id="cli-session")

    print("🤖 GitHub Agent Ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        response = agent.chat(user_input)
        print("Bot:", response)

if __name__ == "__main__":
    main()