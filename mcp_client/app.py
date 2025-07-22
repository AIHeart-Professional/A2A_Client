from LLM.app import handle_intent, handle_response
from .mcp_server import get_available_tools
from .orchestrator import handle_orchestrator
from cache.cache import cache
import logging
import asyncio
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def execute_request(request: dict) -> dict:
    # Step 0: Call the MCP Server to get list of tools
    logger.info("Executing request with MCP workflow...")
    try:
        MCP_Tools = await get_available_tools()    
    # Step 1: Call the intent handler to determine the intent based on the available tools and user request
        intent = await handle_intent(request, MCP_Tools)
        logger.info("Intent determined: %s", intent)
    # Step 2: Pass work to be done to the MCP Server
        result = await handle_orchestrator(request, intent)
    # Steo 3: Send result to the LLM service to handle the response
        if result.get("error"):
            logger.error("Error in MCP workflow: %s", result.get("error"))
            return result
        response = await handle_response(result)
    except asyncio.TimeoutError:
        logger.error("Request timed out while getting MCP tools.")
        return {"error": "Request timed out."} 
    except Exception as e:
        logger.error("Error occurred while getting MCP tools: %s", e)
        return {"error": "Failed to retrieve MCP tools."}

    return response
