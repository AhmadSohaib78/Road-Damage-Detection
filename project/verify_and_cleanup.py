#!/usr/bin/env python
"""
Project cleanup and verification script.
Run this to remove unnecessary files and verify the project is ready.
"""

import os
import shutil
from pathlib import Path
import json

def cleanup_pycache(root_dir):
    """Remove all __pycache__ directories."""
    removed = 0
    for pycache_dir in Path(root_dir).rglob('__pycache__'):
        print(f"Removing {pycache_dir}")
        shutil.rmtree(pycache_dir)
        removed += 1
    return removed

def cleanup_old_training_runs(outputs_dir):
    """Remove old/redundant training runs."""
    # Keep: yolo_transfer_learning, stage1_base_model, ssd_baseline, yolo_dataset
    # Remove: fast_perfect_yolo, ultimate_run_yolo, ssd_baseline_test
    
    dirs_to_remove = [
        'fast_perfect_yolo',
        'ultimate_run_yolo',
        'ssd_baseline_test',
        'eda',
        'weights',
        'models'
    ]
    
    outputs_path = Path(outputs_dir)
    removed = 0
    
    for dir_name in dirs_to_remove:
        dir_path = outputs_path / dir_name
        if dir_path.exists():
            size = get_dir_size(dir_path)
            print(f"Removing {dir_path.name} ({format_size(size)})")
            shutil.rmtree(dir_path)
            removed += 1
    
    return removed

def get_dir_size(path):
    """Get total size of directory in bytes."""
    total = 0
    for entry in Path(path).rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total

def format_size(bytes):
    """Format bytes as human-readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"

def verify_models_exist(outputs_dir):
    """Verify all required model files exist."""
    required_models = [
        ('yolo_transfer_learning/weights/best.pt', 'YOLO Transfer Learning'),
        ('stage1_base_model/weights/best.pt', 'YOLO Basic'),
        ('ssd_baseline/models/model_v1_ssd.pth', 'SSD Baseline'),
    ]
    
    outputs_path = Path(outputs_dir)
    status = []
    
    for rel_path, name in required_models:
        model_path = outputs_path / rel_path
        if model_path.exists():
            size = model_path.stat().st_size
            status.append((name, True, format_size(size)))
        else:
            status.append((name, False, None))
    
    return status

def verify_backend_files(project_root):
    """Verify backend Python files exist."""
    required_files = [
        'backend/main.py',
        'backend/app/routes/detection.py',
        'backend/app/routes/health.py',
        'backend/inference/model_manager.py',
        'requirements.txt'
    ]
    
    project_path = Path(project_root)
    status = []
    
    for rel_path in required_files:
        file_path = project_path / rel_path
        status.append((rel_path, file_path.exists()))
    
    return status

def verify_frontend_files(frontend_dir):
    """Verify frontend files exist."""
    required_files = [
        'src/App.jsx',
        'src/api.js',
        'src/components/Header.jsx',
        'src/components/UploadSection.jsx',
        'src/components/ResultsPanel.jsx',
        'src/components/DetectionTable.jsx',
        'src/components/MetricsCards.jsx',
        'src/components/ModelInfoPanel.jsx',
        'package.json',
    ]
    
    frontend_path = Path(frontend_dir)
    status = []
    
    for rel_path in required_files:
        file_path = frontend_path / rel_path
        status.append((rel_path, file_path.exists()))
    
    return status

def check_imports(py_file):
    """Quick syntax check on Python file."""
    try:
        with open(py_file, 'r') as f:
            compile(f.read(), py_file, 'exec')
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    project_root = Path(__file__).parent
    outputs_dir = project_root / 'outputs'
    frontend_dir = project_root / 'frontend'
    
    print("=" * 60)
    print("🧹 PROJECT CLEANUP & VERIFICATION")
    print("=" * 60)
    
    # Step 1: Cleanup __pycache__
    print("\n1️⃣ Cleaning up __pycache__ directories...")
    removed = cleanup_pycache(project_root)
    print(f"   ✅ Removed {removed} directories")
    
    # Step 2: Cleanup old training runs
    print("\n2️⃣ Removing old training runs...")
    removed = cleanup_old_training_runs(outputs_dir)
    print(f"   ✅ Removed {removed} directories")
    
    # Step 3: Verify models exist
    print("\n3️⃣ Verifying trained models...")
    models = verify_models_exist(outputs_dir)
    for name, exists, size in models:
        status = "✅" if exists else "❌"
        size_str = f" ({size})" if size else ""
        print(f"   {status} {name}{size_str}")
    
    all_models_exist = all(exists for _, exists, _ in models)
    if not all_models_exist:
        print("   ⚠️ Some models are missing. Run training scripts first!")
    
    # Step 4: Verify backend files
    print("\n4️⃣ Verifying backend files...")
    backend_files = verify_backend_files(project_root)
    for path, exists in backend_files:
        status = "✅" if exists else "❌"
        print(f"   {status} {path}")
    
    # Step 5: Verify frontend files
    print("\n5️⃣ Verifying frontend files...")
    frontend_files = verify_frontend_files(frontend_dir)
    for path, exists in frontend_files:
        status = "✅" if exists else "❌"
        print(f"   {status} {path}")
    
    # Step 6: Check Python syntax
    print("\n6️⃣ Checking Python syntax...")
    py_files = [
        project_root / 'backend/main.py',
        project_root / 'backend/app/routes/detection.py',
        project_root / 'backend/app/routes/health.py',
        project_root / 'backend/inference/model_manager.py',
    ]
    
    syntax_ok = True
    for py_file in py_files:
        if py_file.exists():
            ok, error = check_imports(py_file)
            status = "✅" if ok else "❌"
            print(f"   {status} {py_file.name}")
            if error:
                print(f"       Error: {error}")
                syntax_ok = False
    
    # Final summary
    print("\n" + "=" * 60)
    if all_models_exist and syntax_ok:
        print("✅ PROJECT READY TO RUN!")
        print("\nNext steps:")
        print("1. Terminal 1: python project/backend/main.py")
        print("2. Terminal 2: cd project/frontend && npm start")
        print("3. Browser:   http://localhost:3000")
    else:
        print("⚠️ ISSUES DETECTED - See above for details")
    print("=" * 60)

if __name__ == '__main__':
    main()
