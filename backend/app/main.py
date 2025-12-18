from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import run_agent
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Weather AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Weather AI Reasoning Engine is active.",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat [POST]"
        }
    }

class Query(BaseModel):
    message: str

@app.post("/chat")
async def chat(query: Query): # Changed to async
    if not query.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Await the async agent run
    response = await run_agent(query.message)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
