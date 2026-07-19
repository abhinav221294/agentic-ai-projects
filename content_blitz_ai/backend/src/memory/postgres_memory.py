from src.memory.database import SessionLocal
from src.memory.models import (
    User,
    Conversation,
    Message,
    Memory,
)

import logging

from typing import TypeVar
from sqlalchemy.orm import Session

from src.core.config import MIN_IMPORTANCE, MAX_IMPORTANCE

#from pgvector.sqlalchemy import cosine_distance

from src.embeddings.embedding_service import EmbeddingService

T = TypeVar("T")
logger = logging.getLogger(__name__)

class PostgresMemory:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    @staticmethod
    def _commit(db) -> None:
        """
        Commit the current transaction.
        Roll back automatically if anything fails.
        """
        try:
            db.commit()

        except Exception:
            db.rollback()
            logger.exception("Database transaction failed")
            raise

    classmethod
    def _persist(
        cls,
        db: Session,
        obj: T,
        ) -> T:
        """
        Save a SQLAlchemy model and return the refreshed object.
        """
        db.add(obj)

        cls._commit(db)

        db.refresh(obj)

        return obj

    def get_or_create_user(
    self,
    username: str,
    email: str,
    password: str,
    ) -> User:

        user = self.get_user(username)

        if user:
            return user

        with SessionLocal() as db:

            user = User(
            username=username,
            email=email,
            password=password,
            )

            return self._persist(db, user)

    def create_conversation(
        self,
        user_id: int,
        title: str,
    ) -> Conversation:

        with SessionLocal() as db:

            conversation = Conversation(
                user_id=user_id,
                title=title,
            )

            return self._persist(db, conversation)

    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> Message:

        with SessionLocal() as db:

            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
            )

            return self._persist(db, message)

    def get_messages(
        self,
        conversation_id: int,
    ) -> list[Message]:

        with SessionLocal() as db:

            return (
                db.query(Message)
                .filter(
                    Message.conversation_id == conversation_id
                )
                .order_by(Message.created_at.asc())
                .all()
            )
        
    def get_user(
    self,
    username: str,
    ) -> User | None:

        with SessionLocal() as db:

            return (
            db.query(User)
            .filter(User.username == username)
            .first()
            )
        
    def get_conversation(
        self,
        conversation_id: int,
    ) -> Conversation | None:

        with SessionLocal() as db:
            return db.get(Conversation, conversation_id)
        
    
    def get_user_by_id(
        self,
        user_id: int,
    ) -> User | None:

        with SessionLocal() as db:
            return db.get(User, user_id)
        

    
    def delete_conversation(
    self,
    conversation_id: int,
    ) -> bool:

        with SessionLocal() as db:

            conversation = db.get(
            Conversation,
            conversation_id
            )

            if conversation is None:
                return False

            db.delete(conversation)

            self._commit(db)

            return True
        
    
    def delete_message(
        self,
        message_id: int,
        ) -> bool:

        with SessionLocal() as db:

            message = db.get(
            Message,
            message_id
            )

            if message is None:
                return False

            db.delete(message)

            self._commit(db)

            return True
        
        
    def get_memories(
    self,
    user_id: int,
    memory_type: str | None = None,
    ) -> list[Memory]:

        with SessionLocal() as db:

            query = (
            db.query(Memory)
            .filter(
                Memory.user_id == user_id
            )
            )   

            if memory_type:

                query = query.filter(
                Memory.memory_type == memory_type
                )

            return (
                query.order_by(
                Memory.importance.desc(),
                Memory.created_at.desc()
                )
                .all()
            )
        

    def delete_user(
        self,
        user_id: int,
        ) -> bool:

        with SessionLocal() as db:

            user = db.get(User, user_id)

            if user is None:
                return False

            db.delete(user)

            self._commit(db)

            return True
        

    def update_memory_importance(
        self,
        memory_id: int,
        importance: int | None = None,
        increment: int = 0,
    ) -> Memory | None:
        """
        Update the importance score of a memory.

        Parameters
        ----------
        memory_id : int
        Memory ID.

        importance : int | None
            Explicit importance value.
            If provided, overrides the current value.

        increment : int
            Amount to increase/decrease the current importance.
            Ignored if importance is provided.

        Returns
        -------
        Memory | None
        """

        with SessionLocal() as db:

            memory = db.get(Memory, memory_id)

            if memory is None:
                return None

            if importance is not None:
                memory.importance = importance
            else:
                memory.importance += increment

                # Never allow negative importance
                memory.importance = max(
                MIN_IMPORTANCE,
                min(MAX_IMPORTANCE, memory.importance)
                )

            self._commit(db)

            db.refresh(memory)

            return memory
        

    def save_memory(
    self,
    user_id: int,
    conversation_id: int,
    content: str,
    memory_type: str,
    importance: int = 1,
    ) -> Memory:

        embedding = self.embedding_service.embed(content)

        with SessionLocal() as db:

            memory = Memory(
            user_id=user_id,
            conversation_id=conversation_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            embedding=embedding,
            )

            return self._persist(db, memory)


    def search_memories(
    self,
    user_id: int,
    query_embedding: list[float],
    top_k: int = 5,
    memory_type: str | None = None,
    ) -> list[Memory]:

        with SessionLocal() as db:

            query = (
            db.query(Memory)
            .filter(Memory.user_id == user_id)
            )

            if memory_type:
                query = query.filter(
                Memory.memory_type == memory_type
                )

            return (
            query.order_by(
                Memory.embedding.cosine_distance(query_embedding)
                )
                .limit(top_k)
                .all()
                )   
    

    def semantic_search(
    self,
    user_id: int,
    query: str,
    top_k: int = 5,
    memory_type: str | None = None,
    ):

        embedding = self.embedding_service.embed(query)

        return self.search_memories(
        user_id=user_id,
        query_embedding=embedding,
        top_k=top_k,
        memory_type=memory_type,
        )

    def delete_memory(
    self,
    memory_id: int,
    ) -> bool:

        with SessionLocal() as db:

            memory = db.get(Memory, memory_id)

            if memory is None:
                return False

            db.delete(memory)

            self._commit(db)

            return True
    
    def delete_memories_by_conversation(
    self,
    conversation_id: int,
    ) -> int:

        with SessionLocal() as db:

            deleted = (
            db.query(Memory)
            .filter(
                Memory.conversation_id == conversation_id
                )
                .delete()
            )

            self._commit(db)

            return deleted