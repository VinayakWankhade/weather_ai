# Sanchai Weather AI - Deployment Guide

This document outlines the professional strategies for deploying the Sanchai Weather AI platform to a production-grade environment, specifically focusing on Vercel integration.

---

## Deployment Strategy Overview

Due to the **Retrieval-Augmented Generation (RAG)** architecture and the use of a local vector database (ChromaDB), we recommend a **Hybrid Deployment** as the most stable and performant option.

| Component | Recommended Provider | Why? |
|-----------|--------------------|------|
| **Frontend** | **Vercel** | Industry-standard for React/Vite, excellent CD/CI and Edge performance. |
| **Backend** | **Railway / Render** | Supports persistent disk storage required for ChromaDB and long-running Python processes. |

---

## Option 1: Hybrid Deployment (Recommended)

In this setup, your frontend lives on Vercel, and your intelligence engine (FastAPI) lives on a persistent platform like Railway or Render.

### 1. Backend Deployment (Railway/Render)
- Connect your GitHub repository.
- Root directory: `backend/`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Add `OPENWEATHER_API_KEY` and `OPENROUTER_API_KEY`.

### 2. Frontend Deployment (Vercel)
- Connect your GitHub repository.
- Framework Preset: `Vite`
- Root directory: `frontend/`
- **Environment Variable**: Set `VITE_API_URL` to your Backend URL (e.g., `https://your-backend.railway.app`).

---

## Option 2: Pure Vercel Deployment (Monorepo)

If you prefer to keep everything on Vercel, you must address the stateless nature of Serverless Functions.

### 1. Configuration (`vercel.json`)
Create a `vercel.json` in your project root to route requests to the FastAPI backend:

```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" }
  ]
}
```

### 2. Backend Adaptations
- **Statelessness**: Since Vercel is stateless, ChromaDB cannot persist data to `/db`. You should either use a hosted Chroma Cloud instance or disable the Knowledge Base persistence.
- **Cold Starts**: Loading `sentence-transformers` on every request may lead to long "cold starts". For pure serverless, we recommend switching to an API-based embedding model (e.g., OpenAI Embeddings).

---

## Environment Variables Checklist

Ensure these are configured in your deployment dashboard:

| Variable | Source | Purpose |
|----------|---------|---------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap | Real-time telemetry data. |
| `OPENROUTER_API_KEY` | OpenRouter | DeepSeek Reasoning Engine access. |
| `VITE_API_URL` | Deployment | (Frontend only) Points the React UI to the correct API endpoint. |

---

## Post-Deployment Verification
Once deployed, verify the connection by checking the browser console for successful `OPTIONS` (CORS) requests and ensuring the Reasoning Engine provides synthesized responses rather than fallbacks.
