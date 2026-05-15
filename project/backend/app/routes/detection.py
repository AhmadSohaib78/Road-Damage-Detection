"""
Detection Routes — /api/v1/detect
===================================
POST /detect     — Run inference on uploaded image
GET  /model/info — Current model version and config
GET  /health     — Quick health check
"""

import logging
import json
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Query, Request
from fastapi.responses import JSONResponse
import importlib

log = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB


def _get_manager(request: Request):
    """Retrieve the ModelManager instance from app state."""
    return getattr(request.app.state, "model_manager", None)


# ─────────────────────────────────────────────────────────────
# Detection endpoint
# ─────────────────────────────────────────────────────────────

@router.post("/detect")
async def detect_road_damage(
    request: Request,
    file: UploadFile = File(..., description="Road image (JPEG/PNG)"),
    confidence: float = Query(0.50, ge=0.0, le=1.0, description="Confidence threshold"),
):
    """
    Detect road damage (potholes and cracks) in an uploaded image.

    - **file**: Image file (JPEG or PNG, max 15 MB)
    - **confidence**: Minimum confidence to include a detection (default 0.5)

    Returns annotated image (base64), per-detection list with severity,
    aggregate statistics, and inference time.
    """
    try:
        # ── Validate file type ─────────────────────────────
        if file.content_type not in ALLOWED_TYPES:
            return JSONResponse(
                status_code=415,
                content={"error": f"Unsupported file type: {file.content_type}. Use JPEG or PNG."},
            )

        # ── Read bytes ─────────────────────────────────────
        image_bytes = await file.read()
        if not image_bytes:
            return JSONResponse(status_code=400, content={"error": "Empty file received."})
        if len(image_bytes) > MAX_FILE_SIZE:
            return JSONResponse(status_code=413, content={"error": "File exceeds 15 MB limit."})

        # ── Get model ──────────────────────────────────────
        manager = _get_manager(request)
        if manager is None or manager.model is None:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Model not ready. The server is still initialising or model loading failed.",
                    "tip": "Run the training scripts first to generate model weights.",
                },
            )

        # ── Preprocess ─────────────────────────────────────
        image_bgr = manager.preprocess_image(image_bytes)
        if image_bgr is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not decode image. Ensure the file is a valid JPEG or PNG."},
            )

        # ── Inference ──────────────────────────────────────
        result = manager.detect(image_bgr, conf=confidence)

        if "error" in result:
            return JSONResponse(status_code=500, content=result)

        # ── Attach filename ────────────────────────────────
        result["file_name"] = file.filename
        return result

    except Exception as e:
        log.error(f"/detect unhandled exception: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during detection."},
        )


# ─────────────────────────────────────────────────────────────
# Model info
# ─────────────────────────────────────────────────────────────

@router.get("/model/info")
async def get_model_info(request: Request):
    """Return metadata about the currently loaded model."""
    try:
        manager = _get_manager(request)
        if manager is None or manager.model is None:
            return JSONResponse(
                status_code=503,
                content={"status": "Model not loaded", "ready": False},
            )

        eval_report = None
        report_candidates = [
            Path("outputs/models/yolo_transfer_results.json"),
            Path("../outputs/models/yolo_transfer_results.json"),
            Path("../../project/outputs/models/yolo_transfer_results.json"),
            Path("project/outputs/models/yolo_transfer_results.json"),
        ]
        report_path = next((p for p in report_candidates if p.exists()), None)
        if report_path:
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    eval_report = json.load(f)
            except Exception as e:
                log.warning(f"Could not read evaluation report: {e}")

        # ── Dataset Stats ──────────────────────────────────
        dataset_stats = None
        stats_path = Path("project/outputs/dataset_stats.json")
        if stats_path.exists():
            try:
                with open(stats_path, "r", encoding="utf-8") as f:
                    dataset_stats = json.load(f)
            except Exception as e:
                log.warning(f"Could not read dataset stats: {e}")

        # ── Model Comparisons ──────────────────────────────
        comparisons = [
            {"name": "Stage 2: YOLO Fine-tuned (Best)", "mAP50": 0.8354, "size": "50 MB", "latency": "~50ms", "status": "Best"},
            {"name": "Stage 1: SSD MobileNet (Baseline)", "mAP50": 0.6458, "size": "17.3 MB", "latency": "~150ms", "status": "Good"},
            {"name": "YOLO Stock", "mAP50": 0.4471, "size": "23.3 MB", "latency": "~40ms", "status": "Baseline"},
        ]

        response = {
            "ready": True,
            "model_type": manager.model_type,
            "model_version": manager.model_version,
            "device": manager.device,
            "confidence_threshold": manager.confidence_threshold,
            "classes": ["pothole", "crack"],
            "num_classes": 2,
            "image_size": 640,
            "framework": "Ultralytics YOLOv8" if manager.model_type == "yolo" else "torchvision SSD",
            "dataset_stats": dataset_stats,
            "comparisons": comparisons,
            "pipeline": ["Input", "Preprocessing (Resize 640x640, Normalization)", "Model Inference", "Postprocessing (NMS, Scaling)"],
            "severity_thresholds": {
                "low": "area_ratio < 0.02",
                "medium": "0.02 <= area_ratio < 0.08",
                "high": "area_ratio >= 0.08",
            },
        }

        if eval_report:
            response["evaluation"] = eval_report

        return response
    except Exception as e:
        log.error(f"/model/info error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
