import os
import json
from pathlib import Path

def count_classes(label_dir):
    counts = {0: 0, 1: 0}
    label_files = list(Path(label_dir).glob("*.txt"))
    for lf in label_files:
        with open(lf, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    cls = int(parts[0])
                    if cls in counts:
                        counts[cls] += 1
    return counts, len(label_files)

def main():
    base_dir = Path("project/outputs/yolo_dataset")
    
    train_counts, train_files = count_classes(base_dir / "train/labels")
    val_counts, val_files = count_classes(base_dir / "val/labels")
    test_counts, test_files = count_classes(base_dir / "test/labels")
    
    stats = {
        "dataset_size": train_files + val_files + test_files,
        "split": {
            "train": train_files,
            "val": val_files,
            "test": test_files
        },
        "class_distribution": {
            "pothole": train_counts[0] + val_counts[0] + test_counts[0],
            "crack": train_counts[1] + val_counts[1] + test_counts[1]
        },
        "resolution": "640x640 (YOLO default)",
        "nc": 2,
        "names": ["pothole", "crack"]
    }
    
    output_path = Path("project/outputs/dataset_stats.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Stats saved to {output_path}")

if __name__ == "__main__":
    main()
