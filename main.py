from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

# Initialize MCP server
mcp = FastMCP("weather-alerts")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "azure-mcp-demo/1.0"

# Helper function to make HTTP request to weather.gov
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

# Format weather alert nicely
def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
"""

# Tool: Get active weather alerts by state
@mcp.tool()
async def get_alerts(area: str) -> str:
    url = f"{NWS_API_BASE}/alerts/active?area={area}"
    data = await make_nws_request(url)
    if not data or 'features' not in data:
        return "No active alerts found or unable to retrieve data."
    alerts = [format_alert(f) for f in data['features']]
    return "\n\n".join(alerts)

# Tool: Get 3-part forecast by lat/lng
@mcp.tool()
async def get_forecast(location: str) -> str:
    """
    Retrieve weather forecast for a given location (latitude,longitude).
    Example: "38.8894,-77.0352" (Washington, DC)
    """
    try:
        point_url = f"https://api.weather.gov/points/{location}"
        headers = {"User-Agent": USER_AGENT}

        async with httpx.AsyncClient() as client:
            point_resp = await client.get(point_url, headers=headers)
            point_resp.raise_for_status()
            point_data = point_resp.json()

            forecast_url = point_data["properties"]["forecast"]
            forecast_resp = await client.get(forecast_url, headers=headers)
            forecast_resp.raise_for_status()
            forecast_data = forecast_resp.json()

            periods = forecast_data["properties"]["periods"]
            forecast_text = "\n".join([f"{p['name']}: {p['detailedForecast']}" for p in periods[:3]])

            return forecast_text
    except Exception as e:
        return f"Error retrieving forecast: {e}"

# Let MCP provide the FastAPI app
app = mcp.app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
