import React from 'react';

const CLASS_ICONS = { pothole: '🕳', crack: '⚡', manhole: '🔲' };

export default function DetectionTable({ detections }) {
  if (!detections || detections.length === 0) return null;

  return (
    <div className="table-wrapper">
      <table className="det-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Class</th>
            <th>Confidence</th>
            <th>Severity</th>
            <th>Bounding Box</th>
            <th>Area Ratio</th>
          </tr>
        </thead>
        <tbody>
          {detections.map((det, idx) => {
            const cls = det.class || 'unknown';
            const conf = det.confidence ?? 0;
            const sev = det.severity || 'low';
            const [x1, y1, x2, y2] = det.bbox || [0, 0, 0, 0];
            const area = det.area_ratio ?? 0;

            return (
              <tr key={idx}>
                <td style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>

                <td>
                  <span className={`class-chip ${cls}`}>
                    {CLASS_ICONS[cls] || '❓'} {cls}
                  </span>
                </td>

                <td>
                  <div className="conf-bar-wrap">
                    <div className="conf-bar-bg">
                      <div
                        className="conf-bar-fill"
                        style={{ width: `${(conf * 100).toFixed(0)}%` }}
                      />
                    </div>
                    <span className="conf-num">{(conf * 100).toFixed(1)}%</span>
                  </div>
                </td>

                <td>
                  <span className={`sev-chip ${sev}`}>{sev}</span>
                </td>

                <td style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  [{x1}, {y1}, {x2}, {y2}]
                </td>

                <td style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {(area * 100).toFixed(2)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
