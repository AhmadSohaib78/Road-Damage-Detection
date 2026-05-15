#!/usr/bin/env python
"""
Baseline Model Training: SSD MobileNetV2 (torchvision)
=======================================================
Trains an SSD with MobileNetV2 backbone (pretrained on COCO) fine-tuned
on the road damage dataset (two classes: pothole and crack).

This serves as the BASELINE for comparison with YOLOv8n.

Architecture choice rationale:
  - SSD is a well-established single-stage detector (2016, Liu et al.)
  - MobileNetV2 backbone: lightweight, proven on mobile vision tasks
  - Both model + backbone are pretrained on COCO — fair comparison with YOLOv8n
  - Different architecture family → meaningful comparison (anchor-based vs anchor-free)

Usage:
    python train_baseline.py --data_yaml ../outputs/yolo_dataset/data.yaml \
                              --epochs 40 --batch 8 --lr 0.005
"""

import argparse
import json
import logging
import time
from pathlib import Path

import yaml

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ─────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────

def parse_yolo_label(label_path: Path, img_w: int, img_h: int) -> dict:
    """Convert YOLO label file → COCO-style target dict for torchvision."""
    import torch
    boxes, labels = [], []
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls_id = int(parts[0])
            xc, yc, bw, bh = map(float, parts[1:5])
            x1 = (xc - bw / 2) * img_w
            y1 = (yc - bh / 2) * img_h
            x2 = (xc + bw / 2) * img_w
            y2 = (yc + bh / 2) * img_h
            # Clamp to image bounds
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(img_w, x2), min(img_h, y2)
            if x2 > x1 and y2 > y1:
                boxes.append([x1, y1, x2, y2])
                labels.append(cls_id + 1)  # torchvision: 0 = background, so shift +1

    if not boxes:
        return None

    return {
        "boxes": torch.tensor(boxes, dtype=torch.float32),
        "labels": torch.tensor(labels, dtype=torch.int64),
    }


class RoadDamageDataset:
    """PyTorch Dataset for road damage detection (YOLO-format labels)."""

    def __init__(self, images_dir: Path, labels_dir: Path, transforms=None):
        import torchvision.transforms as T
        self.transforms = transforms or T.Compose([T.ToTensor()])
        self.images_dir = images_dir
        self.labels_dir = labels_dir

        self.image_paths = sorted(
            p for p in images_dir.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        # Filter to only images that have a valid label
        valid = []
        for img_path in self.image_paths:
            lbl_path = labels_dir / (img_path.stem + ".txt")
            if lbl_path.exists() and lbl_path.stat().st_size > 0:
                valid.append(img_path)
        self.image_paths = valid
        log.info(f"Dataset loaded: {len(self.image_paths)} images from {images_dir}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        from PIL import Image
        img_path = self.image_paths[idx]
        lbl_path = self.labels_dir / (img_path.stem + ".txt")

        image = Image.open(img_path).convert("RGB")
        img_w, img_h = image.size

        target = parse_yolo_label(lbl_path, img_w, img_h)
        if target is None:
            import torch
            import torchvision.transforms as T
            return T.ToTensor()(image), {
                "boxes": torch.zeros((0, 4), dtype=torch.float32),
                "labels": torch.zeros(0, dtype=torch.int64),
            }

        if self.transforms:
            image = self.transforms(image)

        return image, target


def collate_fn(batch):
    return tuple(zip(*batch))


# ─────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────

def build_ssd_model(num_classes: int):
    """
    Load SSD MobileNetV2 pretrained on COCO, replace classification head
    for num_classes + 1 (background) output classes.
    """
    import torch
    from torchvision.models.detection import ssdlite320_mobilenet_v3_large
    from torchvision.models.detection import SSDLite320_MobileNet_V3_Large_Weights

    log.info("Loading SSDLite320 + MobileNetV3-Large (pretrained COCO)...")
    weights = SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
    model = ssdlite320_mobilenet_v3_large(weights=weights, num_classes=91)

    # Re-build head for our num_classes
    from torchvision.models.detection.ssdlite import SSDLiteClassificationHead
    from functools import partial
    import torch.nn as nn

    in_channels = [m[0][0].in_channels for m in model.head.classification_head.module_list]
    num_anchors = model.anchor_generator.num_anchors_per_location()

    model.head.classification_head = SSDLiteClassificationHead(
        in_channels=in_channels,
        num_anchors=num_anchors,
        num_classes=num_classes,
        norm_layer=partial(nn.BatchNorm2d, eps=0.001, momentum=0.03),
    )

    log.info(f"SSD head rebuilt for {num_classes} classes (incl. background)")
    return model


# ─────────────────────────────────────────────────────────────
# Evaluation helpers
# ─────────────────────────────────────────────────────────────

def compute_iou(box1, box2):
    """Compute IoU between two [x1,y1,x2,y2] boxes."""
    import torch
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    a1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    a2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = a1 + a2 - inter
    return inter / union if union > 0 else 0.0


def evaluate_model(model, data_loader, device, iou_thresh: float = 0.5, conf_thresh: float = 0.5):
    """
    Simple mAP@0.5 evaluation.
    Returns per-class precision, recall, and overall mAP.
    """
    import torch
    model.eval()
    
    # class_id -> list of (conf, tp) pairs; also track total GTs
    all_preds = {}   # cls -> [(conf, tp)]
    all_gt_counts = {}  # cls -> int

    with torch.no_grad():
        for images, targets in data_loader:
            images = [img.to(device) for img in images]
            outputs = model(images)

            for output, target in zip(outputs, targets):
                gt_boxes = target["boxes"].cpu()
                gt_labels = target["labels"].cpu()

                # Count GTs
                for lbl in gt_labels.tolist():
                    all_gt_counts[lbl] = all_gt_counts.get(lbl, 0) + 1

                pred_boxes = output["boxes"].cpu()
                pred_labels = output["labels"].cpu()
                pred_scores = output["scores"].cpu()

                # Filter by confidence
                mask = pred_scores >= conf_thresh
                pred_boxes = pred_boxes[mask]
                pred_labels = pred_labels[mask]
                pred_scores = pred_scores[mask]

                matched_gt = set()
                # Sort by confidence desc
                sorted_idx = pred_scores.argsort(descending=True)
                for idx in sorted_idx.tolist():
                    cls = pred_labels[idx].item()
                    conf = pred_scores[idx].item()
                    pbox = pred_boxes[idx].tolist()

                    best_iou, best_gt_idx = 0.0, -1
                    for gt_idx, (gbox, glbl) in enumerate(zip(gt_boxes.tolist(), gt_labels.tolist())):
                        if glbl != cls or gt_idx in matched_gt:
                            continue
                        iou = compute_iou(pbox, gbox)
                        if iou > best_iou:
                            best_iou, best_gt_idx = iou, gt_idx

                    tp = 1 if best_iou >= iou_thresh else 0
                    if tp == 1:
                        matched_gt.add(best_gt_idx)

                    if cls not in all_preds:
                        all_preds[cls] = []
                    all_preds[cls].append((conf, tp))

    # Compute AP per class
    aps = {}
    for cls, preds in all_preds.items():
        preds.sort(key=lambda x: -x[0])
        tp_cumsum, fp_cumsum = 0, 0
        precisions, recalls = [], []
        n_gt = all_gt_counts.get(cls, 0)
        if n_gt == 0:
            continue
        for _, tp in preds:
            if tp == 1:
                tp_cumsum += 1
            else:
                fp_cumsum += 1
            precisions.append(tp_cumsum / (tp_cumsum + fp_cumsum))
            recalls.append(tp_cumsum / n_gt)
        # 11-point interpolation
        ap = sum(max([p for p, r in zip(precisions, recalls) if r >= t] or [0]) for t in [i / 10 for i in range(11)]) / 11
        aps[cls] = ap

    mean_ap = sum(aps.values()) / len(aps) if aps else 0.0
    return aps, mean_ap


# ─────────────────────────────────────────────────────────────
# Training loop
# ─────────────────────────────────────────────────────────────

def train(args) -> None:
    import torch

    # Load data config
    data_yaml_path = Path(args.data_yaml)
    if not data_yaml_path.exists():
        log.error(f"data.yaml not found: {data_yaml_path}. Run prepare_data.py first.")
        return

    with open(data_yaml_path) as f:
        data_cfg = yaml.safe_load(f)

    dataset_root = Path(data_cfg["path"])
    class_names = data_cfg["names"]
    num_classes = data_cfg["nc"] + 1  # +1 for background

    log.info(f"Classes: {class_names} (+ background = {num_classes} total)")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Device: {device}")

    # Datasets
    import torchvision.transforms as T

    train_ds = RoadDamageDataset(
        dataset_root / "train" / "images",
        dataset_root / "train" / "labels",
        transforms=T.Compose([T.ToTensor()]),
    )
    val_ds = RoadDamageDataset(
        dataset_root / "val" / "images",
        dataset_root / "val" / "labels",
        transforms=T.Compose([T.ToTensor()]),
    )

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=args.batch, shuffle=True,
        collate_fn=collate_fn, num_workers=args.workers, pin_memory=args.pin_memory,
    )
    val_loader = torch.utils.data.DataLoader(
        val_ds, batch_size=args.batch, shuffle=False,
        collate_fn=collate_fn, num_workers=args.workers, pin_memory=args.pin_memory,
    )

    # Model
    model = build_ssd_model(num_classes).to(device)

    # Optimizer — use SGD with momentum (standard for detection)
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(
        params, lr=args.lr, momentum=0.9, weight_decay=5e-4
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=1e-6
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir = output_dir / "logs" / "baseline"
    log_dir.mkdir(parents=True, exist_ok=True)

    best_map = 0.0
    training_history = []

    log.info("=" * 60)
    log.info("SSD MobileNetV2 Baseline — Starting Training")
    log.info(f"  Epochs    : {args.epochs}")
    log.info(f"  Batch     : {args.batch}")
    log.info(f"  LR        : {args.lr}")
    log.info(f"  Workers   : {args.workers}")
    log.info(f"  PinMemory : {args.pin_memory}")
    log.info(f"  Device    : {device}")
    log.info("=" * 60)

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        for batch_idx, (images, targets) in enumerate(train_loader):
            images = [img.to(device) for img in images]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

            loss_dict = model(images, targets)
            loss = sum(loss_dict.values())

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
            optimizer.step()

            epoch_loss += loss.item()

        scheduler.step()
        avg_loss = epoch_loss / len(train_loader)
        elapsed = time.time() - t0

        # Validate every 5 epochs
        if epoch % 5 == 0 or epoch == args.epochs:
            aps, mean_ap = evaluate_model(model, val_loader, device)
            class_aps = {class_names[cls - 1]: round(ap, 4) for cls, ap in aps.items() if 1 <= cls <= len(class_names)}
            log.info(
                f"Epoch {epoch:3d}/{args.epochs} | Loss: {avg_loss:.4f} | "
                f"mAP@0.5: {mean_ap:.4f} | {elapsed:.1f}s"
            )
            log.info(f"  Per-class AP: {class_aps}")

            training_history.append({
                "epoch": epoch, "loss": round(avg_loss, 4), "mAP50": round(mean_ap, 4),
                "class_ap": class_aps, "lr": scheduler.get_last_lr()[0],
            })

            if mean_ap > best_map:
                best_map = mean_ap
                best_path = output_dir / "models" / "model_v1_ssd.pth"
                best_path.parent.mkdir(parents=True, exist_ok=True)
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "mAP50": mean_ap,
                    "class_names": class_names,
                    "num_classes": num_classes,
                }, str(best_path))
                log.info(f"  ✓ New best model saved: mAP@0.5 = {mean_ap:.4f}")
        else:
            log.info(f"Epoch {epoch:3d}/{args.epochs} | Loss: {avg_loss:.4f} | {elapsed:.1f}s")

    # Save training history
    with open(log_dir / "training_history.json", "w") as f:
        json.dump(training_history, f, indent=2)

    log.info("=" * 60)
    log.info(f"SSD Training Complete! Best mAP@0.5: {best_map:.4f}")
    log.info(f"Model saved to: {output_dir / 'models' / 'model_v1_ssd.pth'}")
    log.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SSD MobileNetV2 baseline")
    parser.add_argument("--data_yaml", default="project/outputs/yolo_dataset/data.yaml")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--lr", type=float, default=0.005)
    parser.add_argument("--workers", type=int, default=0,
                        help="Number of DataLoader workers (0 on Windows recommended)")
    parser.add_argument("--pin_memory", type=lambda x: (str(x).lower() in ['1','true','yes']), default=False,
                        help="Whether to use pin_memory for DataLoader")
    parser.add_argument("--output_dir", default="project/outputs")
    args = parser.parse_args()
    train(args)
