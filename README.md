# AI-Powered Road Damage Detection System
**Technical Skills Assessment: AI / Machine Learning Engineering**

---

## 1. System Overview
This project implements a production-ready computer vision system designed to detect and categorize road damage (Potholes and Cracks). The solution achieves a high-precision score of 83.5% mAP50 while maintaining a sub-50ms inference latency, suitable for real-time infrastructure monitoring.

The implementation follows a multi-stage Machine Learning engineering workflow:
- **Stage 1 (Baseline):** SSD MobileNetV2 for initial performance floor establishment.
- **Stage 2 (Production):** Fine-tuned YOLOv8m (Medium) for specialized road texture detection.
- **Deployment:** FastAPI backend serving an interactive React.js dashboard.

---

## 2. Data Engineering and Strategy
### 2.1 Dataset Composition
- **Original Dataset:** 2,009 high-resolution images of urban and rural roads.
- **Augmented Dataset:** 6,027 images (3.0x expansion).
- **Classes:** Pothole (1,858 instances), Crack (4,169 instances).
- **Split Strategy:** 80% Training, 10% Validation, 10% Testing.

### 2.2 Preprocessing Pipeline
To ensure model invariance across diverse environments, a 3-step pipeline was implemented:
1. **Geometric Transformation:** Mosaic augmentation to handle significant scale variance.
2. **Color Jittering:** HSV adjustments to simulate varying weather and lighting conditions.
3. **Normalization:** Input scaling to 640x640 with standard deviation normalization.

---

## 3. Model Development and Selection
### 3.1 Architecture Rationale
Three distinct approaches were evaluated:
- **SSD MobileNetV2 (Baseline):** A lightweight model used to establish a performance baseline.
- **YOLO Stock (Pre-trained):** Tested to verify the capability of generic weights on road textures.
- **YOLOv8m Fine-tuned (Production):** Selected as the primary model. The Medium variant provides the optimal balance between feature extraction depth and inference speed.

### 3.2 Training Methodology
- **Transfer Learning:** Initialized with COCO weights to leverage generic object features.
- **Fine-tuning:** Unfroze the backbone in the final 20 epochs to specialize in granular road damage features.
- **Optimization:** Stochastic Gradient Descent (SGD) with a momentum of 0.937 and weight decay of 0.0005.

---

## 4. Performance Matrix
| Model Architecture | Accuracy (mAP50) | Latency (CPU) | Status |
|--------------------|------------------|---------------|--------|
| **YOLO Fine-tuned (v8m)** | **83.5%** | **~50ms** | **Production** |
| SSD Baseline (v2) | 64.6% | ~150ms | Baseline |
| YOLO Stock | 44.7% | ~40ms | Initial |

---

## 5. Evaluation and Error Analysis
### 5.1 Quantitative Results
The Stage 2 model demonstrated strong class-wise performance:
- **Pothole:** 0.884 Precision, 0.812 Recall, 0.861 mAP50.
- **Crack:** 0.820 Precision, 0.770 Recall, 0.809 mAP50.

### 5.2 Failure Mode Analysis
1. **Small Object Omission:** Fine cracks in low-light environments are occasionally missed. Recommended mitigation: Tiling/Sliding Window inference.
2. **Shadow Confusion:** High-contrast shadows can mimic longitudinal cracks. Mitigation: Increased inclusion of "negative" shadow samples in the training set.

---

## 6. Project Structure
```text
project/
├── backend/            # FastAPI Inference Server
│   ├── app/routes/     # API Endpoints
│   └── inference/      # Model Manager and CV Logic
├── frontend/           # React.js Dashboard
│   ├── src/pages/      # Technical Deliverable Pages
│   └── src/index.css   # Custom Professional Design System
├── outputs/            # Trained Weights and Evaluation Artifacts
└── scripts/            # Training and Data Preparation Logic
```

---

## 7. Setup Instructions

### 7.1 Backend Service (Python 3.10+)
1. Navigate to the project root.
2. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
3. Run the API server:
   ```bash
   python project/backend/main.py
   ```

### 7.2 Frontend Dashboard (Node.js 16+)
1. Navigate to `project/frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the application:
   ```bash
   npm start
   ```

---

## 8. Conclusion
This project demonstrates a disciplined approach to ML engineering, moving from data preparation and baseline establishment to a fine-tuned, production-ready deployment. The system is modular, compute-aware, and optimized for real-world road infrastructure assessment.

---
*Developed for Technical Skills Assessment Submission.*
