from LLM.app import handle_intent
from .mcp_server import get_available_tools
from .plans import handle_plan
from .orchestrator import handle_orchestrator
from .validation import validate_request
from cache.cache import cache
import logging
import asyncio

async def execute_request(request: dict) -> dict:
    # Step 0: Call the MCP Server to get list of tools
    logging.info("Executing request with MCP workflow...")
    try:
        MCP_Tools = await get_available_tools()    
    # Step 1: Call the intent handler to determine the intent based on the available tools and user request
        intent = await handle_intent(request, MCP_Tools)
        logging.info("Intent determined: %s", intent)
    # Step 2: Pass work to be done to the MCP Server
        result = await handle_orchestrator(request, intent)
    except asyncio.TimeoutError:
        logging.error("Request timed out while getting MCP tools.")
        return {"error": "Request timed out."} 
    except Exception as e:
        logging.error("Error occurred while getting MCP tools: %s", e)
        return {"error": "Failed to retrieve MCP tools."}

    return result
