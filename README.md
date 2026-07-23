# Monday.com Business Intelligence Agent

An AI-powered Business Intelligence (BI) agent built with **FastAPI**, **LangGraph**, and **Streamlit** designed to answer founder-level analytical questions by querying and joining Monday.com Deals and Work Orders board records dynamically.

## 🚀 Deployment & Live Demos

The application is deployed across cloud architectures for production testing:
* **Frontend Dashboard (Streamlit Cloud):** [skylark-drones-technical-assignment-ikbpbtjfutdue3gtp7a7jr.streamlit.app](https://skylark-drones-technical-assignment-ikbpbtjfutdue3gtp7a7jr.streamlit.app/)
* **Backend API (Render Cloud):** [skylark-drones-technical-assignment.onrender.com](https://skylark-drones-technical-assignment.onrender.com)

---

## 📌 Features

* **Conversational Interface:** Multi-turn conversation capability using LangGraph's native `MemorySaver` checkpointer.
* **Resilient Key Extraction:** Custom fuzzy case-insensitive substring lookup algorithm to robustly handle inconsistent column names in imported boards.
* **Smart Ambiguity Flow:** Non-blocking query resolution (e.g. defaulting to overall time periods when ambiguous, rather than blocking conversation).
* **Caching Layer:** TTLCache decorators to cache Monday.com GraphQL queries to speed up execution and preserve API quota.
* **Offline / Demo Mode:** Seamless runtime toggle to test queries locally using backup CSV copies (`data/deals.csv` and `data/work_orders.csv`) without credentials or internet access.
* **Executive KPI Dashboard:** Visual representations of Pipeline Value, Expected Revenue, Average Deal Size, outstanding receivables, sector contributions, and stage charts.

---

## 🧠 Detailed Agent Subsystems

The BI Assistant uses specialized agent subsystems coordinated within a LangGraph workflow:

1. **Query Parser Agent ([tools/parser.py](file:///c:/Users/naikr/OneDrive/Desktop/ASSIGNMENT_skylark/tools/parser.py)):** Parses the user's raw query to extract key intent attributes (deal stages, timeframes, or sectors) deterministically. It handles ambiguity by defaulting parameters to sensible stand-ins rather than blocking.
2. **Monday Data Sync Agent ([tools/monday.py](file:///c:/Users/naikr/OneDrive/Desktop/ASSIGNMENT_skylark/tools/monday.py) & [services/normalize.py](file:///c:/Users/naikr/OneDrive/Desktop/ASSIGNMENT_skylark/services/normalize.py)):** Interacts with Monday.com GraphQL API. It features case-insensitive fuzzy key resolution to match messy board column headers (e.g. matching `"Masked Deal value"` to `"Masked Deal Value"`).
3. **Financial Analytics Agent ([tools/analytics.py](file:///c:/Users/naikr/OneDrive/Desktop/ASSIGNMENT_skylark/tools/analytics.py)):** Computes pipeline totals, averages, delays, and outstanding receivables. It maps qualitative CRM indicators (`"High"`, `"Medium"`, `"Low"`) to numeric probabilities (`80%`, `50%`, `20%`) to guarantee accurate expected revenue totals.
4. **Insight Generator Agent ([llm/client.py](file:///c:/Users/naikr/OneDrive/Desktop/ASSIGNMENT_skylark/llm/client.py)):** Takes the computed mathematical summaries, blends them with conversational history retrieved by the checkpointer, and drafts high-level founder bullet points highlighting business opportunities and cash flow risks.

---

## ⚙️ Architecture Overview

The system is constructed with a decoupled modular architecture:

```
                  ┌──────────────────────────────┐
                  │      Streamlit Frontend      │
                  │  (Dashboard + Chat Interface)│
                  └──────────────┬───────────────┘
                                 │ HTTP API requests
                  ┌──────────────▼───────────────┐
                  │       FastAPI Backend        │
                  │ (Endpoints + Session Memory) │
                  └──────────────┬───────────────┘
                                 │ Workflow invocation
                  ┌──────────────▼───────────────┐
                  │      LangGraph Workflow      │
                  │  (Parser -> Monday -> BI)    │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌─────────────────┐                             ┌─────────────────┐
│  Mistral / LLM  │                             │   Monday.com    │
│  Client Agent   │                             │  GraphQL API /  │
│  (Insights Gen) │                             │   Local CSVs    │
└─────────────────┘                             └─────────────────┘
```

1. **Streamlit Frontend (`app.py`):** Serves tabbed panels for Conversational BI, KPI visuals, and Connection Setup, with a persistent sidebar Live Status panel.
2. **FastAPI Backend (`api.py`):** Exposes `/chat`, `/analytics`, `/sessions`, and `/history` endpoints, managing checkpointer states natively.
3. **LangGraph Workflow (`agent/workflow.py`):** Runs a compiled graph state:
   - **`parse_question`:** Resolves intent parameters and initiates empty memory contexts.
   - **`fetch_data`:** Interacts with `monday_client` (API or fallback CSV loader) and cleans data.
   - **`analytics`:** Computes financials, receivables, and milestones.
   - **`generate_response`:** Blends history with analytics variables to draft insights using `llm_client`.
4. **Checkpointer Memory (`MemorySaver`):** Saves and restores the complete graph execution states based on a `thread_id` session context.

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.10 to 3.13
* Virtual environment tool (`venv` or `uv`)

### 1. Clone the repository and install requirements
Ensure you are inside the project root directory and run:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the parameters:

```env
# LLM Key (Mistral API key is primary)
MISTRAL_API_KEY=your_mistral_api_key

# Monday.com Config
MONDAY_API_TOKEN=your_monday_personal_access_token
MONDAY_API_URL=https://api.monday.com/v2

# Board IDs (Retrieved from Monday.com board URLs)
DEALS_BOARD_ID=5030147989
WORK_ORDERS_BOARD_ID=5030148020

# Server bindings
HOST=0.0.0.0
PORT=8000
```

---

##  Monday.com Setup Guide

To load the sample data into Monday.com:

1. **Import Deals CSV:**
   - On Monday.com, click **Add** (Workspace sidebar) -> **Import Data** -> **Excel/CSV**.
   - Upload `Deal funnel Data.xlsx - Deal tracker.csv` from your computer.
   - Designate the first row as the header and configure the columns:
     - `Deal Name` -> **Name** type
     - `Deal Stage` -> **Status** type
     - `Masked Deal value` -> **Numbers** type
     - `Closure Probability` -> **Numbers** type
     - `Sector/service` -> **Text** type
2. **Import Work Orders CSV:**
   - Upload `Work_Order_Tracker Data.xlsx - work order tracker.csv` in the same way.
   - Skip leading empty lines if prompted, and map the column headers:
     - `Deal name masked` -> **Name** type
     - `Execution Status` -> **Status** type
     - `Amount Receivable (Masked)` -> **Numbers** type
3. **Retrieve Board IDs:**
   - Open each board in your browser. The board ID is the long numeric string in the URL: `https://yourspace.monday.com/boards/BOARD_ID`.
   - Copy these IDs and update `DEALS_BOARD_ID` and `WORK_ORDERS_BOARD_ID` in your `.env` file.

---

## 🚀 Running the Application

### 1. Start the API backend
Run the FastAPI backend on port `8000`:
```bash
python api.py
```
Check health at `http://127.0.0.1:8000/health`.

### 2. Start the Streamlit frontend
In a separate terminal (with virtualenv activated), launch Streamlit:
```bash
streamlit run app.py
```
Access the dashboard in your browser at `http://localhost:8501`.

---

## 🧪 Testing

We have built a test suite to assert the correctness of normalizations, metrics calculations, fuzzy key lookups, and graph traversals.

Run the tests using `pytest`:
```bash
pytest
```
