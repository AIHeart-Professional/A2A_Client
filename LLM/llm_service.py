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

load_dotenv()

# Load prompts once at module level
prompt_loader = PromptLoader(os.path.join(os.path.dirname(__file__), 'static/instructions.yaml'))

async def handle_gemini_langchain_request(initial_request: dict, MCP_Tools: str, instruction_key: str):
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
        logging.error("No user query provided in the request.")
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
    cache_key = hashlib.md5(prompt.encode()).hexdigest()
    
    # Check if the result is already in the cache
    if cache_key in cache:
        return cache[cache_key]
    
    # Configure Gemini LLM (adjust as needed)
    api_key = os.getenv("GEMINI_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-pro", 
                            temperature=0.7,
                            google_api_key=api_key
                            )
    # Call Gemini asynchronously
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, llm, prompt)
    # Remove code block markers if present
    response = await remove_code_block_markers(response)
    # Parse the response as JSON
    try:
        response_json = json.loads(response)
        # Store the result in the cache
        cache[cache_key] = response_json
        return response_json
    except Exception as e:
        error_result = {"error": "Failed to parse LLM response as JSON", "raw_response": response, "exception": str(e)}
        # Don't cache error results
        return error_result