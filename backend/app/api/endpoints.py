"""
FastAPI endpoints for car price prediction.
"""

import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.api_schemas import (
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    ErrorResponse,
)
from backend.app.services.llm_service import LLMService
from backend.app.services.model_service import ModelService
from backend.app.services.rate_limiter import DailyRateLimiter
from backend.app.services.validation import validate_features
from backend.app.config import MODEL_PATH

logger = logging.getLogger(__name__)

router = APIRouter()

# These will be set by the main app at startup
llm_service: LLMService = None
model_service: Optional[ModelService] = None
rate_limiter: DailyRateLimiter = None


def set_services(llm: LLMService, model: Optional[ModelService], limiter: DailyRateLimiter):
    """Set service instances (called from main app)."""
    global llm_service, model_service, rate_limiter
    llm_service = llm
    model_service = model
    rate_limiter = limiter


def _load_model_if_needed():
    """
    Lazy load the ML model on first prediction request.
    This reduces startup memory usage and allows the app to start within 256MB.
    """
    global model_service

    if model_service is None:
        logger.info("Lazy loading ML model on first request...")

        if not Path(MODEL_PATH).exists():
            logger.error(f"Model file not found: {MODEL_PATH}")
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        model_service = ModelService(model_path=str(MODEL_PATH))
        logger.info("ML model loaded successfully")

    return model_service


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse with API status and service availability
    """
    return HealthResponse(
        status="healthy",
        model_loaded=model_service is not None,
        llm_configured=llm_service is not None,
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict_price(request: PredictionRequest):
    """
    Predict car price from natural language description.

    Args:
        request: PredictionRequest with car description

    Returns:
        PredictionResponse with price prediction and warnings

    Raises:
        HTTPException: If services are not initialized or prediction fails
    """
    # Check rate limit first
    if rate_limiter is not None:
        if not rate_limiter.is_allowed():
            remaining = rate_limiter.get_remaining()
            logger.warning(f"Rate limit exceeded. Remaining: {remaining}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily request limit exceeded. Please try again tomorrow. (Limit: {rate_limiter.max_requests_per_day} requests/day)",
            )
        # Increment counter after check passes
        rate_limiter.increment()

    # Check LLM service is initialized
    if llm_service is None:
        logger.error("LLM service not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized. Please try again later.",
        )

    try:
        # Lazy load ML model on first request
        model = _load_model_if_needed()
        # Step 1: Extract features from natural language
        logger.info(f"Extracting features from: {request.description[:100]}...")
        features = llm_service.extract_car_features(request.description)
        logger.info(f"Extracted features: {features}")
        logger.info("Features extracted successfully")

        # Step 2: Validate features and get warnings
        logger.info("Validating features...")
        validated_features, warnings = validate_features(features)
        logger.info(f"Validation complete with {len(warnings)} warnings")

        # Step 3: Make prediction
        logger.info("Making price prediction...")
        prediction = model.predict(validated_features.model_dump())
        logger.info(f"Prediction successful: ${prediction['price']:,}")

        # Step 4: Generate friendly summary
        logger.info("Generating friendly summary...")
        friendly_summary = llm_service.generate_friendly_response(
            user_description=request.description,
            price_min=prediction["price_min"],
            price_max=prediction["price_max"],
            warnings=warnings,
        )
        logger.info("Friendly summary generated")

        # Step 5: Build response
        return PredictionResponse(
            price=prediction["price"],
            price_min=prediction["price_min"],
            price_max=prediction["price_max"],
            confidence=prediction["confidence"],
            warnings=warnings,
            friendly_summary=friendly_summary,
        )

    except ValueError as e:
        # LLM extraction or validation errors
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}",
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )
