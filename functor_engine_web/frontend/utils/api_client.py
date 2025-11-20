import requests
import json

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def initialize_world(self, config_text: str):
        try:
            response = requests.post(
                f"{self.base_url}/world/initialize",
                json={"config_text": config_text}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def translate(self, text: str):
        try:
            response = requests.post(
                f"{self.base_url}/translate",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_graph_data(self):
        try:
            response = requests.get(f"{self.base_url}/world/graph")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
