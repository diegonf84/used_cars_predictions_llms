"""
Application configuration settings.

Centralizes configurable values in one place for easy maintenance.
Settings can be overridden via environment variables (.env file or Fly.io secrets).
"""

import os
from pathlib import Path

# =============================================================================
# SECRETS (Always from environment)
# =============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =============================================================================
# CONFIGURABLE SETTINGS (Can change without rebuild)
# =============================================================================

# Gemini model to use for feature extraction
# Options: "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"
# See: https://ai.google.dev/gemini-api/docs/models/gemini
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

# API request rate limit (requests per day)
RATE_LIMIT_PER_DAY = int(os.getenv("RATE_LIMIT_PER_DAY", "30"))

# LLM retry attempts on failure
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))

# =============================================================================
# PATHS (Fixed)
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "base_simple_model_v0.pkl"

# =============================================================================
# API SETTINGS (Fixed)
# =============================================================================

API_VERSION_PREFIX = "/api/v1"
PORT = int(os.getenv("PORT", "8000"))
