#!/usr/bin/env python
"""
Data Preparation Script for Road Damage Detection
=================================================
Reads images + YOLO labels from dataset/data/, performs a stratified
80/10/10 train/val/test split, and writes the final splits to
outputs/yolo_dataset/ along with a data.yaml and class stats report.

Classes kept for training:
    0 = pothole
    1 = crack
Excluded from training:
    2 = manhole (reserved for error analysis)

Usage:
    python prepare_data.py --dataset_root ../../dataset/data \
                           --output_root ../outputs/yolo_dataset
"""

import argparse
import json
import logging
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CLASS_NAMES = ["pothole", "crack"]
VALID_CLASS_IDS = {0, 1}
MANHOLE_CLASS_ID = 2


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def parse_label_file(label_path: Path) -> tuple[list[dict], int]:
    """Return filtered annotations and the number of excluded manhole labels."""
    annotations = []
    manhole_count = 0
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls_id = int(parts[0])
            if cls_id == MANHOLE_CLASS_ID:
                manhole_count += 1
                continue
            if cls_id not in VALID_CLASS_IDS:
                continue
            x_c, y_c, w, h = map(float, parts[1:5])
            annotations.append(
                {"class_id": cls_id, "x_c": x_c, "y_c": y_c, "w": w, "h": h}
            )
    return annotations, manhole_count


def dominant_class(annotations: list[dict]) -> int:
    """Return the class_id that appears most in an annotation list."""
    if not annotations:
        return -1
    counts = Counter(a["class_id"] for a in annotations)
    return counts.most_common(1)[0][0]


def stratified_split(
    samples: list[tuple[Path, Path, list[dict]]],
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    seed: int = 42,
) -> tuple[list, list, list]:
    """
    Stratify by dominant class, then split.
    Returns (train, val, test) lists of (img_path, lbl_path, annotations).
    """
    random.seed(seed)

    # Group by dominant class
    groups: dict[int, list] = defaultdict(list)
    for sample in samples:
        cls = dominant_class(sample[2])
        groups[cls].append(sample)

    train, val, test = [], [], []
    for cls_id, items in groups.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        train.extend(items[:n_train])
        val.extend(items[n_train : n_train + n_val])
        test.extend(items[n_train + n_val :])

    # Shuffle within each split for variety
    for split in (train, val, test):
        random.shuffle(split)

    return train, val, test


def copy_split(
    samples: list[tuple[Path, Path, list[dict]]],
    split_name: str,
    output_root: Path,
) -> None:
    """Copy images and labels into output_root/<split_name>/{images,labels}/."""
    img_dir = output_root / split_name / "images"
    lbl_dir = output_root / split_name / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)

    for img_path, lbl_path, annotations in samples:
        # Copy image
        shutil.copy2(img_path, img_dir / img_path.name)

        # Write filtered / clean label file
        out_lbl = lbl_dir / (img_path.stem + ".txt")
        with open(out_lbl, "w") as f:
            for ann in annotations:
                f.write(
                    f"{ann['class_id']} {ann['x_c']:.6f} {ann['y_c']:.6f} "
                    f"{ann['w']:.6f} {ann['h']:.6f}\n"
                )

    log.info(f"  {split_name}: {len(samples)} images")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main(dataset_root: str, output_root: str) -> None:
    dataset_root = Path(dataset_root).resolve()
    output_root = Path(output_root).resolve()

    images_dir = dataset_root / "images"
    labels_dir = dataset_root / "labels-YOLO"

    log.info(f"Dataset root : {dataset_root}")
    log.info(f"Output root  : {output_root}")

    # ── 1. Scan all images ──────────────────────────────────
    image_files = sorted(
        p for p in images_dir.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    log.info(f"Total images found: {len(image_files)}")

    # ── 2. Pair with labels; skip images with no valid training annotations ─
    samples = []
    manhole_examples = []
    skipped = 0
    class_counter: Counter = Counter()

    for img_path in image_files:
        lbl_path = labels_dir / (img_path.stem + ".txt")
        if not lbl_path.exists():
            skipped += 1
            continue

        annotations, manhole_count = parse_label_file(lbl_path)
        if manhole_count > 0 and not annotations:
            manhole_examples.append((img_path, lbl_path))

        if not annotations:
            skipped += 1
            continue

        for ann in annotations:
            class_counter[ann["class_id"]] += 1
        samples.append((img_path, lbl_path, annotations))

    log.info(f"Usable images: {len(samples)}  (skipped {skipped} with no valid annotations)")
    log.info("Class distribution (training dataset):")
    for cls_id, name in enumerate(CLASS_NAMES):
        log.info(f"  [{cls_id}] {name}: {class_counter[cls_id]} annotations")

    # ── 3. Stratified split ─────────────────────────────────
    train, val, test = stratified_split(samples)
    log.info(f"Split — train: {len(train)}  val: {len(val)}  test: {len(test)}")

    # ── 4. Copy files ───────────────────────────────────────
    output_root.mkdir(parents=True, exist_ok=True)

    # Preserve manhole-only examples for error analysis, but do not train on them.
    error_dir = output_root / "error_analysis" / "manhole"
    error_dir.mkdir(parents=True, exist_ok=True)
    for img_path, lbl_path in manhole_examples:
        shutil.copy2(img_path, error_dir / img_path.name)
        shutil.copy2(lbl_path, error_dir / lbl_path.name)

    for split_name, split_data in [("train", train), ("val", val), ("test", test)]:
        copy_split(split_data, split_name, output_root)

    # ── 5. Write data.yaml ──────────────────────────────────
    data_yaml = {
        "path": str(output_root),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": len(CLASS_NAMES),
        "names": CLASS_NAMES,
    }
    yaml_path = output_root / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f, default_flow_style=False, sort_keys=False)
    log.info(f"data.yaml written to {yaml_path}")

    # ── 6. Save EDA stats ───────────────────────────────────
    eda_dir = output_root.parent / "eda"
    eda_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "total_images": len(image_files),
        "usable_images": len(samples),
        "skipped_images": skipped,
        "split": {
            "train": len(train),
            "val": len(val),
            "test": len(test),
        },
        "class_distribution": {CLASS_NAMES[i]: class_counter[i] for i in range(len(CLASS_NAMES))},
    }
    with open(eda_dir / "dataset_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    log.info(f"EDA stats saved to {eda_dir / 'dataset_stats.json'}")

    log.info("=" * 60)
    log.info("Data preparation complete!")
    log.info(f"Run training with: python train_yolo.py --data {yaml_path}")
    log.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare road damage dataset")
    parser.add_argument(
        "--dataset_root",
        default="../../dataset/data",
        help="Path to raw dataset directory",
    )
    parser.add_argument(
        "--output_root",
        default="../outputs/yolo_dataset",
        help="Where to write the split dataset",
    )
    args = parser.parse_args()
    main(args.dataset_root, args.output_root)
