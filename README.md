# Apollo Hospitals Chennai Appointment Booking API

A FastAPI backend application for booking appointments at Apollo Hospitals Chennai, with a PostgreSQL database.

## Features

- RESTful API for CRUD operations on appointments
- PostgreSQL database integration (Neon DB cloud hosted)
- Containerized for easy deployment
- Cloud-ready
- Automatic deletion of old appointments when a patient books a new one
- Separate date and time fields for better appointment management
- Automated database migrations

## Requirements

- Python 3.9+
- Neon PostgreSQL account
- Docker & Docker Compose (optional)

## Installation and Setup

### Using Docker (Recommended)

1. Clone the repository
2. Copy `.env.template` to `.env` and update the DB_PASSWORD with your Neon DB password:
   ```bash
   cp .env.template .env
   # Edit .env file to add your Neon DB password
   ```
3. Run with Docker Compose for development:
   ```bash
   docker-compose up -d
   ```
   This will automatically:
   - Run database migrations
   - Start the FastAPI application in development mode with hot-reload

4. For production deployment:
   ```bash
   # Set environment variables
   export DB_PASSWORD=your-neon-db-password
   export DOCKER_REGISTRY=your-registry.com
   export TAG=1.0.0

   # Deploy the application
   docker-compose -f docker-compose.prod.yml up -d
   ```
5. Access the API at http://localhost:8000/v1/docs (development) or https://api.apollohospitalschennai.com (production)

### Running with the Start Script

We provide a convenient start script that handles migrations and application startup:

```bash
# Make sure the script is executable
chmod +x scripts/start.sh

# Run the application
./scripts/start.sh
```

### Manual Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.template` to `.env` and update with your Neon DB password
5. Run the database migrations:
   ```bash
   python -m migrations.migrate_datetime_to_date_time
   ```
6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Migrations

The application now uses separate date and time fields instead of a combined dateTime field. Migrations are handled automatically when using Docker or the start script.

If you need to run migrations manually:

```bash
python -m migrations.migrate_datetime_to_date_time
```

See the [migrations README](migrations/README.md) for more details.

## Environment Variables

Create a `.env` file with the following variables:

```
DATABASE_URL=postgresql://neondb_owner:<password>@ep-fancy-lab-a5kqy0m9-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
API_PREFIX=/v1
DEBUG=True
DB_PASSWORD=<your-neon-db-password>
```

## API Documentation

Once the server is running, access the API documentation at:

- Swagger UI: http://localhost:8000/v1/docs
- ReDoc: http://localhost:8000/v1/redoc

## API Data Structure

Appointments now use separate date and time fields:

```json
{
  "appointmentId": "6123456789abcdef",
  "patientId": "PAT-12345",
  "name": "John Doe",
  "date": "2025-03-15",
  "time": "10:30:00",
  "department": "Cardiology",
  "doctorName": "Dr. Priya Sharma"
}
```

## Docker Compose Configuration

### Development (docker-compose.yml)
- FastAPI application connected to Neon DB
- Hot-reload enabled for development
- Automatic database migrations
- Health checks for application monitoring

### Production (docker-compose.prod.yml)
- Enhanced security with appropriate networking
- Resource constraints for containers
- Multi-worker configuration for better performance
- Separate migrations service
- Nginx for SSL termination and load balancing
- Environment variables for sensitive information
- Multiple replicas of the API service

## Building and Pushing Docker Images

Use the provided script to build and push Docker images:

```bash
# Set environment variables
export DOCKER_REGISTRY=your-registry.com
export TAG=1.0.0
export DB_PASSWORD=your-neon-db-password

# Build and push
bash scripts/build_and_push.sh
```

## Cloud Deployment

This application is designed for easy deployment to cloud platforms:

### AWS

1. Push the Docker image to Amazon ECR
2. Deploy using ECS or EKS
3. Set environment variables for DB connection

### Google Cloud

1. Push the Docker image to Google Container Registry
2. Deploy using Cloud Run or GKE
3. Set environment variables for DB connection

### Azure

1. Push the Docker image to Azure Container Registry
2. Deploy using Azure Container Instances or AKS
3. Set environment variables for DB connection

## License

MIT 