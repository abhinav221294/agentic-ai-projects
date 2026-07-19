from src.memory.redis_memory import (
    append_message,
    get_messages
)

from src.memory.postgres_memory import PostgresMemory

class MemoryManager:

    def __init__(self):
        self.postgres = PostgresMemory()

    def save_message(
       self,
       conversation_id: str,
       role: str,
       content: str,     
    ) -> None:
        
        append_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

    def get_short_term(
            self,
            conversation_id:str
    ):
        return get_messages(conversation_id=conversation_id)
    

    def save_persistent_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ):

        return self.postgres.save_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

    def get_persistent_history(
        self,
        conversation_id: int,
    ):

        return self.postgres.get_messages(
            conversation_id=conversation_id
        )


    def save_memory(
    self,
    user_id: int,
    conversation_id: int,
    content: str,
    memory_type: str,
    importance: int = 1,
    ):
        return self.postgres.save_memory(
        user_id=user_id,
        conversation_id=conversation_id,
        content=content,
        memory_type=memory_type,
        importance=importance,
        )

    def semantic_search(
    self,
    user_id: int,
    query: str,
    top_k: int = 5,
    memory_type: str | None = None,
    ):
        return self.postgres.semantic_search(
        user_id=user_id,
        query=query,
        top_k=top_k,
        memory_type=memory_type,
        )

    def get_memories(
    self,
    user_id: int,
    memory_type: str | None = None,
    ):
        return self.postgres.get_memories(
        user_id=user_id,
        memory_type=memory_type,
        )

    def update_memory_importance(
    self,
    memory_id: int,
    importance: int | None = None,
    increment: int = 0,
    ):
        return self.postgres.update_memory_importance(
        memory_id=memory_id,
        importance=importance,
        increment=increment,
        )

memory_manager = MemoryManager()