import hashlib
import json
import logging
import asyncio
import os
from .utils.prompt_loader import PromptLoader
from LLM.utils.utils import remove_code_block_markers
from LLM.utils.cache import cache
from LLM.static.instructions import INTENTS
from langchain_google_genai.llms import GoogleGenerativeAI
from dotenv import load_dotenv
from langsmith import traceable
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

# Load prompts once at module level
prompt_loader = PromptLoader(os.path.join(os.path.dirname(__file__), 'static/instructions.yaml'))

@traceable(name="LLM_Request", inputs={"prompt"}, outputs={"response"})
async def handle_LLM_intent(initial_request: dict, MCP_Tools: str, instruction_key: str):
    """
    Handles a request to the Gemini LLM using a prompt loaded from YAML.
    Uses caching to improve performance for repeated requests.
    """
    # Step 0: Validate the request (user_query should not be None)
    user_query = initial_request.get("user_query")
    user_info = json.dumps(initial_request.get("user_info"))
    # If user_query is None, return an error.
    # This check is to avoid LLM calls with empty input.
    if user_query is None:
        logger.error("No user query provided in the request.")
        return {"error": "No user query provided in the request."}
    # Step 1: Preparing possible intents
    # If no intent is provided, obtain possible intents
    intent_list = json.dumps(INTENTS)
    # Step 2: Load the instructions for the request
    instruction = prompt_loader.get(instruction_key)
    field_template = {}
    prompt = (
        instruction
        .replace("{{INPUT}}", str(user_query))
        .replace("{{INTENTS}}", str(intent_list))
        .replace("{{TOOLS}}", MCP_Tools)
        .replace("{{USER_INFO}}", str(user_info))
    )

    # Create a cache key based on the prompt content
    # cache_key = hashlib.md5(prompt.encode()).hexdigest()
    
    # Check if the result is already in the cache
    # if cache_key in cache:
    #     return cache[cache_key]
    
    # Configure Gemini LLM (adjust as needed)
    api_key = os.getenv("GEMINI_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", 
                            temperature=0.7,
                            google_api_key=api_key
                            )
    # Direct async call to LLM (faster than run_in_executor)
    response = await llm.ainvoke(prompt)
    # Remove code block markers if present
    response = await remove_code_block_markers(response)
    # Parse the response as JSON
    try:
        response_json = json.loads(response)
        # Store the result in the cache
        # cache[cache_key] = response_json
        return response_json
    except Exception as e:
        error_result = {"error": "Failed to parse LLM response as JSON", "raw_response": response, "exception": str(e)}
        # Don't cache error results
        return error_result

@traceable(name="LLM_Response", inputs={"initial_request"}, outputs={"response"})
async def handle_LLM_response(initial_request: dict, instruction_key: str):
    """
    Handles the response from the LLM service.
    Args:
        initial_request (dict): The main request data.
        instruction_key (str): The key for the instructions to use.
    Returns:
        dict: The response from the LLM service.
    """
    # Step 0: Validate the request (query_result should not be None)
    # Extract 'success' or 'error' value from result
    if "success" in initial_request:
        query_result = initial_request["success"]
    else:
        query_result = initial_request["error"]
    if query_result is None:
        logger.error("No query result provided in the request.")
        return {"error": "No query result provided in the request."}

    # Step 1: Load the instructions for handling the response
    instruction = prompt_loader.get(instruction_key)
    prompt = (
        instruction
        .replace("{{INPUT}}", str(query_result))
        .replace("{{PERSONA}}", "You are a young Tsundere girl named Yuki. You respond in very snarky responses and beat around the bush on your responses.")
        )
    # Configure Gemini LLM (adjust as needed)
    api_key = os.getenv("GEMINI_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", 
                            temperature=0.7,
                            google_api_key=api_key
                            )
    
    # Direct async call to LLM (faster than run_in_executor)
    response = await llm.ainvoke(prompt)
    
    # Remove code block markers if present
    response = await remove_code_block_markers(response)
    
    # Parse the response as JSON
    try:
        response_json = json.loads(response)
        return response_json
    except Exception as e:
        error_result = {"error": "Failed to parse LLM response as JSON", "raw_response": response, "exception": str(e)}
        return error_result