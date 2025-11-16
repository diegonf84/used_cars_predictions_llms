"""
Pydantic schemas for FastAPI request/response models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request model for car price prediction."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language description of the car",
        examples=["2020 Toyota Camry, 45k miles, automatic transmission, clean title"]
    )


class PredictionResponse(BaseModel):
    """Response model for car price prediction."""

    price: int = Field(
        ...,
        description="Predicted price in USD"
    )
    price_min: int = Field(
        ...,
        description="Lower bound of price range (90% of predicted price)"
    )
    price_max: int = Field(
        ...,
        description="Upper bound of price range (110% of predicted price)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings about missing or defaulted features"
    )
    friendly_summary: str = Field(
        ...,
        description="Human-friendly explanation of the prediction results"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(
        ...,
        description="API status"
    )
    model_loaded: bool = Field(
        ...,
        description="Whether ML model is loaded successfully"
    )
    llm_configured: bool = Field(
        ...,
        description="Whether LLM service is configured"
    )


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str = Field(
        ...,
        description="Error message"
    )
    detail: Optional[str] = Field(
        None,
        description="Detailed error information"
    )
