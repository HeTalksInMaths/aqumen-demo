"""
FastAPI server for dynamic adversarial question generation with SSE streaming.

REFACTORED: This file now imports from the modular api/ package.
The original monolithic implementation has been split into:
- api/main.py - FastAPI app initialization and configuration
- api/models.py - Pydantic request/response models
- api/endpoints.py - Route handlers
- api/streaming.py - SSE streaming implementation

This file remains as the entry point for backward compatibility.
"""

# Import the FastAPI app from the new modular structure

# Import all endpoints to register them with the app
import api.endpoints  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    # Run server
    # For development: uvicorn api_server:app --reload --port 8000
    # For production: configured via Render
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (dev only)
        log_level="info",
    )
