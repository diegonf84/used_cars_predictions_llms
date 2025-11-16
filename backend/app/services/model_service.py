"""
Model Service for making price predictions using the trained XGBoost pipeline.

The saved model is a scikit-learn Pipeline that includes:
- Feature transformations
- Unknown category handling
- XGBoost prediction
"""

import joblib
import logging
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from backend.app.constants import MODEL_FEATURES

logger = logging.getLogger(__name__)


class ModelService:
    """Service for loading the model pipeline and making predictions."""

    def __init__(self, model_path: str):
        """
        Initialize model service and load the pipeline.

        Args:
            model_path: Path to the pickled model file

        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        self.model_path = Path(model_path)
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the model pipeline using joblib."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make price prediction from car features.

        Args:
            features: Dictionary with all 14 required features

        Returns:
            Dictionary with:
                - price: Predicted price
                - price_min: Lower bound (price - 10%)
                - price_max: Upper bound (price + 10%)
                - confidence: Simple confidence estimate (0.9)

        Raises:
            ValueError: If features are invalid or prediction fails
        """
        if self.model is None:
            raise ValueError("Model not loaded")

        try:
            # Convert features dict to DataFrame with correct column order
            df = self._features_to_dataframe(features)

            # Make prediction (pipeline handles all transformations)
            prediction = self.model.predict(df)[0]

            # Calculate confidence interval (±10%)
            price = float(prediction)
            price_min = price * 0.9
            price_max = price * 1.1

            # Round to nearest hundred (more practical for car prices)
            result = {
                "price": int(round(price / 100) * 100),
                "price_min": int(round(price_min / 100) * 100),
                "price_max": int(round(price_max / 100) * 100),
                "confidence": 0.9,  # Simple fixed confidence for now
            }

            logger.info(f"Prediction successful: ${result['price']:,.2f}")
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise ValueError(f"Prediction failed: {str(e)}")

    def _features_to_dataframe(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert features dictionary to DataFrame with correct column order.

        Args:
            features: Dictionary with feature values

        Returns:
            DataFrame with single row and columns in MODEL_FEATURES order

        Raises:
            ValueError: If required features are missing
        """
        # Check all required features are present
        missing = [f for f in MODEL_FEATURES if f not in features]
        if missing:
            raise ValueError(f"Missing required features: {missing}")

        # Create DataFrame with features in correct order
        # This is critical - XGBoost expects features in the training order
        df = pd.DataFrame([features], columns=MODEL_FEATURES)

        logger.debug(f"Created DataFrame with shape {df.shape}")
        return df


# Convenience function for testing
def test_prediction(model_path: str, features: Dict[str, Any]):
    """
    Test function for quick prediction testing.

    Args:
        model_path: Path to model file
        features: Feature dictionary

    Returns:
        Prediction result dictionary
    """
    service = ModelService(model_path=model_path)
    return service.predict(features)
