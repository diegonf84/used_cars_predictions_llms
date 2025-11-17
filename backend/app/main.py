"""
FastAPI main application for used car price prediction.

This module initializes the FastAPI app, loads ML models and services at startup,
and configures the API routes.
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from backend.app.api.endpoints import router, set_services
from backend.app.services.llm_service import LLMService
from backend.app.services.model_service import ModelService
from backend.app.services.rate_limiter import DailyRateLimiter
from backend.app.config import (
    GEMINI_API_KEY,
    RATE_LIMIT_PER_DAY,
    MODEL_PATH,
    API_VERSION_PREFIX,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global service instances
llm_service: LLMService = None
model_service: ModelService = None
rate_limiter: DailyRateLimiter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Loads services at startup and cleans up at shutdown.
    """
    global llm_service, model_service, rate_limiter

    # Startup
    logger.info("Starting up application...")

    try:
        # Initialize rate limiter
        logger.info("Initializing rate limiter...")
        rate_limiter = DailyRateLimiter(max_requests_per_day=RATE_LIMIT_PER_DAY)
        logger.info(f"Rate limiter initialized: {RATE_LIMIT_PER_DAY} requests/day")

        # Initialize LLM service
        logger.info("Initializing LLM service...")
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found in environment")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        llm_service = LLMService(api_key=GEMINI_API_KEY)
        logger.info(f"LLM service initialized with model: {llm_service.model_name}")

        # Note: Model service will be lazy-loaded on first prediction request
        # This reduces startup memory usage from ~138MB to minimal
        logger.info("ML model will be loaded on first prediction request (lazy loading)")

        # Set services in endpoints (model_service=None for now)
        set_services(llm=llm_service, model=None, limiter=rate_limiter)
        logger.info("Services configured successfully")

        logger.info("Application startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Used Car Price Prediction API",
    description="Predict used car prices from natural language descriptions using ML and LLM",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix=API_VERSION_PREFIX, tags=["predictions"])

# Mount static files
project_root = Path(__file__).parent.parent.parent
frontend_path = project_root / "frontend"
static_path = frontend_path / "static"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted from: {static_path}")
else:
    logger.warning(f"Static files directory not found: {static_path}")


# Root endpoint - serve index.html
@app.get("/")
async def root():
    """Serve the frontend application."""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        # Fallback to API info if frontend not available
        return {
            "message": "Used Car Price Prediction API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
        }
