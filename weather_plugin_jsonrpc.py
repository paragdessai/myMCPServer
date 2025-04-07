from fastmcp.plugin import Plugin, PluginResponse
import requests
import os
import json

class WeatherPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="weather-plugin",
            description="Get current weather information using either simple text or JSON-RPC"
        )

    def run(self, input_text: str) -> PluginResponse:
        try:
            data = json.loads(input_text)
            if isinstance(data, dict) and "jsonrpc" in data:
                # JSON-RPC format
                method = data.get("method")
                params = data.get("params", {})
                location = params.get("location")
                if method != "getWeather" or not location:
                    return PluginResponse(text=json.dumps({
                        "jsonrpc": "2.0",
                        "error": { "code": -32602, "message": "Invalid params" },
                        "id": data.get("id")
                    }))
                return self._get_weather_jsonrpc(location, data.get("id"))
        except Exception:
            # Not JSON-RPC or invalid JSON, treat as plain text
            return self._get_weather_plain(input_text.strip())

    def _get_weather_plain(self, location: str) -> PluginResponse:
        api_key = os.getenv("WEATHER_API_KEY", "your-api-key-here")
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return PluginResponse(text=f"Error: {data['error']['message']}")

        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        city = data["location"]["name"]
        country = data["location"]["country"]

        return PluginResponse(
            text=f"The current weather in {city}, {country} is {condition} with {temp}°C."
        )

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
