from .mcp_server import get_available_tools, get_available_intents
from .orchestrator import handle_orchestrator
from .A2A_Server import get_agent_cards_endpoint, get_instructions_endpoint, handle_request
from .llm import get_agents_to_use_endpoint
from .utils import get_card_descriptions
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
        # MCP-A2A Hybrid
        agent_cards = await get_agent_cards_endpoint()
        print(f"The type of 'card_description' is: {type(agent_cards)}") # This will print the type
        instructions = await get_instructions_endpoint()
        logger.info("Agent cards retrieved: %s", agent_cards)
        agents = await get_agents_to_use_endpoint(request, agent_cards)
        results = await handle_request(request, agent_cards, agents)

        #______________________
       # get_intents = await get_available_intents()
#        intents = await handle_intent(request, get_intents, instructions.get("intent"))
#        get_tools = await get_available_tools(intents.get("agents"), intents.get("tools"))
    # Step 1: Call the intent handler to determine the intent based on the available tools and user request
    #     tools = await handle_tools(request, intents, instructions.get("tools"), get_tools)
    #     logger.info("Intent determined: %s", tools.get("intent"))
    #    logger.info("Tasks determined: %s", tools.get("tasks"))

    # Step 2: Pass work to be done to the MCP Server
    #     result = await handle_orchestrator(request, tools)
    # Steo 3: Send result to the LLM service to handle the response
    #     if result.get("error"):
    #        logger.error("Error in MCP workflow: %s", result.get("error"))
    #        return result
    #    response = await handle_response(result)
    except asyncio.TimeoutError:
        logger.error("Request timed out while getting MCP tools.")
        return {"error": "Request timed out."} 
    except Exception as e:
        logger.error("Error occurred while getting MCP tools: %s", e)
        return {"error": "Failed to retrieve MCP tools."}

    return results.get("response")
