from fastapi import FastAPI
from fastmcp import FastMCP
import httpx
from typing import Any

app = FastAPI()
mcp = FastMCP(app, name="weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "azure-mcp-demo/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
"""


@mcp.tool()
async def get_alerts(area: str) -> str:
    """
    Get active weather alerts for a given US state (2-letter code).
    Example: "TX" for Texas
    """
    url = f"{NWS_API_BASE}/alerts/active?area={area}"
    data = await make_nws_request(url)
    if not data or 'features' not in data or not data['features']:
        return "No active alerts found or unable to retrieve data."
    alerts = [format_alert(f) for f in data['features']]
    return "\n\n".join(alerts)


@mcp.tool()
async def hello(name: str) -> str:
    """
    Return a simple greeting.
    """
    return f"Hello, {name}! 👋"


# Azure runs this with gunicorn, but you can run locally for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
