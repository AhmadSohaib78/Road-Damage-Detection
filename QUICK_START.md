# 🚀 QUICK START REFERENCE

## ⚡ In 30 Seconds

### Open Two Terminals

**Terminal 1 - Backend:**
```bash
cd C:\Users\sodub\OneDrive\Desktop\P2
.venv\Scripts\python.exe project/backend/main.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
cd C:\Users\sodub\OneDrive\Desktop\P2\project\frontend
npm start
```
Wait for: `webpack compiled...`

### Browser
Open: **`http://localhost:3000`**

---

## 📱 What You Can Do

1. **Upload a road image** (JPEG or PNG)
2. **Adjust confidence slider** (0.0 – 1.0)
3. **Click "Detect Damage"**
4. **See results** with annotations

---

## 📊 Model Performance

| Model | Accuracy | Speed |
|-------|----------|-------|
| YOLO Transfer | 0.8163 | Fast |
| SSD | 0.6458 | Medium |
| YOLO Basic | 0.4471 | Fast |

**Recommended:** Use YOLO Transfer (best accuracy)

---

## 🔍 API Endpoints (Advanced)

**Backend URL:** `http://localhost:8000`

```bash
# Health Check
curl http://localhost:8000/api/v1/health

# Get Model Info
curl http://localhost:8000/api/v1/model/info

# Detect Image (requires file upload)
curl -X POST http://localhost:8000/api/v1/detect \
  -F "file=@image.jpg" \
  -F "confidence=0.5"
```

---

## 📁 Important Files

- **Backend:** `project/backend/main.py`
- **Frontend:** `project/frontend/src/App.jsx`
- **Models:** `project/outputs/yolo_transfer_learning/weights/best.pt`
- **Setup Guide:** `project/HOW_TO_RUN.md`
- **Architecture:** `project/FILE_DOCUMENTATION.md`
- **Status Report:** `project/FINAL_STATUS_REPORT.md`

---

## ⚙️ Environment

- **Python:** 3.14 (in `.venv/`)
- **Node.js:** v18+ (for npm)
- **GPU:** NVIDIA RTX 5050 (or CPU auto-fallback)
- **OS:** Windows

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| API won't start | Port 8000 in use? Kill process or use different port |
| Frontend won't load | Port 3000 in use? Or npm not installed? |
| "API offline" | Make sure Terminal 1 (backend) is running |
| Models not found | Run: `python project/verify_and_cleanup.py` |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **HOW_TO_RUN.md** | Simple setup guide |
| **FILE_DOCUMENTATION.md** | Architecture & function details |
| **FINAL_STATUS_REPORT.md** | Complete project status |
| **verify_and_cleanup.py** | QA & cleanup script |
| **start.sh** | Automated startup script |

---

## ✅ Everything is Ready!

- ✅ All models trained
- ✅ Backend API ready
- ✅ Frontend dashboard ready
- ✅ Code verified
- ✅ Documentation complete
- ✅ Project cleaned

**Just run the two commands above and enjoy!** 🎉

