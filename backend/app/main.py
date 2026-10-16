"""FastAPI application entry point."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.assessment import router as assessment_router
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)

app = FastAPI(
    title="CyberExplain AI",
    description="Multi-Agent Cybersecurity Risk Assessment with Explainability",
    version="1.0.0",
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(assessment_router)


@app.get("/")
async def root():
    return {
        "name": "CyberExplain AI",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "groq_configured": bool(settings.groq_api_key),
        "supabase_configured": bool(settings.supabase_url and settings.supabase_key),
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
