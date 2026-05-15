import os
import cv2
import albumentations as A
from pathlib import Path
import random
from tqdm import tqdm

# Path to the prepared YOLO dataset
DATASET_ROOT = Path(__file__).parent.parent / "outputs" / "yolo_dataset"
TRAIN_IMAGES_DIR = DATASET_ROOT / "train" / "images"
TRAIN_LABELS_DIR = DATASET_ROOT / "train" / "labels"

# We will generate 3 new augmented versions per image
AUGMENTATIONS_PER_IMAGE = 3

# Define the aggressive offline augmentation pipeline
# YOLO format bbox requires: [x_center, y_center, width, height] (normalized 0 to 1)
transform = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.MotionBlur(p=0.3),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
    A.OneOf([
        A.RandomRain(p=1.0),
        A.RandomSnow(p=1.0),
        A.RandomFog(p=1.0),
        A.Spatter(p=1.0)
    ], p=0.2),
    A.ShiftScaleRotate(shift_limit=0.06, scale_limit=0.1, rotate_limit=15, p=0.5),
    A.HorizontalFlip(p=0.5),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'], min_area=0.0, min_visibility=0.1))

def augment_dataset():
    print(f"Starting aggressive offline augmentation...")
    print(f"Target directory: {TRAIN_IMAGES_DIR}")
    
    if not TRAIN_IMAGES_DIR.exists():
        print("Error: Training images directory not found. Did you run prepare_data.py?")
        return

    # Get all original images (filter out already augmented ones if script ran before)
    original_images = [p for p in TRAIN_IMAGES_DIR.glob("*.jpg") if "_aug_" not in p.name]
    print(f"Found {len(original_images)} original training images.")
    
    total_generated = 0
    
    for img_path in tqdm(original_images, desc="Augmenting Images"):
        # Load image
        image = cv2.imread(str(img_path))
        if image is None:
            continue
            
        # Load labels
        label_path = TRAIN_LABELS_DIR / f"{img_path.stem}.txt"
        if not label_path.exists():
            continue
            
        bboxes = []
        class_labels = []
        
        with open(label_path, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id = int(parts[0])
                    # Ensure bbox coordinates are strictly within [0.0, 1.0] to prevent albumentations errors
                    x_center = min(max(float(parts[1]), 0.0), 1.0)
                    y_center = min(max(float(parts[2]), 0.0), 1.0)
                    width = min(max(float(parts[3]), 0.0), 1.0)
                    height = min(max(float(parts[4]), 0.0), 1.0)
                    
                    bboxes.append([x_center, y_center, width, height])
                    class_labels.append(class_id)
        
        if not bboxes:
            continue
            
        # Generate N augmented versions
        for i in range(AUGMENTATIONS_PER_IMAGE):
            try:
                augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
                aug_img = augmented['image']
                aug_bboxes = augmented['bboxes']
                aug_classes = augmented['class_labels']
                
                # If all bounding boxes were cut off during augmentation (e.g. cropped out), skip
                if not aug_bboxes:
                    continue
                    
                # Save new image
                new_img_name = f"{img_path.stem}_aug_{i}.jpg"
                new_img_path = TRAIN_IMAGES_DIR / new_img_name
                cv2.imwrite(str(new_img_path), aug_img)
                
                # Save new labels
                new_label_name = f"{img_path.stem}_aug_{i}.txt"
                new_label_path = TRAIN_LABELS_DIR / new_label_name
                
                with open(new_label_path, 'w') as f:
                    for bbox, cls_id in zip(aug_bboxes, aug_classes):
                        f.write(f"{cls_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")
                        
                total_generated += 1
            except Exception as e:
                # Sometimes extreme crops cause bbox math errors in albumentations
                continue
                
    print(f"\n=================================================")
    print(f"Augmentation Complete!")
    print(f"Generated {total_generated} new augmented images.")
    print(f"Your training dataset is now roughly {len(original_images) + total_generated} images.")
    print(f"=================================================")

if __name__ == "__main__":
    augment_dataset()
