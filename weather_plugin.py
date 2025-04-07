from fastmcp.plugin import Plugin, PluginResponse
import requests
import os

class WeatherPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="weather-plugin",
            description="Get current weather information",
        )

    def run(self, input_text: str) -> PluginResponse:
        location = input_text.strip()
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
