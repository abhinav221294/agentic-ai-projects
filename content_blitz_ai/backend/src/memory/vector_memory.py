from typing import List

class VectorMemory:

    def add_memory(
        self,
        user_id: int,
        conversation_id: int,
        content: str,
        memory_type: str,
        importance: int = 1,
    ) -> None:
        """Create an embedding and store a new memory."""
        ...

    def search(
        self,
        user_id: int,
        query: str,
        top_k: int = 5,
    ) -> List:
        """Return the most similar memories."""
        ...

    def delete(
        self,
        memory_id: int,
    ) -> None:
        """Delete a single memory."""
        ...

    def delete_conversation(
        self,
        conversation_id: int,
    ) -> None:
        """Delete all memories for a conversation."""
        ...