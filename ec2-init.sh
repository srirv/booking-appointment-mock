#!/bin/bash
# Install Docker
apt-get update
apt-get install -y docker.io
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ECR_REPO_URI

# Create project directory
mkdir -p /app
cd /app

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://neondb_owner:YOUR_DB_PASSWORD@ep-fancy-lab-a5kqy0m9-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
API_PREFIX=/v1
DEBUG=False
DB_PASSWORD=YOUR_DB_PASSWORD
EOF

# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  app:
    image: ECR_REPO_URI:latest
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=postgresql://neondb_owner:YOUR_DB_PASSWORD@ep-fancy-lab-a5kqy0m9-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
      - API_PREFIX=/v1
      - DEBUG=False
      - DB_PASSWORD=YOUR_DB_PASSWORD
    restart: always
    
EOF

# Start the application
docker-compose up -d