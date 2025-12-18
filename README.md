# 🌤️ Sanchai Weather AI

> **Weather intelligence that thinks before it speaks.**

Welcome to **Sanchai Weather AI**, a production-grade weather assistant designed to demonstrate the power of **democratized, local-first AI**. 

Unlike standard weather bots that just read API data, Sanchai uses a **Reasoning Engine (DeepSeek R1T2 Chimera)** to analyze meteorological data, understand context, and provide expert-level insights—all for **100% free**.

---

## 🌟 Why Sanchai?

### 🧠 The Reasoning Engine
Most weather apps just display numbers. Sanchai "thinks" about them. 
Powered by **DeepSeek R1T2 Chimera** (via OpenRouter), it analyzes:
- "Is it safe for a garden party given the humidity?"
- "Compare the visibility in Mumbai vs. Delhi."
- "What should I wear for a morning run?"

### 🆓 Democratized AI (100% Free)
We believe powerful AI should be accessible to everyone.
- **LLM**: DeepSeek R1T2 Chimera (via OpenRouter Free Tier)
- **Weather Data**: OpenWeatherMap (Free Tier)
- **Vector DB**: ChromaDB (Local)
- **Embeddings**: Sentence Transformers (Local/CPU)

### 🔒 Privacy-First RAG
Your queries aren't just sent to a cloud. Sanchai uses **Retrieval-Augmented Generation (RAG)** with a local Knowledge Base. It learns from your queries, building a personalized database of weather insights that stays on your machine.

---

## 🚀 Get Started

### Prerequisites
- [Node.js](https://nodejs.org/) & [Python 3.10+](https://www.python.org/)
- A free **OpenRouter API Key** ([Get it here](https://openrouter.ai))
- A free **OpenWeatherMap API Key** ([Get it here](https://openweathermap.org/api))

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Open .env and paste your API keys
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Run It!
Open two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
.\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Visit **http://localhost:5173** and ask: *"I'm planning a hike in Pune tomorrow. Is it safe?"*

---

## 🏗️ How It Works

1.  **Intent Analysis**: The LLM determines if you need current weather, a forecast, or a comparison.
2.  **Smart Retrieval**: It checks your local Knowledge Base for past insights.
3.  **Live Telemetry**: If needed, it fetches fresh data from OpenWeatherMap.
4.  **Reasoning Synthesis**: DeepSeek R1T2 combines the data and context to generate a natural, helpful answer (stripping away raw "thinking" logs for a clean experience).

## 🛠️ Tech Stack

-   **Intelligence**: DeepSeek R1T2 Chimera (via OpenRouter)
-   **Backend**: Python, FastAPI, LangChain
-   **Memory**: ChromaDB (Vector Store)
-   **Frontend**: React, Vite, TailwindCSS
-   **Design**: Glassmorphism & Dynamic UI

## 📄 License

MIT License. Built with ❤️ for the Open Source community.
