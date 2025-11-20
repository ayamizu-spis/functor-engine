import os
import json
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .graph_logic import CategoryGraph
from .models import WorldObject, Morphism

class FunctorEngine:
    def __init__(self, graph: CategoryGraph, api_key: str):
        self.graph = graph
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.7
        )

    async def extract_entities(self, text: str) -> List[str]:
        """Extracts key concepts/entities from the input text."""
        prompt = ChatPromptTemplate.from_template(
            "Extract key concepts (nouns, entities) from the following text as a JSON list of strings.\n"
            "Text: {text}\n"
            "JSON List:"
        )
        chain = prompt | self.llm | JsonOutputParser()
        try:
            return await chain.ainvoke({"text": text})
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return []

    def _find_nearest_node(self, entity: str) -> str:
        """
        Finds the most relevant node in the graph for a given entity.
        For now, this is a simple string match or fuzzy match.
        In a real production system, we would use vector embeddings.
        """
        # Simple exact match or substring match for this prototype
        for node_id in self.graph.graph.nodes:
            if entity.lower() in node_id.lower() or node_id.lower() in entity.lower():
                return node_id
        return None

    async def translate_text(self, text: str) -> Dict[str, Any]:
        """Translates text based on the world graph."""
        
        # 1. Extract entities
        entities = await self.extract_entities(text)
        
        # 2. Retrieve context (laws)
        applied_laws = []
        context_str = ""
        
        for entity in entities:
            node_id = self._find_nearest_node(entity)
            if node_id:
                laws = self.graph.get_context(node_id)
                if laws:
                    law_entry = f"Concept '{entity}' maps to '{node_id}' with laws:\n{laws}"
                    applied_laws.append(law_entry)
                    context_str += law_entry + "\n"

        # 3. Generate translation
        system_prompt = (
            "You are a 'Functor Engine', a system that translates reality into a specific worldview.\n"
            "Rewrite the input text according to the provided World Laws.\n"
            "If no specific laws apply to a part of the text, try to adapt it to the general tone implied by the laws.\n"
            "Output ONLY the translated text."
        )
        
        user_prompt = f"""
        Original Text: {text}
        
        World Laws:
        {context_str if context_str else "No specific laws found. Apply a general fantasy/SF filter."}
        """
        
        messages = [
            ("system", system_prompt),
            ("user", user_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        translated_text = response.content
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "applied_laws": applied_laws
        }

    async def initialize_world_from_text(self, world_text: str):
        """Parses a world description text and populates the graph."""
        self.graph.clear()
        
        prompt = ChatPromptTemplate.from_template(
            "Analyze the following world description and extract 'Concepts' (Nodes) and 'Laws/Relationships' (Edges).\n"
            "Return a JSON object with two keys: 'nodes' and 'edges'.\n"
            "Each 'node' should have: id, label, description, type.\n"
            "Each 'edge' should have: source (id), target (id), label, rule.\n"
            "Text:\n{text}\n"
            "JSON:"
        )
        
        chain = prompt | self.llm | JsonOutputParser()
        try:
            data = await chain.ainvoke({"text": world_text})
            
            for node_data in data.get("nodes", []):
                node = WorldObject(**node_data)
                self.graph.add_node(node)
                
            for edge_data in data.get("edges", []):
                morphism = Morphism(**edge_data)
                self.graph.add_morphism(morphism)
                
            return len(self.graph.graph.nodes)
        except Exception as e:
            print(f"Error initializing world: {e}")
            raise e
