import React from 'react';

const STATUS_LABELS = {
  healthy:  { label: 'API Online',    icon: '●' },
  degraded: { label: 'API Degraded',  icon: '●' },
  offline:  { label: 'API Offline',   icon: '●' },
  checking: { label: 'Connecting…',   icon: '○' },
};

export default function Header({ apiStatus }) {
  const s = STATUS_LABELS[apiStatus] || STATUS_LABELS.checking;

  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="header-brand">
          <div className="header-icon">🛣</div>
          <div>
            <div className="header-title">AI Smart Road Damage Detection</div>
            <div className="header-subtitle">YOLOv8n · SSD MobileNetV2 · FastAPI · React</div>
          </div>
        </div>

        <div className="header-right">
          <div className={`status-pill ${apiStatus}`}>
            <span className={`status-dot ${apiStatus}`} />
            {s.label}
          </div>
        </div>
      </div>
    </header>
  );
}
