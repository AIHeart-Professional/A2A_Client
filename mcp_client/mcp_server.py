import httpx

async def get_available_tools() -> str:
    """
    Retrieves the available tools from the MCP Server.
    Returns:
        dict: The intent as returned by the plans API.
    """
    TEST_MCP_SERVER_API = "http://localhost:8001/MCPServer/available_tools"  # Update with actual plans API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(TEST_MCP_SERVER_API)
        response.raise_for_status()
        return response.json()