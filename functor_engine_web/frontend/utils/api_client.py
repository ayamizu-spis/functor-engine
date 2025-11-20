import requests
import json

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def _handle_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
            # ステータスコードが4xx, 5xxの場合でも、サーバーからのレスポンス(detail)を取得して表示する
            if not response.ok:
                try:
                    error_detail = response.json().get("detail", response.text)
                    return {"error": f"{response.status_code} Error: {error_detail}"}
                except:
                    return {"error": f"{response.status_code} Error: {response.reason}"}
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def initialize_world(self, config_text: str):
        return self._handle_request(
            "POST",
            f"{self.base_url}/world/initialize",
            json={"config_text": config_text}
        )

    def translate(self, text: str):
        return self._handle_request(
            "POST",
            f"{self.base_url}/translate",
            json={"text": text}
        )

    def translate_image(self, image_file):
        files = {"file": image_file}
        return self._handle_request(
            "POST",
            f"{self.base_url}/translate/image",
            files=files
        )

    def get_graph_data(self):
        try:
            response = requests.get(f"{self.base_url}/world/graph")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
