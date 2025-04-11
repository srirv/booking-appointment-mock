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



# Start the application based on the environment
if [ "$DEBUG" = "True" ]; then
  echo "Starting application in development mode..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  echo "Starting application in production mode..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi 