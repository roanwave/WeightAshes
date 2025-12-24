"""
WeightAshes Backend - FastAPI Application
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

app = FastAPI(
    title="WeightAshes",
    description="Personal writing IDE for The Weight of Ashes",
    version="0.1.0",
)

# CORS middleware for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from routes import ai_router, codex_router, manuscript_router

app.include_router(codex_router)
app.include_router(manuscript_router)
app.include_router(ai_router)

# TODO: Register session router when implemented
# from routes import session_router
# app.include_router(session_router)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "WeightAshes"}
