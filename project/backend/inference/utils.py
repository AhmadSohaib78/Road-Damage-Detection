"""
Utility functions for image processing and inference
"""

import cv2
import numpy as np
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


def load_image(image_path: str) -> np.ndarray:
    """Load image from file"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    return img


def resize_image(image: np.ndarray, target_size: int = 640) -> Tuple[np.ndarray, float]:
    """
    Resize image to target size maintaining aspect ratio
    
    Returns:
        Resized image and scale factor
    """
    h, w = image.shape[:2]
    scale = target_size / max(h, w)
    new_size = (int(w * scale), int(h * scale))
    resized = cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)
    return resized, scale


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to [0, 1]"""
    return image.astype(np.float32) / 255.0


def draw_detections(image: np.ndarray, detections: list) -> np.ndarray:
    """Draw bounding boxes on image"""
    annotated = image.copy()
    
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        conf = det['confidence']
        class_name = det['class']
        
        # Color based on class
        color = (0, 0, 255) if class_name == 'pothole' else (0, 165, 255)
        
        # Draw box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{class_name} {conf:.2f}"
        cv2.putText(annotated, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return annotated


def calculate_iou(box1: List[int], box2: List[int]) -> float:
    """Calculate Intersection over Union"""
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    inter_xmin = max(x1_min, x2_min)
    inter_ymin = max(y1_min, y2_min)
    inter_xmax = min(x1_max, x2_max)
    inter_ymax = min(y1_max, y2_max)
    
    if inter_xmax < inter_xmin or inter_ymax < inter_ymin:
        return 0.0
    
    inter_area = (inter_xmax - inter_xmin) * (inter_ymax - inter_ymin)
    
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    
    union_area = box1_area + box2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0.0


def filter_detections(detections: list, confidence_threshold: float = 0.5) -> list:
    """Filter detections below confidence threshold"""
    return [det for det in detections if det['confidence'] >= confidence_threshold]
