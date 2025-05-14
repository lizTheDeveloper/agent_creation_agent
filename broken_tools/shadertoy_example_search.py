from typing import List, Dict
import requests

@function_tool
def search_shadertoy_examples(keyword: str, limit: int = 5) -> List[Dict[str, str]]:
    """Searches for ShaderToy examples by keyword and returns a list of shaders with their name and description."""
    api_url = "https://www.shadertoy.com/api/v1/shaders"
    params = {
        'query': keyword,
        'limit': limit,
        'key': 'YOUR_API_KEY'  # Replace with a valid ShaderToy API key
    }
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from ShaderToy API")
    json_data = response.json()
    return [
        {'name': shader['info']['name'], 'description': shader['info']['description']}
        for shader in json_data['Results']
    ]