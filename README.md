# 🌤️ Sanchai Weather AI - RAG System

A production-grade **Retrieval-Augmented Generation (RAG)** weather intelligence system powered by **100% free APIs**.

## ✨ Features

- 🤖 **LLM-Driven Intent Analysis** - Understands natural language queries
- 🧠 **Knowledge Base** - ChromaDB vector store with local embeddings
- 💬 **Natural Responses** - Conversational AI, not templates
- 🆓 **100% Free** - Uses OpenRouter's free tier + OpenWeatherMap free tier
- ⚡ **Real-Time Data** - Fresh meteorological telemetry
- 📊 **Comprehensive Metrics** - Temperature, pressure, humidity, wind, visibility, solar cycles

## 🚀 Quick Start (5 minutes)

### 1. Get Free API Keys

#### OpenRouter (100% Free - No Credit Card)
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign in with Google/GitHub
3. Go to "Keys" → Create new key
4. Copy the key (starts with `sk-or-v1-`)

#### OpenWeatherMap (Free Tier)
1. Go to [openweathermap.org](https://openweathermap.org/api)
2. Sign up for free account
3. Get your API key from dashboard

### 2. Configure Backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Install Dependencies

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 4. Run the Application

```bash
# Terminal 1: Backend
cd backend
.\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev -- --port 5173
```

### 5. Test It!

Open [http://localhost:5173](http://localhost:5173) and try:
- "What's the weather like in Pune?"
- "Tell me about Mumbai weather"
- "How's London doing?"

## 🏗️ Architecture

```
User Query → LLM Intent Analysis → Knowledge Base Retrieval
                                           ↓
                                    Fresh Data Fetch
                                           ↓
                                    LLM Synthesis → Natural Response
```

## 📁 Project Structure

```
sanchai-weather-ai/
├── backend/
│   ├── app/
│   │   ├── agent.py          # RAG orchestration
│   │   ├── kb_manager.py     # ChromaDB Knowledge Base
│   │   ├── tools.py          # Weather API integration
│   │   ├── config.py         # Configuration
│   │   └── main.py           # FastAPI server
│   ├── db/                   # ChromaDB storage (auto-created)
│   ├── venv/                 # Virtual environment
│   ├── .env                  # API keys (create from .env.example)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   └── components/
    │       └── ChatBox.jsx   # React UI
    └── package.json
```

## 🔧 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - LLM orchestration
- **ChromaDB** - Vector database
- **OpenRouter** - Free LLM access (Gemini 2.0 Flash)
- **Sentence Transformers** - Local embeddings

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling

## 📊 Free API Limits

| Service | Free Tier Limit | Enough For |
|---------|----------------|------------|
| OpenRouter | ~20 req/min | ✅ Personal use |
| OpenWeatherMap | 1000 req/day | ✅ Development |

## 🧪 Testing

### Backend RAG System
```bash
cd backend
.\venv\Scripts\python verify_rag_system.py
```

### LLM Connection
```bash
.\venv\Scripts\python diagnose_llm.py
```

## 📚 Documentation

- [OpenRouter Free Setup Guide](file:///C:/Users/wankh/.gemini/antigravity/brain/2e373e57-cf86-4c04-b6e2-a100df07518a/OPENROUTER_FREE_SETUP.md)
- [RAG System Walkthrough](file:///C:/Users/wankh/.gemini/antigravity/brain/2e373e57-cf86-4c04-b6e2-a100df07518a/walkthrough.md)

## ⚠️ Troubleshooting

### "LLM is NOT initialized"
- Check that `OPENROUTER_API_KEY` is in `.env`
- Restart the backend server

### Getting template responses instead of natural language?
- Verify OpenRouter API key is correct
- Run `diagnose_llm.py` to check connection
- Check backend logs for errors

### "402 Payment Required"
- Make sure you're using the free model: `google/gemini-2.0-flash-exp:free`
- Check `backend/app/agent.py` line 35

## 🎯 What Makes This RAG?

1. **Retrieval**: Vector similarity search in ChromaDB
2. **Augmentation**: LLM uses retrieved context + fresh data
3. **Generation**: Natural language synthesis (not templates)

## 🚀 Next Steps

- [ ] Add more sophisticated prompts
- [ ] Implement multi-city comparisons
- [ ] Add weather forecasting
- [ ] Enhance KB with historical trends

## 📝 License

MIT

---

**Built with ❤️ using 100% free APIs**
