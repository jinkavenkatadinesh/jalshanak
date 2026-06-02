from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

db_url = settings.DATABASE_URL

# Safeguard against empty or None environment variable injection
if not db_url or not db_url.strip():
    db_url = "sqlite:///./jalrakshak.db"

# Auto-correct deprecated Heroku/Render DB URL prefixes
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Adjust engine params if using SQLite (which is our standard local fallback)
if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# DB Dependency for routing injections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
