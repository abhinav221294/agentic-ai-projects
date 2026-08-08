from src.workflows.state_management import AgentState


def build_prompt_context(state: AgentState) -> str:

    sections = []

    conversation_history = state.get("conversation_history", [])

    if conversation_history:

        history = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in conversation_history
        )

        print("\n========== PROMPT CONTEXT ==========")
        print("Conversation messages:", len(conversation_history))
        print("Conversation characters:", len(history))
        print("====================================")

        sections.append(
            f"Conversation History:\n{history}"
        )

    retrieved_memories = state.get(
        "retrieved_memories",
        []
    )

    if retrieved_memories:

        memory = "\n".join(
            m.content for m in retrieved_memories
        )

        print("\n========== MEMORY CONTEXT ==========")
        print("Retrieved memories:", len(retrieved_memories))
        print("Memory characters:", len(memory))
        print("====================================")

        sections.append(
            f"Relevant User Memories:\n{memory}"
        )

    context = "\n\n".join(sections)

    print("\n========== TOTAL PROMPT CONTEXT ==========")
    print("Total context characters:", len(context))
    print("==========================================\n")

    return context