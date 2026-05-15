import React, { useState, useRef } from 'react';
import axios from 'axios';

function Deliverable4({ modelInfo, API_BASE }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const runInference = async () => {
    if (!selectedFile) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('conf_thresh', '0.40');

    try {
      const res = await axios.post(`${API_BASE}/detect`, formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Inference failed. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Deliverable 4: Inference & Deployment</h1>
        <p className="page-description">Real-time road damage detection using the Stage 2 Fine-tuned YOLOv8 model.</p>
      </header>

      <section className="section">
        <h2 className="section-title">Inference Pipeline Workflow</h2>
        <div className="pipeline" style={{ justifyContent: 'center' }}>
          <div className="pipeline-step">Input Image</div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-step">Resize (640x640)</div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-step">Inference (YOLOv8m)</div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-step">NMS & Box Scaling</div>
          <div className="pipeline-arrow">→</div>
          <div className="pipeline-step" style={{ background: 'var(--accent-secondary)', color: 'white', borderColor: 'var(--accent-secondary)' }}>Detected Output</div>
        </div>
      </section>

      <div className="grid grid-cols-2" style={{ alignItems: 'start', gap: '3rem' }}>
        <section className="section">
          <h2 className="section-title">Inference Control</h2>
          <div className="card">
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={handleFileSelect}
              accept="image/*"
            />
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
              <button className="button button-secondary" onClick={() => fileInputRef.current.click()} style={{ flex: 1 }}>
                Select Image
              </button>
              <button 
                className="button button-primary" 
                onClick={runInference} 
                disabled={!selectedFile || loading}
                style={{ flex: 2 }}
              >
                {loading ? 'Processing...' : 'Run Detection'}
              </button>
            </div>

            {previewUrl && (
              <div className="image-box">
                <div className="image-label">Input Preview</div>
                <div className="image-container" style={{ maxHeight: '500px', background: '#000' }}>
                  <img src={previewUrl} alt="Preview" style={{ objectFit: 'contain' }} />
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Detection Results</h2>
          <div className="card" style={{ minHeight: '400px' }}>
            {!result && !loading && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px', color: 'var(--text-secondary)', textAlign: 'center' }}>
                Upload an image and run detection <br/> to see results here.
              </div>
            )}
            
            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
                <div className="loading-spinner"></div>
              </div>
            )}

            {result && (
              <>
                <div className="image-box" style={{ marginBottom: '1.5rem' }}>
                  <div className="image-label">Processed Output (Annotated)</div>
                  <div className="image-container" style={{ maxHeight: '500px', background: '#000' }}>
                    <img src={`data:image/jpeg;base64,${result.annotated_image_b64}`} alt="Result" style={{ objectFit: 'contain' }} />
                  </div>
                </div>
                
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Damage Type</th>
                        <th>Confidence</th>
                        <th>Severity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.detections.map((d, i) => (
                        <tr key={i}>
                          <td style={{ textTransform: 'capitalize', fontWeight: 600 }}>{d.class}</td>
                          <td>{(d.confidence * 100).toFixed(1)}%</td>
                          <td>
                            <span style={{ 
                              color: d.severity === 'high' ? 'var(--error)' : d.severity === 'medium' ? 'var(--warning)' : 'var(--accent-secondary)',
                              fontWeight: 800,
                              fontSize: '0.8rem'
                            }}>
                              {d.severity.toUpperCase()}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {result.detections.length === 0 && (
                        <tr><td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No damage detected.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Deliverable4;
