# AI-Powered Road Damage Detection System

A production-ready computer vision system designed to detect and categorize road damage (Potholes and Cracks) with high precision (83.5% mAP50).

## 🚀 System Overview
This project implements a multi-stage ML engineering workflow:
1.  **Stage 1 (Baseline):** SSD MobileNetV2 for initial data validation.
2.  **Stage 2 (Production):** Fine-tuned YOLOv8m (Medium) achieving 83.5% mAP50.
3.  **Deployment:** FastAPI backend serving real-time inference to a React.js dashboard.

## 📁 Project Structure
```text
project/
├── backend/            # FastAPI Inference Server
│   ├── app/routes/     # API Endpoints (Detection, Health, Info)
│   └── inference/      # Model Manager & Processing Logic
├── frontend/           # React.js Dashboard
│   ├── src/pages/      # Deliverable Pages (1-5)
│   └── src/index.css   # Custom Design System
├── outputs/            # Trained Weights & Dataset Stats
└── scripts/            # Training & Data Prep Scripts
```

## 🛠️ Setup Instructions

### 1. Backend (Python 3.10+)
1. Navigate to the project root.
2. Activate your virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
3. Run the API server:
   ```bash
   python project/backend/main.py
   ```
   *The server will start at `http://localhost:8000`*

### 2. Frontend (Node.js 16+)
1. Navigate to the frontend directory:
   ```bash
   cd project/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dashboard:
   ```bash
   npm start
   ```
   *The dashboard will open at `http://localhost:3000`*

## 📊 Performance Summary
| Model | Accuracy (mAP50) | Latency (CPU) | Status |
|-------|------------------|---------------|--------|
| **YOLO Fine-tuned** | **83.5%** | **~50ms** | **Best** |
| SSD Baseline | 64.6% | ~150ms | Baseline |
| YOLO Stock | 44.7% | ~40ms | Initial |

## 🧠 Technical Highlights
- **Transfer Learning:** Fine-tuned YOLOv8m on 6,027 augmented road samples.
- **Compute Aware:** Optimized for local inference with sub-100ms latency.
- **Modular Design:** Decoupled CV logic from API routing for high maintainability.
- **Robustness:** Handles varied lighting and weather conditions via Mosaic augmentation.

---
*Developed as part of an AI/ML Engineering Technical Skills Assessment.*
