"""
Central Configuration
=====================
Single source of truth for all paths, thresholds, and model settings.
All scripts import from here; override via environment variables or a .env file.
"""

from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Project root (2 levels up from this file: project/training/config.py → project/)
# ─────────────────────────────────────────────────────────────
TRAINING_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = TRAINING_DIR.parent.resolve()
REPO_ROOT = PROJECT_DIR.parent.resolve()

# ─────────────────────────────────────────────────────────────
# Dataset paths
# ─────────────────────────────────────────────────────────────
DATASET_RAW_ROOT = REPO_ROOT / "dataset" / "data"
DATASET_IMAGES = DATASET_RAW_ROOT / "images"
DATASET_LABELS_YOLO = DATASET_RAW_ROOT / "labels-YOLO"
DATASET_LABELS_POLY = DATASET_RAW_ROOT / "labels"

# ─────────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────────
OUTPUTS_DIR = PROJECT_DIR / "outputs"
YOLO_DATASET_DIR = OUTPUTS_DIR / "yolo_dataset"
DATA_YAML = YOLO_DATASET_DIR / "data.yaml"
MODELS_DIR = OUTPUTS_DIR / "models"
LOGS_DIR = OUTPUTS_DIR / "logs"
EDA_DIR = OUTPUTS_DIR / "eda"
AUG_DEMO_DIR = OUTPUTS_DIR / "augmentation_demo"

# ─────────────────────────────────────────────────────────────
# Model weights (after training)
# ─────────────────────────────────────────────────────────────
SSD_WEIGHTS = MODELS_DIR / "model_v1_ssd.pth"
YOLO_WEIGHTS = MODELS_DIR / "model_v2_yolo.pt"

# ─────────────────────────────────────────────────────────────
# Classes
# ─────────────────────────────────────────────────────────────
CLASS_NAMES = ["pothole", "crack"]
NUM_CLASSES = len(CLASS_NAMES)
VALID_CLASS_IDS = set(range(NUM_CLASSES))

# ─────────────────────────────────────────────────────────────
# Inference settings
# ─────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.50    # Detections below this are discarded
IOU_THRESHOLD = 0.45           # NMS IoU threshold
IMAGE_SIZE = 640               # Model input size

# ─────────────────────────────────────────────────────────────
# Severity thresholds (bbox_area / image_area)
# ─────────────────────────────────────────────────────────────
SEVERITY_LOW_MAX = 0.02        # < 2% of image → Low
SEVERITY_MED_MAX = 0.08        # 2–8% of image → Medium
# > 8% → High

# ─────────────────────────────────────────────────────────────
# Training defaults
# ─────────────────────────────────────────────────────────────
YOLO_EPOCHS = 120
YOLO_BATCH = 8
SSD_EPOCHS = 40
SSD_BATCH = 8
TRAIN_VAL_TEST_SPLIT = (0.80, 0.10, 0.10)
RANDOM_SEED = 42
