"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import analyze, history, stock
from app.services.cache_service import cache_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting up...")
    await cache_service.connect()
    yield
    # Shutdown
    print("🛑 Shutting down...")
    await cache_service.disconnect()


app = FastAPI(
    title="AI Stock Analyzer API",
    description="API for analyzing A-shares with DeepSeek AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(stock.router, prefix="/api", tags=["stock"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Stock Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }
