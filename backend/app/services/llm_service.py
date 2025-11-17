"""
LLM Service for extracting structured car features from natural language.

This service uses Google Gemini API to parse user descriptions and extract
the 14 features required by the XGBoost model.
"""

import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

from backend.app.config import GEMINI_MODEL_NAME, LLM_MAX_RETRIES
from backend.app.constants import (
    MANUFACTURERS,
    TRANSMISSIONS,
    DRIVETRAINS,
    FUEL_TYPES,
    INTERIOR_COLORS,
    estimate_mpg,
    get_default_features,
    YEAR_MIN,
    YEAR_MAX,
    DEFAULT_YEAR,
    DEFAULT_MILEAGE,
    CATEGORICAL_DEFAULTS,
)

logger = logging.getLogger(__name__)


class LLMService:
    """Service for extracting car features using LLM."""

    def __init__(self, api_key: str, model_name: str = None):
        """
        Initialize LLM service.

        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: from config.GEMINI_MODEL_NAME)
        """
        if model_name is None:
            model_name = GEMINI_MODEL_NAME

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        logger.info(f"LLMService initialized with model: {model_name}")

    def _build_extraction_prompt(self, user_input: str) -> str:
        """
        Build the prompt for feature extraction.

        Args:
            user_input: Natural language description of the car

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a car feature extraction assistant. Extract structured information from the user's car description.

**IMPORTANT RULES:**
1. Extract ONLY the features mentioned by the user
2. Return ONLY valid JSON, no other text
3. Use null for features not mentioned
4. Map common terms to valid values (examples below)

**Valid Values for Categorical Features:**

manufacturer: {', '.join(MANUFACTURERS)}
transmission: {', '.join(TRANSMISSIONS)}
drivetrain: {', '.join(DRIVETRAINS)}
fuel_type: {', '.join(FUEL_TYPES)}
interior_color: {', '.join(INTERIOR_COLORS)}

**Mapping Examples:**
- "FWD" or "front wheel" → "front_wheel_drive"
- "AWD" or "all wheel" → "all_wheel_drive"
- "4WD" or "4x4" → "four_wheel_drive"
- "RWD" or "rear wheel" → "rear_wheel_drive"
- "automatic" → "Automatic" (find closest match in transmission list)
- "manual" → "6-Speed Manual" (find closest match)
- "Benz" → "Mercedes-Benz"
- Unknown values → "others"

**Binary Features (0 or 1):**
- accidents_or_damage: 1 if mentioned accidents/damage, 0 if "no accidents" or "clean title"
- one_owner: 1 if mentioned "one owner" or "single owner", 0 otherwise
- personal_use_only: 1 if mentioned "personal use" or "daily driver", 0 if "fleet" or "rental"

**Numeric Features:**
- year: Extract 4-digit year (range: {YEAR_MIN}-{YEAR_MAX})
- mileage: Extract number in miles (e.g., "45k miles" → 45000)
- mpg: Extract if mentioned, otherwise null

**Example 1:**
Input: "2020 Toyota Camry, 45k miles, automatic, one owner, no accidents"
Output:
{{
  "manufacturer": "Toyota",
  "year": 2020,
  "mileage": 45000,
  "transmission": "Automatic",
  "one_owner": 1,
  "accidents_or_damage": 0,
  "drivetrain": null,
  "fuel_type": null,
  "interior_color": null,
  "mpg": null,
  "personal_use_only": null
}}

**Example 2:**
Input: "2018 Honda Civic manual, 60k miles, black interior, clean title, FWD"
Output:
{{
  "manufacturer": "Honda",
  "year": 2018,
  "mileage": 60000,
  "transmission": "6-Speed Manual",
  "drivetrain": "front_wheel_drive",
  "interior_color": "Black",
  "accidents_or_damage": 0,
  "one_owner": null,
  "fuel_type": null,
  "mpg": null,
  "personal_use_only": null
}}

**Example 3:**
Input: "Ford F-150 2021, 4x4, automatic, 30k miles"
Output:
{{
  "manufacturer": "Ford",
  "year": 2021,
  "mileage": 30000,
  "transmission": "10-Speed Automatic",
  "drivetrain": "four_wheel_drive",
  "accidents_or_damage": null,
  "one_owner": null,
  "fuel_type": null,
  "interior_color": null,
  "mpg": null,
  "personal_use_only": null
}}

Now extract features from this description:
"{user_input}"

Return ONLY the JSON object, no other text:"""

        return prompt

    def extract_car_features(
        self, user_input: str, max_retries: int = None
    ) -> Dict[str, Any]:
        """
        Extract car features from natural language description.

        Args:
            user_input: User's car description
            max_retries: Maximum number of retry attempts (default: from config.LLM_MAX_RETRIES)

        Returns:
            Dictionary with extracted features (nulls for missing values)

        Raises:
            ValueError: If extraction fails after all retries
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        if max_retries is None:
            max_retries = LLM_MAX_RETRIES

        prompt = self._build_extraction_prompt(user_input)

        # Try extraction with retries
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Extraction attempt {attempt + 1}/{max_retries}")

                # Call Gemini API
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()

                # Parse JSON
                features = self._parse_json_response(response_text)

                # Fill defaults and estimates
                features = self._fill_missing_features(features)

                logger.info("Feature extraction successful")
                return features

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}", exc_info=True
                )

                if attempt < max_retries - 1:
                    continue

        # All retries failed
        raise ValueError(
            f"Failed to extract features after {max_retries} attempts: {str(last_error)}"
        )

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response.

        Args:
            response_text: Raw response text from LLM

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        # Try to extract JSON from response (in case LLM adds extra text)
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first and last lines if they're code fences
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            response_text = "\n".join(lines).strip()

        # Try to find JSON object
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")

        json_str = response_text[start_idx:end_idx]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")

    def _fill_missing_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill in missing features with defaults and estimates.

        Args:
            features: Extracted features (may have null values)

        Returns:
            Complete feature dictionary
        """
        # Get default seller features
        defaults = get_default_features()
        features.update(defaults)

        # Set default year and mileage if missing (BEFORE MPG estimation)
        if features.get("year") is None:
            features["year"] = DEFAULT_YEAR
        if features.get("mileage") is None:
            features["mileage"] = DEFAULT_MILEAGE

        # Set null categorical features from constants
        for field, default_value in CATEGORICAL_DEFAULTS.items():
            if features.get(field) is None:
                features[field] = default_value

        # Set null binary features to 0 (assume no accidents, not one owner, etc.)
        for binary_field in ["accidents_or_damage", "one_owner", "personal_use_only"]:
            if features.get(binary_field) is None:
                features[binary_field] = 0

        # Estimate MPG if not provided (AFTER year and fuel_type are filled)
        if features.get("mpg") is None:
            features["mpg"] = estimate_mpg(features["fuel_type"], features["year"])

        return features

    def generate_friendly_response(
        self,
        user_description: str,
        price_min: int,
        price_max: int,
        warnings: list[str],
    ) -> str:
        """
        Generate a human-friendly summary of the prediction results.

        Args:
            user_description: Original user description
            price_min: Minimum price in range
            price_max: Maximum price in range
            warnings: List of warning messages

        Returns:
            Human-friendly summary text
        """
        # Build warnings section
        warnings_text = "\n".join(f"- {w}" for w in warnings) if warnings else "None - all information was provided"

        prompt = f"""You are a friendly car pricing assistant. Based on the user's car description and our price analysis, write a natural, helpful summary.

**User's Description:**
"{user_description}"

**Considerations:**
{warnings_text}

**Instructions:**
Write a concise 2 paragraph response with this structure:

**Paragraph 1:** Start with a simple greeting (like "Hello" or "Hi there"), then mention that using the information provided and a machine learning model, we estimated the value. DO NOT repeat the actual price numbers - they are shown separately. Just mention that the estimate was made.

**Paragraph 2:** If there are considerations/warnings, explain them in user-friendly, natural language. If no considerations exist (all info was provided), just add a brief positive note about having complete information for an accurate estimate. Don't forget to explain the assumtipons made (e.g., mileage, condition), when they apply.

Keep it warm but concise. Don't repeat back all the features the user already told you. Write directly to the user ("your car", "based on your description").

Generate the response:"""

        try:
            response = self.model.generate_content(prompt)
            friendly_text = response.text.strip()
            logger.info("Friendly response generated successfully")
            return friendly_text

        except Exception as e:
            logger.error(f"Failed to generate friendly response: {str(e)}", exc_info=True)
            # Simple fallback
            fallback = f"Based on your description, the estimated price range is ${price_min:,} to ${price_max:,}."
            if warnings:
                fallback += f"\n\nNote: {warnings[0]}"
            return fallback


# Convenience function for testing
def test_extraction(api_key: str, user_input: str, model_name: str = None):
    """
    Test function for quick extraction testing.

    Args:
        api_key: Google Gemini API key
        user_input: Car description
        model_name: Model to use (default: from config)

    Returns:
        Extracted features dictionary
    """
    service = LLMService(api_key=api_key, model_name=model_name)
    return service.extract_car_features(user_input)
