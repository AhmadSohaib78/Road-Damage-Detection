"""
Health Route — /api/v1/health
"""

import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import importlib

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns system status, model state, and dependency availability.
    """
    try:
        import torch
        torch_ok = True
        cuda_ok = torch.cuda.is_available()
        cuda_device = torch.cuda.get_device_name(0) if cuda_ok else "N/A"
    except ImportError:
        torch_ok = False
        cuda_ok = False
        cuda_device = "N/A"

    try:
        import cv2
        cv2_ok = True
    except ImportError:
        cv2_ok = False

    try:
        from ultralytics import YOLO
        yolo_ok = True
    except ImportError:
        yolo_ok = False

    # Model status
    try:
        module = importlib.import_module("main")
        manager = getattr(module, "model_manager", None)
        model_loaded = manager is not None and manager.model is not None
        model_type = getattr(manager, "model_type", "none") if manager else "none"
        model_version = getattr(manager, "model_version", "unloaded") if manager else "unloaded"
    except Exception:
        model_loaded = False
        model_type = "unknown"
        model_version = "unknown"

    all_ok = torch_ok and cv2_ok and model_loaded

    return JSONResponse(
        status_code=200 if all_ok else 206,
        content={
            "status": "healthy" if all_ok else "degraded",
            "model": {
                "loaded": model_loaded,
                "type": model_type,
                "version": model_version,
            },
            "dependencies": {
                "torch": torch_ok,
                "cuda": cuda_ok,
                "cuda_device": cuda_device,
                "cv2": cv2_ok,
                "ultralytics": yolo_ok,
            },
        },
    )
