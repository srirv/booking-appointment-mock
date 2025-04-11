#!/bin/bash
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | awk NF | xargs)
fi

# Check if DB_PASSWORD is set
if [ -z "$DB_PASSWORD" ]; then
  echo "Error: DB_PASSWORD environment variable is not set."
  echo "Please set it in your .env file or export it directly."
  exit 1
fi

# Run the migration script
echo "Running database migrations..."
python -m migrations.migrate_datetime_to_date_time

# Check if the migration was successful
if [ $? -eq 0 ]; then
  echo "Migrations completed successfully!"
else
  echo "Migration failed. Please check the logs for details."
  exit 1
fi

# Start the application based on the environment
if [ "$DEBUG" = "True" ]; then
  echo "Starting application in development mode..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  echo "Starting application in production mode..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi 