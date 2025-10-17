"""
FastAPI application initialization and configuration.

This module sets up the FastAPI app, CORS middleware, and manages
the pipeline singleton instances.
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from corrected_7step_pipeline import CorrectedSevenStepPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Toggle lightweight "mock" mode for local development/testing
MOCK_PIPELINE = os.getenv("AQU_MOCK_PIPELINE", "0") == "1"
if MOCK_PIPELINE:
    logger.warning(
        "AQU_MOCK_PIPELINE=1 detected – running API server in mock mode; "
        "pipeline-dependent endpoints will return placeholders."
    )

# Initialize FastAPI app
app = FastAPI(
    title="Aqumen Question Generation API",
    description="Real-time adversarial AI/ML code review question generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - allow frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://localhost:8501",  # Streamlit local
        "https://demo.aqumen.ai",  # Production React frontend
        "https://dev.aqumen.ai",  # Dev Streamlit frontend
        "https://*.vercel.app",  # Vercel preview deployments
        "https://*.streamlit.app",  # Streamlit Cloud
        "https://*.onrender.com",  # Render preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pipeline singleton instances (keyed by provider)
pipelines: dict[str, CorrectedSevenStepPipeline] = {}


def get_pipeline(provider: str = "anthropic") -> CorrectedSevenStepPipeline:
    """
    Lazy initialization of pipeline singleton for specified provider.

    Args:
        provider: Either "anthropic" or "openai" (default: "anthropic")

    Returns:
        Pipeline instance for the specified provider

    Raises:
        HTTPException: If pipeline is in mock mode or initialization fails
    """
    global pipelines

    if MOCK_PIPELINE:
        raise HTTPException(503, "Pipeline is disabled in mock mode.")

    # Validate provider
    if provider not in ["anthropic", "openai"]:
        raise HTTPException(400, f"Invalid provider: {provider}. Must be 'anthropic' or 'openai'")

    # Initialize pipeline for this provider if not already done
    if provider not in pipelines:
        logger.info(f"Initializing CorrectedSevenStepPipeline with provider: {provider}...")
        try:
            pipelines[provider] = CorrectedSevenStepPipeline(provider=provider)
            logger.info(f"Pipeline initialized successfully for provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline for provider '{provider}': {e}")
            raise HTTPException(500, f"Failed to initialize pipeline: {str(e)}")

    return pipelines[provider]


@app.on_event("startup")
async def startup_event():
    """Pre-initialize pipeline on server startup"""
    logger.info("Server starting up...")
    if MOCK_PIPELINE:
        logger.info("Mock mode enabled – skipping pipeline initialization.")
        return
    try:
        get_pipeline()
        logger.info("Server ready to accept requests")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
