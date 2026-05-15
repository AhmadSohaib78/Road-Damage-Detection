import React from 'react';

const ProjectChecklist = () => {
  const deliverables = [
    { label: 'YOLOv8 transfer-learning model trained', status: 'complete' },
    { label: 'SSD MobileNetV2 baseline model trained', status: 'complete' },
    { label: 'Backend FastAPI detection API', status: 'complete' },
    { label: 'React image upload + annotation UI', status: 'complete' },
    { label: 'Live model evaluation metrics', status: 'complete' },
    { label: 'Severity & damage statistics summary', status: 'complete' },
    { label: 'Docker-ready project deployment', status: 'complete' },
  ];

  return (
    <div className="card checklist-card">
      <div className="checklist-grid">
        {deliverables.map((item, idx) => (
          <div key={idx} className="checklist-item">
            <span className="check-icon">✓</span>
            <span className="check-label">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectChecklist;
