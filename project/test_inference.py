#!/usr/bin/env python
"""
Test inference on random images to verify models are working.
Run this to validate the complete inference pipeline.
"""

import sys
import json
from pathlib import Path
from PIL import Image
import numpy as np

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from project.backend.inference.model_manager import ModelManager

def test_inference():
    """Test inference on random images."""
    
    print("=" * 60)
    print("🧪 Testing Model Inference Pipeline")
    print("=" * 60)
    
    # Initialize model manager
    print("\n1️⃣ Loading Models...")
    try:
        manager = ModelManager()
        manager.load_yolov8_model()
        print("   ✅ YOLO Transfer Learning model loaded")
    except Exception as e:
        print(f"   ❌ Failed to load model: {e}")
        return False
    
    # Get test images
    test_images_dir = project_root / "project/outputs/test_images"
    test_images = list(test_images_dir.glob("*.jpg"))
    
    if not test_images:
        print(f"   ❌ No test images found in {test_images_dir}")
        return False
    
    print(f"   ✅ Found {len(test_images)} test images")
    
    # Test inference on each image
    print("\n2️⃣ Running Inference Tests...")
    all_passed = True
    
    for i, image_path in enumerate(test_images, 1):
        print(f"\n   Testing image {i}: {image_path.name}")
        
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Preprocess
            image_bgr = manager.preprocess_image(image_bytes)
            print(f"      ✅ Image preprocessed: {image_bgr.shape}")
            
            # Detect
            results = manager.detect(image_bgr, confidence=0.5)
            
            # Check results structure
            if 'detections' in results:
                detections = results['detections']
                print(f"      ✅ Detection complete: {len(detections)} detections found")
                
                # Show details
                if detections:
                    for j, det in enumerate(detections[:3]):  # Show first 3
                        print(f"         - [{j+1}] {det['class']}: {det['confidence']:.2f} confidence")
                else:
                    print(f"         - No damage detected (confidence threshold may be too high)")
            else:
                print(f"      ❌ Invalid results structure: {results.keys()}")
                all_passed = False
            
            # Check statistics
            if 'statistics' in results:
                stats = results['statistics']
                print(f"      ✅ Statistics: {stats['total_detections']} total, "
                      f"{stats['avg_confidence']:.2f} avg confidence")
            
            # Check inference time
            if 'inference_time_ms' in results:
                inf_time = results['inference_time_ms']
                print(f"      ✅ Inference time: {inf_time:.0f}ms")
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            all_passed = False
    
    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("   Models are working correctly on random data.")
    else:
        print("⚠️ SOME TESTS FAILED - See details above")
    
    print("=" * 60)
    
    # Cleanup
    manager.cleanup()
    
    return all_passed

if __name__ == '__main__':
    success = test_inference()
    sys.exit(0 if success else 1)
