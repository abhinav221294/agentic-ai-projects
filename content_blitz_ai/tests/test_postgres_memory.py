from backend.src.memory.postgres_memory import PostgresMemory


def test_postgres_memory():
    memory = PostgresMemory()

    user = memory.get_or_create_user(
        username="demo_user",
        email="demo_user@example.com",
        password="test_password",
    )

    assert user.id is not None

    conversation = memory.create_conversation(
        user.id,
        "Redis Blog"
    )

    assert conversation.id is not None

    message = memory.save_message(
        conversation.id,
        "user",
        "Write a Redis blog"
    )

    assert message.id is not None

    saved_memory = memory.save_memory(
        user_id=user.id,
        conversation_id=conversation.id,
        content="The user wants to write a Redis blog.",
        memory_type="preference",
    )

    assert saved_memory.id is not None

    results = memory.semantic_search(
        user_id=user.id,
        query="What does the user want to write?",
    )

    assert len(results) > 0
    assert "Redis" in results[0].content