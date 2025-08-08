import httpx
import json
from typing import Dict, Any

async def get_agents_to_use_endpoint(request: Dict[str, Any], agent_cards: Dict[str, Any]) -> str:
    """
    Retrieves the available tools from the MCP Server using a POST request.
    Returns:
        dict: The intent as returned by the plans API.
    """
    TEST_MCP_SERVER_API = "http://localhost:8001/LLM/agents_to_use"
    
    json_payload = {
        "request": request.get("user_query", ""),
        "agent_cards": agent_cards
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(TEST_MCP_SERVER_API, json=json_payload)
        response.raise_for_status()
        return response.json()