"""
Constants and metadata for the used car price prediction model.

This module contains:
- Valid values for categorical features (extracted from training data)
- Default values for features users cannot provide
- Feature metadata and validation ranges
"""

# =============================================================================
# CATEGORICAL FEATURE VALUES
# These are the valid values extracted from the training dataset
# =============================================================================

MANUFACTURERS = [
    'BMW', 'Chevrolet', 'Ford', 'GMC', 'Honda', 'Jeep', 'Kia',
    'Mercedes-Benz', 'Nissan', 'Toyota', 'others'
]

TRANSMISSIONS = [
    'Automatic CVT', '6-Speed Automatic', '8-Speed Automatic', 'Automatic',
    '9-Speed Automatic', '10-Speed Automatic', '5-Speed Automatic',
    '7-Speed Automatic', '7-Speed Automatic with Auto-Shift',
    '6-Speed Manual', 'others'
]

DRIVETRAINS = [
    'front_wheel_drive', 'all_wheel_drive', 'four_wheel_drive',
    'rear_wheel_drive', 'others'
]

FUEL_TYPES = [
    'Gasoline', 'Hybrid', 'Diesel', 'E85 Flex Fuel', 'Electric',
    'Flexible Fuel', 'Plug-In Hybrid', 'Gasoline/Mild Electric Hybrid',
    'Gasoline Fuel', 'others'
]

INTERIOR_COLORS = [
    'Black', 'Gray', 'Jet Black', 'Ebony', 'Charcoal', 'Beige',
    'Graphite', 'Titan Black', 'Tan', 'Charcoal Black', 'others'
]

# =============================================================================
# DEFAULT VALUES FOR NON-CAR FEATURES
# =============================================================================
# IMPORTANT: These features are about the SELLER/DEALER, not the car itself.
# When a user describes their car, they don't have these values.
# We use median values from the training dataset as defaults.
#
# Future improvement: Retrain model without these features OR create separate
# models for buyer vs seller scenarios.
# =============================================================================

DEFAULT_SELLER_RATING = 4.5  # Median from training data
DEFAULT_DRIVER_RATING = 4.7  # Median from training data
DEFAULT_DRIVER_REVIEWS_NUM = 64  # Median from training data

# =============================================================================
# DEFAULT VALUES FOR MISSING USER INPUT
# =============================================================================
# These are used when the user doesn't provide specific information
# =============================================================================

DEFAULT_YEAR = 2020  # Reasonable default for missing year
DEFAULT_MILEAGE = 50000  # Reasonable default for missing mileage

# Default values for categorical features when not provided or invalid
CATEGORICAL_DEFAULTS = {
    'manufacturer': 'others',
    'transmission': 'others',
    'drivetrain': 'others',
    'fuel_type': 'Gasoline',  # More reasonable than "others"
    'interior_color': 'others',
}

# =============================================================================
# NUMERIC FEATURE RANGES
# =============================================================================

YEAR_MIN = 2010
YEAR_MAX = 2024

MILEAGE_MIN = 0
MILEAGE_MAX = 300000  # Reasonable upper limit

MPG_MIN = 5
MPG_MAX = 150  # Includes electric MPGe

# =============================================================================
# FEATURE SCHEMA
# Complete list of features required by the model in the correct order
# =============================================================================

MODEL_FEATURES = [
    'accidents_or_damage',   # Binary: 0 or 1
    'one_owner',             # Binary: 0 or 1
    'personal_use_only',     # Binary: 0 or 1
    'manufacturer',          # Categorical
    'transmission',          # Categorical
    'drivetrain',            # Categorical
    'fuel_type',             # Categorical
    'interior_color',        # Categorical
    'year',                  # Numeric
    'mileage',               # Numeric
    'mpg',                   # Numeric
    'driver_reviews_num',    # Numeric (DEFAULT APPLIED)
    'seller_rating',         # Numeric (DEFAULT APPLIED)
    'driver_rating',         # Numeric (DEFAULT APPLIED)
]

# Features the user CAN provide
USER_PROVIDABLE_FEATURES = [
    'accidents_or_damage',
    'one_owner',
    'personal_use_only',
    'manufacturer',
    'transmission',
    'drivetrain',
    'fuel_type',
    'interior_color',
    'year',
    'mileage',
    'mpg',
]

# Features we auto-fill with defaults (seller-related)
AUTO_FILLED_FEATURES = [
    'driver_reviews_num',
    'seller_rating',
    'driver_rating',
]

# =============================================================================
# FEATURE TYPE MAPPING
# =============================================================================

FEATURE_TYPES = {
    # Binary features
    'accidents_or_damage': 'binary',
    'one_owner': 'binary',
    'personal_use_only': 'binary',

    # Categorical features
    'manufacturer': 'categorical',
    'transmission': 'categorical',
    'drivetrain': 'categorical',
    'fuel_type': 'categorical',
    'interior_color': 'categorical',

    # Numeric features
    'year': 'numeric',
    'mileage': 'numeric',
    'mpg': 'numeric',
    'driver_reviews_num': 'numeric',
    'seller_rating': 'numeric',
    'driver_rating': 'numeric',
}

# =============================================================================
# MPG ESTIMATION TABLE
# Used when MPG is not provided by user
# =============================================================================

MPG_ESTIMATES_BY_FUEL_TYPE = {
    'Gasoline': 25.0,
    'Hybrid': 45.0,
    'Plug-In Hybrid': 50.0,
    'Diesel': 30.0,
    'Electric': 100.0,  # MPGe
    'E85 Flex Fuel': 23.0,
    'Flexible Fuel': 23.0,
    'Gasoline/Mild Electric Hybrid': 35.0,
    'Gasoline Fuel': 25.0,
    'others': 25.0,
}

# Adjustment factors based on year (newer cars tend to be more efficient)
def estimate_mpg(fuel_type: str, year: int) -> float:
    """
    Estimate MPG based on fuel type and year.

    Args:
        fuel_type: Type of fuel
        year: Model year

    Returns:
        Estimated MPG
    """
    base_mpg = MPG_ESTIMATES_BY_FUEL_TYPE.get(fuel_type, 25.0)

    # Apply year-based adjustment
    if year >= 2020:
        base_mpg *= 1.1  # 10% better efficiency for newer cars
    elif year <= 2015:
        base_mpg *= 0.9  # 10% worse efficiency for older cars

    return round(base_mpg, 1)


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_categorical(value: str, valid_values: list, feature_name: str) -> str:
    """
    Validate categorical value and map to 'others' if invalid.

    Args:
        value: Value to validate
        valid_values: List of valid values
        feature_name: Name of the feature (for error messages)

    Returns:
        Valid value or 'others'
    """
    if value in valid_values:
        return value

    # Map to 'others' if invalid
    return 'others'


def get_default_features() -> dict:
    """
    Get dictionary of default values for auto-filled features.

    Returns:
        Dictionary with default values
    """
    return {
        'driver_reviews_num': DEFAULT_DRIVER_REVIEWS_NUM,
        'seller_rating': DEFAULT_SELLER_RATING,
        'driver_rating': DEFAULT_DRIVER_RATING,
    }
