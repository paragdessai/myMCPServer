from fastapi import FastAPI
from mcp_sdk.server import FastMCP
import httpx
from typing import Any

# Step 1: Create FastAPI app
app = FastAPI()

# Step 2: Create FastMCP instance
mcp = FastMCP(name="weather")  # Just 'name' now, no 'app'

# Step 3: Mount MCP router into FastAPI
app.include_router(mcp.router, prefix="/api")

# -----------------------
# Weather Tools
# -----------------------

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
    """Get active weather alerts by 2-letter state code (e.g., TX, NY)."""
    url = f"{NWS_API_BASE}/alerts/active?area={area}"
    data = await make_nws_request(url)
    if not data or 'features' not in data:
        return "No active alerts found or unable to retrieve data."
    alerts = [format_alert(f) for f in data['features']]
    return "\n\n".join(alerts)

@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get forecast by lat,long. Example: '38.8894,-77.0352' for Washington, DC."""
    try:
        point_url = f"{NWS_API_BASE}/points/{location}"
        headers = {"User-Agent": USER_AGENT}
        async with httpx.AsyncClient() as client:
            point_resp = await client.get(point_url, headers=headers)
            point_resp.raise_for_status()
            forecast_url = point_resp.json()["properties"]["forecast"]

            forecast_resp = await client.get(forecast_url, headers=headers)
            forecast_resp.raise_for_status()
            forecast_data = forecast_resp.json()

            periods = forecast_data["properties"]["periods"]
            return "\n".join(f"{p['name']}: {p['detailedForecast']}" for p in periods[:3])
    except Exception as e:
        return f"Error retrieving forecast: {e}"

# -----------------------
# Optional: For local testing
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
