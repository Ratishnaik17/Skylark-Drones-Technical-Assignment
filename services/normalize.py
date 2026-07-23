from __future__ import annotations

from datetime import datetime
from typing import Any 


class DataNormalizer:
    """
    Utility class for cleaning and normalizing
    Monday.com board data.
    """

    # ----------------------------
    # Basic Normalizers
    # ----------------------------

    @staticmethod
    def normalize_null(value: Any) -> Any:
        """Convert null-like values to None."""

        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value.lower() in {
                "",
                "null",
                "none",
                "nan",
                "n/a",
                "-",
            }:
                return None

        return value

    @staticmethod
    def normalize_text(value: Any) -> str | None:
        """Clean and standardize text."""

        value = DataNormalizer.normalize_null(value)

        if value is None:
            return None

        return str(value).strip()

    @staticmethod
    def normalize_title(value: Any) -> str | None:
        """Convert text to title case."""

        text = DataNormalizer.normalize_text(value)

        if text is None:
            return None

        return text.title()

    # ----------------------------
    # Numbers
    # ----------------------------

    @staticmethod
    def normalize_currency(value: Any) -> float:
        """Convert currency strings into float."""

        value = DataNormalizer.normalize_null(value)

        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        text = (
            str(value)
            .replace(",", "")
            .replace("₹", "")
            .replace("$", "")
            .strip()
        )

        try:
            return float(text)
        except ValueError:
            return 0.0

    @staticmethod
    def normalize_percentage(value: Any) -> float:
        """Convert percentage strings into float."""

        value = DataNormalizer.normalize_null(value)

        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).replace("%", "").strip()

        try:
            return float(text)
        except ValueError:
            return 0.0

    # ----------------------------
    # Dates
    # ----------------------------

    DATE_FORMATS = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%m/%d/%Y",
        "%Y/%m/%d",
    )

    @staticmethod
    def normalize_date(value: Any):
        """
        Convert supported date formats
        into datetime objects.
        """

        value = DataNormalizer.normalize_null(value)

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        value = str(value).strip()

        for fmt in DataNormalizer.DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        return None

    # ----------------------------
    # Status
    # ----------------------------

    @staticmethod
    def normalize_status(value: Any) -> str:
        """Normalize common status values."""

        text = DataNormalizer.normalize_text(value)

        if text is None:
            return "Unknown"

        mapping = {
            "completed": "Completed",
            "complete": "Completed",
            "done": "Completed",
            "closed": "Completed",

            "in progress": "In Progress",
            "ongoing": "In Progress",
            "running": "In Progress",

            "delay": "Delayed",
            "delayed": "Delayed",
            "late": "Delayed",
            "hold": "Delayed",

            "open": "Open",
        }

        key = text.lower()

        return mapping.get(key, text.title())

    # ----------------------------
    # Record Normalization
    # ----------------------------

    @staticmethod
    def normalize_record(record: dict) -> dict:
        """
        Normalize an entire record from Monday.com.
        """

        normalized = {}

        for key, value in record.items():

            key_lower = key.lower()

            if "date" in key_lower:
                normalized[key] = DataNormalizer.normalize_date(value)

            elif (
                "value" in key_lower
                or "amount" in key_lower
                or "revenue" in key_lower
                or "receivable" in key_lower
            ):
                normalized[key] = DataNormalizer.normalize_currency(value)

            elif (
                "probability" in key_lower
                or "%" in key_lower
            ):
                normalized[key] = DataNormalizer.normalize_percentage(value)

            elif "status" in key_lower:
                normalized[key] = DataNormalizer.normalize_status(value)

            elif (
                "sector" in key_lower
                or "stage" in key_lower
                or "owner" in key_lower
                or "client" in key_lower
            ):
                normalized[key] = DataNormalizer.normalize_title(value)

            else:
                normalized[key] = DataNormalizer.normalize_text(value)

        return normalized

    @staticmethod
    def normalize_records(records: list[dict]) -> list[dict]:
        """Normalize a list of records."""

        return [
            DataNormalizer.normalize_record(record)
            for record in records
        ]


normalizer = DataNormalizer()