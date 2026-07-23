"""
Application-wide constants for the Founder Business Intelligence Agent.
"""

# ==========================================================
# Application
# ==========================================================

APP_NAME = "Founder Business Intelligence Agent"
APP_VERSION = "1.0.0"

# ==========================================================
# Monday.com Board Names
# ==========================================================

DEALS_BOARD = "Deals"
WORK_ORDERS_BOARD = "Work Orders"

# ==========================================================
# Query Intents
# ==========================================================

INTENT_PIPELINE = "pipeline"
INTENT_REVENUE = "revenue"
INTENT_SECTOR = "sector"
INTENT_WORK_ORDERS = "work_orders"
INTENT_DEALS = "deals"
INTENT_LEADERSHIP = "leadership_summary"

SUPPORTED_INTENTS = [
    INTENT_PIPELINE,
    INTENT_REVENUE,
    INTENT_SECTOR,
    INTENT_WORK_ORDERS,
    INTENT_DEALS,
    INTENT_LEADERSHIP,
]

# ==========================================================
# Deal Stages
# ==========================================================

STAGE_LEAD = "Lead"
STAGE_CONTACTED = "Contacted"
STAGE_PROPOSAL = "Proposal Sent"
STAGE_NEGOTIATION = "Negotiation"
STAGE_WON = "Won"
STAGE_LOST = "Lost"

DEAL_STAGES = [
    STAGE_LEAD,
    STAGE_CONTACTED,
    STAGE_PROPOSAL,
    STAGE_NEGOTIATION,
    STAGE_WON,
    STAGE_LOST,
]

# ==========================================================
# Work Order Statuses
# ==========================================================

STATUS_PENDING = "Pending"
STATUS_IN_PROGRESS = "In Progress"
STATUS_COMPLETED = "Completed"
STATUS_DELAYED = "Delayed"
STATUS_CANCELLED = "Cancelled"

WORK_ORDER_STATUSES = [
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_DELAYED,
    STATUS_CANCELLED,
]

# ==========================================================
# Default Values
# ==========================================================

DEFAULT_CURRENCY = "₹"

DEFAULT_CACHE_TTL = 300

DEFAULT_HISTORY_LIMIT = 20

DEFAULT_MODEL = "mistral-small-latest"

DEFAULT_TEMPERATURE = 0.2

# ==========================================================
# API
# ==========================================================

HEALTH_STATUS = "healthy"

DEFAULT_TIMEOUT = 30

# ==========================================================
# Logging
# ==========================================================

LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "{level} | "
    "{message}"
)