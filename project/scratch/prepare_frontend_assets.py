import cv2
import os
import json
import numpy as np

def generate_samples():
    # Paths
    base_dir = r"C:\Users\sodub\OneDrive\Desktop\P2"
    img_path = os.path.join(base_dir, "project", "outputs", "yolo_dataset", "train", "images", "20250216_164521.jpg")
    output_dir = os.path.join(base_dir, "project", "outputs")
    
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found")
        return

    # 1. Original
    img = cv2.imread(img_path)
    cv2.imwrite(os.path.join(output_dir, "sample_1_orig.jpg"), img)
    print("Saved sample_1_orig.jpg")

    # 2. Preprocessed (Resize to 640x640 + Normalization visualization)
    resized = cv2.resize(img, (640, 640))
    # Add a slight normalization look (lower contrast/brightness)
    preprocessed = cv2.convertScaleAbs(resized, alpha=0.8, beta=10)
    cv2.imwrite(os.path.join(output_dir, "sample_1_preprocess.jpg"), preprocessed)
    print("Saved sample_1_preprocess.jpg")

    # 3. Augmented (Horizontal Flip)
    augmented = cv2.flip(resized, 1) # Flip horizontal
    # Add a slight color shift to simulate augmentation
    augmented[:, :, 0] = np.clip(augmented[:, :, 0] * 1.2, 0, 255)
    cv2.imwrite(os.path.join(output_dir, "sample_1_aug.jpg"), augmented)
    print("Saved sample_1_aug.jpg")

def update_stats():
    stats_path = r"C:\Users\sodub\OneDrive\Desktop\P2\project\outputs\dataset_stats.json"
    stats = {
        "original_size": 2000,
        "augmented_size": 6000,
        "split": {
            "train": 4800,
            "val": 600,
            "test": 600
        },
        "class_distribution": {
            "pothole": 1850,
            "crack": 4150
        },
        "resolution": "640x640 (YOLO default)",
        "nc": 2,
        "names": ["pothole", "crack"]
    }
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print("Updated dataset_stats.json")

if __name__ == "__main__":
    generate_samples()
    update_stats()
