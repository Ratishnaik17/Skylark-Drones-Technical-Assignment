from collections import Counter, defaultdict
from typing import Any
from utils.helpers import get_fuzzy_value


class BusinessAnalytics:
    """
    Business Intelligence calculations for Founder BI Agent.
    Resilient to dynamic key casing and naming variations.
    """

    @staticmethod
    def total_pipeline_value(deals: list[dict]) -> float:
        """Sum all deal values."""
        total = 0.0

        for deal in deals:
            value = get_fuzzy_value(deal, "Masked Deal Value", 0)

            try:
                total += float(str(value).replace(",", ""))
            except (ValueError, TypeError):
                continue

        return round(total, 2)

    @staticmethod
    def deals_by_stage(deals: list[dict]) -> dict:
        """Count deals in each stage."""
        stages = [
            get_fuzzy_value(deal, "Deal Stage", "Unknown")
            for deal in deals
        ]

        return dict(Counter(stages))

    @staticmethod
    def deals_by_sector(deals: list[dict]) -> dict:
        """Count deals by sector."""
        sectors = [
            get_fuzzy_value(deal, "Sector", "Unknown")
            for deal in deals
        ]

        return dict(Counter(sectors))

    @staticmethod
    def revenue_by_sector(deals: list[dict]) -> dict:
        """Calculate revenue grouped by sector."""

        revenue = defaultdict(float)

        for deal in deals:
            sector = get_fuzzy_value(deal, "Sector", "Unknown")

            try:
                value = float(
                    str(
                        get_fuzzy_value(deal, "Masked Deal Value", 0)
                    ).replace(",", "")
                )
            except (ValueError, TypeError):
                value = 0

            revenue[sector] += value

        return dict(revenue)

    @staticmethod
    def average_deal_size(deals: list[dict]) -> float:
        """Average deal value."""

        values = []

        for deal in deals:
            try:
                values.append(
                    float(
                        str(
                            get_fuzzy_value(deal, "Masked Deal Value", 0)
                        ).replace(",", "")
                    )
                )
            except (ValueError, TypeError):
                continue

        if not values:
            return 0.0

        return round(sum(values) / len(values), 2)

    @staticmethod
    def expected_revenue(deals: list[dict]) -> float:
        """
        Expected Revenue =
        Deal Value × Closure Probability
        """

        expected = 0.0

        for deal in deals:
            try:
                value = float(
                    str(
                        get_fuzzy_value(deal, "Masked Deal Value", 0)
                    ).replace(",", "")
                )

                prob_val = get_fuzzy_value(deal, "Closure Probability", 0)
                probability = float(
                    str(prob_val).replace("%", "")
                )

                expected += value * (probability / 100)

            except (ValueError, TypeError):
                continue

        return round(expected, 2)

    @staticmethod
    def work_orders_by_status(work_orders: list[dict]) -> dict:
        """Count work orders by execution status."""

        statuses = [
            get_fuzzy_value(order, "Execution Status", "Unknown")
            for order in work_orders
        ]

        return dict(Counter(statuses))

    @staticmethod
    def delayed_work_orders(work_orders: list[dict]) -> list[dict]:
        """Return delayed work orders."""

        delayed = []

        for order in work_orders:
            status = str(
                get_fuzzy_value(order, "Execution Status", "")
            ).lower()

            if any(
                keyword in status
                for keyword in [
                    "delay",
                    "late",
                    "hold",
                    "overdue",
                ]
            ):
                delayed.append(order)

        return delayed

    @staticmethod
    def outstanding_receivables(work_orders: list[dict]) -> float:
        """Total outstanding receivables."""

        total = 0.0

        for order in work_orders:
            try:
                amount = float(
                    str(
                        get_fuzzy_value(order, "Amount Receivable", 0)
                    ).replace(",", "")
                )

                total += amount

            except (ValueError, TypeError):
                continue

        return round(total, 2)

    @staticmethod
    def leadership_summary(
        deals: list[dict],
        work_orders: list[dict],
    ) -> dict:
        """
        Generate a high-level business summary
        for founders.
        """

        return {
            "pipeline_value":
                BusinessAnalytics.total_pipeline_value(deals),

            "expected_revenue":
                BusinessAnalytics.expected_revenue(deals),

            "average_deal_size":
                BusinessAnalytics.average_deal_size(deals),

            "sector_breakdown":
                BusinessAnalytics.deals_by_sector(deals),

            "deal_stage_breakdown":
                BusinessAnalytics.deals_by_stage(deals),

            "revenue_by_sector":
                BusinessAnalytics.revenue_by_sector(deals),

            "work_order_status":
                BusinessAnalytics.work_orders_by_status(
                    work_orders
                ),

            "delayed_projects":
                len(
                    BusinessAnalytics.delayed_work_orders(
                        work_orders
                    )
                ),

            "outstanding_receivables":
                BusinessAnalytics.outstanding_receivables(
                    work_orders
                ),
        }


analytics = BusinessAnalytics()