import hashlib
import json
import logging
import asyncio
import os
from .utils.prompt_loader import PromptLoader
from LLM.utils.utils import remove_code_block_markers
from LLM.utils.cache import cache
from langchain_google_genai.llms import GoogleGenerativeAI
from dotenv import load_dotenv
from langsmith import traceable
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

# Load prompts once at module level
prompt_loader = PromptLoader(os.path.join(os.path.dirname(__file__), 'static/instructions.yaml'))


async def _validate_intent_request(initial_request: dict):
    """Validate the initial request for intent handling."""
    user_query = initial_request.get("user_query")
    if not user_query:
        logger.error("No user query provided in the request.")
        raise ValueError("No user query provided in the request.")


async def _prepare_intent_prompt(
    user_query: str, instruction_key: str, intent: str = None, tools: str = None, user_identifiers: dict = None):
    """Prepare the prompt for the LLM intent request. 'intent' and 'tools' are optional."""
    instruction = prompt_loader.get(instruction_key)
    prompt = instruction.replace("{{USER_QUERY}}", user_query)
    if intent is not None:
        prompt = prompt.replace("{{INTENT}}", intent)
    if tools is not None:
        prompt = prompt.replace("{{TOOLS}}", tools)
    if user_identifiers is not None:
        prompt = prompt.replace("{{USER_IDENTIFIERS}}", json.dumps(user_identifiers))
    return prompt


async def _execute_llm_call(prompt: str, model: str):
    """Configure and execute the LLM call."""
    api_key = os.getenv("GEMINI_API_KEY")
    llm = GoogleGenerativeAI(
        model=model, temperature=0.7, google_api_key=api_key
    )
    return await llm.ainvoke(prompt)

async def _convert_to_string(data: dict) -> str:
    """Convert data to string, handling various types."""
    if isinstance(data, (dict, list)):
        return json.dumps(data)
    elif isinstance(data, str):
        return data
    else:
        return str(data)
    
async def _process_llm_response(response: str):
    """Process the raw response from the LLM."""
    response = await remove_code_block_markers(response)
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(
            "Failed to parse LLM response as JSON: %s. Raw response: %s",
            e,
            response,
        )
        return {
            "error": "Failed to parse LLM response as JSON",
            "raw_response": response,
            "exception": str(e),
        }


@traceable(name="LLM_Request", inputs={"prompt"}, outputs={"response"})
async def handle_LLM_request(initial_request: dict, instruction_key: str, intent: str = None, tools: str = None):
    """
    Handles a request to the Gemini LLM by breaking it into smaller steps.
    """
    try:
        await _validate_intent_request(initial_request)
        intent_str = await _convert_to_string(intent)
        prompt = await _prepare_intent_prompt(initial_request.get("user_query"), instruction_key, intent_str, tools, initial_request.get("user_info"))
        response = await _execute_llm_call(prompt, "gemini-1.5-flash")
        return await _process_llm_response(response)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        logger.error("An unexpected error occurred in handle_LLM_request: %s", e)
        return {"error": "An unexpected error occurred."}


@traceable(name="LLM_Response", inputs={"response"}, outputs={"response"})
async def handle_LLM_response(response: dict, instruction_key: str):
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
    if "success" in response:
        query_result = response["success"]
    else:
        query_result = response["error"]
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