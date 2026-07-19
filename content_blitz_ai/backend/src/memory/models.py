from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
    Boolean
)


from enum import Enum

from pgvector.sqlalchemy import Vector

from sqlalchemy.orm import relationship

from src.memory.database import Base

class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PREFERENCE = "preference"


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    memories = relationship(
        "Memory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    is_active = Column(Boolean, default=True)

    is_admin = Column(Boolean, default=False)


class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
    DateTime,
    server_default=func.now()
    )

    updated_at = Column(
    DateTime,
    server_default=func.now(),
    onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )



class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    conversation_id = Column(
    Integer,
    ForeignKey("conversations.id"),
    nullable=False,
    index=True
    )

    conversation = relationship(
    "Conversation"
    )



class Memory(Base):

    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=False)

    memory_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    importance = Column(
        Integer,
        default=1,
        index=True,
    )

    embedding = Column(
        Vector(3072),   # replace with your actual embedding dimension
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user = relationship(
        "User",
        back_populates="memories",
    )

    conversation = relationship("Conversation")