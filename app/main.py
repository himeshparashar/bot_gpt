from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db

# logging setting
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events"""
    # startup
    logger.info("Starting Bot GPT API...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # shutdown
    logger.info("Shutting down Bot GPT API...")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    Bot GPT - A production-grade conversational AI platform.
    
    ## Features
    - **Open Chat Mode**: General conversation with LLM
    - **RAG Mode**: Grounded conversations with documents
    - **Sliding Window Context Management**: Efficient token usage
    - **Full CRUD Operations**: Create, Read, Update, Delete conversations
    
    ## API Endpoints
    - `/api/v1/conversations` - Full CRUD for conversations (recommended)
    - `/api/v1/documents` - Document management for RAG
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Bot GPT API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "debug": settings.DEBUG
    }
