import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

from core.graph_logic import CategoryGraph
from core.llm_service import FunctorEngine
from core.models import TranslationRequest, TranslationResponse, GraphDataResponse

# Load environment variables
# Load environment variables
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
    load_dotenv(ENV_PATH)
    print(f"Loaded environment from: {ENV_PATH}")
else:
    # Fallback: try local .env
    load_dotenv()
    print("WARNING: Gemini.env not found, using default .env or system variables.")

API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Functor Engine API")

# Global State
graph = CategoryGraph()
engine = None

if API_KEY:
    engine = FunctorEngine(graph, API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found. Engine will not work.")

class WorldInitRequest(BaseModel):
    config_text: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Functor Engine API"}

@app.post("/world/initialize")
async def initialize_world(request: WorldInitRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized (Missing API Key)")
    
    try:
        node_count = await engine.initialize_world_from_text(request.config_text)
        return {"status": "initialized", "nodes": node_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    result = await engine.translate_text(request.text)
    return TranslationResponse(**result)

@app.post("/translate/image", response_model=TranslationResponse)
async def translate_image(file: UploadFile = File(...)):
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized")
    
    try:
        contents = await file.read()
        result = await engine.translate_image(contents, file.content_type)
        return TranslationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/world/graph", response_model=GraphDataResponse)
def get_graph():
    return graph.export_for_vis()
