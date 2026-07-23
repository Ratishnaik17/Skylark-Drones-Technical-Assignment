"""
Date utility functions for the Founder Business Intelligence Agent.
"""

from datetime import date, datetime, timedelta
from typing import Optional, Tuple


def today() -> date:
    """Return today's date."""
    return date.today()


def now() -> datetime:
    """Return the current datetime."""
    return datetime.now()


def yesterday() -> date:
    """Return yesterday's date."""
    return today() - timedelta(days=1)


def last_n_days(days: int) -> Tuple[date, date]:
    """
    Return the start and end dates for the last N days.
    """
    end = today()
    start = end - timedelta(days=days)
    return start, end


def current_week() -> Tuple[date, date]:
    """
    Return the start and end dates of the current week.
    """
    end = today()
    start = end - timedelta(days=end.weekday())
    return start, start + timedelta(days=6)


def current_month() -> Tuple[date, date]:
    """
    Return the start and end dates of the current month.
    """
    start = today().replace(day=1)

    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1)
    else:
        next_month = start.replace(month=start.month + 1)

    end = next_month - timedelta(days=1)

    return start, end


def current_year() -> Tuple[date, date]:
    """
    Return the start and end dates of the current year.
    """
    year = today().year
    return date(year, 1, 1), date(year, 12, 31)


def current_quarter() -> Tuple[date, date]:
    """
    Return the start and end dates of the current quarter.
    """
    month = today().month
    year = today().year

    quarter = (month - 1) // 3

    start_month = quarter * 3 + 1
    start = date(year, start_month, 1)

    if start_month == 10:
        end = date(year, 12, 31)
    else:
        next_quarter = date(year, start_month + 3, 1)
        end = next_quarter - timedelta(days=1)

    return start, end


def parse_date(
    value: str,
    fmt: str = "%Y-%m-%d",
) -> Optional[date]:
    """
    Parse a string into a date.
    """
    try:
        return datetime.strptime(value, fmt).date()
    except (ValueError, TypeError):
        return None


def format_date(
    value: date,
    fmt: str = "%d %b %Y",
) -> str:
    """
    Format a date.
    """
    return value.strftime(fmt)


def is_between(
    value: date,
    start: date,
    end: date,
) -> bool:
    """
    Check if a date falls within a range.
    """
    return start <= value <= end


def days_between(
    start: date,
    end: date,
) -> int:
    """
    Return the number of days between two dates.
    """
    return (end - start).days


def age_in_days(value: date) -> int:
    """
    Return the age of a date in days.
    """
    return (today() - value).days