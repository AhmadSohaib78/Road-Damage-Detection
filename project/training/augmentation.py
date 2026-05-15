#!/usr/bin/env python
"""
Augmentation Strategy Documentation
=====================================
This module documents and demonstrates the augmentation pipeline used
during training. YOLOv8 applies augmentation natively via its training
loop using Albumentations internally; this script also shows how to apply
augmentations manually for analysis/visualization.

Augmentation rationale:
  Road imagery varies significantly across:
  - Lighting (sunny, overcast, low-angle sun)
  - Weather (dry, wet, light rain)
  - Camera angle & motion blur
  - Road type (asphalt, concrete, patchy)
  
  We simulate these variations to improve generalization.

Usage:
    python augmentation.py --sample_image path/to/image.jpg
"""

import argparse
import logging
from pathlib import Path

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Augmentation Configuration (used by YOLOv8 hyp.yaml override)
# ─────────────────────────────────────────────────────────────

YOLO_AUGMENTATION_CONFIG = {
    # Geometric transforms
    "degrees": 5.0,          # Rotation ±5° (road tilt from mounting)
    "translate": 0.1,        # 10% translation (camera shake)
    "scale": 0.5,            # Scale ±50% (distance variation)
    "shear": 2.0,            # Shear ±2° (perspective change)
    "perspective": 0.001,    # Perspective warp
    "flipud": 0.0,           # No vertical flip (roads always on bottom)
    "fliplr": 0.5,           # 50% horizontal flip (left/right road symmetry)

    # Color & photometric transforms
    "hsv_h": 0.015,          # Hue shift (lighting color temperature)
    "hsv_s": 0.7,            # Saturation change (vivid vs. muted)
    "hsv_v": 0.4,            # Brightness change (shadows, sun glare)

    # Advanced augmentations
    "mosaic": 1.0,           # Mosaic (combine 4 images) — trains multi-scale
    "mixup": 0.1,            # MixUp — improves generalization
    "copy_paste": 0.1,       # Copy-paste augmentation for small objects
    "erasing": 0.4,          # Random erasing (simulates partial occlusion)
    "auto_augment": "randaugment",  # Additional auto-augment policy
    "blur": 0.01,            # Gaussian blur (motion / defocus)
    "median_blur": 0.01,     # Median blur (noise in wet conditions)
}

AUGMENTATION_RATIONALE = """
AUGMENTATION DECISIONS
======================

1. HorizontalFlip (p=0.5)
   - Road damage is symmetric left-right
   - Doubles effective dataset size for free
   - Well-established for road image augmentation

2. BrightnessContrast (hsv_v=0.4)
   - Dataset captured Feb-Mar under varying lighting
   - Shadows from trees/buildings can obscure cracks
   - Models trained without this fail on shadows

3. GaussianBlur / MedianBlur (p=0.01)
   - Vehicle speed 20-50 km/h introduces motion blur
   - Ensures model works with real dashcam footage

4. Scale (±50%) + Mosaic
   - Pothole size varies greatly (15cm vs 1m)
   - Mosaic aggregates 4 images → enriches context
   - Critical for small-pothole detection

5. Rotation (±5°)
   - Cameras mounted at 10-15° angles vary slightly
   - Road cant on curved roads

6. MixUp (p=0.1)
   - Helps model generalize across road types
   - Reduces overconfidence on clean asphalt patterns

7. Copy-Paste (p=0.1)
   - Synthetically increases rare small-pothole samples
   - Addresses slight class imbalance in small objects

Excluded augmentations:
- VerticalFlip: roads always appear in correct orientation
- RandomFog/Rain: dataset explicitly excludes severe weather
- CutOut >40%: excessive occlusion destroys bounding box signal
"""


def demonstrate_augmentations(sample_image_path: str, output_dir: str = "outputs/augmentation_demo") -> None:
    """
    Apply augmentation pipeline to a sample image and save results.
    Requires: albumentations, opencv-python, matplotlib
    """
    try:
        import albumentations as A
        import cv2
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        log.error(f"Missing dependency for demo: {e}. Install with: pip install albumentations matplotlib")
        return

    img_path = Path(sample_image_path)
    if not img_path.exists():
        log.error(f"Image not found: {img_path}")
        return

    image = cv2.imread(str(img_path))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    transforms = [
        ("Original", None),
        ("HorizontalFlip", A.HorizontalFlip(p=1.0)),
        ("BrightnessContrast", A.RandomBrightnessContrast(p=1.0)),
        ("GaussianBlur", A.GaussianBlur(blur_limit=(3, 7), p=1.0)),
        ("HueSaturation", A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=40, p=1.0)),
        ("ShiftScaleRotate", A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.2, rotate_limit=5, p=1.0)),
        ("GridDistort", A.GridDistortion(p=1.0)),
        ("RandomGamma", A.RandomGamma(p=1.0)),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle("Road Damage Detection — Augmentation Pipeline Demo", fontsize=14, fontweight="bold")

    for ax, (name, transform) in zip(axes.flat, transforms):
        if transform is None:
            aug_img = image
        else:
            aug_img = transform(image=image)["image"]
        ax.imshow(aug_img)
        ax.set_title(name, fontsize=10)
        ax.axis("off")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "augmentation_demo.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Augmentation demo saved to {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Show augmentation pipeline")
    parser.add_argument("--sample_image", required=False, default=None, help="Path to sample image")
    parser.add_argument("--output_dir", default="outputs/augmentation_demo", help="Output directory")
    args = parser.parse_args()

    print(AUGMENTATION_RATIONALE)

    if args.sample_image:
        demonstrate_augmentations(args.sample_image, args.output_dir)
    else:
        log.info("No sample image provided. Run with --sample_image path/to/img.jpg to generate demo.")
