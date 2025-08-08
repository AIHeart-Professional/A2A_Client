from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
from a2a_client.app import execute_request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Application Setup ---

app = FastAPI(title="Discord RP Bot MCP Server API")


@app.on_event("startup")
async def startup_event():
    """Handles application startup logic: connect to DB and initialize services."""
    global rag_service, data_service, interpreter, llm_service
    logging.info("Application startup...")

@app.on_event("shutdown")
async def shutdown_event():
    """Handles application shutdown logic: close DB connection."""
    logging.info("Application shutdown...")

# --- API Models and Endpoints ---
class UserInfo(BaseModel):
    user_id: str
    server_id: str
    
class QueryRequest(BaseModel):
    user_query: str
    user_info: UserInfo
    
@app.post("/MCPClient/requestHandler")
async def interpret_query(request: QueryRequest):
    """
    API endpoint to interpret a user query using the MCP workflow.
    """
    # Route the request through the MCP interpreter
    response = await execute_request(request.model_dump())
    return response
