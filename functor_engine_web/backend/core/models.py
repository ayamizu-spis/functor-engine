from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

# --- Domain Models ---

class WorldObject(BaseModel):
    """Represents a concept or object in the world."""
    id: str
    label: str
    description: str
    type: str = "concept" # concept, place, person, etc.
    meta: Dict[str, Any] = Field(default_factory=dict)

class Morphism(BaseModel):
    """Represents a relationship or law between nodes."""
    source: str
    target: str
    label: str
    rule: str # The logic or law of transformation

# --- API Models ---

class TranslationRequest(BaseModel):
    text: str
    world_id: str = "default"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    applied_laws: List[str]

class GraphDataResponse(BaseModel):
    """Data format for PyVis/Vis.js"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
