import os
import logging
from typing import List, Dict, Any, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Configure logging
logger = logging.getLogger(__name__)

# Constants for KB management
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
COLLECTION_NAME = "weather_insights"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class WeatherKB:
    """
    Knowledge Base Manager for Sanchai Weather AI.
    Handles embedding and storage of granular meteorological insights.
    """
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        logger.info(f"Weather KB staged (deferred initialization)")

    def _ensure_initialized(self):
        """Lazy-load the heavy embedding model and vector store."""
        if self.embeddings is None:
            logger.info(f"Initializing embedding model: {EMBEDDING_MODEL}...")
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            self.vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=DB_DIR
            )
            logger.info("Weather KB fully initialized.")

    def generate_insight_document(self, city: str, country: str, data: Dict[str, Any]) -> str:
        """
        Synthesizes raw telemetry data into a professional meteorological insight string.
        This string will be embedded into the knowledge base.
        """
        temp = data.get('temperature', {})
        atm = data.get('atmosphere', {})
        cond = data.get('conditions', {})
        wind = data.get('wind', {})
        solar = data.get('solar_cycle', {})
        
        insight = (
            f"Meteorological context for {city}, {country}. "
            f"Atmospheric state is currently {cond.get('description', 'unobserved')} with a recorded temperature of {temp.get('current')}°C. "
            f"The thermal perception (feels like) is {temp.get('feels_like')}°C. "
            f"Barometric pressure is {atm.get('pressure')} hPa with a relative humidity of {atm.get('humidity')}%. "
            f"Visibility range extends to {atm.get('visibility_km')} km. "
            f"Anemometer readings show wind speeds of {wind.get('speed_ms')} m/s at a direction of {wind.get('direction_deg')}°. "
            f"Solar cycle indicates sunrise at {solar.get('sunrise')} and sunset at {solar.get('sunset')} local time."
        )
        return insight

    def add_insight(self, city: str, country: str, data: Dict[str, Any]):
        """
        Adds a new meteorological insight to the vector store.
        """
        self._ensure_initialized()
        insight_text = self.generate_insight_document(city, country, data)
        doc = Document(
            page_content=insight_text,
            metadata={"city": city, "country": country, "timestamp": os.path.getmtime(__file__)}
        )
        self.vector_store.add_documents([doc])
        logger.info(f"Insight for {city} persisted to Knowledge Base.")

    def retrieve_insights(self, query: str, k: int = 3) -> List[str]:
        """
        Retrieves the most relevant weather insights stored in the KB.
        Useful for grounding the LLM in historical or comparable telemetry.
        """
        try:
            self._ensure_initialized()
            results = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"KB Retrieval Failure: {e}")
            return []

# Singleton instance
_kb_instance = None

def get_kb_instance() -> WeatherKB:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = WeatherKB()
    return _kb_instance
