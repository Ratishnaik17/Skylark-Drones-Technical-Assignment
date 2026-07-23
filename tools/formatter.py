from typing import Any


class ResponseFormatter:
    """
    Formats analytics output into human-readable
    markdown responses.
    """

    @staticmethod
    def currency(value: float) -> str:
        """Format number as currency."""
        return f"₹{value:,.2f}"

    @staticmethod
    def bullet_dict(title: str, data: dict) -> str:
        """Convert dictionary to bullet list."""

        lines = [f"### {title}", ""]

        if not data:
            lines.append("- No data available")
            return "\n".join(lines)

        for key, value in data.items():
            lines.append(f"- **{key}:** {value}")

        return "\n".join(lines)

    @staticmethod
    def pipeline_summary(summary: dict) -> str:
        """Pipeline KPI summary."""

        return f"""
## 📊 Pipeline Summary

**Total Pipeline Value:** {ResponseFormatter.currency(summary['pipeline_value'])}

**Expected Revenue:** {ResponseFormatter.currency(summary['expected_revenue'])}

**Average Deal Size:** {ResponseFormatter.currency(summary['average_deal_size'])}
""".strip()

    @staticmethod
    def sector_summary(data: dict) -> str:
        return ResponseFormatter.bullet_dict(
            "Sector Breakdown",
            data,
        )

    @staticmethod
    def stage_summary(data: dict) -> str:
        return ResponseFormatter.bullet_dict(
            "Deal Stage Breakdown",
            data,
        )

    @staticmethod
    def work_order_summary(summary: dict) -> str:
        """Work order overview."""

        return f"""
## 🚧 Work Orders

**Delayed Projects:** {summary['delayed_projects']}

**Outstanding Receivables:** {ResponseFormatter.currency(summary['outstanding_receivables'])}
""".strip()

    @staticmethod
    def status_summary(status: dict) -> str:
        return ResponseFormatter.bullet_dict(
            "Execution Status",
            status,
        )

    @staticmethod
    def leadership_report(summary: dict) -> str:
        """
        Complete leadership report.
        """

        report = []

        report.append("# 📈 Leadership Business Update\n")

        report.append(
            ResponseFormatter.pipeline_summary(summary)
        )

        report.append("")

        report.append(
            ResponseFormatter.sector_summary(
                summary["sector_breakdown"]
            )
        )

        report.append("")

        report.append(
            ResponseFormatter.stage_summary(
                summary["deal_stage_breakdown"]
            )
        )

        report.append("")

        report.append(
            ResponseFormatter.work_order_summary(summary)
        )

        report.append("")

        report.append(
            ResponseFormatter.status_summary(
                summary["work_order_status"]
            )
        )

        return "\n".join(report)

    @staticmethod
    def simple_response(message: str) -> str:
        return message.strip()


formatter = ResponseFormatter()