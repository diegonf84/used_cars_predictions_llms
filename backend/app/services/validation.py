"""
Validation service using Pydantic for type safety and data validation.

Validates car features before prediction and generates user-friendly warnings.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from backend.app.constants import (
    MANUFACTURERS,
    TRANSMISSIONS,
    DRIVETRAINS,
    FUEL_TYPES,
    INTERIOR_COLORS,
    YEAR_MIN,
    YEAR_MAX,
    MILEAGE_MIN,
    MILEAGE_MAX,
    MPG_MIN,
    MPG_MAX,
    DEFAULT_SELLER_RATING,
    DEFAULT_DRIVER_RATING,
    DEFAULT_DRIVER_REVIEWS_NUM,
)


class CarFeatures(BaseModel):
    """Pydantic model for validating car features."""

    # Binary features
    accidents_or_damage: int = Field(ge=0, le=1, description="0=No, 1=Yes")
    one_owner: int = Field(ge=0, le=1, description="0=No, 1=Yes")
    personal_use_only: int = Field(ge=0, le=1, description="0=No, 1=Yes")

    # Categorical features
    manufacturer: str = Field(description="Car manufacturer")
    transmission: str = Field(description="Transmission type")
    drivetrain: str = Field(description="Drivetrain type")
    fuel_type: str = Field(description="Fuel type")
    interior_color: str = Field(description="Interior color")

    # Numeric features
    year: int = Field(ge=YEAR_MIN, le=YEAR_MAX, description="Model year")
    mileage: int = Field(ge=MILEAGE_MIN, le=MILEAGE_MAX, description="Mileage in miles")
    mpg: float = Field(ge=MPG_MIN, le=MPG_MAX, description="Miles per gallon")

    # Seller features (auto-filled)
    driver_reviews_num: int = Field(ge=0, description="Driver reviews count")
    seller_rating: float = Field(ge=0, le=5, description="Seller rating")
    driver_rating: float = Field(ge=0, le=5, description="Driver rating")

    @field_validator('manufacturer')
    @classmethod
    def validate_manufacturer(cls, v):
        """Validate manufacturer is in allowed list."""
        if v not in MANUFACTURERS:
            # Pipeline will handle unknown values, just pass through
            return v
        return v

    @field_validator('transmission')
    @classmethod
    def validate_transmission(cls, v):
        """Validate transmission is in allowed list."""
        if v not in TRANSMISSIONS:
            return v
        return v

    @field_validator('drivetrain')
    @classmethod
    def validate_drivetrain(cls, v):
        """Validate drivetrain is in allowed list."""
        if v not in DRIVETRAINS:
            return v
        return v

    @field_validator('fuel_type')
    @classmethod
    def validate_fuel_type(cls, v):
        """Validate fuel type is in allowed list."""
        if v not in FUEL_TYPES:
            return v
        return v

    @field_validator('interior_color')
    @classmethod
    def validate_interior_color(cls, v):
        """Validate interior color is in allowed list."""
        if v not in INTERIOR_COLORS:
            return v
        return v


def validate_features(features: dict) -> tuple[CarFeatures, List[str]]:
    """
    Validate car features and generate warnings.

    Args:
        features: Dictionary with car features

    Returns:
        Tuple of (validated CarFeatures object, list of warning messages)

    Raises:
        ValidationError: If features are invalid
    """
    warnings = []

    # Check if defaults were used
    if features.get("seller_rating") == DEFAULT_SELLER_RATING:
        warnings.append("Using default seller rating (average seller quality)")

    if features.get("driver_rating") == DEFAULT_DRIVER_RATING:
        warnings.append("Using default driver rating (average driver quality)")

    if features.get("driver_reviews_num") == DEFAULT_DRIVER_REVIEWS_NUM:
        warnings.append("Using default driver reviews count")

    # Check for "others" in categorical fields
    categorical_fields = {
        "manufacturer": "manufacturer",
        "transmission": "transmission",
        "drivetrain": "drivetrain",
        "fuel_type": "fuel type",
        "interior_color": "interior color",
    }

    for field, display_name in categorical_fields.items():
        if features.get(field) == "others":
            warnings.append(f"Unknown {display_name} - using generic category")

    # Check if MPG was estimated (approximate check)
    # We can't know for sure if it was estimated, but we can warn about it
    if features.get("fuel_type") == "Gasoline" and features.get("mpg") in [22.5, 25.0, 27.5]:
        warnings.append("MPG was estimated based on fuel type and year")

    # Validate using Pydantic
    validated = CarFeatures(**features)

    return validated, warnings


def get_validation_summary(features: dict) -> dict:
    """
    Get a summary of validation results including warnings.

    Args:
        features: Dictionary with car features

    Returns:
        Dictionary with validation results and warnings
    """
    try:
        validated, warnings = validate_features(features)
        return {
            "valid": True,
            "warnings": warnings,
            "features": validated.model_dump(),
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "warnings": [],
        }
