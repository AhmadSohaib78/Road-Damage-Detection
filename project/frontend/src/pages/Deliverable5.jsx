import React from 'react';

function Deliverable5() {
  const engineeringPrinciples = [
    { 
      title: 'Modularity & OOP', 
      desc: 'The ModelManager class encapsulates all CV logic, allowing for easy swapping between YOLO, SSD, or other future architectures without changing API routes.' 
    },
    { 
      title: 'Request Validation', 
      desc: 'Implemented FastAPI Pydantic models to ensure all incoming inference requests have valid confidence thresholds and file formats.' 
    },
    { 
      title: 'Resource Management', 
      desc: 'Automatic GPU/CPU detection and memory cleanup ensure the system runs reliably on both high-end servers and local edge devices.' 
    },
    { 
      title: 'Scalability', 
      desc: 'Decoupled frontend (React) and backend (FastAPI) allows for independent scaling and containerization via Docker.' 
    }
  ];

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Deliverable 5: Engineering Quality</h1>
        <p className="page-description">Software design patterns and production-ready implementation details.</p>
      </header>

      <section className="section">
        <h2 className="section-title">System Architecture</h2>
        <div className="card" style={{ padding: '2rem', background: 'var(--bg-accent)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', textAlign: 'center' }}>
            <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--accent-primary)', width: '150px' }}>
              <div style={{ fontWeight: 800 }}>React SPA</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Dashboard UI</div>
            </div>
            <div style={{ color: 'var(--accent-primary)', fontWeight: 800 }}>REST API</div>
            <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--accent-secondary)', width: '150px' }}>
              <div style={{ fontWeight: 800 }}>FastAPI</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Inference Engine</div>
            </div>
            <div style={{ color: 'var(--accent-secondary)', fontWeight: 800 }}>PyTorch</div>
            <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--error)', width: '150px' }}>
              <div style={{ fontWeight: 800 }}>Model Registry</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>.pt / .pth Weights</div>
            </div>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-2">
        <section className="section">
          <h2 className="section-title">Technology Stack</h2>
          <div className="card">
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700 }}>CV Framework</span>
                <span style={{ color: 'var(--accent-primary)' }}>Ultralytics YOLOv8 / PyTorch</span>
              </li>
              <li style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700 }}>Backend API</span>
                <span style={{ color: 'var(--accent-primary)' }}>FastAPI (Asynchronous)</span>
              </li>
              <li style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700 }}>Frontend UI</span>
                <span style={{ color: 'var(--accent-primary)' }}>React.js + Vanilla CSS</span>
              </li>
              <li style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700 }}>Image Processing</span>
                <span style={{ color: 'var(--accent-primary)' }}>OpenCV-Python</span>
              </li>
            </ul>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Directory Structure</h2>
          <div className="card" style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
            <div style={{ color: 'var(--accent-secondary)' }}>project/</div>
            <div style={{ paddingLeft: '1rem' }}>├── backend/ <span style={{ color: 'var(--text-secondary)' }}># Logic</span></div>
            <div style={{ paddingLeft: '2rem' }}>├── app/routes/ <span style={{ color: 'var(--text-secondary)' }}># Endpoints</span></div>
            <div style={{ paddingLeft: '2rem' }}>└── inference/ <span style={{ color: 'var(--text-secondary)' }}># Model Managers</span></div>
            <div style={{ paddingLeft: '1rem' }}>├── frontend/ <span style={{ color: 'var(--text-secondary)' }}># React UI</span></div>
            <div style={{ paddingLeft: '1rem' }}>├── outputs/ <span style={{ color: 'var(--text-secondary)' }}># Weights/Stats</span></div>
            <div style={{ paddingLeft: '1rem' }}>└── scripts/ <span style={{ color: 'var(--text-secondary)' }}># Training/Data Utils</span></div>
          </div>
        </section>
      </div>

      <section className="section">
        <h2 className="section-title">ML Engineering Highlights</h2>
        <div className="grid grid-cols-2">
          {engineeringPrinciples.map((item, i) => (
            <div key={i} className="card">
              <h3 style={{ marginBottom: '0.75rem', color: 'var(--accent-primary)', fontSize: '1.1rem' }}>{item.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', lineHeight: 1.6 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Deliverable5;
