#!/usr/bin/env python
"""
Main Model Training: YOLOv8m (Ultralytics) — Full Fine-tuning
==============================================================
Trains YOLOv8m with transfer learning on the road damage dataset.
Training is restricted to two classes: pothole and crack.

This is the PRIMARY model deployed in the FastAPI inference service.

Model choice rationale:
  - YOLOv8m balances accuracy and GPU memory on an RTX 5050
  - Pretrained COCO weights → strong transfer learning starting point
  - Significantly different from SSD (anchor-based) → meaningful baseline comparison
  - Best.pt weights deploy directly to ONNX/TensorRT for production

Usage:
    python train_yolo.py --data ../outputs/yolo_dataset/data.yaml \
                          --epochs 120 --batch 16 --device 0
"""

import argparse
import json
import logging
import random
import shutil
from pathlib import Path

import numpy as np
import yaml

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ─────────────────────────────────────────────────────────────
# Hyperparameter config (rich augmentation + tuning)
# ─────────────────────────────────────────────────────────────

HYPER_PARAMS = {
    "optimizer": "SGD",
    "lr0": 0.0005,
    "patience": 15,
    "imgsz": 512,
    "mosaic": 1.0,
    "auto_augment": "randaugment",
    "copy_paste": 0.0,
}


def verify_dataset(data_yaml_path: Path) -> bool:
    """Check data.yaml and all split directories exist."""
    if not data_yaml_path.exists():
        log.error(f"data.yaml not found.")
        return False

    with open(data_yaml_path) as f:
        cfg = yaml.safe_load(f)

    root = Path(cfg["path"])
    for split in ["train", "val", "test"]:
        split_dir = root / split / "images"
        if not split_dir.exists():
            log.error(f"Missing split directory: {split_dir}")
            return False
        count = len(list(split_dir.glob("*.[jJ][pP]*")))
        log.info(f"  {split}: {count} images")

    return True


def main(args) -> None:
    try:
        from ultralytics import YOLO
        import torch
    except ImportError:
        log.error("ultralytics or torch not found.")
        return

    data_yaml_path = Path(args.data).resolve()
    output_dir = Path("project/outputs").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Verify data ──────────────────────────────────────
    log.info("Verifying dataset...")
    if not verify_dataset(data_yaml_path):
        return

    # ── 2. Device check ─────────────────────────────────────
    if args.device == "0" and not torch.cuda.is_available():
        args.device = "cpu"
    elif args.device == "0":
        log.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # ── 2.1 Reproducibility ─────────────────────────────────
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    # ── 3. Load model (TRANSFER LEARNING) ──────────────────
    log.info(f"STAGE 1: Loading pretrained {args.model} for fine-tuning...")
    model = YOLO(args.model)

    if args.half and args.device == "cpu":
        log.warning("FP16 mixed precision is not supported on CPU; disabling half precision.")
        args.half = False

    # ── 4. Train ────────────────────────────────────────────
    log.info("=" * 60)
    log.info(f"{args.model} — TRANSFER LEARNING")
    log.info(f"  Training Classes : pothole, crack")
    log.info(f"  Transfer Learning: ENABLED")
    log.info(f"  Epochs           : {args.epochs}")
    log.info(f"  Image Size       : {args.imgsz}")
    log.info(f"  Batch Size       : {args.batch}")
    log.info("=" * 60)

    results = model.train(
        data=str(data_yaml_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=str(output_dir),
        name="yolo_transfer_learning",
        lr0=args.lr,
        optimizer=args.optimizer,
        patience=args.patience,
        save=True,
        plots=True,
        val=True,
        exist_ok=True,
        augment=args.augment,
        mosaic=args.mosaic,
        auto_augment=args.auto_augment,
        copy_paste=args.copy_paste,
        half=args.half,
        workers=args.workers,
    )

    # ── 5. Copy weights ─────────────────────────────────────
    run_dir = output_dir / "yolo_transfer_learning"
    best_src = run_dir / "weights" / "best.pt"
    models_dir = output_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    if not best_src.exists():
        last_src = run_dir / "weights" / "last.pt"
        if last_src.exists():
            best_src = last_src
            log.warning("Best weights file not found; using last checkpoint instead.")

    if best_src.exists():
        shutil.copy2(best_src, models_dir / "model_v2_yolo.pt")
        shutil.copy2(best_src, models_dir / "model_v2_yolo_transfer.pt")
        log.info(f"TRANSFER LEARNING COMPLETE: Weights saved to: {models_dir / 'model_v2_yolo.pt'}")
        log.info(f"Transfer checkpoint also saved to: {models_dir / 'model_v2_yolo_transfer.pt'}")
    else:
        log.error("No trained YOLO weights were found after training. Please check the run directory and verify training completed successfully.")

    # ── 6. Evaluate on test set ─────────────────────────────
    log.info("Running evaluation on test set...")
    best_model = YOLO(str(models_dir / "model_v2_yolo.pt"))
    test_metrics = best_model.val(
        data=str(data_yaml_path),
        split="test",
        device=args.device,
    )

    log.info("=" * 60)
    log.info("TRANSFER LEARNING SUMMARY")
    log.info(f"  Final mAP@0.5: {test_metrics.box.map50:.4f}")
    log.info(f"  mAP@0.5-0.95: {test_metrics.box.map:.4f}")
    log.info("=" * 60)

    # Save evaluation results for comparison and dashboard reporting
    eval_report = {
        "model": f"{args.model} Transfer Learning",
        "classes": ["pothole", "crack"],
        "mAP50": float(test_metrics.box.map50),
        "mAP50_95": float(test_metrics.box.map),
        "confidence": float(test_metrics.box.conf[0]) if hasattr(test_metrics.box, 'conf') else None,
        "device": args.device,
    }
    with open(models_dir / "yolo_transfer_results.json", "w") as f:
        json.dump(eval_report, f, indent=2)
    log.info(f"Evaluation report written to {models_dir / 'yolo_transfer_results.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8m with transfer learning and high-accuracy tuning")
    parser.add_argument("--data", default="project/outputs/yolo_dataset/data.yaml")
    parser.add_argument("--model", default="yolov8m.pt", help="Pretrained YOLOv8 backbone for transfer learning")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size")
    parser.add_argument("--device", default="0")
    parser.add_argument("--lr", type=float, default=0.0005, help="Learning rate for fine-tuning")
    parser.add_argument("--optimizer", default="SGD", help="Optimizer to use during training")
    parser.add_argument("--patience", type=int, default=12, help="Early stopping patience (epochs)")
    parser.add_argument("--workers", type=int, default=0, help="Number of data loader workers (0 for Windows compatibility)")
    parser.add_argument("--no-augment", dest="augment", action="store_false", default=True, help="Disable standard YOLO augmentation")
    parser.add_argument("--auto-augment", default="randaugment", help="Auto augment policy")
    parser.add_argument("--mosaic", type=float, default=1.0, help="Mosaic augmentation probability")
    parser.add_argument("--copy-paste", type=float, default=0.0, help="Copy-paste augmentation probability")
    parser.add_argument("--half", action="store_true", default=True, help="Enable FP16 mixed precision")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()
    main(args)
