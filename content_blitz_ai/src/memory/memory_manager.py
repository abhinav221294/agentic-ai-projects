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

    

memory_manager = MemoryManager()