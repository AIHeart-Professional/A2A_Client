import yaml
from LLM.llm_service import handle_LLM_request, handle_LLM_response

async def handle_intent(request: dict, intent: str) -> dict:
    """
    Executes a request to the LLM in order to determine the users intent
    Args:
        user_query (dict): Contains 'id' and 'request' fields.
    Returns:
        dict: The result of the plan execution.
    """
    # Step 0: Validate the request (placeholder, implement as needed)
    # Step 1: Call the LLM service
    result = await handle_LLM_request(request.get("initial_request"), "intent_handler_instructions", intent)
    return result

async def handle_tools(request: dict, intent: dict, tools: dict) -> dict:
    """
    Handles the tools based on the intent and available tools.
    Args:
        request (dict): The main request data.
        intent (dict): The determined intent.
        MCP_Tools (str): The available tools from the MCP Server.
    Returns:
        dict: The updated intent with additional fields.
    """
    # Step 0: Validate the request (placeholder, implement as needed)
    # Step 1: Call the LLM service to handle the tools
    result = await handle_LLM_request(request.get("initial_request"), "tools_handler_instructions", intent, yaml.dump(tools))
    return result

async def handle_response(response: dict) -> dict:
    """
    Handles the response from the LLM service.
    Args:
        request (dict): The main request data.
        MCP_Tools (str): The available tools from the MCP Server.
    Returns:
        dict: The response from the LLM service.
    """
    # Step 1: Call the LLM service to handle the response
    result = await handle_LLM_response(response, "response_handler_instructions")
    return result