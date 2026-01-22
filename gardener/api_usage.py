"""API usage tracking and rate limiting for Gardener.

Tracks all AI backend API calls to prevent runaway usage and enforce quotas.
"""

import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, TypeVar

import config

logger = logging.getLogger(__name__)

# Rate limiting configuration
MAX_CALLS_PER_HOUR = int(os.environ.get("MAX_API_CALLS_PER_HOUR", "100"))
MAX_CALLS_PER_DAY = int(os.environ.get("MAX_API_CALLS_PER_DAY", "500"))
WARN_THRESHOLD_PERCENT = int(os.environ.get("API_WARN_THRESHOLD_PERCENT", "80"))

# Database schema for API usage tracking
API_USAGE_SCHEMA = """
-- Track individual API calls
CREATE TABLE IF NOT EXISTS api_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backend TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'classify', 'refine', 'ask'
    timestamp TEXT DEFAULT (datetime('now')),
    success INTEGER DEFAULT 1,  -- 1 for success, 0 for failure
    error TEXT
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_api_calls_timestamp ON api_calls(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_calls_backend ON api_calls(backend);
CREATE INDEX IF NOT EXISTS idx_api_calls_operation ON api_calls(operation);
"""


@dataclass
class UsageStats:
    """API usage statistics."""

    total_calls: int
    calls_last_hour: int
    calls_last_day: int
    hourly_limit: int
    daily_limit: int
    warn_threshold_hourly: int
    warn_threshold_daily: int

    @property
    def hourly_usage_percent(self) -> float:
        """Calculate percentage of hourly quota used."""
        return (self.calls_last_hour / self.hourly_limit * 100) if self.hourly_limit > 0 else 0

    @property
    def daily_usage_percent(self) -> float:
        """Calculate percentage of daily quota used."""
        return (self.calls_last_day / self.daily_limit * 100) if self.daily_limit > 0 else 0

    @property
    def is_near_hourly_limit(self) -> bool:
        """Check if approaching hourly limit."""
        return self.calls_last_hour >= self.warn_threshold_hourly

    @property
    def is_near_daily_limit(self) -> bool:
        """Check if approaching daily limit."""
        return self.calls_last_day >= self.warn_threshold_daily

    @property
    def is_over_hourly_limit(self) -> bool:
        """Check if hourly limit exceeded."""
        return self.calls_last_hour >= self.hourly_limit

    @property
    def is_over_daily_limit(self) -> bool:
        """Check if daily limit exceeded."""
        return self.calls_last_day >= self.daily_limit


def init_api_usage_db() -> None:
    """Initialize API usage tracking tables."""
    conn = config.get_db_connection()
    try:
        conn.executescript(API_USAGE_SCHEMA)
        conn.commit()
        logger.debug("API usage tracking tables initialized")
    finally:
        conn.close()


def record_api_call(backend: str, operation: str, success: bool = True, error: str | None = None) -> None:
    """Record an API call to the database.

    Args:
        backend: Backend name (e.g., 'openai', 'anthropic')
        operation: Operation type ('classify', 'refine', 'ask')
        success: Whether the call succeeded
        error: Error message if call failed
    """
    conn = config.get_db_connection()
    try:
        conn.execute(
            "INSERT INTO api_calls (backend, operation, success, error) VALUES (?, ?, ?, ?)",
            (backend, operation, 1 if success else 0, error),
        )
        conn.commit()
        logger.debug(f"Recorded API call: {backend}.{operation} (success={success})")
    finally:
        conn.close()


def get_usage_stats() -> UsageStats:
    """Get current API usage statistics.

    Returns:
        UsageStats with current usage counts and limits
    """
    conn = config.get_db_connection()
    try:
        # Total calls
        total = conn.execute("SELECT COUNT(*) FROM api_calls WHERE success = 1").fetchone()[0]

        # Calls in last hour
        hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        hourly = conn.execute(
            "SELECT COUNT(*) FROM api_calls WHERE success = 1 AND timestamp > ?",
            (hour_ago,),
        ).fetchone()[0]

        # Calls in last 24 hours
        day_ago = (datetime.now() - timedelta(days=1)).isoformat()
        daily = conn.execute(
            "SELECT COUNT(*) FROM api_calls WHERE success = 1 AND timestamp > ?",
            (day_ago,),
        ).fetchone()[0]

        return UsageStats(
            total_calls=total,
            calls_last_hour=hourly,
            calls_last_day=daily,
            hourly_limit=MAX_CALLS_PER_HOUR,
            daily_limit=MAX_CALLS_PER_DAY,
            warn_threshold_hourly=int(MAX_CALLS_PER_HOUR * WARN_THRESHOLD_PERCENT / 100),
            warn_threshold_daily=int(MAX_CALLS_PER_DAY * WARN_THRESHOLD_PERCENT / 100),
        )
    finally:
        conn.close()


def check_rate_limit() -> tuple[bool, str | None]:
    """Check if we're within rate limits.

    Returns:
        Tuple of (allowed, reason). If not allowed, reason explains why.
    """
    stats = get_usage_stats()

    # Check daily limit first (more restrictive)
    if stats.is_over_daily_limit:
        return False, f"Daily API limit reached ({stats.calls_last_day}/{stats.daily_limit} calls)"

    # Check hourly limit
    if stats.is_over_hourly_limit:
        return False, f"Hourly API limit reached ({stats.calls_last_hour}/{stats.hourly_limit} calls)"

    # Log warnings if approaching limits
    if stats.is_near_daily_limit and not stats.is_over_daily_limit:
        logger.warning(
            f"API usage at {stats.daily_usage_percent:.1f}% of daily limit "
            f"({stats.calls_last_day}/{stats.daily_limit} calls)"
        )

    if stats.is_near_hourly_limit and not stats.is_over_hourly_limit:
        logger.warning(
            f"API usage at {stats.hourly_usage_percent:.1f}% of hourly limit "
            f"({stats.calls_last_hour}/{stats.hourly_limit} calls)"
        )

    return True, None


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    pass


@contextmanager
def track_api_call(backend: str, operation: str, enforce_limit: bool = True):
    """Context manager to track and optionally enforce rate limits for API calls.

    Args:
        backend: Backend name (e.g., 'openai', 'anthropic')
        operation: Operation type ('classify', 'refine', 'ask')
        enforce_limit: If True, raise RateLimitError when limit exceeded

    Raises:
        RateLimitError: If enforce_limit=True and rate limit exceeded

    Example:
        with track_api_call('openai', 'classify'):
            result = client.classify(...)
    """
    # Check rate limit before making the call
    if enforce_limit:
        allowed, reason = check_rate_limit()
        if not allowed:
            logger.error(f"Rate limit exceeded: {reason}")
            raise RateLimitError(reason)

    success = False
    error = None
    try:
        yield
        success = True
    except Exception as e:
        error = str(e)
        raise
    finally:
        # Record the call attempt
        record_api_call(backend, operation, success, error)


T = TypeVar("T")


def with_api_tracking(backend: str, operation: str, enforce_limit: bool = True) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to track API calls.

    Args:
        backend: Backend name
        operation: Operation type
        enforce_limit: Whether to enforce rate limits

    Example:
        @with_api_tracking('openai', 'classify')
        def classify(self, content: str) -> str:
            return self.client.classify(content)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            with track_api_call(backend, operation, enforce_limit):
                return func(*args, **kwargs)
        return wrapper
    return decorator
