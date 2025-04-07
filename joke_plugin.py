from fastmcp.plugin import Plugin, PluginResponse
import json
import random

class JokePlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="joke-plugin",
            description="Tells a random joke using method 'getJoke'"
        )

    def run(self, input_text: str) -> PluginResponse:
        try:
            data = json.loads(input_text)
            if data.get("method") != "getJoke":
                raise ValueError("Unsupported method")
            return self._get_joke_jsonrpc(data.get("id"))
        except Exception as e:
            return PluginResponse(text=json.dumps({
                "jsonrpc": "2.0",
                "error": { "code": -32601, "message": str(e) },
                "id": data.get("id") if 'data' in locals() else None
            }))

    def _get_joke_jsonrpc(self, request_id) -> PluginResponse:
        jokes = [
            "Why did the developer go broke? Because they used up all their cache.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "Why did the function stop calling? Because it had too many arguments."
        ]
        joke = random.choice(jokes)

        return PluginResponse(text=json.dumps({
            "jsonrpc": "2.0",
            "result": joke,
            "id": request_id
        }))
