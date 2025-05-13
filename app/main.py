from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import time
from dotenv import load_dotenv

from app.api.appointments import router as appointments_router
from app.api.appointments import fixed_router as appointments_fixed_router
from app.api.appointments import nested_router as appointments_nested_router
from app.api.appointments import auth_router, notifications_router
from app.db.base import Base, engine

# Load environment variables
load_dotenv()

# Configure logging
log_level = logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables if they don't exist")
Base.metadata.create_all(bind=engine)

# API prefix from env
api_prefix = os.getenv("API_PREFIX", "/v1")
logger.debug(f"API prefix set to: {api_prefix}")

# Create FastAPI app
app = FastAPI(
    title="Apollo Hospitals Chennai Appointment Booking API",
    description="API for CRUD operations on appointments, slot availability, booking details, rescheduling, cancellation, OTP and SMS notifications",
    version="1.1.0",
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

# Middleware to log requests and response times
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.4f}s")
    return response

# Include routers
logger.info("Registering API routers")
# Important: Respect the order of router registration for correct route resolution
app.include_router(appointments_fixed_router, prefix=api_prefix)    # First: fixed paths (no parameters)
app.include_router(appointments_nested_router, prefix=api_prefix)   # Second: multi-segment paths (more specific)
app.include_router(appointments_router, prefix=api_prefix)          # Third: single parameterized paths (less specific)
app.include_router(auth_router, prefix=api_prefix)
app.include_router(notifications_router, prefix=api_prefix)

@app.get("/", include_in_schema=False)
def root():
    logger.debug("Root endpoint called")
    return {"message": "Welcome to Apollo Hospitals Chennai Appointment Booking API. Navigate to /v1/docs for API documentation."}

@app.get(f"{api_prefix}/health", tags=["health"])
def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"} 