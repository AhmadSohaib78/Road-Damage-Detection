#!/usr/bin/env python
"""
Standalone script to train YOLOv8 model for road damage detection

Usage:
    python train.py --epochs 100 --batch 16 --device 0
"""

import argparse
import logging
from pathlib import Path
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 model for road damage detection"
    )
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", default="0", help="Device (0 for GPU, cpu for CPU)")
    parser.add_argument("--model", default="yolov8n.pt", help="Model variant")
    parser.add_argument("--dataset", type=str, default="outputs/yolo_dataset/data.yaml",
                       help="Path to dataset yaml")
    parser.add_argument("--project", default="outputs", help="Project directory")
    parser.add_argument("--name", default="yolov8n_road_damage", help="Run name")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Road Damage Detection - YOLOv8 Training")
    logger.info("=" * 60)
    logger.info(f"Model: {args.model}")
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Batch Size: {args.batch}")
    logger.info(f"Image Size: {args.imgsz}")
    logger.info(f"Device: {args.device}")
    logger.info(f"Dataset: {args.dataset}")
    logger.info("=" * 60)
    
    # Verify dataset exists
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.info("Please run data preparation notebook first")
        return
    
    # Load model
    logger.info(f"Loading {args.model}...")
    model = YOLO(args.model)
    
    # Train
    logger.info("Starting training...")
    results = model.train(
        data=str(dataset_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        save=True,
        plots=True,
        project=args.project,
        name=args.name,
        patience=20,
        augment=True,
        conf=0.5,
        verbose=True
    )
    
    logger.info("=" * 60)
    logger.info("Training Completed!")
    logger.info(f"Best model: {Path(args.project) / args.name / 'weights' / 'best.pt'}")
    logger.info("=" * 60)
    
    # Evaluate
    logger.info("Evaluating on test set...")
    metrics = model.val()
    logger.info(f"mAP50: {metrics.box.map50:.4f}")
    logger.info(f"mAP50-95: {metrics.box.map:.4f}")


if __name__ == "__main__":
    main()
