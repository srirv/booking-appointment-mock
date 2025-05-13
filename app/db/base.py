from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv
import certifi

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
logger.info("Connecting to database")
logger.debug(f"Database URL: {DATABASE_URL.split('@')[0].split(':')[0]}:***@{DATABASE_URL.split('@')[1]}")

# Create engine with SSL configuration
try:
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
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.debug("Session factory created")

Base = declarative_base()

def get_db():
    logger.debug("Getting database session")
    db = SessionLocal()
    try:
        logger.debug("Database session obtained")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        logger.debug("Closing database session")
        db.close() 