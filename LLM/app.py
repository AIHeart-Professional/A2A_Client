from LLM.llm_service import handle_LLM_intent, handle_LLM_response

async def handle_intent(request: dict, MCP_Tools: str) -> dict:
    """
    Executes a request to the LLM in order to determine the users intent
    Args:
        user_query (dict): Contains 'id' and 'request' fields.
    Returns:
        dict: The result of the plan execution.
    """
    # Step 0: Validate the request (placeholder, implement as needed)
    # Step 1: Call the LLM service
    result = await handle_LLM_intent(request.get("initial_request"), MCP_Tools, "intent_handler_instructions")    
    return result

async def handle_response(request: dict) -> dict:
    """
    Handles the response from the LLM service.
    Args:
        request (dict): The main request data.
        MCP_Tools (str): The available tools from the MCP Server.
    Returns:
        dict: The response from the LLM service.
    """
    # Step 0: Validate the request (placeholder, implement as needed)
    # Step 1: Call the LLM service to handle the response
    result = await handle_LLM_response(request, "response_handler_instructions")
    return result