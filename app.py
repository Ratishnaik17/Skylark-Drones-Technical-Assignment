import os
import requests
import pandas as pd
import streamlit as st

from config import settings

# Resolve API URL dynamically (prefer local server if running, fallback to Render cloud)
BASE_API_URL = "https://skylark-drones-technical-assignment.onrender.com"
try:
    # Quick low-timeout check for local server
    import requests as req_check
    local_health = req_check.get("http://127.0.0.1:8000/health", timeout=0.8)
    if local_health.status_code == 200:
        BASE_API_URL = "http://127.0.0.1:8000"
except Exception:
    pass

API_URL = f"{BASE_API_URL}/chat"


# -------------------------------------------------------------
# Page Configuration & Styles
# -------------------------------------------------------------

st.set_page_config(
    page_title="Founder BI Agent - Skylark Drones",
    page_icon="📊",
    layout="wide",
)

# Custom premium styling system - Outfit font, glassmorphism, card border indicators, and transitions
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Main Background & Fonts */
    .stApp {
        background-color: #0d111a;
        color: #f1f5f9;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Custom Slim Header Navbar */
    .header-container {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        padding: 1rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .header-title {
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #64748b !important;
        font-size: 0.88rem;
        margin: 0;
        font-weight: 500;
        border-left: 1px solid rgba(255, 255, 255, 0.15);
        padding-left: 0.75rem;
    }
    .header-badge {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 0.72rem;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Premium KPI Widget Cards */
    .kpi-container {
        display: flex;
        gap: 1.25rem;
        margin-bottom: 2.5rem;
        flex-wrap: wrap;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        flex: 1;
        min-width: 210px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 12px 30px rgba(56, 189, 248, 0.15);
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: #38bdf8;
        border-radius: 5px 0 0 5px;
    }
    .kpi-card.expected::after {
        background: #34d399;
    }
    .kpi-card.delayed::after {
        background: #f87171;
    }
    .kpi-card.receivable::after {
        background: #fb923c;
    }
    .kpi-title {
        color: #64748b;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 1.7rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .kpi-trend {
        font-size: 0.72rem;
        margin-top: 0.4rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #070a13 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Tab Navigation Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        font-weight: 600;
        color: #64748b !important;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-color: #38bdf8 !important;
    }
    
    /* Custom Chat Bubbles - Glassmorphism */
    .stChatMessage {
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 16px !important;
        margin-bottom: 1rem !important;
        padding: 1.25rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        border-left: 3px solid #38bdf8 !important;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        border-left: 3px solid #818cf8 !important;
    }
    
    /* Button styles */
    .stButton>button {
        background-color: #1e293b;
        color: #f1f5f9;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        transition: all 0.2s;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #0f172a;
        border-color: #38bdf8;
        color: #38bdf8;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------
# API Helper Methods
# -------------------------------------------------------------

def api_toggle_mock(mock_status: bool):
    try:
        resp = requests.post(f"{BASE_API_URL}/settings/toggle-mock", json={"mock": mock_status})
        return resp.json()
    except Exception:
        return None

def api_clear_cache():
    try:
        resp = requests.post(f"{BASE_API_URL}/settings/clear-cache")
        return resp.json()
    except Exception:
        return None

def api_get_settings():
    try:
        resp = requests.get(f"{BASE_API_URL}/settings")
        return resp.json()
    except Exception:
        return {}

def api_get_analytics():
    try:
        resp = requests.get(f"{BASE_API_URL}/analytics")
        return resp.json()
    except Exception:
        return {}


# -------------------------------------------------------------
# Cached Top-level Analytics Fetch
# -------------------------------------------------------------

@st.cache_data(ttl=30)
def get_cached_analytics():
    return api_get_analytics()


# -------------------------------------------------------------
# Initialize Session States
# -------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "mock_mode" not in st.session_state:
    # Read initial setting or default to False
    init_settings = api_get_settings()
    st.session_state.mock_mode = init_settings.get("mock_mode", False)


# -------------------------------------------------------------
# Header Layout (Sleek Compact Navbar)
# -------------------------------------------------------------

st.markdown(
    """
    <div class="header-container">
        <div class="header-left">
            <h1 class="header-title">📊 Founder BI Agent</h1>
            <p class="header-subtitle">Real-time Monday.com Conversational Intelligence</p>
        </div>
        <div class="header-badge">CLOUD DEPLOYED</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------
# Sidebar Navigation and Control Panel
# -------------------------------------------------------------

# Fetch analytics for sidebar live status
top_analytics = get_cached_analytics()

with st.sidebar:
    # Clean styled text header instead of broken image link
    st.markdown(
        """
        <div style="text-align: center; padding: 1.2rem 0; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
            <h2 style="color: #38bdf8; margin: 0; font-weight: 800; letter-spacing: 0.5px; font-size: 1.6rem; font-family: 'Outfit', sans-serif;">🏢 Monday.com</h2>
            <p style="color: #64748b; font-size: 0.72rem; text-transform: uppercase; margin-top: 0.2rem; letter-spacing: 1.5px; font-weight: 600;">BI Intelligence Agent</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Live Pipeline Status Widget (Visible if API server is connected)
    if top_analytics.get("success"):
        metrics = top_analytics.get("metrics", {})
        pipeline_val = metrics.get("pipeline_value", 0.0)
        expected_rev = metrics.get("expected_revenue", 0.0)
        delayed_p = metrics.get("delayed_projects", 0)
        
        st.markdown(
            f"""
            <div style="background: rgba(56, 189, 248, 0.04); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 12px; padding: 0.95rem; margin-bottom: 1.2rem; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                <div style="color: #38bdf8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
                    <span style="display:inline-block; width: 6.5px; height: 6.5px; background: #34d399; border-radius: 50%; animation: pulse 2s infinite;"></span>
                    📊 Live Pipeline Status
                </div>
                <div style="font-size: 0.8rem; margin-bottom: 0.3rem; color: #94a3b8;">Pipeline: <span style="color: #f8fafc; font-weight:600;">₹{pipeline_val:,.0f}</span></div>
                <div style="font-size: 0.8rem; margin-bottom: 0.3rem; color: #94a3b8;">Expected: <span style="color: #34d399; font-weight:600;">₹{expected_rev:,.0f}</span></div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Delays: <span style="color: #f87171; font-weight:600;">{delayed_p} Work Orders</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(248, 113, 113, 0.05); border: 1px solid rgba(248, 113, 113, 0.2); border-radius: 12px; padding: 0.95rem; margin-bottom: 1.2rem; text-align: center;">
                <div style="color: #f87171; font-size: 0.72rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">
                    ⚠️ Pipeline Offline
                </div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.2rem;">Cannot reach API server</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("⚙️ Control Panel")
    
    # Toggle Mock/Offline Demo Mode
    mock_mode = st.toggle("Offline / Demo Mode", value=st.session_state.mock_mode, 
                          help="If enabled, reads local CSV copies directly instead of fetching from Monday.com API.")
    
    if mock_mode != st.session_state.mock_mode:
        st.session_state.mock_mode = mock_mode
        api_toggle_mock(mock_mode)
        st.toast(f"Switched to {'Offline Demo' if mock_mode else 'Live API'} Mode", icon="🔄")
        st.cache_data.clear()

    # Clear cache button
    if st.button("🧹 Clear API Cache", use_container_width=True):
        api_clear_cache()
        st.toast("Monday.com API Caching Cleared!", icon="🧼")
    
    st.divider()

    st.subheader("💬 Chat Control")
    
    # Toggle clean up actions
    col_new, col_del = st.columns(2)
    with col_new:
        if st.button("➕ New Chat", use_container_width=True, help="Start a new chat session"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.toast("New conversation session started", icon="💬")
            st.rerun()
            
    with col_del:
        if st.button("🗑️ Delete", use_container_width=True, help="Delete current conversation from memory"):
            if st.session_state.session_id:
                try:
                    requests.delete(f"{BASE_API_URL}/history/{st.session_state.session_id}")
                    st.toast("Session deleted from LangGraph memory", icon="🗑️")
                except Exception:
                    pass
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

    # Dynamic Session Selector (Reads from LangGraph thread list catalog)
    try:
        sessions_resp = requests.get(f"{BASE_API_URL}/sessions")
        if sessions_resp.ok:
            session_list = sessions_resp.json().get("sessions", [])
            if session_list:
                options = ["-- Active Thread --"] + session_list
                
                # Check currently selected option index
                current_idx = 0
                if st.session_state.session_id in session_list:
                    current_idx = session_list.index(st.session_state.session_id) + 1
                    
                selected_opt = st.selectbox(
                    "Switch Session", 
                    options=options, 
                    index=current_idx,
                    help="Switch between past thread histories retrieved from backend checkpointer."
                )
                
                if selected_opt == "-- Active Thread --":
                    if st.session_state.session_id is not None:
                        st.session_state.session_id = None
                        st.session_state.messages = []
                        st.rerun()
                elif selected_opt != st.session_state.session_id:
                    st.session_state.session_id = selected_opt
                    # Load chat history from backend checkpointer state
                    hist_resp = requests.get(f"{BASE_API_URL}/history/{selected_opt}")
                    if hist_resp.ok:
                        history_data = hist_resp.json().get("history", [])
                        st.session_state.messages = history_data
                    st.rerun()
    except Exception:
        pass

    st.divider()
    
    st.subheader("💡 Example Questions")

    examples = [
        "Summarize our current sales pipeline.",
        "Which sector has the highest pipeline value?",
        "Show delayed work orders.",
        "What is our total outstanding receivable amount?",
        "How many deals are in negotiation?",
        "Give me a founder summary.",
    ]

    for question in examples:
        if st.button(question, key=f"ex_{question}", use_container_width=True):
            # Save query in session state and rerun to process it correctly in the main loop
            st.session_state.button_query = question
            st.rerun()


# -------------------------------------------------------------
# Main Application Content Tabs
# -------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["💬 BI Conversation Agent", "📊 Leadership KPI Dashboard", "⚙️ Integration Setup & Status"])

# =============================================================
# TAB 1: BI Conversation Agent
# =============================================================
with tab1:
    st.markdown("### Ask Business Intelligence Questions")
    
    # Render connection/wake-up options only before the conversation starts AND when the backend is offline
    if not st.session_state.messages and not top_analytics.get("success"):
        st.info("💡 **API Server Connection Notice:** Your cloud backend on Render sleep-cycles when idle. If the sidebar status shows offline, click the button below to wake it up and synchronize the live Monday.com pipeline data.")
        if st.button("🔄 Connect & Sync Cloud Server", key="wake_up_server_btn", use_container_width=True):
            with st.spinner("Connecting to Render Cloud... Waking up server container (takes 30-45 seconds)..."):
                try:
                    # Clear Streamlit cache to force fetch
                    st.cache_data.clear()
                    # Ping backend endpoints to wake it up (with a long timeout)
                    health_check = requests.get(f"{BASE_API_URL}/health", timeout=60)
                    if health_check.ok:
                        # Fetch analytics to populate cache
                        requests.get(f"{BASE_API_URL}/analytics", timeout=60)
                        st.success("🟢 Connected! Server is awake and live pipeline data has synced successfully.")
                        st.toast("Cloud server connected!", icon="🟢")
                        st.rerun()
                    else:
                        st.error("🔴 Server responded with an error. Please try again.")
                except Exception as e:
                    st.error(f"🔴 Could not establish connection to the server: {str(e)}")
        st.divider()
        
    # Render chat history with customized clean avatars
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Resolve new queries (handles both text input and button clicks)
    user_query = None

    chat_prompt = st.chat_input("Ask a business question about pipeline values, delays, or sectors...")
    if chat_prompt:
        user_query = chat_prompt
    elif "button_query" in st.session_state and st.session_state.button_query:
        user_query = st.session_state.button_query
        del st.session_state.button_query

    # Process new user query
    if user_query:
        # Append and display user message instantly
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
            
        # Query API backend and render response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing Monday.com data..."):
                try:
                    payload = {
                        "question": user_query,
                        "session_id": st.session_state.session_id
                    }
                    response = requests.post(API_URL, json=payload, timeout=120)
                    response.raise_for_status()
                    
                    result = response.json()
                    answer = result.get("response", "Could not format response.")
                    st.session_state.session_id = result.get("session_id")
                    
                except Exception as e:
                    answer = f"❌ **Error executing query:**\n\n`{str(e)}`\n\nEnsure that the API server is running (`api.py` on port 8000)."
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()


# =============================================================
# TAB 2: Leadership KPI Dashboard
# =============================================================
with tab2:
    st.markdown("### Executive Performance Dashboard")
    
    # Refresh dashboard button
    if st.button("🔄 Refresh Data", key="refresh_dashboard"):
        st.cache_data.clear()
        st.rerun()
        
    # We use top_analytics fetched earlier to speed up tab load times
    analytics_data = top_analytics
        
    if analytics_data.get("success"):
        metrics = analytics_data.get("metrics", {})
        
        # Format display variables
        pipeline_val = metrics.get("pipeline_value", 0.0)
        expected_rev = metrics.get("expected_revenue", 0.0)
        avg_deal = metrics.get("average_deal_size", 0.0)
        delayed_p = metrics.get("delayed_projects", 0)
        outstanding_rec = metrics.get("outstanding_receivables", 0.0)
        
        # Render Premium KPI Cards via HTML
        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-card">
                    <div class="kpi-title">💼 Total Pipeline</div>
                    <div class="kpi-value">₹{pipeline_val:,.2f}</div>
                    <div class="kpi-trend">All Opportunities</div>
                </div>
                <div class="kpi-card expected">
                    <div class="kpi-title">📈 Expected Revenue</div>
                    <div class="kpi-value">₹{expected_rev:,.2f}</div>
                    <div class="kpi-trend">Weighted by Prob.</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">🤝 Avg Deal Size</div>
                    <div class="kpi-value">₹{avg_deal:,.2f}</div>
                    <div class="kpi-trend">Average Value</div>
                </div>
                <div class="kpi-card delayed">
                    <div class="kpi-title">🚨 Delayed Projects</div>
                    <div class="kpi-value" style="color: #f87171;">{delayed_p}</div>
                    <div class="kpi-trend" style="color: #f87171;">Needs Action</div>
                </div>
                <div class="kpi-card receivable">
                    <div class="kpi-title">💰 Receivables</div>
                    <div class="kpi-value" style="color: #fb923c;">₹{outstanding_rec:,.2f}</div>
                    <div class="kpi-trend" style="color: #fb923c;">Outstanding</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Graphical breakdowns
        st.markdown("### Visual Performance Breakdowns")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sector Revenue Contribution")
            rev_by_sec = metrics.get("revenue_by_sector", {})
            if rev_by_sec:
                df_rev = pd.DataFrame(list(rev_by_sec.items()), columns=["Sector", "Revenue (₹)"])
                df_rev = df_rev.sort_values(by="Revenue (₹)", ascending=False)
                st.bar_chart(df_rev.set_index("Sector"), color="#38bdf8")
            else:
                st.info("No sector revenue data available.")
                
        with col2:
            st.subheader("Deals Count by Stage")
            stage_breakdown = metrics.get("deal_stage_breakdown", {})
            if stage_breakdown:
                df_stage = pd.DataFrame(list(stage_breakdown.items()), columns=["Stage", "Count"])
                st.bar_chart(df_stage.set_index("Stage"), color="#818cf8")
            else:
                st.info("No deal stage data available.")
                
        # Second row: Work Order Execution Status
        st.divider()
        col3, col4 = st.columns([2, 1])
        
        with col3:
            st.subheader("Work Orders Execution Status")
            wo_status = metrics.get("work_order_status", {})
            if wo_status:
                df_wo = pd.DataFrame(list(wo_status.items()), columns=["Execution Status", "Total Orders"])
                st.bar_chart(df_wo.set_index("Execution Status"), color="#34d399")
            else:
                st.info("No work order status data available.")
                
        with col4:
            st.subheader("Key Risks & Action Plans")
            st.info(
                f"**Outstanding Receivable Alert:** There is a total of **₹{outstanding_rec:,.2f}** in receivables awaiting collection. "
                "Contact KAM personnel for major customer segments to expedite billings."
            )
            if delayed_p > 0:
                st.error(
                    f"**Execution Risk:** **{delayed_p}** projects are currently flagged as delayed or late. "
                    "This directly impacts billing milestones. Re-allocate operations teams to unblock bottlenecks."
                )
            else:
                st.success("🎉 **Execution Healthy:** All current work orders are executing on schedule.")
                
    else:
        st.error("Failed to load dashboard metrics. Ensure that the FastAPI backend server is running.")


# =============================================================
# TAB 3: Integration Setup & Status
# =============================================================
with tab3:
    st.markdown("### Integration & Connection Management")
    
    server_health = api_get_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monday.com Boards")
        st.markdown(f"**Deals Board ID:** `{settings.DEALS_BOARD_ID}`")
        st.markdown(f"**Work Orders Board ID:** `{settings.WORK_ORDERS_BOARD_ID}`")
        st.markdown(f"**Monday API URL:** `{settings.MONDAY_API_URL}`")
        st.markdown(f"**Host / Port:** `{settings.HOST}:{settings.PORT}`")
        
    with col2:
        st.subheader("Connection Status")
        if server_health:
            st.success("🟢 **FastAPI Backend Server:** Running & Connected")
            
            # Check Monday API health
            conn_status = server_health.get("cache_size", {})
            if "error" in conn_status:
                st.warning(f"🟡 **Monday.com API Connection:** Disconnected ({conn_status.get('error')})")
                st.info("The application will read from local CSV backup files when querying data.")
            elif "status" in conn_status and "Mock" in conn_status.get("status"):
                st.info("🔵 **Monday.com API Connection:** Running in Offline/Demo Mode (reading CSV copies).")
            else:
                st.success("🟢 **Monday.com API Connection:** Connected successfully!")
                if "me" in conn_status:
                    me = conn_status.get("me", {})
                    st.write(f"Connected User: **{me.get('name')}** ({me.get('email')})")
        else:
            st.error("🔴 **FastAPI Backend Server:** Disconnected / Not Running")
            st.info("Please start the backend server using: `python api.py` in your terminal.")
            
    st.divider()
    st.subheader("📁 Data Integrity & Sources")
    st.markdown(
        """
        The agent has access to raw datasets inside the `data/` folder which are loaded if connection to Monday.com fails:
        1. **Deals Data (`data/deals.csv`)**: Contains sales opportunities, owner codes, deal values, probabilities, and closing dates.
        2. **Work Orders Data (`data/work_orders.csv`)**: Contains project implementation data, serial references, execution statuses, and billing updates.
        """
    )