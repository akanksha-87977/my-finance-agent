from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# NOTE: In some environments psycopg2 binary DLLs aren't available.
# If the postgres URL can't be used, fall back to a local SQLite DB so
# the API can run end-to-end for development.
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
    DATABASE_URL = "sqlite:///./financial_ai_dev.sqlite3"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)