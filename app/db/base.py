from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with SSL configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "sslcert": None,
        "sslkey": None,
        "sslrootcert": certifi.where()
    },
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Maximum number of connections in the pool
    max_overflow=10      # Maximum number of connections that can be created beyond pool_size
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 