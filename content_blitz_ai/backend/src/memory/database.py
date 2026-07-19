from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_DB

import os
from dotenv import load_dotenv

load_dotenv()



DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"localhost:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



Base = declarative_base()


