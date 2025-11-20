import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

from core.graph_logic import CategoryGraph
from core.llm_service import FunctorEngine
from core.models import TranslationRequest, TranslationResponse, GraphDataResponse

# Load environment variables
# Try to load from the project root (2 levels up from here if running from backend dir, or just absolute path)
# The user specified the file is at d:/VRChat/World/OccultPunk/Simulator/FunctorEngine/Gemini.env
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Gemini.env"))
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    # Fallback: try local .env
    load_dotenv()

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

@app.get("/world/graph", response_model=GraphDataResponse)
def get_graph():
    return graph.export_for_vis()
