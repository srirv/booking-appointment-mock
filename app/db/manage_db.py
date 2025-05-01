import os
import psycopg2
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a database connection with SSL configuration"""
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        sslmode='require',
        sslcert=None,
        sslkey=None,
        sslrootcert=certifi.where()
    )

def init_db():
    """Initialize the database with tables and functions"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Read and execute the init.sql script
        with open(os.path.join(os.path.dirname(__file__), 'init.sql'), 'r') as f:
            cur.execute(f.read())
        conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def clean_db():
    """Clean up the database by dropping all objects"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Read and execute the clean.sql script
        with open(os.path.join(os.path.dirname(__file__), 'clean.sql'), 'r') as f:
            cur.execute(f.read())
        conn.commit()
        print("Database cleaned successfully!")
    except Exception as e:
        print(f"Error cleaning database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def reset_db():
    """Reset the database by cleaning and reinitializing"""
    clean_db()
    init_db()
    print("Database reset completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [init|clean|reset]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        init_db()
    elif command == "clean":
        clean_db()
    elif command == "reset":
        reset_db()
    else:
        print("Invalid command. Use 'init', 'clean', or 'reset'")
        sys.exit(1) 