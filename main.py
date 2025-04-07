from mcp.server.fastmcp import FastMCP
import httpx
from typing import Any

mcp = FastMCP("weather-alerts")

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
    url = f"{NWS_API_BASE}/alerts/active?area={area}"
    data = await make_nws_request(url)
    if not data or 'features' not in data:
        return "No active alerts found or unable to retrieve data."
    alerts = [format_alert(f) for f in data['features']]
    return "\n\n".join(alerts)

@mcp.tool()
async def get_forecast(location: str) -> str:
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

# ✅ Correct server launch for jlowin/fastmcp
if __name__ == "__main__":
    mcp.serve()
