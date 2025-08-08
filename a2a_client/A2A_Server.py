import httpx
import json
from typing import Dict, Any

async def get_agent_cards_endpoint() -> str:
    """
    Retrieves the available agent cards from the MCP Server.
    Returns:
        dict: The agent cards as returned by the A2A API.
    """
    TEST_A2A_SERVER_API = "http://localhost:8001/A2A/agent.json"  # Update with actual plans API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(TEST_A2A_SERVER_API)
        response.raise_for_status()
        return response.json()
    
async def get_instructions_endpoint() -> Dict[str, Any]:
    """
    Retrieves the instructions from the MCP Server.
    Returns:
        dict: The instructions as returned by the MCP Server.
    """
    TEST_MCP_SERVER_API = "http://localhost:8001/A2A/instructions"  # Update with actual instructions API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(TEST_MCP_SERVER_API)
        response.raise_for_status()
        data = response.json()
    
    if isinstance(data, dict):
        return data