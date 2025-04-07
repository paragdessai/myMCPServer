from fastapi import FastAPI
from fastmcp.server import MCPServer
from weather_plugin import WeatherPlugin

app = FastAPI()
mcp_server = MCPServer(plugins=[WeatherPlugin()])
app.include_router(mcp_server.router, prefix="/api")
