"""
AI Smart Road Damage Detection API
Main FastAPI application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from app.routes import detection, health
    from inference.model_manager import ModelManager
except ImportError:
    from .app.routes import detection, health
    from .inference.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model manager
model_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global model_manager
    
    # Startup
    logger.info("Initializing AI Smart Road Damage Detection API...")
    manager = ModelManager()
    app.state.model_manager = manager
    
    # Load models
    try:
        if manager.load_yolov8_model():
            logger.info("YOLOv8 model loaded successfully")
        else:
            logger.error("Failed to load YOLOv8 model")
    except Exception as e:
        logger.error(f"Failed to load YOLOv8 model: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    manager = getattr(app.state, "model_manager", None)
    if manager:
        manager.cleanup()


# Create FastAPI app
app = FastAPI(
    title="AI Smart Road Damage Detection API",
    description="Production-ready API for detecting road damage (potholes & cracks)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(detection.router, prefix="/api/v1", tags=["Detection"])

# Serve static files from outputs
import os
outputs_path = "project/outputs"
if os.path.exists(outputs_path):
    app.mount("/outputs", StaticFiles(directory=outputs_path), name="outputs")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Smart Road Damage Detection API",
        "version": "1.0.0",
        "status": "active"
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
