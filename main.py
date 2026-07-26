"""
KSP Crime Intelligence — Backend Entrypoint

Run with:  uvicorn app.main:app --reload  (from inside backend/)

This wires together the two route modules built so far. Both routes.search
and routes.chatbot_rag currently raise NotImplementedError at the point
where a real database session and LLM client are needed — see the
REPLACE ME comments in each file. Nothing here works against a live
database yet; it's the real, correct shape to fill in once:
  1. PostgreSQL is running and the schema (see dataset/data_dictionary.md
     and the original ER diagram) is loaded
  2. app/database.py's DATABASE_URL points at it
  3. app/models.py's SQLAlchemy models are confirmed against the real schema
  4. An LLM client (e.g. langchain_ollama) is wired into chatbot_rag.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import search, chatbot_rag

app = FastAPI(
    title="KSP Crime Intelligence API",
    description="Backend for the Intelligent Conversational AI Crime Database platform (Datathon 2026).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # REPLACE ME: lock this down to your real frontend origin(s) before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(chatbot_rag.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ksp-crime-intelligence-backend"}
