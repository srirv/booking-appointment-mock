import os
import psycopg2
import certifi
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
log_level = logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a database connection with SSL configuration"""
    db_url = os.getenv("DATABASE_URL")
    logger.info("Establishing database connection")
    logger.debug(f"Database URL: {db_url.split('@')[0].split(':')[0]}:***@{db_url.split('@')[1]}")
    
    try:
        conn = psycopg2.connect(
            db_url,
            sslmode='require',
            sslcert=None,
            sslkey=None,
            sslrootcert=certifi.where()
        )
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def init_db():
    """Initialize the database with tables and functions"""
    logger.info("Starting database initialization")
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Read and execute the init.sql script
        script_path = os.path.join(os.path.dirname(__file__), 'init.sql')
        logger.debug(f"Reading init script from {script_path}")
        with open(script_path, 'r') as f:
            sql_script = f.read()
            logger.debug(f"Executing init script ({len(sql_script.splitlines())} lines)")
            cur.execute(sql_script)
        conn.commit()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
        logger.debug("Database connection closed")

def clean_db():
    """Clean up the database by dropping all objects"""
    logger.info("Starting database cleanup")
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Read and execute the clean.sql script
        script_path = os.path.join(os.path.dirname(__file__), 'clean.sql')
        logger.debug(f"Reading cleanup script from {script_path}")
        with open(script_path, 'r') as f:
            sql_script = f.read()
            logger.debug(f"Executing cleanup script ({len(sql_script.splitlines())} lines)")
            cur.execute(sql_script)
        conn.commit()
        logger.info("Database cleaned successfully!")
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
        logger.debug("Database connection closed")

def reset_db():
    """Reset the database by cleaning and reinitializing"""
    logger.info("Starting database reset")
    clean_db()
    init_db()
    logger.info("Database reset completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        logger.error("Missing command argument")
        print("Usage: python manage_db.py [init|clean|reset]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    logger.info(f"Executing command: {command}")
    
    try:
        if command == "init":
            init_db()
        elif command == "clean":
            clean_db()
        elif command == "reset":
            reset_db()
        else:
            logger.error(f"Invalid command: {command}")
            print("Invalid command. Use 'init', 'clean', or 'reset'")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Command failed with error: {str(e)}")
        sys.exit(1) 