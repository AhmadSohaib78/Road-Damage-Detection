# 🚗 Road Damage Detection System – How to Run

## Quick Start (Simple Version)

### 1. **Start the Backend API** (Terminal 1)
```bash
cd C:\Users\sodub\OneDrive\Desktop\P2
.venv\Scripts\python.exe project/backend/main.py
```
The API will start at **`http://localhost:8000`**

### 2. **Start the Frontend** (Terminal 2)
```bash
cd C:\Users\sodub\OneDrive\Desktop\P2\project\frontend
npm start
```
The frontend will open at **`http://localhost:3000`**

### 3. **Open Browser**
Go to **`http://localhost:3000`** and upload a road image to detect damage!

---

## What Each Part Does

### Backend (`project/backend/main.py`)
- Runs the FastAPI server on port **8000**
- Loads trained YOLO and SSD models
- Provides `/api/v1/detect` endpoint for damage detection
- Provides `/api/v1/health` and `/api/v1/model/info` endpoints

### Frontend (`project/frontend/`)
- React application on port **3000**
- Displays detection results with annotations
- Shows damage statistics and model performance metrics
- Uploads images to the backend

---

## Requirements

✅ **Already Installed:**
- Python 3.14 with `.venv` virtual environment
- Node.js and npm
- All required packages (torch, ultralytics, FastAPI, React, etc.)

✅ **Models Already Trained:**
- YOLO Transfer Learning: `project/outputs/yolo_transfer_learning/weights/best.pt` (mAP50: 0.8163)
- YOLO Basic: `project/outputs/stage1_base_model/` (mAP50: 0.4471)
- SSD Baseline: `project/outputs/ssd_baseline/models/model_v1_ssd.pth` (mAP50: 0.6458)

---

## Troubleshooting

### API won't start
- Make sure port 8000 is not in use: `netstat -ano | findstr :8000`
- Activate virtual environment: `.venv\Scripts\activate`

### Frontend won't load
- Make sure port 3000 is not in use
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `npm install`

### "API is offline" error in frontend
- Check if backend is running: Visit `http://localhost:8000` in browser
- Should show: `{"message":"AI Smart Road Damage Detection API","version":"1.0.0","status":"active"}`

### GPU not detected
- The system will automatically fall back to CPU
- CUDA detection happens on backend startup

---

## Environment Setup (Already Done)

The virtual environment is already configured. To manually recreate:

```bash
cd C:\Users\sodub\OneDrive\Desktop\P2
python -m venv .venv
.venv\Scripts\activate
pip install -r project/requirements.txt
```

For frontend:
```bash
cd project/frontend
npm install
```

---

## Testing the API Directly

Without the frontend, you can test the backend directly:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get model info
curl http://localhost:8000/api/v1/model/info

# Upload image for detection (via POST with file upload)
# Requires multipart form data with 'file' field
```

---

## Project Structure

```
project/
├── backend/
│   ├── main.py                 ← START BACKEND HERE
│   ├── app/
│   │   └── routes/
│   │       ├── detection.py    (API endpoints)
│   │       └── health.py       (health checks)
│   └── inference/
│       └── model_manager.py    (model loading and inference)
├── frontend/
│   ├── src/
│   │   ├── App.jsx            (main React app)
│   │   └── api.js             (API client)
│   └── package.json
├── training/
│   ├── train_yolo.py          (YOLO fine-tuning)
│   └── train_baseline.py      (SSD training)
├── outputs/
│   ├── yolo_transfer_learning/ (best YOLO model)
│   ├── stage1_base_model/      (basic YOLO)
│   └── ssd_baseline/           (SSD model)
└── requirements.txt
```

---

## Performance Summary

| Model | Type | mAP50 | Status |
|-------|------|-------|--------|
| YOLO Transfer Learning | Fine-tuned | **0.8163** | ✅ Best |
| SSD MobileNetV2 | Baseline | 0.6458 | ✅ Good |
| YOLO Basic | Pretrained | 0.4471 | ✅ Baseline |

---

## Next Steps

1. ✅ All models trained
2. ✅ Backend API ready
3. ✅ Frontend dashboard ready
4. 🚀 Upload a road image with damage to test!

Enjoy the Road Damage Detection System! 🎯
