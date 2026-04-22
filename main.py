from agent.agent import build_agent, get_initial_state

def main():
    print("\n" + "="*60)
    print("  Welcome to AutoStream AI Assistant 🎬")
    print("  Automated Video Editing for Content Creators")
    print("="*60)
    print("  Type 'quit' or 'exit' to stop the conversation")
    print("="*60 + "\n")

    # Build the agent
    agent = build_agent()

    # Initialize state (this is the agent's memory)
    state = get_initial_state()

    while True:
        # Get user input
        user_input = input("You: ").strip()

        # Exit conditions
        if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
            print("\nAgent: Thanks for chatting! Have a great day! 👋\n")
            break

        if not user_input:
            continue

        # Add user message to state
        state["messages"].append({
            "role": "user",
            "content": user_input
        })

        # Run the agent
        state = agent.invoke(state)

        # Print agent's last response
        last_response = state["messages"][-1]["content"]
        print(f"\nAgent: {last_response}\n")

        # If lead is captured, optionally end
        if state.get("lead_captured"):
            print("="*60)
            print("  Lead successfully saved! Conversation complete.")
            print("="*60 + "\n")
            break


if __name__ == "__main__":
    main()