import React, { useRef, useState, useCallback } from 'react';

export default function UploadSection({
  onImageSelected,
  imagePreviewUrl,
  confidence,
  onConfidenceChange,
  onDetect,
  onReset,
  loading,
  disabled,
  hasImage,
}) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return;
    onImageSelected(file);
  }, [onImageSelected]);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    handleFile(file);
  };

  const confPct = Math.round(confidence * 100);

  return (
    <div className="upload-grid">
      {/* Drop zone */}
      <div>
        {!imagePreviewUrl ? (
          <div
            className={`dropzone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
          >
            <span className="dropzone-icon">📂</span>
            <p className="dropzone-title">Drop image or click to upload</p>
            <p className="dropzone-sub">JPEG · PNG · WebP · Max 15 MB</p>
            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </div>
        ) : (
          <div className="img-thumb-wrap">
            <img src={imagePreviewUrl} alt="Preview" className="img-thumb" />
            <div className="img-thumb-label">Ready for detection</div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="controls-card">
        <div>
          <span className="control-label">Confidence Threshold</span>
          <div className="conf-row">
            <input
              type="range"
              className="conf-slider"
              min={0.1} max={0.95} step={0.05}
              value={confidence}
              style={{ '--val': `${((confidence - 0.1) / (0.95 - 0.1)) * 100}%` }}
              onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
            />
            <span className="conf-value">{confPct}%</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
            Detections below this confidence are discarded
          </p>
        </div>

        <button
          className="btn-detect"
          onClick={onDetect}
          disabled={disabled || loading}
        >
          {loading ? (
            <span className="btn-loading">
              <span className="spinner" />
              Analysing…
            </span>
          ) : (
            '🚀 Run Detection'
          )}
        </button>

        {hasImage && (
          <button className="btn-reset" onClick={onReset}>
            ↺ Clear & Reset
          </button>
        )}

        {!hasImage && (
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            Upload a road image to begin
          </p>
        )}
      </div>
    </div>
  );
}
