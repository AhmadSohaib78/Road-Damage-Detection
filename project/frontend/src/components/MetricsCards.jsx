import React from 'react';

export default function MetricsCards({ statistics, inferenceTime }) {
  const { total = 0, by_class = {}, severity = {}, avg_confidence = 0 } = statistics || {};
  const pothole = by_class.pothole ?? 0;
  const crack   = by_class.crack   ?? 0;

  const cards = [
    {
      icon: '🕳',
      label: 'Potholes',
      value: pothole,
      sub: `of ${total} total detections`,
      accent: '#ef4444',
    },
    {
      icon: '⚡',
      label: 'Cracks',
      value: crack,
      sub: `of ${total} total detections`,
      accent: '#22c55e',
    },
    {
      icon: '🎯',
      label: 'Avg Confidence',
      value: `${(avg_confidence * 100).toFixed(1)}%`,
      sub: 'mean detection score',
      accent: '#3b82f6',
      mono: true,
    },
    {
      icon: '⚡',
      label: 'Inference Time',
      value: inferenceTime ? `${inferenceTime}ms` : '—',
      sub: 'model forward pass',
      accent: '#8b5cf6',
      mono: true,
    },
    {
      icon: '📊',
      label: 'Severity',
      value: null,   // custom render
      severityData: severity,
      accent: '#64748b',
    },
  ];

  return (
    <div className="metrics-grid">
      {cards.map((c) => (
        <div
          key={c.label}
          className="metric-card"
          style={{ '--metric-accent': c.accent }}
        >
          <span className="metric-icon">{c.icon}</span>
          <span className="metric-label">{c.label}</span>

          {c.value !== null && (
            <span
              className="metric-value"
              style={c.mono ? { fontFamily: "'JetBrains Mono', monospace" } : {}}
            >
              {c.value}
            </span>
          )}

          {c.severityData && (
            <div className="severity-bars">
              {['low', 'medium', 'high'].map((sev) => (
                <div key={sev} className={`sev-bar ${sev}`}>
                  {c.severityData[sev] ?? 0}
                  <br />
                  <span style={{ fontWeight: 400, fontSize: '0.65rem' }}>{sev}</span>
                </div>
              ))}
            </div>
          )}

          {c.sub && <span className="metric-sub">{c.sub}</span>}
        </div>
      ))}
    </div>
  );
}
