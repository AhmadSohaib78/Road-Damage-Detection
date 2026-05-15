import React from 'react';

export default function ResultsPanel({ originalUrl, annotatedB64, loading, hasResults }) {
  const annotatedSrc = annotatedB64 ? `data:image/jpeg;base64,${annotatedB64}` : null;

  return (
    <div className="results-grid">
      {/* Original */}
      <div className="result-card">
        <div className="result-card-header">
          <span>🖼</span> Original Image
        </div>
        <div className="result-card-body">
          {originalUrl ? (
            <img src={originalUrl} alt="Original road" className="result-img" />
          ) : (
            <div className="result-placeholder">
              <span className="result-placeholder-icon">📷</span>
              <span>No image uploaded</span>
            </div>
          )}
        </div>
      </div>

      {/* Annotated */}
      <div className="result-card">
        <div className="result-card-header">
          <span>🎯</span> AI Detection Output
        </div>
        <div className="result-card-body">
          {loading ? (
            <div className="inferring-overlay">
              <div className="inferring-spinner" />
              <span>Running inference…</span>
            </div>
          ) : annotatedSrc ? (
            <img src={annotatedSrc} alt="Annotated detections" className="result-img" />
          ) : hasResults ? (
            <div className="result-placeholder">
              <span className="result-placeholder-icon">✅</span>
              <span>No damage detected</span>
            </div>
          ) : (
            <div className="result-placeholder">
              <span className="result-placeholder-icon">🤖</span>
              <span>Results will appear here</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
