import requests
import json

def test_initialize():
    url = "http://localhost:8000/world/initialize"
    data = {"config_text": "In the land of Test, there exists a TestObject."}
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_initialize()
