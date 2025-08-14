import httpx
import json
import requests
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

async def handle_request(request: dict, agent_cards: list, agents: dict) -> dict:
    """
    Handles the request by calling the MCP Server to get the available tools and intents.
    Args:
        request (dict): The request to be handled.
    Returns:
        dict: The result of the request handling as returned by the MCP Server.
    """
    TEST_MCP_SERVER_API = "http://localhost:8001/A2A/handle_request_stream"  # Update with actual request API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        async with client.stream('POST', TEST_MCP_SERVER_API, json={
            "request": request, "agent_card": agent_cards, "agents": agents
        }) as response:
            response.raise_for_status()
            
            final_result = None
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    event_data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if event_data['type'] == 'agent_event':
                        print(f"🤖 Agent: {event_data['content']}")
                    elif event_data['type'] == 'complete':
                        print("✅ Processing complete!")
                        # Store the final result if provided in the complete event
                        final_result = {"response": event_data.get('message')}
                        break
            
            # Return the final result collected from the stream
            return final_result

def stream_agent_request(request_data):
    response = requests.post(
        'http://localhost:8001/A2A/handle_request_stream',
        json=request_data,
        stream=True
    )
    
    for line in response.iter_lines():
        if line.startswith(b'data: '):
            event_data = json.loads(line[6:])  # Remove 'data: ' prefix
            
            if event_data['type'] == 'agent_event':
                print(f"🤖 Agent: {event_data['content']}")
            elif event_data['type'] == 'complete':
                print("✅ Processing complete!")
                break
    return response.json()