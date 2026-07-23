from typing import TypedDict, Optional, List, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from tools.monday import monday_client
from tools.analytics import analytics
from tools.parser import parser
from tools.formatter import formatter

from services.normalize import normalizer
from services.logger import app_logger

from llm.client import llm_client
from llm.prompts import (
    SYSTEM_PROMPT,
    FOUNDER_INSIGHT_PROMPT,
    CLARIFICATION_PROMPT,
    FOLLOW_UP_PROMPT,
)


# ==========================================================
# Agent State
# ==========================================================

class AgentState(TypedDict):
    question: str
    parsed_query: Optional[Any]
    deals: list
    work_orders: list
    summary: dict
    response: str
    history: List[dict]


# ==========================================================
# Parse User Question
# ==========================================================

def parse_question(state: AgentState):

    app_logger.info("Parsing founder question...")

    # Initialize history list if it doesn't exist in the checkpoint state
    if "history" not in state or state["history"] is None:
        state["history"] = []

    parsed = parser.parse(state["question"])
    state["parsed_query"] = parsed

    if parsed and parsed.requires_clarification:
        app_logger.info("Question requires clarification. Formulating question...")
        
        clarification_msg = parsed.clarification_message or "Could you clarify your question?"
        prompt = f"""
{CLARIFICATION_PROMPT}

User Question: "{state['question']}"
Clarification details: {clarification_msg}
"""
        try:
            state["response"] = llm_client.generate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt
            )
        except Exception:
            state["response"] = clarification_msg

    return state


# ==========================================================
# Fetch Monday Data
# ==========================================================

def fetch_data(state: AgentState):

    app_logger.info("Fetching Monday boards...")

    deals = monday_client.get_deals()
    work_orders = monday_client.get_work_orders()

    state["deals"] = normalizer.normalize_records(deals)
    state["work_orders"] = normalizer.normalize_records(work_orders)

    return state


# ==========================================================
# Business Analytics
# ==========================================================

def run_analytics(state: AgentState):

    app_logger.info("Running analytics...")

    parsed = state["parsed_query"]

    # Fix: dataclass property access instead of .get()
    intent = parsed.intent if parsed else "leadership_summary"

    if intent == "pipeline":
        summary = {
            "pipeline_value": analytics.total_pipeline_value(
                state["deals"]
            ),
            "expected_revenue": analytics.expected_revenue(
                state["deals"]
            ),
            "average_deal_size": analytics.average_deal_size(
                state["deals"]
            ),
            "sector_breakdown": analytics.deals_by_sector(
                state["deals"]
            ),
            "deal_stage_breakdown": analytics.deals_by_stage(
                state["deals"]
            ),
            "revenue_by_sector": analytics.revenue_by_sector(
                state["deals"]
            )
        }

    elif intent == "sector":
        summary = analytics.revenue_by_sector(
            state["deals"]
        )

    elif intent == "work_orders":
        summary = {
            "work_order_status": analytics.work_orders_by_status(
                state["work_orders"]
            ),
            "delayed_projects": len(
                analytics.delayed_work_orders(state["work_orders"])
            ),
            "outstanding_receivables": analytics.outstanding_receivables(
                state["work_orders"]
            )
        }

    else:
        summary = analytics.leadership_summary(
            state["deals"],
            state["work_orders"],
        )

    state["summary"] = summary

    return state


# ==========================================================
# Generate AI Response
# ==========================================================

def generate_response(state: AgentState):

    app_logger.info("Generating founder insight...")

    history_str = ""
    if state.get("history"):
        history_str = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in state["history"]
        ])

    if history_str:
        prompt = f"""
{FOLLOW_UP_PROMPT}

Previous Conversation History:
{history_str}

Founder Question:
{state["question"]}

Business Analytics Metrics:
{state["summary"]}
"""
    else:
        prompt = FOUNDER_INSIGHT_PROMPT.format(
            question=state["question"],
            analytics=state["summary"],
        )

    try:
        response = llm_client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
        )
    except Exception as e:
        app_logger.error(f"LLM Error: {e}")
        # Fallback
        response = formatter.leadership_report(
            state["summary"]
        )

    state["response"] = response

    # Append current turn to conversation history
    state["history"].append({"role": "user", "content": state["question"]})
    state["history"].append({"role": "assistant", "content": response})

    return state


# ==========================================================
# Router
# ==========================================================

def router(state: AgentState):

    parsed = state["parsed_query"]

    # Fix: dataclass property access instead of .get()
    if parsed and parsed.requires_clarification:
        return END

    return "fetch_data"


# ==========================================================
# Build Graph & Memory checkpointer
# ==========================================================

builder = StateGraph(AgentState)

builder.add_node("parse_question", parse_question)
builder.add_node("fetch_data", fetch_data)
builder.add_node("analytics", run_analytics)
builder.add_node("response", generate_response)

builder.set_entry_point("parse_question")

builder.add_conditional_edges(
    "parse_question",
    router,
    {
        "fetch_data": "fetch_data",
        END: END,
    },
)

builder.add_edge("fetch_data", "analytics")
builder.add_edge("analytics", "response")
builder.add_edge("response", END)

# Native Memory Saver checkpointer
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


# ==========================================================
# Public Function
# ==========================================================

def run_agent(question: str, session_id: str) -> str:

    config = {"configurable": {"thread_id": session_id}}

    result = graph.invoke(
        {
            "question": question,
        },
        config=config
    )

    return result["response"]