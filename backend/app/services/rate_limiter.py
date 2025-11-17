"""
Simple in-memory rate limiter for API endpoints.

Limits requests to a specified number per day. Counter resets at midnight UTC
or when the application restarts.
"""

from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DailyRateLimiter:
    """
    Simple in-memory rate limiter that tracks daily request counts.

    Thread-safe for single-process applications.
    """

    def __init__(self, max_requests_per_day: int = 30):
        """
        Initialize the rate limiter.

        Args:
            max_requests_per_day: Maximum number of requests allowed per day
        """
        self.max_requests_per_day = max_requests_per_day
        self.request_count = 0
        self.current_date: Optional[str] = None
        logger.info(f"Rate limiter initialized: {max_requests_per_day} requests/day")

    def _get_current_date(self) -> str:
        """Get current date in UTC as string (YYYY-MM-DD)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _reset_if_new_day(self) -> None:
        """Reset counter if it's a new day."""
        today = self._get_current_date()

        if self.current_date != today:
            logger.info(f"New day detected. Resetting counter from {self.request_count} to 0")
            self.request_count = 0
            self.current_date = today

    def is_allowed(self) -> bool:
        """
        Check if a request is allowed under the rate limit.

        Returns:
            True if request is allowed, False if limit exceeded
        """
        self._reset_if_new_day()
        return self.request_count < self.max_requests_per_day

    def increment(self) -> None:
        """Increment the request counter."""
        self._reset_if_new_day()
        self.request_count += 1
        logger.info(f"Request count: {self.request_count}/{self.max_requests_per_day}")

    def get_remaining(self) -> int:
        """
        Get remaining requests for today.

        Returns:
            Number of remaining requests
        """
        self._reset_if_new_day()
        remaining = max(0, self.max_requests_per_day - self.request_count)
        return remaining

    def get_status(self) -> dict:
        """
        Get current rate limiter status.

        Returns:
            Dictionary with current status information
        """
        self._reset_if_new_day()
        return {
            "limit": self.max_requests_per_day,
            "used": self.request_count,
            "remaining": self.get_remaining(),
            "date": self.current_date,
        }
