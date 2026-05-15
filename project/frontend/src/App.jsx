import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Deliverable1 from './pages/Deliverable1';
import Deliverable2 from './pages/Deliverable2';
import Deliverable3 from './pages/Deliverable3';
import Deliverable4 from './pages/Deliverable4';
import Deliverable5 from './pages/Deliverable5';

const API_BASE = 'http://localhost:8000/api/v1';

function App() {
  const [activePage, setActivePage] = useState('deliverable4');
  const [modelInfo, setModelInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState('offline');

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [healthRes, infoRes] = await Promise.all([
          axios.get(`${API_BASE}/health`),
          axios.get(`${API_BASE}/model/info`)
        ]);
        setApiStatus(healthRes.data.status === 'healthy' ? 'online' : 'degraded');
        setModelInfo(infoRes.data);
      } catch (err) {
        setApiStatus('offline');
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    const props = { modelInfo, apiStatus, API_BASE };
    switch (activePage) {
      case 'deliverable1': return <Deliverable1 {...props} />;
      case 'deliverable2': return <Deliverable2 {...props} />;
      case 'deliverable3': return <Deliverable3 {...props} />;
      case 'deliverable4': return <Deliverable4 {...props} />;
      case 'deliverable5': return <Deliverable5 {...props} />;
      default: return <Deliverable4 {...props} />;
    }
  };

  return (
    <div className="app-root">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">AI Road Damage</h1>
          <p className="sidebar-subtitle">Technical Assessment</p>
        </div>
        
        <ul className="nav-list">
          {[
            { id: 'deliverable1', label: '1. Data Preparation' },
            { id: 'deliverable2', label: '2. Model Selection' },
            { id: 'deliverable3', label: '3. Error Analysis' },
            { id: 'deliverable4', label: '4. Live Inference' },
            { id: 'deliverable5', label: '5. Engineering' },
          ].map(item => (
            <li key={item.id} className="nav-item">
              <a 
                href={`#${item.id}`}
                className={`nav-link ${activePage === item.id ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); setActivePage(item.id); }}
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="api-status-box">
          <div className={`status-indicator ${apiStatus}`}></div>
          <span className="status-text">API {apiStatus.toUpperCase()}</span>
        </div>
      </nav>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
