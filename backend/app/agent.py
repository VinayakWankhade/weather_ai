from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .tools import get_weather
from .kb_manager import get_kb_instance
from .config import OPENROUTER_API_KEY
import os
import logging
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAgent:
    """
    Production-Grade RAG Weather Intelligence System with API Optimization.
    """
    
    def __init__(self, llm_mode="smart"):
        """
        Args:
            llm_mode: "always" (use LLM for all), "smart" (use LLM only for complex), "never" (fallback only)
        """
        self.llm = None
        self.kb = get_kb_instance()
        self.llm_mode = llm_mode
        self.response_cache = {}  # Cache responses to avoid duplicate API calls
        self.cache_ttl = 300  # 5 minutes cache
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM for RAG operations."""
        # DeepSeek R1T2 Chimera via OpenRouter
        if OPENROUTER_API_KEY:
            try:
                # Using DeepSeek R1T2 Chimera - 671B reasoning model
                self.llm = ChatOpenAI(
                    model="tngtech/deepseek-r1t2-chimera:free",
                    openai_api_key=OPENROUTER_API_KEY,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.3,
                    default_headers={
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "Sanchai Weather AI - RAG Expert",
                    },
                    request_timeout=45
                )
                logger.info("Using OpenRouter API (DeepSeek R1T2 Chimera)")
                return
            except Exception as e:
                logger.error(f"OpenRouter init failed: {e}")
        
        logger.warning("No valid LLM credentials found. LLM features disabled.")
        self.llm = None
    
    def _clean_llm_output(self, text: str) -> str:
        """Clean LLM output of markdown blocks and reasoning tags."""
        text = text.strip()
        
        # Remove reasoning tags <think>...</think> if present
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        
        # Remove markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            # Filter out lines starting with ```
            text = "\n".join([l for l in lines if not l.startswith("```")]).strip()
            
        return text

    def _is_simple_query(self, query: str) -> bool:
        """
        Detect if a query is simple enough to handle without LLM.
        Simple queries: "weather in [city]", "what's the weather in [city]"
        Complex queries: comparisons, analysis, subjective questions
        """
        q = query.lower()
        
        # Explicit simple patterns (High confidence)
        simple_patterns = [
            r'^weather (?:in|at|for) [a-z\s\-\.]+\??$',
            r'^what.?s? (?:the )?weather (?:in|at|for) [a-z\s\-\.]+\??$',
            r'^how.?s? [a-z\s\-\.]+ weather\??$',
            r'^[a-z\s\-\.]+ weather\??$',
            r'^current weather (?:in|at|for) [a-z\s\-\.]+\??$',
        ]
        
        # If it matches a simple pattern exactly, it's simple
        for pattern in simple_patterns:
            if re.match(pattern, q):
                return True
        
        # Complex indicators (Strong signal for LLM)
        complex_keywords = [
            'compare', 'analysis', 'picnic', 'should i', 'recommend', 'better', 
            'worse', 'why', 'planning', 'party', 'safe', 'run', 'bike', 'hike',
            'opinion', 'think', 'suggest', 'advice', 'wear', 'umbrella', 'raincoat'
        ]
        if any(keyword in q for keyword in complex_keywords):
            return False
            
        # Default: Assume COMPLEX if it doesn't match simple patterns
        # This ensures we don't accidentally fallback on long/unusual queries
        return False
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return query.lower().strip()
    
    def _get_cached_response(self, query: str) -> str:
        """Get cached response if available and not expired."""
        import time
        cache_key = self._get_cache_key(query)
        
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                logger.info(f"Cache hit for query: {query}")
                return cached_data['response']
            else:
                # Expired, remove from cache
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_response(self, query: str, response: str):
        """Cache a response."""
        import time
        cache_key = self._get_cache_key(query)
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.info(f"Cached response for: {query}")

    async def _analyze_intent(self, user_query: str) -> dict:
        """
        Use LLM to analyze user intent and extract location.
        Returns: {"city": str, "intent": str, "needs_fresh_data": bool}
        """
        # Smart mode: use fallback for simple queries to save API calls
        if self.llm_mode == "smart" and self._is_simple_query(user_query):
            logger.info("Simple query detected, using fallback (saving API call)")
            return self._fallback_intent_analysis(user_query)
        
        # Never mode: always use fallback
        if self.llm_mode == "never" or not self.llm:
            logger.warning("LLM unavailable or disabled, using fallback intent analysis")
            return self._fallback_intent_analysis(user_query)
        
        try:
            intent_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at analyzing meteorological queries. 
Extract the following from the user's query:
1. City name (if mentioned, extract the FIRST city mentioned)
2. Intent (what they want: current weather, forecast, comparison, analysis, etc.)
3. Whether fresh data is needed (true if asking for current/now/today)

IMPORTANT: 
- For comparison queries like "Compare Mumbai and Pune", extract the FIRST city only
- If multiple cities are mentioned, only extract the first one
- If no city is mentioned, use null

Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
{{"city": "CityName", "intent": "brief description", "needs_fresh_data": true}}

Examples:
- "What's the weather in Pune?" → {{"city": "Pune", "intent": "current weather", "needs_fresh_data": true}}
- "Compare Mumbai and Pune" → {{"city": "Mumbai", "intent": "comparison", "needs_fresh_data": true}}
- "Tell me about London weather" → {{"city": "London", "intent": "weather info", "needs_fresh_data": true}}"""),
                ("user", "{query}")
            ])
            
            chain = intent_prompt | self.llm | StrOutputParser()
            result = await chain.ainvoke({"query": user_query})
            
            # Clean up the result (handle reasoning tags and markdown)
            result = self._clean_llm_output(result)
            
            # Parse JSON response
            try:
                parsed = json.loads(result)
                logger.info(f"LLM Intent Analysis Success: {parsed}")
                return parsed
            except json.JSONDecodeError as je:
                logger.warning(f"JSON parse error: {je}. Raw LLM output: {result}")
                # Try to extract city from the raw output
                return self._fallback_intent_analysis(user_query)
            
        except Exception as e:
            logger.warning(f"LLM intent analysis failed: {e}. Using fallback.")
            return self._fallback_intent_analysis(user_query)

    def _fallback_intent_analysis(self, query: str) -> dict:
        """Regex-based fallback for intent analysis."""
        city = self._extract_city_regex(query)
        needs_fresh = any(word in query.lower() for word in ['current', 'now', 'today', 'what', 'how'])
        return {
            "city": city,
            "intent": "weather query",
            "needs_fresh_data": needs_fresh
        }

    def _extract_city_regex(self, query: str) -> str:
        """Regex-based city extraction as fallback."""
        q = query.lower()
        patterns = [
            r"weather (?:in|of|for|at) ([a-z\s\-\.']+?)(?:\?|$|today|now|tomorrow)",
            r"report (?:for|of|on) ([a-z\s\-\.']+?)(?:\?|$)",
            r"(?:in|for|at) ([a-z\s\-\.']+?)(?:\?|$)",
        ]
        
        for p in patterns:
            m = re.search(p, q)
            if m:
                city = m.group(1).strip()
                # Remove noise words
                city = re.sub(r'\b(the|a|an|weather|report|now|today)\b', '', city, flags=re.IGNORECASE).strip()
                if city:
                    return city.title()
        
        # Capitalized word fallback
        words = query.split()
        for w in reversed(words):
            wc = w.strip('?.,!')
            if wc and len(wc) > 2 and wc[0].isupper():
                return wc
        
        return None

    async def _generate_rag_response(self, user_query: str, intent: dict, kb_context: str, fresh_data: dict = None) -> str:
        """
        Use LLM to generate a natural response using RAG context.
        This is the CORE of the RAG system - LLM synthesizes everything.
        """
        # Smart/Never mode: use fallback for simple queries
        if self.llm_mode in ["smart", "never"] and self._is_simple_query(user_query):
            logger.info("Simple query, using enhanced fallback (saving API call)")
            return self._enhanced_fallback(fresh_data, kb_context)
        
        if not self.llm or self.llm_mode == "never":
            logger.warning("LLM unavailable or disabled. Using fallback.")
            return self._enhanced_fallback(fresh_data, kb_context)
        
        try:
            # Prepare context for LLM
            context_parts = []
            
            if kb_context:
                context_parts.append(f"**Knowledge Base Context**:\n{kb_context}")
            
            if fresh_data:
                context_parts.append(f"**Fresh Telemetry**:\n{json.dumps(fresh_data, indent=2)}")
            
            combined_context = "\n\n".join(context_parts) if context_parts else "No context available."
            
            # RAG Synthesis Prompt
            rag_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Senior Meteorological Analyst. Your role is to provide natural, conversational, and accurate weather insights.

You have access to:
1. Historical insights from our Knowledge Base
2. Fresh real-time telemetry data

**CRITICAL INSTRUCTIONS**:
- Synthesize the information naturally - DO NOT just list data points
- Use professional but conversational language
- Include specific metrics (temperature, pressure, humidity, wind, visibility, sunrise/sunset) when available
- If you see both KB context and fresh data, compare or correlate them
- Be precise with numbers but explain what they mean
- Keep responses concise but informative (2-4 sentences for simple queries, more for analysis requests)

**NEVER**:
- Use bullet points or lists
- Sound robotic or templated
- Hallucinate data not provided in the context"""),
                ("user", """User Query: {query}

Available Context:
{context}

Provide a natural, expert meteorological response:""")
            ])
            
            chain = rag_prompt | self.llm | StrOutputParser()
            response = await chain.ainvoke({
                "query": user_query,
                "context": combined_context
            })
            
            # Clean up response (handle reasoning tags)
            response = self._clean_llm_output(response)
            
            logger.info(f"LLM RAG response generated successfully")
            return response.strip()
            
        except Exception as e:
            logger.error(f"LLM RAG synthesis failed: {e}")
            return self._enhanced_fallback(fresh_data, kb_context)

    def _enhanced_fallback(self, data: dict, kb_context: str) -> str:
        """Enhanced fallback with better formatting (no LLM needed)."""
        if not data:
            return "I apologize, but I'm currently unable to process weather queries. Please try again in a moment."
        
        try:
            loc = data.get('location', 'Unknown')
            country = data.get('country', '')
            temp = data.get('temperature', {})
            atm = data.get('atmosphere', {})
            cond = data.get('conditions', {})
            wind = data.get('wind', {})
            
            # Build a natural-sounding response without LLM
            response = f"The current temperature in {loc}" 
            if country:
                response += f", {country}"
            response += f" is {temp.get('current', 'N/A')}°C (feels like {temp.get('feels_like', 'N/A')}°C) with {cond.get('description', 'N/A')}. "
            response += f"Humidity is {atm.get('humidity', 'N/A')}% and wind speed is {wind.get('speed_ms', 'N/A')} m/s."
            
            return response
        except Exception as e:
            logger.error(f"Fallback formatting error: {e}")
            return "Weather data retrieved but formatting failed. Please try again."
    


    async def process_query(self, user_query: str) -> str:
        """
        Main RAG pipeline orchestration with API optimization.
        
        Flow:
        1. Check cache for recent identical queries
        2. Analyze user intent (smart mode: use regex for simple queries)
        3. Retrieve relevant KB context
        4. Fetch fresh data if needed
        5. Generate response (smart mode: use fallback for simple queries)
        """
        logger.info(f"Processing query: {user_query} [Mode: {self.llm_mode}]")
        
        # Step 0: Check cache
        cached = self._get_cached_response(user_query)
        if cached:
            return cached
        
        # Step 1: Intent Analysis
        intent = await self._analyze_intent(user_query)
        city = intent.get('city')
        
        if not city:
            return "I'd be happy to help with weather information! Could you please specify which city you're interested in?"
        
        # Step 2: Knowledge Base Retrieval
        kb_context = ""
        try:
            insights = self.kb.retrieve_insights(city, k=2)
            if insights:
                kb_context = "\n".join(insights)
                logger.info(f"Retrieved {len(insights)} insights from KB for {city}")
        except Exception as e:
            logger.warning(f"KB retrieval failed: {e}")
        
        # Step 3: Fresh Data Retrieval (if needed)
        fresh_data = None
        if intent.get('needs_fresh_data', True):
            try:
                result = get_weather.invoke(city)
                if isinstance(result, dict):
                    fresh_data = result
                    # Store in KB for future queries
                    self.kb.add_insight(
                        fresh_data.get('location', city),
                        fresh_data.get('country', ''),
                        fresh_data
                    )
                    logger.info(f"Fresh telemetry retrieved and stored for {city}")
            except Exception as e:
                logger.error(f"Fresh data retrieval failed: {e}")
        
        # Step 4: LLM RAG Synthesis
        response = await self._generate_rag_response(
            user_query=user_query,
            intent=intent,
            kb_context=kb_context,
            fresh_data=fresh_data
        )
        
        # Cache the response
        self._cache_response(user_query, response)
        
        return response

# Global singleton
_rag_agent = None

async def run_agent(user_query: str, llm_mode: str = "smart") -> str:
    """
    Run the weather agent with configurable LLM usage.
    
    Args:
        user_query: User's weather query
        llm_mode: "always" (use LLM for all), "smart" (default - use LLM only for complex), "never" (fallback only)
    """
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = WeatherAgent(llm_mode=llm_mode)
    return await _rag_agent.process_query(user_query)
