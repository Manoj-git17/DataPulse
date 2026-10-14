import React from 'react';
import './SettingsPage.css';

export default function SettingsPage({ theme, onToggleTheme, onLogout, dataSource }) {
  return (
    <div className="settings-page">
      <h1 className="settings-page-title">Settings</h1>

      {/* Appearance */}
      <section className="settings-section">
        <h2 className="settings-section-title">Appearance</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">Color Theme</span>
            <span className="settings-row-desc">
              Currently using <strong>{theme === 'dark' ? 'Dark' : 'Light'}</strong> mode
            </span>
          </div>
          <button className="settings-btn-toggle" onClick={onToggleTheme} type="button">
            {theme === 'dark' ? '☀ Switch to Light' : '☾ Switch to Dark'}
          </button>
        </div>
      </section>

      {/* Session */}
      <section className="settings-section">
        <h2 className="settings-section-title">Session</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">Current Data Source</span>
            <span className="settings-row-desc">{dataSource}</span>
          </div>
          <span className="settings-status-pill">Live</span>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">Sign out of DataPulse</span>
            <span className="settings-row-desc">
              Clears your session token from this browser tab
            </span>
          </div>
          <button className="settings-btn-danger" onClick={onLogout} type="button">
            ↩ Sign Out
          </button>
        </div>
      </section>

      {/* Platform info */}
      <section className="settings-section">
        <h2 className="settings-section-title">Platform</h2>
        <div className="settings-info-grid">
          {[
            { label: 'Version',       value: 'DataPulse v1.0.0' },
            { label: 'Backend',       value: 'FastAPI · Uvicorn · SQLAlchemy' },
            { label: 'Frontend',      value: 'React 19 · Vite 8' },
            { label: 'Database',      value: 'SQLite (local) — PostgreSQL via DATABASE_URL' },
            { label: 'AI Assistant',  value: 'Local Text-to-SQL · No external APIs · ₹0 cost' },
            { label: 'Auth',          value: 'JWT · Argon2 password hashing · pwdlib' },
          ].map(({ label, value }) => (
            <div key={label} className="settings-info-card">
              <span className="settings-info-label">{label}</span>
              <span className="settings-info-value">{value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
