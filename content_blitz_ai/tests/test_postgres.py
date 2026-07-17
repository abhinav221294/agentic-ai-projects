from sqlalchemy import text

from src.memory.database import engine

with engine.connect() as conn:

    result = conn.execute(
        text("SELECT version();")
    )

    print(result.scalar())