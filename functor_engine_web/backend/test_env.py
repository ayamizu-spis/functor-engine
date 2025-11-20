import os
from dotenv import load_dotenv

def find_env_file(filename="Gemini.env"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        file_path = os.path.join(current_dir, filename)
        if os.path.exists(file_path):
            return file_path
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir: # Reached root
            return None
        current_dir = parent_dir

ENV_PATH = find_env_file()
if ENV_PATH:
    print(f"Found ENV_PATH: {ENV_PATH}")
    load_dotenv(ENV_PATH)
    print(f"API Key: {os.getenv('GEMINI_API_KEY')}")
else:
    print("ENV_PATH not found")
