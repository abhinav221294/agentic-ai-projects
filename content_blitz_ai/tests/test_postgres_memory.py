from src.memory.postgres_memory import PostgresMemory

memory = PostgresMemory()

user = memory.get_or_create_user("demo_user")
print("User:", user)
print("User ID:", user.id)

conversation = memory.create_conversation(
    user.id,
    "Redis Blog"
)

print("Conversation:", conversation)

if conversation is None:
    raise Exception("Conversation is None!")

print("Conversation ID:", conversation.id)

message = memory.save_message(
    conversation.id,
    "user",
    "Write a Redis blog"
)

print("Message:", message.id)

history = memory.get_messages(conversation.id)

for msg in history:
    print(f"{msg.role}: {msg.content}")

history = memory.get_messages(conversation.id)

print("\nConversation History")
print("---------------------")

for msg in history:
    print(f"{msg.role}: {msg.content}")

memory.close()