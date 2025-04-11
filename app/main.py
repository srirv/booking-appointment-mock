from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.api.appointments import router as appointments_router
from app.db.base import Base, engine

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# API prefix from env
api_prefix = os.getenv("API_PREFIX", "/v1")

# Create FastAPI app
app = FastAPI(
    title="Apollo Hospitals Chennai Appointment Booking API",
    description="API for CRUD operations on appointments",
    version="1.0.0",
    openapi_url=f"{api_prefix}/openapi.json",
    docs_url=f"{api_prefix}/docs",
    redoc_url=f"{api_prefix}/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(appointments_router, prefix=api_prefix)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Apollo Hospitals Chennai Appointment Booking API. Navigate to /v1/docs for API documentation."}

@app.get(f"{api_prefix}/health", tags=["health"])
def health_check():
    return {"status": "healthy"} 