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
from dotenv import load_dotenv

from backend.app.api.endpoints import router, set_services
from backend.app.services.llm_service import LLMService
from backend.app.services.model_service import ModelService

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Loads services at startup and cleans up at shutdown.
    """
    global llm_service, model_service

    # Startup
    logger.info("Starting up application...")

    try:
        # Initialize LLM service
        logger.info("Initializing LLM service...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        llm_service = LLMService(api_key=api_key)
        logger.info(f"LLM service initialized with model: {llm_service.model_name}")

        # Initialize model service
        logger.info("Loading ML model...")
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "models" / "base_simple_model_v0.pkl"

        if not model_path.exists():
            logger.error(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")

        model_service = ModelService(model_path=str(model_path))
        logger.info("Model loaded successfully")

        # Set services in endpoints
        set_services(llm=llm_service, model=model_service)
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
app.include_router(router, prefix="/api/v1", tags=["predictions"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Used Car Price Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
