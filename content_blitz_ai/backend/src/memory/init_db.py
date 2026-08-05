from sqlalchemy import text

from src.memory.database import Base, engine
from src.memory.models import User, Conversation, Message, Memory


def init_database():

    # Enable pgvector extension
    with engine.begin() as conn:
        conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Tables created successfully!")


if __name__ == "__main__":
    init_database()