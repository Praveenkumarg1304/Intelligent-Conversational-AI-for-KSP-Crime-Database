"""
Database session setup — REPLACE ME once a real PostgreSQL instance exists.

1. Copy .env.example to .env and set DATABASE_URL to your real connection string.
2. Load your team's actual schema against it (see dataset/data_dictionary.md
   for the field reference this project was built from).
3. Uncomment `Depends(get_db)` in routes/search.py and routes/chatbot_rag.py.

Nothing in this file has been tested against a live database — it's the
standard SQLAlchemy pattern, not a verified connection.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ksp_user:changeme@localhost:5432/ksp_crime_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
