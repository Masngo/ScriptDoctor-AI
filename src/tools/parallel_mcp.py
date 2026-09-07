import os
import httpx
from typing import Dict, Any, List

class ParallelSearchTool:
    """Parallel Search MCP client for low-latency web research."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PARALLEL_API_KEY", "")
        # Parallel Search MCP Endpoint
        self.mcp_url = "https://search.parallel.ai/mcp"

    async def execute_search(self, objective: str, search_queries: List[str]) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {
                    "objective": objective,
                    "search_queries": search_queries,
                    "max_results": 3,
                    "excerpts": {"max_chars_per_result": 1200}
                }
            }
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            try:
                response = await client.post(self.mcp_url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Parallel API status: {response.status_code}"}
            except Exception as e:
                return {"error": f"Parallel Search failed: {str(e)}"}
