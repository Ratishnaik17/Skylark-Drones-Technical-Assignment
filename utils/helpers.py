"""
Common helper functions used throughout the application.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    """

    try:
        if value in (None, "", "None"):
            return default

        if isinstance(value, str):
            value = value.replace(",", "").replace("₹", "").strip()

        return float(value)

    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int.
    """

    try:
        return int(float(value))

    except (ValueError, TypeError):
        return default


def format_currency(amount: Any, symbol: str = "₹") -> str:
    """
    Format a number as currency.
    """

    amount = safe_float(amount)

    return f"{symbol}{amount:,.2f}"


def percentage(part: float, total: float) -> float:
    """
    Calculate percentage safely.
    """

    if total == 0:
        return 0.0

    return round((part / total) * 100, 2)


def average(values: List[float]) -> float:
    """
    Calculate average safely.
    """

    if not values:
        return 0.0

    return round(sum(values) / len(values), 2)


def flatten(items: List[List[Any]]) -> List[Any]:
    """
    Flatten nested lists.
    """

    return [item for sublist in items for item in sublist]


def remove_none(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys whose values are None.
    """

    return {
        key: value
        for key, value in data.items()
        if value is not None
    }


def truncate(text: str, max_length: int = 200) -> str:
    """
    Truncate long text.
    """

    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def current_timestamp() -> str:
    """
    Return current UTC timestamp.
    """

    return datetime.utcnow().isoformat()


def parse_date(date_str: Optional[str], fmt: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    """

    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, fmt)

    except ValueError:
        return None


def sort_dict_desc(data: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Sort a dictionary by value in descending order.
    """

    return dict(
        sorted(
            data.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )


def top_n(data: Dict[Any, Any], n: int = 5) -> Dict[Any, Any]:
    """
    Return the top N items from a dictionary.
    """

    return dict(
        list(
            sort_dict_desc(data).items()
        )[:n]
    )


def get_fuzzy_value(record: dict, search_term: str, default: Any = None) -> Any:
    """
    Search for a key inside 'record' containing the 'search_term' case-insensitively.
    If multiple matches are found, prioritize exact case-insensitive matches,
    otherwise returns the value of the first match.
    """
    if not record or not isinstance(record, dict):
        return default

    search_lower = search_term.lower()

    # First check: exact match
    if search_term in record:
        return record[search_term]

    # Second check: case-insensitive exact match
    for key, value in record.items():
        if key.lower() == search_lower:
            return value

    # Third check: substring match
    for key, value in record.items():
        if search_lower in key.lower():
            return value

    return default


def find_fuzzy_key(record: dict, search_term: str) -> Optional[str]:
    """
    Finds the key in the record matching the search term.
    """
    if not record or not isinstance(record, dict):
        return None

    search_lower = search_term.lower()

    for key in record.keys():
        if key.lower() == search_lower or search_lower in key.lower():
            return key

    return None