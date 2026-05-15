# 📋 Project Architecture & File Documentation

## Backend Structure

### `project/backend/main.py`
**Purpose:** FastAPI application entry point and server bootstrap

**Functions:**
- `lifespan()` – Startup/shutdown context manager for app lifecycle
  - Initializes ModelManager on startup
  - Loads YOLO model
  - Cleans up resources on shutdown
- `root()` – GET `/` returns API metadata
- `global_exception_handler()` – Centralized error handling

**Key Features:**
- CORS middleware enabled (allows frontend requests)
- Global model manager instance
- Graceful error responses

**Run Command:**
```bash
python project/backend/main.py
```

---

### `project/backend/app/routes/detection.py`
**Purpose:** Detection API endpoints for damage detection

**Endpoints:**
- `POST /detect` – Upload image and run inference
  - Input: Image file + confidence threshold
  - Output: Annotated image (base64), detections, statistics
  - File validation: JPEG/PNG only, max 15 MB
- `GET /model/info` – Return model metadata
  - Returns: Model type, version, classes, evaluation metrics
  - Attempts to load evaluation reports if available

**Functions:**
- `detect_road_damage()` – Main detection pipeline
  1. Validates file type and size
  2. Gets ModelManager instance
  3. Preprocesses image
  4. Runs inference
  5. Returns results with annotations
- `get_model_info()` – Returns current model configuration and performance
- `_get_manager()` – Retrieves global ModelManager instance

**Error Handling:**
- 400: Invalid input (empty file, wrong format)
- 413: File too large
- 415: Unsupported file type
- 503: Model not ready

---

### `project/backend/app/routes/health.py`
**Purpose:** System health and dependency monitoring

**Endpoints:**
- `GET /health` – System status check
  - Checks: PyTorch, CUDA, OpenCV, YOLO availability
  - Checks: Model loading status
  - Returns: Overall system status + dependency details

**Functions:**
- `health_check()` – Comprehensive system diagnostic
  - Tests GPU availability (CUDA)
  - Verifies all dependencies are installed
  - Reports model readiness

---

### `project/backend/inference/model_manager.py`
**Purpose:** Unified model loading and inference interface

**Classes:**
- `ModelManager` – Loads and manages YOLO/SSD models

**Key Methods:**
- `__init__()` – Initialize with default settings
- `load_yolov8_model()` – Load YOLO transfer learning weights
  - Tries: Best → Last → Failed (error reporting)
  - Path: `outputs/yolo_transfer_learning/weights/best.pt`
- `load_ssd_model()` – Load SSD baseline weights
  - Path: `outputs/ssd_baseline/models/model_v1_ssd.pth`
- `preprocess_image(bytes)` – Convert image bytes → BGR tensor
  - Decodes JPEG/PNG
  - Resizes to model input size (640×640)
  - Normalizes pixel values
- `detect(image_bgr, conf)` – Run inference
  - Outputs: Detections, statistics, annotation
  - Computes: Area ratios, damage severity
- `cleanup()` – Release GPU memory and resources

**Inference Pipeline:**
1. Preprocess image (decode, resize, normalize)
2. Run model forward pass
3. Filter by confidence threshold
4. Compute metrics:
   - Bounding box area ratio
   - Severity classification (low/medium/high)
   - Class-specific counts
5. Annotate image with bounding boxes
6. Return results as JSON

---

## Frontend Structure

### `project/frontend/src/App.jsx`
**Purpose:** Main React application component and state management

**State Variables:**
- `imageFile` – Selected image file object
- `imagePreviewUrl` – Image preview data URL
- `annotatedImageB64` – Inference result image (base64)
- `detections` – Array of detected damage objects
- `statistics` – Aggregated detection stats
- `inferenceTime` – Backend inference time in ms
- `modelInfo` – Current model metadata
- `apiStatus` – Backend health status (checking/healthy/degraded/offline)
- `confidence` – Detection confidence threshold
- `loading` – API request in progress
- `error` – Error message to display

**Key Functions:**
- `useEffect()` (health check) – Poll backend health every 30 seconds
- `handleImageSelected()` – Process user image selection
- `handleDetect()` – Call `/detect` API endpoint
- `render()` – Render all dashboard components

**Renders:**
- `<Header />` – Title and status
- `<UploadSection />` – Image upload UI
- `<ResultsPanel />` – Annotated image display
- `<DetectionTable />` – Tabular detections list
- `<MetricsCards />` – Statistics visualization
- `<ModelInfoPanel />` – Model metadata panel
- `<ProjectChecklist />` – Deliverables checklist

---

### `project/frontend/src/api.js`
**Purpose:** API client library for backend communication

**Constants:**
- `BASE_URL` – Backend endpoint (default: `http://localhost:8000/api/v1`)
  - Configurable via `REACT_APP_API_URL` environment variable

**Functions:**
- `handleResponse(res)` – Parse JSON response + error handling
- `healthCheck()` – GET `/health`
- `getModelInfo()` – GET `/model/info`
- `detectImage(file, confidence)` – POST `/detect` with multipart form

**Error Handling:**
- Parses JSON error responses
- Falls back to HTTP status code if no JSON
- Throws error object for React to catch

---

### `project/frontend/src/components/`

#### `Header.jsx`
**Purpose:** Application header and API status display
- Shows title "🚗 Road Damage Detection"
- Displays API health indicator (🟢 healthy / 🟡 degraded / 🔴 offline)
- Updates via prop changes

#### `UploadSection.jsx`
**Purpose:** Image file upload and confidence threshold control
- Drag-and-drop image upload
- File type validation (JPEG/PNG)
- Confidence slider (0.0 – 1.0)
- "Detect Damage" button with loading state

#### `ResultsPanel.jsx`
**Purpose:** Display annotated image result
- Shows annotated image (base64 decoded)
- Displays inference time
- Shows error messages
- Skeleton loader during processing

#### `DetectionTable.jsx`
**Purpose:** Tabular list of all detected damage objects
- Columns: Class (Pothole/Crack), Confidence, Area %, Severity
- Sortable/filterable
- Color-coded severity badges

#### `MetricsCards.jsx`
**Purpose:** Statistical summary cards
- Total detections
- Pothole count
- Crack count
- Average confidence
- Severity distribution (low/medium/high)

#### `ModelInfoPanel.jsx`
**Purpose:** Model metadata and performance display
- Model type (YOLO/SSD)
- Framework (Ultralytics/torchvision)
- Classes: pothole, crack
- Performance: mAP50, precision, recall
- Severity thresholds explanation

#### `ProjectChecklist.jsx`
**Purpose:** Deliverables completion checklist
- ✅ Model training
- ✅ API development
- ✅ Frontend dashboard
- ✅ Documentation
- ✅ Testing on random data

#### `ImageUpload.jsx`
**Purpose:** File input component
- File selection via dialog
- Accepts JPEG/PNG
- Passes file to parent via callback

#### `DetectionCanvas.jsx`
**Purpose:** Canvas-based image annotation (optional visualization)
- Draws bounding boxes on canvas
- Shows class labels and confidence scores
- Alternative to base64 image display

---

## Training Scripts

### `project/training/train_yolo.py`
**Purpose:** Fine-tune YOLO on road damage dataset

**Key Features:**
- Loads pretrained `yolov8m.pt`
- Transfers learning on custom dataset
- Configuration:
  - Epochs: 60 (configurable)
  - Batch: 4 (configurable)
  - Workers: 0 (Windows safe)
  - No augmentation (to avoid incompatibilities)
  - Half precision (faster + smaller GPU memory)
- Outputs:
  - Best weights: `outputs/yolo_transfer_learning/weights/best.pt`
  - Results CSV: `outputs/yolo_transfer_learning/results.csv`
  - Visualization: Training curves and confusion matrices

**Output Metrics:**
- mAP50: 0.8163 (excellent)
- Per-class accuracy

**Usage:**
```bash
python project/training/train_yolo.py \
  --data project/outputs/yolo_dataset/data.yaml \
  --epochs 60 --batch 4 --workers 0 --no-augment
```

---

### `project/training/train_baseline.py`
**Purpose:** Train SSD MobileNetV3 baseline model

**Key Features:**
- Pretrained SSD + MobileNetV3 backbone (COCO weights)
- Replaces classification head for 2-class detection
- Configuration:
  - Epochs: 40
  - Batch: 8
  - Workers: 0 (Windows safe)
- Outputs:
  - Best weights: `outputs/ssd_baseline/models/model_v1_ssd.pth`
  - Training history JSON with per-epoch metrics

**Output Metrics:**
- mAP50: 0.6458 (good baseline)
- Per-class AP

---

## Data Structure

### Dataset Format
**Location:** `project/outputs/yolo_dataset/`
```
data.yaml                 # Dataset config
├── train/
│   ├── images/          (5430 images)
│   └── labels/          (YOLO format .txt)
├── val/
│   ├── images/          (316 images)
│   └── labels/
└── test/
    ├── images/          (314 images)
    └── labels/
```

**YOLO Label Format:**
```
<class_id> <x_center> <y_center> <width> <height>
```
- Class 0: pothole
- Class 1: crack

---

### Model Outputs

#### Detection Result JSON
```json
{
  "annotated_image_b64": "...",
  "detections": [
    {
      "class": "pothole",
      "confidence": 0.92,
      "box": [x1, y1, x2, y2],
      "area_ratio": 0.045,
      "severity": "medium"
    }
  ],
  "statistics": {
    "total_detections": 5,
    "pothole_count": 3,
    "crack_count": 2,
    "avg_confidence": 0.88,
    "severity_distribution": {"low": 1, "medium": 3, "high": 1}
  },
  "inference_time_ms": 234
}
```

---

## Configuration Files

### `project/requirements.txt`
Lists all Python dependencies:
- torch, torchvision, torchaudio
- ultralytics (YOLO)
- fastapi, uvicorn (API)
- opencv-python, pillow (image processing)
- pandas, numpy (data handling)
- pyyaml (config parsing)
- albumentations (augmentation)
- psutil (process monitoring)

### `project/frontend/package.json`
Node.js dependencies:
- react, react-dom
- axios (HTTP client)
- tailwind CSS (styling)

---

## Environment & Paths

**Python Executable:**
```
C:\Users\sodub\OneDrive\Desktop\P2\.venv\Scripts\python.exe
```

**Backend:**
- Port: 8000
- Base URL: `http://localhost:8000/api/v1`

**Frontend:**
- Port: 3000
- React dev server with hot reload

**Models:**
- Transfer Learning: `project/outputs/yolo_transfer_learning/weights/best.pt`
- Baseline SSD: `project/outputs/ssd_baseline/models/model_v1_ssd.pth`

---

## Quality Assurance Checklist

✅ **Models Trained:**
- YOLO Transfer: mAP50 = 0.8163
- YOLO Basic: mAP50 = 0.4471
- SSD Baseline: mAP50 = 0.6458

✅ **API Endpoints:**
- `GET /` – Root info
- `GET /health` – System status
- `GET /model/info` – Model metadata
- `POST /detect` – Image detection

✅ **Frontend Components:**
- Image upload
- Detection display
- Metrics visualization
- Model info panel
- Project checklist

✅ **Error Handling:**
- File validation
- GPU/CPU fallback
- Model loading errors
- API error responses

✅ **Documentation:**
- This file (architecture + functions)
- HOW_TO_RUN.md (simple setup guide)
- Inline code comments

---

## Performance Summary

| Component | Status | Performance |
|-----------|--------|-------------|
| YOLO Transfer Learning | ✅ | mAP50: 0.8163 |
| SSD Baseline | ✅ | mAP50: 0.6458 |
| YOLO Basic | ✅ | mAP50: 0.4471 |
| FastAPI Backend | ✅ | ~200-300ms inference |
| React Frontend | ✅ | Instant UI updates |
| CUDA Support | ✅ | GPU acceleration enabled |

---

## Next Steps for Production

1. **Dockerize:**
   - Create Docker image for backend
   - Deploy to cloud (AWS/GCP)

2. **Database:**
   - Store detection history
   - Track false positives for retraining

3. **Monitoring:**
   - Log all detections
   - Alert on infrastructure issues

4. **Performance:**
   - Model quantization for faster inference
   - Batch processing support

5. **Model Improvement:**
   - Retrain on new data
   - Hyperparameter tuning
   - Ensemble methods

