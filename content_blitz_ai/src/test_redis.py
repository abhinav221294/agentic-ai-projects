from src.memory.redis_memory import *

append_message(
    "test",
    "user",
    "Hello"
)

append_message(
    "test",
    "assistant",
    "Hi there!"
)

print(get_messages("test"))