#!/usr/bin/env python
"""
API Integration Test
====================
Tests the FastAPI backend endpoints with a real road image.
Verifies: response schema, JSON structure, HTTP status codes.

Usage:
    python tests/test_api.py
    python tests/test_api.py --url http://localhost:8000 --image path/to/test.jpg
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests not installed: pip install requests")
    sys.exit(1)


BASE_URL = "http://localhost:8000/api/v1"


def check(condition: bool, msg: str) -> bool:
    status = "✓" if condition else "✗"
    print(f"  {status} {msg}")
    return condition


def test_health(url: str) -> bool:
    print("\n[1] Health check — GET /health")
    try:
        r = requests.get(f"{url}/health", timeout=10)
        ok = True
        ok &= check(r.status_code in (200, 206), f"Status code {r.status_code} (200 or 206)")
        data = r.json()
        ok &= check("status" in data, f"Response has 'status' field: {data.get('status')}")
        ok &= check("model" in data, "Response has 'model' field")
        ok &= check("dependencies" in data, "Response has 'dependencies' field")
        return ok
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_model_info(url: str) -> bool:
    print("\n[2] Model info — GET /model/info")
    try:
        r = requests.get(f"{url}/model/info", timeout=10)
        if r.status_code == 503:
            print("  ⚠ Model not loaded (503) — skipping schema validation")
            return True
        ok = True
        ok &= check(r.status_code == 200, f"Status 200 (got {r.status_code})")
        data = r.json()
        for field in ["ready", "model_type", "model_version", "device", "classes"]:
            ok &= check(field in data, f"Field '{field}' present")
        return ok
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_detection(url: str, image_path: str) -> bool:
    print(f"\n[3] Detection — POST /detect  (image: {image_path})")
    path = Path(image_path)
    if not path.exists():
        print(f"  ⚠ Image not found: {image_path}. Skipping detection test.")
        return True

    try:
        with open(path, "rb") as f:
            r = requests.post(
                f"{url}/detect?confidence=0.4",
                files={"file": (path.name, f, "image/jpeg")},
                timeout=60,
            )

        if r.status_code == 503:
            print("  ⚠ Model not loaded (503). Run training first.")
            return True

        ok = True
        ok &= check(r.status_code == 200, f"Status 200 (got {r.status_code})")
        data = r.json()
        ok &= check("detections" in data, f"'detections' list present ({len(data.get('detections', []))} items)")
        ok &= check("statistics" in data, "'statistics' present")
        ok &= check("inference_time_ms" in data, f"'inference_time_ms' present: {data.get('inference_time_ms')}ms")
        ok &= check("annotated_image_b64" in data, "'annotated_image_b64' (base64 image) present")

        # Per-detection schema
        for det in data.get("detections", [])[:3]:
            ok &= check("class" in det, f"  Det has 'class': {det.get('class')}")
            ok &= check("confidence" in det, f"  Det has 'confidence': {det.get('confidence')}")
            ok &= check("bbox" in det and len(det["bbox"]) == 4, f"  Det has 4-element bbox")
            ok &= check("severity" in det, f"  Det has 'severity': {det.get('severity')}")

        # Stats schema
        stats = data.get("statistics", {})
        ok &= check("total" in stats, f"  Stats has 'total': {stats.get('total')}")
        ok &= check("by_class" in stats, "  Stats has 'by_class'")
        ok &= check("severity" in stats, "  Stats has 'severity'")
        ok &= check("avg_confidence" in stats, "  Stats has 'avg_confidence'")

        return ok
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_bad_file(url: str) -> bool:
    print("\n[4] Bad file type — POST /detect (text file)")
    try:
        r = requests.post(
            f"{url}/detect",
            files={"file": ("test.txt", b"hello world", "text/plain")},
            timeout=10,
        )
        ok = check(r.status_code == 415, f"Returns 415 Unsupported Media Type (got {r.status_code})")
        return ok
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=BASE_URL)
    parser.add_argument("--image", default="", help="Path to test image")
    args = parser.parse_args()

    print("=" * 55)
    print("  Road Damage Detection API — Integration Tests")
    print(f"  Target: {args.url}")
    print("=" * 55)

    results = []
    results.append(test_health(args.url))
    results.append(test_model_info(args.url))
    results.append(test_detection(args.url, args.image or ""))
    results.append(test_bad_file(args.url))

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 55}")
    print(f"Results: {passed}/{total} test groups passed")
    print("=" * 55)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
