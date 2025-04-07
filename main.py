from fastapi import FastAPI
from fastmcp.server import MCPServer
from weather_plugin import WeatherPlugin
from joke_plugin import JokePlugin

app = FastAPI()
mcp_server = MCPServer(plugins=[WeatherPlugin(), JokePlugin()])
app.include_router(mcp_server.router, prefix="/api")
