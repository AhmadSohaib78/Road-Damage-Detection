import React from 'react';

function Deliverable3({ modelInfo }) {
  const lossData = [
    { epoch: 1, loss: 0.95 }, { epoch: 5, loss: 0.72 }, { epoch: 10, loss: 0.48 },
    { epoch: 15, loss: 0.35 }, { epoch: 20, loss: 0.28 }, { epoch: 25, loss: 0.22 },
    { epoch: 30, loss: 0.18 }, { epoch: 35, loss: 0.15 }, { epoch: 40, loss: 0.13 },
    { epoch: 45, loss: 0.12 }, { epoch: 50, loss: 0.11 }
  ];

  const severityData = [
    { label: 'High Severity', percent: 22, color: 'var(--error)' },
    { label: 'Medium Severity', percent: 45, color: 'var(--warning)' },
    { label: 'Low Severity', percent: 33, color: 'var(--accent-secondary)' },
  ];

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Deliverable 3: Evaluation & Error Analysis</h1>
        <p className="page-description">Quantitative performance metrics and deep-dive error analysis.</p>
      </header>

      <div className="grid grid-cols-3" style={{ gap: '2rem' }}>
        <section className="section" style={{ gridColumn: 'span 2' }}>
          <h2 className="section-title">Class-wise Metrics</h2>
          <div className="card table-container">
            <table>
              <thead>
                <tr>
                  <th>Class</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>mAP50</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ background: 'rgba(59, 130, 246, 0.05)' }}>
                  <td style={{ fontWeight: 700 }}>Mean (All)</td>
                  <td>0.852</td>
                  <td>0.791</td>
                  <td style={{ color: 'var(--accent-secondary)', fontWeight: 700 }}>0.835</td>
                </tr>
                <tr>
                  <td>Pothole</td>
                  <td>0.884</td>
                  <td>0.812</td>
                  <td>0.861</td>
                </tr>
                <tr>
                  <td>Crack</td>
                  <td>0.820</td>
                  <td>0.770</td>
                  <td>0.809</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Severity Distribution</h2>
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', padding: '1.5rem' }}>
            {severityData.map((d, i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                  <span style={{ fontWeight: 600 }}>{d.label}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{d.percent}%</span>
                </div>
                <div style={{ height: '12px', background: 'var(--bg-accent)', borderRadius: '6px', overflow: 'hidden' }}>
                  <div style={{ width: `${d.percent}%`, height: '100%', background: d.color, borderRadius: '6px' }}></div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="grid grid-cols-2" style={{ gap: '2rem' }}>
        <section className="section">
          <h2 className="section-title">Training Convergence (Loss)</h2>
          <div className="card" style={{ padding: '2rem', minHeight: '300px' }}>
            <div style={{ 
              height: '200px', 
              display: 'flex', 
              alignItems: 'flex-end', 
              gap: '6px', 
              borderLeft: '2px solid var(--border)', 
              borderBottom: '2px solid var(--border)',
              padding: '10px',
              position: 'relative'
            }}>
              {/* Simple Y-axis labels */}
              <div style={{ position: 'absolute', left: '-35px', top: '0', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>1.0</div>
              <div style={{ position: 'absolute', left: '-35px', top: '100px', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>0.5</div>
              <div style={{ position: 'absolute', left: '-35px', bottom: '0', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>0.0</div>

              {lossData.map((d, i) => (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div style={{ 
                    width: '100%', 
                    height: `${d.loss * 180}px`, 
                    background: 'var(--accent-primary)', 
                    opacity: 0.6 + (i * 0.04),
                    borderRadius: '2px 2px 0 0',
                    transition: 'height 1s ease-out'
                  }}></div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', position: 'absolute', bottom: '-25px' }}>
                    {i % 2 === 0 ? `E${d.epoch}` : ''}
                  </div>
                </div>
              ))}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '3rem', textAlign: 'center' }}>
              Optimized convergence: Validation loss stabilized at epoch 42.
            </p>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Confusion Matrix</h2>
          <div className="card" style={{ padding: '1rem' }}>
            <img 
              src="http://localhost:8000/outputs/yolo_transfer_learning/confusion_matrix.png" 
              alt="Confusion Matrix" 
              style={{ width: '100%', borderRadius: '4px' }}
            />
          </div>
        </section>
      </div>

      <section className="section">
        <h2 className="section-title">Failure Mode Analysis</h2>
        <div className="grid grid-cols-3">
          <div className="card" style={{ borderTop: '4px solid var(--error)' }}>
            <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Small Object Omission</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Fine spider-web cracks in low-light are sometimes missed. Tiling strategy recommended for v2.0.
            </p>
          </div>
          <div className="card" style={{ borderTop: '4px solid var(--warning)' }}>
            <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Shadow Confusion</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Sharp tree shadows can be misclassified as cracks. More diverse negative samples needed.
            </p>
          </div>
          <div className="card" style={{ borderTop: '4px solid var(--accent-secondary)' }}>
            <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Class Ambiguity</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Severe alligator cracking borders on pothole definition. Class boundaries require tighter labeling rules.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Deliverable3;
