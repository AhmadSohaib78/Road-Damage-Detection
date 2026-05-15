"""
Model Manager — Inference Engine
=================================
Handles loading, preprocessing, inference, and postprocessing for both:
  - Model v1: SSD MobileNetV2 (baseline)
  - Model v2: YOLOv8n (main model, default for deployment)

Design principles:
  - Singleton: model loaded once at startup, reused across requests
  - Configurable: switch model versions via config without code changes
  - Separation: preprocessing / inference / postprocessing are distinct methods
  - Production-ready: confidence threshold filtering, severity estimation,
    annotated image generation, error handling with logging
"""

import base64
import io
import logging
import os
import time
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# ── Optional heavyweight imports — fail gracefully ──────────────
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    cv2 = None
    np = None
    Image = None
    ImageDraw = None
    ImageFont = None
    log.warning(f"Image dependency missing: {e}")

try:
    import torch
    from ultralytics import YOLO
except ImportError:
    torch = None
    YOLO = None
    log.warning("ultralytics / torch not available")

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

CLASS_NAMES = ["pothole", "crack"]

# Severity: area_ratio = bbox_area / image_area
SEVERITY_LOW_MAX = 0.02
SEVERITY_MED_MAX = 0.08

# Bounding box colours per class (BGR for cv2)
CLASS_COLORS_BGR = {
    "pothole": (0, 77, 255),    # vivid orange-red
    "crack":   (0, 220, 30),    # green
}

# RGB versions for PIL
CLASS_COLORS_RGB = {
    "pothole": (255, 77, 0),
    "crack":   (30, 220, 0),
}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _calculate_severity(area_ratio: float) -> str:
    """
    Heuristic severity based on bounding box area relative to image.
    Note: This is NOT a learned model — it is a rule-based heuristic
    suitable for a production MVP where ground-truth severity labels
    are unavailable.
    """
    if area_ratio < SEVERITY_LOW_MAX:
        return "low"
    elif area_ratio < SEVERITY_MED_MAX:
        return "medium"
    return "high"


def _draw_annotations(image_bgr: "np.ndarray", detections: list[dict]) -> "np.ndarray":
    """Draw bounding boxes and labels onto a copy of the image."""
    out = image_bgr.copy()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cls_name = det["class"]
        conf = det["confidence"]
        severity = det["severity"]

        color = CLASS_COLORS_BGR.get(cls_name, (255, 255, 255))
        thickness = 2

        cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness)

        label = f"{cls_name} {conf:.0%} [{severity}]"
        (lw, lh), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        label_y = max(y1, lh + 6)
        cv2.rectangle(out, (x1, label_y - lh - baseline - 4), (x1 + lw + 4, label_y), color, -1)
        cv2.putText(out, label, (x1 + 2, label_y - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    return out


def _image_to_base64(image_bgr: "np.ndarray") -> str:
    """Encode annotated BGR image as base64 JPEG string."""
    _, buf = cv2.imencode(".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return base64.b64encode(buf.tobytes()).decode("utf-8")


# ─────────────────────────────────────────────────────────────
# Model Manager
# ─────────────────────────────────────────────────────────────

class ModelManager:
    """
    Singleton-style manager for the active detection model.
    Supports both YOLOv8n (primary) and SSD MobileNetV2 (baseline).
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        confidence_threshold: float = 0.40,
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_type: str = "none"   # "yolo" | "ssd"
        self.model_version: str = "unloaded"

        # Auto-detect device
        if device:
            self.device = device
        elif torch is not None and torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        log.info(f"ModelManager initialised | device={self.device} | conf_thresh={confidence_threshold}")

    # ── Loading ───────────────────────────────────────────────

    def load_yolov8_model(self, weights_path: Optional[str] = None) -> bool:
        """Load YOLOv8n weights (custom fine-tuned or pretrained)."""
        if YOLO is None or torch is None:
            log.error("ultralytics / torch not installed")
            return False

        try:
            # Try custom weights first
            if weights_path and Path(weights_path).exists():
                path = weights_path
                self.model_version = "model_v2_yolo (fine-tuned)"
            else:
                # Fallback: search for trained weights relative to project
                # We check multiple common locations and naming conventions
                candidates = [
                    # Best model locations
                    Path("project/outputs/yolo_transfer_learning/weights/best.pt"),
                    Path("outputs/yolo_transfer_learning/weights/best.pt"),
                    
                    # Unified model folder
                    Path("project/outputs/models/model_v2_yolo_transfer.pt"),
                    Path("outputs/models/model_v2_yolo_transfer.pt"),
                    Path("project/outputs/models/model_v2_yolo.pt"),
                    Path("outputs/models/model_v2_yolo.pt"),
                    
                    # Basic model as fallback
                    Path("project/outputs/stage1_base_model/weights/best.pt"),
                    Path("outputs/stage1_base_model/weights/best.pt"),
                    
                    # Relative to script (for different execution contexts)
                    Path(__file__).parent.parent.parent / "outputs/yolo_transfer_learning/weights/best.pt",
                    Path(__file__).parent.parent.parent / "outputs/models/model_v2_yolo_transfer.pt",
                ]
                
                found = next((p for p in candidates if p.exists()), None)
                if found:
                    path = str(found.absolute())
                    self.model_version = "model_v2_yolo (fine-tuned)"
                    log.info(f"Found fine-tuned weights at: {path}")
                else:
                    path = "yolov8n.pt"   # Download pretrained from ultralytics
                    self.model_version = "yolov8n (COCO pretrained — not fine-tuned)"
                    log.warning(
                        "Fine-tuned weights not found in any candidate path. Using stock yolov8n.pt.\n"
                        "Expected locations: project/outputs/yolo_transfer_learning/weights/best.pt"
                    )

            log.info(f"Loading YOLOv8 model from: {path}")
            self.model = YOLO(path)
            self.model_type = "yolo"
            log.info(f"YOLOv8 loaded ✓ — {self.model_version}")
            return True

        except Exception as e:
            log.error(f"Failed to load YOLOv8: {e}", exc_info=True)
            return False

    def load_ssd_model(self, weights_path: str) -> bool:
        """Load SSD MobileNetV2 baseline model."""
        if torch is None:
            log.error("torch not installed")
            return False
        try:
            from torchvision.models.detection import ssdlite320_mobilenet_v3_large
            from functools import partial
            import torch.nn as nn
            from torchvision.models.detection.ssdlite import SSDLiteClassificationHead

            num_classes = len(CLASS_NAMES) + 1  # +1 background

            model = ssdlite320_mobilenet_v3_large(weights=None, num_classes=num_classes)
            checkpoint = torch.load(weights_path, map_location=self.device)

            # Rebuild head to match checkpoint
            in_channels = [96, 1280]
            num_anchors = model.anchor_generator.num_anchors_per_location()
            model.head.classification_head = SSDLiteClassificationHead(
                in_channels=in_channels,
                num_anchors=num_anchors,
                num_classes=num_classes,
                norm_layer=partial(nn.BatchNorm2d, eps=0.001, momentum=0.03),
            )

            model.load_state_dict(checkpoint["model_state_dict"])
            model.to(self.device)
            model.eval()

            self.model = model
            self.model_type = "ssd"
            self.model_version = f"model_v1_ssd (mAP@0.5={checkpoint.get('mAP50', 'N/A')})"
            log.info(f"SSD model loaded ✓ — {self.model_version}")
            return True

        except Exception as e:
            log.error(f"Failed to load SSD: {e}", exc_info=True)
            return False

    # ── Preprocessing ─────────────────────────────────────────

    def preprocess_image(self, image_bytes: bytes) -> Optional["np.ndarray"]:
        """
        Decode image bytes → numpy BGR array.
        Handles JPEG, PNG, RGBA inputs.
        """
        if Image is None or np is None or cv2 is None:
            log.error("PIL / numpy / cv2 missing")
            return None
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_array = np.array(pil_img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            log.debug(f"Image decoded: {img_bgr.shape}")
            return img_bgr
        except Exception as e:
            log.error(f"Image preprocessing failed: {e}")
            return None

    # ── Inference ─────────────────────────────────────────────

    def detect(self, image_bgr: "np.ndarray", conf: Optional[float] = None) -> dict:
        """
        Full inference pipeline:
          image_bgr → model_predict → parse → severity → annotate → base64

        Returns:
            dict with keys:
              detections, statistics, inference_time_ms,
              annotated_image_b64, model_name, device, confidence_threshold
        """
        if self.model is None:
            return {"error": "Model not loaded. Call load_yolov8_model() first.", "detections": []}

        if cv2 is None or np is None:
            return {"error": "cv2 / numpy not available", "detections": []}

        confidence = conf if conf is not None else self.confidence_threshold
        t_start = time.perf_counter()

        try:
            if self.model_type == "yolo":
                detections = self._infer_yolo(image_bgr, confidence)
            elif self.model_type == "ssd":
                detections = self._infer_ssd(image_bgr, confidence)
            else:
                return {"error": "Unknown model type", "detections": []}

        except Exception as e:
            log.error(f"Inference error: {e}", exc_info=True)
            return {"error": str(e), "detections": []}

        inference_ms = round((time.perf_counter() - t_start) * 1000, 2)

        # Annotate image
        annotated = _draw_annotations(image_bgr, detections)
        annotated_b64 = _image_to_base64(annotated)

        # Statistics
        stats = self._compute_statistics(detections)

        return {
            "detections": detections,
            "statistics": stats,
            "inference_time_ms": inference_ms,
            "annotated_image_b64": annotated_b64,
            "model_name": "YOLOv8n" if self.model_type == "yolo" else "SSD MobileNetV2",
            "model_version": self.model_version,
            "device": self.device,
            "confidence_threshold": confidence,
            "image_shape": {
                "height": image_bgr.shape[0],
                "width": image_bgr.shape[1],
            },
        }

    # ── Model-specific inference ──────────────────────────────

    def _infer_yolo(self, image_bgr: "np.ndarray", confidence: float) -> list[dict]:
        results = self.model.predict(image_bgr, conf=confidence, device=self.device, verbose=False)
        return self._parse_yolo_result(results[0], image_bgr.shape)

    def _infer_ssd(self, image_bgr: "np.ndarray", confidence: float) -> list[dict]:
        import torch
        import torchvision.transforms as T

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        from PIL import Image as PILImage
        pil_img = PILImage.fromarray(image_rgb)
        tensor = T.ToTensor()(pil_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)

        output = outputs[0]
        h, w = image_bgr.shape[:2]
        detections = []

        for box, label, score in zip(
            output["boxes"].cpu().tolist(),
            output["labels"].cpu().tolist(),
            output["scores"].cpu().tolist(),
        ):
            if score < confidence:
                continue
            cls_id = label - 1  # undo background shift
            if cls_id < 0 or cls_id >= len(CLASS_NAMES):
                continue
            x1, y1, x2, y2 = [int(v) for v in box]
            area_ratio = ((x2 - x1) * (y2 - y1)) / (w * h)
            detections.append({
                "class": CLASS_NAMES[cls_id],
                "class_id": cls_id,
                "confidence": round(score, 4),
                "bbox": [x1, y1, x2, y2],
                "area_ratio": round(area_ratio, 4),
                "severity": _calculate_severity(area_ratio),
            })

        return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    def _parse_yolo_result(self, result, image_shape: tuple) -> list[dict]:
        h, w = image_shape[:2]
        detections = []
        if result.boxes is None:
            return detections

        for box in result.boxes:
            try:
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].cpu().tolist()]
                conf = float(box.conf[0].cpu())
                cls_id = int(box.cls[0].cpu())
                cls_name = result.names.get(cls_id, f"class_{cls_id}")
                area_ratio = ((x2 - x1) * (y2 - y1)) / (w * h)

                detections.append({
                    "class": cls_name,
                    "class_id": cls_id,
                    "confidence": round(conf, 4),
                    "bbox": [x1, y1, x2, y2],
                    "area_ratio": round(area_ratio, 4),
                    "severity": _calculate_severity(area_ratio),
                })
            except Exception as e:
                log.warning(f"Skipping malformed detection: {e}")

        return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    # ── Statistics ────────────────────────────────────────────

    @staticmethod
    def _compute_statistics(detections: list[dict]) -> dict:
        if not detections:
            return {
                "total": 0,
                "by_class": {name: 0 for name in CLASS_NAMES},
                "severity": {"low": 0, "medium": 0, "high": 0},
                "avg_confidence": 0.0,
            }

        by_class = {name: 0 for name in CLASS_NAMES}
        severity = {"low": 0, "medium": 0, "high": 0}
        confs = []

        for d in detections:
            by_class[d["class"]] = by_class.get(d["class"], 0) + 1
            severity[d["severity"]] = severity.get(d["severity"], 0) + 1
            confs.append(d["confidence"])

        return {
            "total": len(detections),
            "by_class": by_class,
            "severity": severity,
            "avg_confidence": round(sum(confs) / len(confs), 4),
        }

    # ── Cleanup ───────────────────────────────────────────────

    def cleanup(self) -> None:
        """Release model from memory."""
        if self.model is not None:
            try:
                del self.model
                if torch is not None:
                    torch.cuda.empty_cache()
                log.info("Model released from memory.")
            except Exception as e:
                log.warning(f"Cleanup warning: {e}")
            finally:
                self.model = None
