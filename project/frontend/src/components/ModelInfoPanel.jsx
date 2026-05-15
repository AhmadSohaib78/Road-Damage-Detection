import React from 'react';

export default function ModelInfoPanel({ modelInfo }) {
  if (!modelInfo || !modelInfo.ready) {
    return (
      <div className="card">
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Model not loaded. Start the backend and run training first.
        </p>
      </div>
    );
  }

  const sev = modelInfo.severity_thresholds || {};

  return (
    <div className="model-info-grid">
      {/* Architecture */}
      <div className="model-info-card">
        <h4>Active Model</h4>
        <div className="model-kv">
          <div className="kv-row">
            <span className="kv-key">Type</span>
            <span className="kv-val accent">{modelInfo.model_type?.toUpperCase()}</span>
          </div>
          <div className="kv-row">
            <span className="kv-key">Version</span>
            <span className="kv-val" style={{ fontSize: '0.72rem', maxWidth: '160px', textAlign: 'right' }}>
              {modelInfo.model_version}
            </span>
          </div>
          <div className="kv-row">
            <span className="kv-key">Framework</span>
            <span className="kv-val">{modelInfo.framework}</span>
          </div>
          <div className="kv-row">
            <span className="kv-key">Device</span>
            <span className="kv-val accent">{modelInfo.device?.toUpperCase()}</span>
          </div>
        </div>
      </div>

      {/* Config */}
      <div className="model-info-card">
        <h4>Configuration</h4>
        <div className="model-kv">
          <div className="kv-row">
            <span className="kv-key">Image Size</span>
            <span className="kv-val">{modelInfo.image_size ?? 640}px</span>
          </div>
          <div className="kv-row">
            <span className="kv-key">Conf Threshold</span>
            <span className="kv-val accent">{((modelInfo.confidence_threshold ?? 0.5) * 100).toFixed(0)}%</span>
          </div>
          <div className="kv-row">
            <span className="kv-key">Num Classes</span>
            <span className="kv-val">{modelInfo.num_classes}</span>
          </div>
        </div>
        <div className="class-chips-row">
          {(modelInfo.classes || []).map((cls) => (
            <span key={cls} className={`class-chip ${cls}`}>
              {cls}
            </span>
          ))}
        </div>
      </div>

      {/* Severity */}
      <div className="model-info-card">
        <h4>Severity Heuristic</h4>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
          Based on bbox area ÷ image area. Rule-based — not learned.
        </p>
        <div className="model-kv">
          {Object.entries(sev).map(([level, rule]) => (
            <div key={level} className="kv-row">
              <span className={`sev-chip ${level}`}>{level}</span>
              <span className="kv-val" style={{ fontSize: '0.72rem' }}>{rule}</span>
            </div>
          ))}
        </div>
      </div>

      {modelInfo.evaluation && (
        <div className="model-info-card evaluation-card">
          <h4>Latest Evaluation</h4>
          <div className="model-kv">
            <div className="kv-row">
              <span className="kv-key">mAP@0.5</span>
              <span className="kv-val accent">{(modelInfo.evaluation.mAP50 ?? modelInfo.evaluation.map50 ?? 0).toFixed(3)}</span>
            </div>
            <div className="kv-row">
              <span className="kv-key">mAP@0.5-0.95</span>
              <span className="kv-val accent">{(modelInfo.evaluation.mAP50_95 ?? modelInfo.evaluation.map ?? 0).toFixed(3)}</span>
            </div>
            {modelInfo.evaluation.confidence !== undefined && (
              <div className="kv-row">
                <span className="kv-key">Confidence</span>
                <span className="kv-val">{Math.round(modelInfo.evaluation.confidence * 100)}%</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
