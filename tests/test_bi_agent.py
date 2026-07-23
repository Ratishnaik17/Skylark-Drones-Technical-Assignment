import sys
import os
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import get_fuzzy_value, find_fuzzy_key
from services.normalize import normalizer
from tools.analytics import analytics
from agent.workflow import run_agent


def test_fuzzy_key_retrieval():
    """Verify that get_fuzzy_value can extract key value case-insensitively and by substring."""
    record = {
        "Masked Deal value": "120,000",
        "Sector/service": "Mining",
        "Amount Receivable (Masked)": "50000"
    }

    # Case mismatch
    assert get_fuzzy_value(record, "Masked Deal Value") == "120,000"
    
    # Casing and substring
    assert get_fuzzy_value(record, "Sector") == "Mining"
    
    # Substring match
    assert get_fuzzy_value(record, "Amount Receivable") == "50000"
    
    # No match
    assert get_fuzzy_value(record, "Nonexistent Key", "Default") == "Default"


def test_data_normalization():
    """Verify that messy data formats are normalized properly."""
    # Currency
    assert normalizer.normalize_currency("₹1,250.50") == 1250.50
    assert normalizer.normalize_currency(None) == 0.0
    
    # Date
    parsed_date = normalizer.normalize_date("27/09/2025")
    assert parsed_date is not None
    assert parsed_date.year == 2025
    assert parsed_date.month == 9
    assert parsed_date.day == 27
    
    # Status mapping
    assert normalizer.normalize_status("late") == "Delayed"
    assert normalizer.normalize_status("done") == "Completed"
    assert normalizer.normalize_status(None) == "Unknown"


def test_analytics_computations():
    """Verify metrics calculation logic with mock normalized data records."""
    deals = [
        {"Masked Deal value": 100000.0, "Sector/service": "Mining", "Deal Stage": "Negotiation", "Closure Probability": 80.0},
        {"Masked Deal value": 200000.0, "Sector/service": "Solar", "Deal Stage": "Proposal", "Closure Probability": 50.0}
    ]
    
    work_orders = [
        {"Execution Status": "Completed", "Amount Receivable (Masked)": 50000.0},
        {"Execution Status": "Delayed", "Amount Receivable (Masked)": 25000.0}
    ]
    
    # Calculations
    assert analytics.total_pipeline_value(deals) == 300000.0
    assert analytics.average_deal_size(deals) == 150000.0
    assert analytics.expected_revenue(deals) == 180000.0  # 100k*0.8 + 200k*0.5 = 80k + 100k = 180k
    
    delayed_orders = analytics.delayed_work_orders(work_orders)
    assert len(delayed_orders) == 1
    assert delayed_orders[0]["Amount Receivable (Masked)"] == 25000.0
    
    assert analytics.outstanding_receivables(work_orders) == 75000.0


def test_workflow_execution():
    """Verify that the LangGraph workflow runs successfully without exceptions in demo/mock mode."""
    # Force mock mode
    from tools.monday import monday_client
    monday_client.use_mock_data = True
    
    # Run simple query
    response = run_agent("What is our sales pipeline summary this quarter?", "test-session")
    assert response is not None
    assert "pipeline" in response.lower() or "demo" in response.lower()
