import React from 'react';

function Deliverable2({ modelInfo }) {
  const comparisons = [
    { name: 'Stage 2: YOLO Fine-tuned (Best)', mAP50: 0.835, size: '50 MB', latency: 50, status: 'Optimal' },
    { name: 'Stage 1: SSD MobileNet (Baseline)', mAP50: 0.646, size: '17.3 MB', latency: 150, status: 'Baseline' },
    { name: 'YOLO Stock', mAP50: 0.447, size: '23.3 MB', latency: 40, status: 'Initial' },
  ];

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Deliverable 2: Model Selection & Training</h1>
        <p className="page-description">Phased training strategy: from Stage 1 Baseline to Stage 2 Production-ready YOLO.</p>
      </header>

      <div className="grid grid-cols-2" style={{ gap: '2rem' }}>
        <section className="section">
          <h2 className="section-title">Accuracy Comparison (mAP50)</h2>
          <div className="card" style={{ padding: '1.5rem', minHeight: '300px' }}>
            <div className="chart-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {comparisons.map((m, idx) => (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{m.name}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ flex: 1, height: '18px', background: 'var(--bg-accent)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ 
                        width: `${m.mAP50 * 100}%`, 
                        height: '100%', 
                        background: m.status === 'Optimal' ? 'var(--accent-secondary)' : m.status === 'Baseline' ? 'var(--accent-primary)' : 'var(--text-secondary)',
                        transition: 'width 1s ease-out'
                      }}></div>
                    </div>
                    <div style={{ fontWeight: 700, minWidth: '50px' }}>{(m.mAP50 * 100).toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Latency Comparison (Inference ms)</h2>
          <div className="card" style={{ padding: '1.5rem', minHeight: '300px' }}>
            <div className="chart-container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {comparisons.map((m, idx) => (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{m.name}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ flex: 1, height: '18px', background: 'var(--bg-accent)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ 
                        width: `${(m.latency / 200) * 100}%`, 
                        height: '100%', 
                        background: m.latency < 60 ? 'var(--accent-secondary)' : m.latency < 100 ? 'var(--warning)' : 'var(--error)',
                        transition: 'width 1s ease-out'
                      }}></div>
                    </div>
                    <div style={{ fontWeight: 700, minWidth: '50px' }}>{m.latency}ms</div>
                  </div>
                </div>
              ))}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '1rem', textAlign: 'center' }}>
              Lower is better. Stage 2 (YOLO) is 3x faster than Stage 1 (SSD) on same hardware.
            </p>
          </div>
        </section>
      </div>

      <section className="section">
        <h2 className="section-title">Model Comparison Matrix</h2>
        <div className="card table-container">
          <table>
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>Model Size</th>
                <th>Primary Strength</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((m, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{m.name}</td>
                  <td>{m.size}</td>
                  <td>{idx === 0 ? 'Highest Accuracy' : idx === 1 ? 'Legacy Stability' : 'Speed Baseline'}</td>
                  <td>
                    <span style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem', 
                      background: m.status === 'Optimal' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                      color: m.status === 'Optimal' ? 'var(--accent-secondary)' : 'var(--accent-primary)',
                      border: `1px solid ${m.status === 'Optimal' ? 'var(--accent-secondary)' : 'var(--accent-primary)'}`
                    }}>
                      {m.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Deliverable2;
