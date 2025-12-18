from langchain.tools import tool
from typing import Dict, Union, Any
import requests
import logging
from .config import OPENWEATHER_API_KEY
from .kb_manager import get_kb_instance
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

@tool
def get_weather(city: str) -> Union[Dict[str, Any], str]:
    """
    Fetch comprehensive meteorological data for a specified city.
    
    Provides precise data points including temperature, atmospheric pressure, 
    humidity, wind vectors, visibility, and solar cycles (sunrise/sunset).
    This data is also used to ground the RAG Knowledge Base.
    
    Args:
        city: The target city name for data retrieval.
        
    Returns:
        A dictionary containing granular weather metrics or an error message.
    """
    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY not configured")
        return "System Error: Weather API key missing."
    
    city = city.strip()
    logger.info(f"Retrieving high-precision telemetry for: {city}")
    
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "units": "metric",
        "appid": OPENWEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=12)
        data = response.json()
        
        if data.get("cod") != 200:
            error_msg = data.get("message", "Unknown API error")
            logger.warning(f"API rejection for {city}: {error_msg}")
            return f"Data Retrieval Error: {error_msg}"
        
        # Extract and structured high-precision data
        main = data.get("main", {})
        sys = data.get("sys", {})
        
        meteorological_report = {
            "location": data.get("name"),
            "country": sys.get("country"),
            "temperature": {
                "current": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "min": main.get("temp_min"),
                "max": main.get("temp_max")
            },
            "atmosphere": {
                "pressure": main.get("pressure"),
                "humidity": main.get("humidity"),
                "visibility_km": data.get("visibility", 0) / 1000
            },
            "conditions": {
                "main": data["weather"][0]["main"],
                "description": data["weather"][0]["description"].capitalize()
            },
            "wind": {
                "speed_ms": data.get("wind", {}).get("speed"),
                "direction_deg": data.get("wind", {}).get("deg")
            },
            "solar_cycle": {
                "sunrise": datetime.fromtimestamp(sys.get("sunrise")).strftime('%H:%M'),
                "sunset": datetime.fromtimestamp(sys.get("sunset")).strftime('%H:%M')
            }
        }
        
        # Enrich Knowledge Base with fresh telemetry
        try:
            kb = get_kb_instance()
            kb.add_insight(meteorological_report['location'], meteorological_report['country'], meteorological_report)
        except Exception as kb_err:
            logger.error(f"KB Enrichment failed for {city}: {kb_err}")

        logger.info(f"Precision telemetry successfully retrieved and persisted for {city}")
        return meteorological_report
        
    except Exception as e:
        logger.error(f"Critical failure during telemetry retrieval for {city}: {str(e)}", exc_info=True)
        return f"Telemetry Transmission Error: {str(e)}"
