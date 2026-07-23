"""
FastAPI backend for the Founder Business Intelligence Agent.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from agent.workflow import run_agent, graph

from models.schemas import ChatRequest
from models.responses import (
    ChatResponse,
    HealthResponse,
    ErrorResponse,
    ConversationHistoryResponse,
)

from services.logger import app_logger
from services.history import history_service
from config import settings
from tools.monday import monday_client


app = FastAPI(
    title="Founder Business Intelligence Agent",
    description="AI-powered Business Intelligence Assistant for Monday.com",
    version="1.0.0",
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Root
# ==========================================================

@app.get("/")
def root():
    return {
        "message": "Founder Business Intelligence Agent",
        "version": "1.0.0",
        "docs": "/docs",
    }


# ==========================================================
# Health Check & Configuration
# ==========================================================

@app.get(
    "/health",
    response_model=HealthResponse,
)
def health():
    return HealthResponse(
        status="healthy",
        service="Founder Business Intelligence Agent",
        version="1.0.0",
    )


@app.get("/settings")
def get_settings():
    return {
        "deals_board_id": settings.DEALS_BOARD_ID,
        "work_orders_board_id": settings.WORK_ORDERS_BOARD_ID,
        "mock_mode": monday_client.use_mock_data,
        "cache_size": monday_client.health()
    }


@app.post("/settings/toggle-mock")
def toggle_mock(mock: bool = Body(..., embed=True)):
    monday_client.use_mock_data = mock
    app_logger.info(f"Toggled Mock Mode to: {mock}")
    return {"success": True, "mock_mode": monday_client.use_mock_data}


@app.post("/settings/clear-cache")
def clear_cache():
    from services.cache import cache_service
    cache_service.clear()
    app_logger.info("Cleared caching service entries.")
    return {"success": True, "message": "Cache cleared successfully"}


@app.get("/analytics")
def get_analytics():
    try:
        deals = monday_client.get_deals()
        work_orders = monday_client.get_work_orders()
        
        from services.normalize import normalizer
        norm_deals = normalizer.normalize_records(deals)
        norm_work_orders = normalizer.normalize_records(work_orders)
        
        from tools.analytics import analytics
        summary = analytics.leadership_summary(norm_deals, norm_work_orders)
        
        from datetime import datetime
        return {
            "success": True,
            "metrics": summary,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        app_logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Chat Endpoint
# ==========================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        500: {
            "model": ErrorResponse
        }
    },
)
def chat(request: ChatRequest):
    try:
        app_logger.info(f"Received Question: {request.question}")

        session_id = request.session_id
        if not session_id or not history_service.session_exists(session_id):
            session_id = history_service.create_session()
            app_logger.info(f"Created new session catalog: {session_id}")

        # Run agent: LangGraph MemorySaver loads and saves conversation states based on session_id
        answer = run_agent(request.question, session_id)

        return ChatResponse(
            success=True,
            response=answer,
            session_id=session_id,
        )

    except Exception as e:
        app_logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# History Endpoints (Resolves directly to LangGraph Memory)
# ==========================================================

@app.get(
    "/history/{session_id}",
    response_model=ConversationHistoryResponse,
)
def get_session_history(session_id: str):
    if not history_service.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session catalog record not found")
        
    config = {"configurable": {"thread_id": session_id}}
    state = graph.get_state(config)
    history = state.values.get("history", []) if state.values else []
    
    return ConversationHistoryResponse(
        success=True,
        session_id=session_id,
        history=history,
    )


@app.delete("/history/{session_id}")
def clear_session_history(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    # Native update_state to reset the history list inside the checkpoint
    graph.update_state(config, {"history": []})
    
    return {"success": True, "message": "Session history cleared in LangGraph MemorySaver"}


@app.get("/sessions")
def list_sessions():
    return {"sessions": history_service.list_sessions()}


# ==========================================================
# Startup
# ==========================================================

@app.on_event("startup")
def startup():
    app_logger.info("Founder BI Agent API Started")


# ==========================================================
# Shutdown
# ==========================================================

@app.on_event("shutdown")
def shutdown():
    app_logger.info("Founder BI Agent API Stopped")


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )