"""Timestamp handling utilities for ROS bag data.

This module provides functions to convert ROS timestamps (nanoseconds since epoch)
to various Python datetime formats. Follows the Single Responsibility Principle (SRP)
by focusing solely on timestamp conversion.
"""

from datetime import datetime, timezone


def ros_timestamp_to_seconds(timestamp_ns: int) -> float:
    """Convert ROS timestamp (nanoseconds) to seconds (float).

    Args:
        timestamp_ns: Timestamp in nanoseconds since Unix epoch

    Returns:
        Timestamp in seconds as a floating point number

    Example:
        >>> ros_timestamp_to_seconds(1000000000)
        1.0
    """
    return timestamp_ns / 1e9


def ros_timestamp_to_datetime(timestamp_ns: int) -> datetime:
    """Convert ROS timestamp (nanoseconds) to Python datetime object.

    Args:
        timestamp_ns: Timestamp in nanoseconds since Unix epoch

    Returns:
        datetime object in UTC timezone

    Example:
        >>> dt = ros_timestamp_to_datetime(1000000000)
        >>> dt.year
        1970
    """
    seconds = ros_timestamp_to_seconds(timestamp_ns)
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def format_timestamp_iso(dt: datetime) -> str:
    """Format datetime object to ISO 8601 string.

    Args:
        dt: datetime object to format

    Returns:
        ISO 8601 formatted timestamp string

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2023, 11, 19, 12, 30, 45, tzinfo=timezone.utc)
        >>> format_timestamp_iso(dt)
        '2023-11-19T12:30:45+00:00'
    """
    return dt.isoformat()
