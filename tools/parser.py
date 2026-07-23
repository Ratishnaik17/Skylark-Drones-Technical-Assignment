from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedQuery:
    """
    Structured representation of a founder's question.
    """

    intent: str

    sector: Optional[str] = None

    deal_stage: Optional[str] = None

    work_order_status: Optional[str] = None

    client: Optional[str] = None

    owner: Optional[str] = None

    period: Optional[str] = None

    metric: Optional[str] = None

    raw_query: str = ""

    requires_clarification: bool = False

    clarification_message: Optional[str] = None


class QueryParser:
    """
    Lightweight parser.

    Extracts structured parameters that analytics.py can use.
    If details like period are missing, we default instead of blocking.
    """

    SECTORS = [
        "energy",
        "telecom",
        "oil",
        "gas",
        "solar",
        "wind",
        "railways",
        "power",
        "mining",
    ]

    DEAL_STAGES = [
        "lead",
        "qualified",
        "proposal",
        "negotiation",
        "won",
        "lost",
    ]

    PERIODS = [
        "today",
        "this week",
        "this month",
        "this quarter",
        "this year",
        "overall",
        "all-time",
    ]

    @staticmethod
    def parse(question: str) -> ParsedQuery:

        q = question.lower()

        intent = "general"

        if "pipeline" in q:
            intent = "pipeline"

        elif "revenue" in q:
            intent = "revenue"

        elif "sector" in q:
            intent = "sector"

        elif "delay" in q or "late" in q or "work order" in q:
            intent = "work_orders"

        elif "leadership" in q or "summary" in q or "founder" in q:
            intent = "leadership"

        sector = None
        for s in QueryParser.SECTORS:
            if s in q:
                sector = s.title()
                break

        stage = None
        for s in QueryParser.DEAL_STAGES:
            if s in q:
                stage = s.title()
                break

        period = None
        for p in QueryParser.PERIODS:
            if p in q:
                period = p.title()
                break
        
        # Default to "Overall / All-Time" if not specified, rather than blocking the user
        if period is None:
            period = "Overall"

        clarification = False
        clarification_message = None

        return ParsedQuery(
            intent=intent,
            sector=sector,
            deal_stage=stage,
            period=period,
            raw_query=question,
            requires_clarification=clarification,
            clarification_message=clarification_message,
        )


parser = QueryParser()