from src.memory.database import Base, engine
from src.memory.models import User, Conversation, Message, Memory

def init_database():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_database()