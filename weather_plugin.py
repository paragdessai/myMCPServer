from fastmcp.plugin import Plugin, PluginResponse
import requests
import os
import json

class WeatherPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="weather-plugin",
            description="Returns weather using JSON-RPC with method 'getWeather'"
        )

    def run(self, input_text: str) -> PluginResponse:
        try:
            data = json.loads(input_text)
            if data.get("method") != "getWeather":
                raise ValueError("Unsupported method")
            location = data.get("params", {}).get("location")
            if not location:
                raise ValueError("Missing location")
            return self._get_weather_jsonrpc(location, data.get("id"))
        except Exception as e:
            return PluginResponse(text=json.dumps({
                "jsonrpc": "2.0",
                "error": { "code": -32602, "message": str(e) },
                "id": data.get("id") if 'data' in locals() else None
            }))

    def _get_weather_jsonrpc(self, location: str, request_id) -> PluginResponse:
        api_key = os.getenv("WEATHER_API_KEY", "your-api-key-here")
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return PluginResponse(text=json.dumps({
                "jsonrpc": "2.0",
                "error": { "code": -32000, "message": data["error"]["message"] },
                "id": request_id
            }))

        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        city = data["location"]["name"]
        country = data["location"]["country"]

        result = {
            "jsonrpc": "2.0",
            "result": f"The weather in {city}, {country} is {condition} with {temp}°C.",
            "id": request_id
        }

        return PluginResponse(text=json.dumps(result))
