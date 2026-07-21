from src.workflows.state_management import AgentState


def build_prompt_context(state: AgentState) -> str:

    sections = []

    conversation_history = state.get("conversation_history", [])

    if conversation_history:
        history = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in conversation_history
        )

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

        sections.append(
        f"Relevant User Memories:\n{memory}"
        )

    return "\n\n".join(sections)