import React from 'react';

function Deliverable1({ modelInfo }) {
  const stats = {
    original_size: modelInfo?.dataset_stats?.original_size || 2009,
    augmented_size: modelInfo?.dataset_stats?.augmented_size || 6027,
    split: modelInfo?.dataset_stats?.split || { train: 4822, val: 602, test: 603 },
    class_distribution: modelInfo?.dataset_stats?.class_distribution || { pothole: 1858, crack: 4169 }
  };

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Deliverable 1: Data Understanding & Preparation</h1>
        <p className="page-description">Dataset scale-up, preprocessing workflow, and multi-stage augmentation strategy.</p>
      </header>

      <section className="section">
        <h2 className="section-title">Dataset Scale & Distribution</h2>
        <div className="grid grid-cols-4">
          <div className="card stat-card">
            <div className="stat-value">{stats.original_size}</div>
            <div className="stat-label">Original Images</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{stats.augmented_size}</div>
            <div className="stat-label">Augmented Images</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">3x</div>
            <div className="stat-label">Dataset Expansion</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">640x640</div>
            <div className="stat-label">Target Resolution</div>
          </div>
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">Train / Val / Test Splits</h2>
        <div className="card table-container">
          <table>
            <thead>
              <tr>
                <th>Split Name</th>
                <th>Image Count</th>
                <th>Percentage</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600, color: 'var(--accent-secondary)' }}>Training</td>
                <td>{stats.split.train}</td>
                <td>80%</td>
                <td>Weight updates & Backpropagation</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600, color: 'var(--warning)' }}>Validation</td>
                <td>{stats.split.val}</td>
                <td>10%</td>
                <td>Hyperparameter tuning & Early stopping</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>Testing</td>
                <td>{stats.split.test}</td>
                <td>10%</td>
                <td>Unseen data performance evaluation</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">Preprocessing & Augmentation Flow</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          To ensure model robustness across various lighting and weather conditions, we applied a standardized 3-step pipeline to every source image.
        </p>
        <div className="grid grid-cols-3">
          <div className="image-box">
            <div className="image-label">1. Original Image</div>
            <div className="image-container">
              <img src="http://localhost:8000/outputs/sample_1_orig.jpg" alt="Original" />
            </div>
            <p className="image-caption" style={{ fontSize: '0.8rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Raw high-res capture from mobile device/camera.
            </p>
          </div>
          <div className="image-box">
            <div className="image-label">2. Preprocessed</div>
            <div className="image-container">
              <img src="http://localhost:8000/outputs/sample_1_preprocess.jpg" alt="Preprocessed" />
            </div>
            <p className="image-caption" style={{ fontSize: '0.8rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Bilinear resize to 640x640 and channel normalization.
            </p>
          </div>
          <div className="image-box">
            <div className="image-label">3. Augmented</div>
            <div className="image-container">
              <img src="http://localhost:8000/outputs/sample_1_aug.jpg" alt="Augmented" />
            </div>
            <p className="image-caption" style={{ fontSize: '0.8rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Random horizontal flip & HSV jitter to prevent overfitting.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Deliverable1;
