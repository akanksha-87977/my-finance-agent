from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# NOTE: In some environments psycopg2 binary DLLs aren't available.
# If the postgres URL can't be used, fall back to a local SQLite DB so
# the API can run end-to-end for development.
is_serverless = bool(os.getenv("VERCEL") or os.getenv("NOW_REGION") or os.path.exists("/var/task"))

if is_serverless:
    DATABASE_URL = "sqlite:////tmp/financial_ai_dev.sqlite3"
else:
    DATABASE_URL = settings.DATABASE_URL

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    # Force dialect import early.
    if DATABASE_URL.startswith("postgres"):
        conn = engine.connect()
        conn.close()
except Exception:
    database_path = "/tmp/financial_ai_dev.sqlite3" if is_serverless else "./financial_ai_dev.sqlite3"
    DATABASE_URL = f"sqlite:///{database_path}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
_database_initialized = False



def get_db():
    """Dependency for getting DB session"""
    global _database_initialized
    if not _database_initialized:
        init_db()
        _database_initialized = True
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)