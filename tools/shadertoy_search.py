import os
from typing import List, Dict
import requests

def custom_tool(keyword: str, limit: int = 5) -> List[Dict[str, str]]:
    """Search for ShaderToy examples by keyword and return a list of shaders with their name and description."""
    api_url = "https://www.shadertoy.com/api/v1/shaders"
    params = {
        'query': keyword,
        'limit': limit,
        'key': os.getenv('SHADERTOY_API_KEY')  # Use environment variable for API key
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Improved error handling
    json_data = response.json()
    return [
        {'name': shader['info']['name'], 'description': shader['info']['description']}
        for shader in json_data.get('Results', [])
    ]