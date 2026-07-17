from src.memory.database import Base, engine

# Import all models so SQLAlchemy registers them
from src.memory.models import User, Conversation, Message, Memory


def init_database():
    Base.metadata.create_all(bind=engine)