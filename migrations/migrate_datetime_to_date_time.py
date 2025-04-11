from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Date, Time
from sqlalchemy.sql import select, func
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a MetaData instance
metadata = MetaData()

# Define the existing appointments table with the dateTime column
appointments_table = Table(
    "appointments",
    metadata,
    Column("appointmentId", String, primary_key=True),
    Column("patientId", String),
    Column("name", String),
    Column("dateTime", DateTime),
    Column("department", String),
    Column("doctorName", String),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)

def migrate():
    # Connect to the database
    connection = engine.connect()
    transaction = connection.begin()

    try:
        # Check if the table exists and if date/time columns already exist
        inspector = engine.dialect.has_table(connection, "appointments")
        if not inspector:
            print("Appointments table does not exist. Nothing to migrate.")
            return
        
        # Add date and time columns if they don't exist
        if not engine.dialect.has_column(connection, "appointments", "date"):
            connection.execute('ALTER TABLE appointments ADD COLUMN "date" DATE')
        
        if not engine.dialect.has_column(connection, "appointments", "time"):
            connection.execute('ALTER TABLE appointments ADD COLUMN "time" TIME')
        
        # Get all appointments with dateTime
        query = select([appointments_table.c.appointmentId, appointments_table.c.dateTime])
        result = connection.execute(query)
        
        # Update each appointment's date and time fields
        for row in result:
            appointment_id = row[0]
            date_time = row[1]
            
            if date_time:
                date_value = date_time.date()
                time_value = date_time.time()
                
                # Update the appointment with separate date and time
                connection.execute(
                    appointments_table.update()
                    .where(appointments_table.c.appointmentId == appointment_id)
                    .values(date=date_value, time=time_value)
                )
        
        # Drop the dateTime column if it exists
        if engine.dialect.has_column(connection, "appointments", "dateTime"):
            connection.execute('ALTER TABLE appointments DROP COLUMN "dateTime"')
            
        transaction.commit()
        print("Migration completed successfully")
    
    except Exception as e:
        transaction.rollback()
        print(f"Error during migration: {e}")
    
    finally:
        connection.close()

if __name__ == "__main__":
    migrate() 