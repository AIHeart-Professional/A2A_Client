import httpx
import json
from typing import Dict, Any

async def get_available_tools(agents: Dict[str, Any], tools: Dict[str, Any]) -> str:
    """
    Retrieves the available tools from the MCP Server using a POST request.
    Returns:
        dict: The intent as returned by the plans API.
    """
    TEST_MCP_SERVER_API = "http://localhost:8001/MCPServer/available_tools"
    
    json_payload = {
        "agents": agents,
        "tools": tools
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(TEST_MCP_SERVER_API, json=json_payload)
        response.raise_for_status()
        return response.json()
    
async def get_available_intents() -> str:
    """
    Retrieves the available intents from the MCP Server.
    Returns:
        dict: The intent as returned by the plans API.
    """
    TEST_MCP_SERVER_API = "http://localhost:8001/MCPServer/available_intents"  # Update with actual plans API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(TEST_MCP_SERVER_API)
        response.raise_for_status()
        return response.json()