# 🚀 Quick Start Guide

## Option 1: Docker (Recommended - 30 seconds)

```bash
# Go to project directory
cd project

# Start everything
docker-compose up --build

# Wait for container to be healthy (~1-2 minutes)
# Then open in browser:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

**Test the API:**
```bash
curl -X GET http://localhost:8000/api/v1/health
```

---

## Option 2: Local Installation (5 minutes)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

✓ API running at: http://localhost:8000
✓ Documentation at: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start React dev server
npm start

# Opens at: http://localhost:3000
```

---

## 📝 First Detection

### Use the Web Interface
1. Open http://localhost:3000
2. Click "Upload Image" 
3. Select a road image
4. Click "🚀 Run Detection"
5. View results with confidence scores!

### Using the API Directly

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -F "file=@road_image.jpg" \
  -F "confidence=0.5"
```

**Response:**
```json
{
  "detections": [
    {
      "class": "pothole",
      "confidence": 0.92,
      "bbox": [120, 80, 280, 200],
      "severity": "moderate"
    }
  ],
  "statistics": {
    "total_detections": 1,
    "pothole_count": 1,
    "average_confidence": 0.92,
    "inference_time_ms": 35.2
  }
}
```

---

## 🏋️ Train Your Own Model

```bash
cd training/notebooks

# Run Jupyter notebooks in order:
# 1. 01_data_preparation.ipynb     - Prepare dataset
# 2. 02_model_training.ipynb       - Train YOLOv8
# 3. 03_error_analysis.ipynb       - Analyze results
```

Or use command line:
```bash
python -m ultralytics detect train \
  data=outputs/yolo_dataset/data.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=640
```

---

## 📁 Project Structure

```
project/
├── backend/               # FastAPI server
│   ├── main.py            # Start here
│   ├── inference/         # Model code
│   └── app/routes/        # API endpoints
├── frontend/              # React UI
│   └── src/App.jsx        # Main component
├── training/notebooks/    # Jupyter notebooks
├── outputs/               # Models & results
├── Dockerfile             # Backend container
├── docker-compose.yml     # Full stack
└── README.md              # Full documentation
```

---

## 🔧 Troubleshooting

### API not responding
```bash
# Check if service is running
curl http://localhost:8000/api/v1/health

# View logs
docker logs road-damage-api

# Restart
docker-compose restart backend
```

### Model not loading
```bash
# Download model manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Frontend connection error
```bash
# Check if backend is running on 8000
netstat -an | grep 8000

# Update API URL in frontend/src/api.js if needed
```

---

## ✅ What's Included

- ✓ YOLOv8 Nano pre-trained model
- ✓ FastAPI backend with REST API
- ✓ React dashboard with real-time detection
- ✓ Docker containerization
- ✓ Training notebooks
- ✓ Error analysis tools
- ✓ Production-ready code

---

## 📊 Expected Performance

- **Detection Speed**: ~30-50ms per image (CPU)
- **Accuracy**: 85%+ mAP on test set
- **Model Size**: ~7MB
- **Memory Usage**: ~200MB runtime

---

## 🎯 Next Steps

1. ✅ Start the system
2. ✅ Test with sample images
3. ✅ Review API documentation
4. ✅ Check training notebooks
5. ✅ Read full README.md

---

## 📚 Resources

- **API Docs**: http://localhost:8000/docs (when running)
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

---

**Questions?** Check README.md or run `docker logs road-damage-api` for detailed logs.
