from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from weather_plugin import WeatherPlugin
from joke_plugin import JokePlugin

app = FastAPI()
mcp = FastMCP("MyMCPServer")

# Register plugins
mcp.include_plugin(WeatherPlugin())
mcp.include_plugin(JokePlugin())

# Include MCP router
app.include_router(mcp.router, prefix="/api")
