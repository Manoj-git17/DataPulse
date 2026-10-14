import React, { useState } from 'react';
import './ProfilePage.css';

export default function ProfilePage({ user, onUpdateUser }) {
  const [isEditing, setIsEditing] = useState(false);
  const [fullNameInput, setFullNameInput] = useState(user?.full_name || '');
  const [message, setMessage] = useState(null);

  if (!user) {
    return (
      <div className="profile-page">
        <p className="profile-loading">Loading profile…</p>
      </div>
    );
  }

  const initials = user.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : (user.email || 'U').slice(0, 2).toUpperCase();

  const joinedDate = user.created_at
    ? new Date(user.created_at).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : '—';

  const handleStartEditing = () => {
    setFullNameInput(user.full_name || '');
    setMessage(null);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setFullNameInput(user.full_name || '');
    setMessage(null);
    setIsEditing(false);
  };

  const handleSave = (e) => {
    e.preventDefault();
    const trimmed = fullNameInput.trim();

    if (!trimmed || trimmed.length < 2) {
      setMessage({
        type: 'error',
        text: 'Full name must be at least 2 characters long.',
      });
      return;
    }

    if (trimmed.length > 100) {
      setMessage({
        type: 'error',
        text: 'Full name cannot exceed 100 characters.',
      });
      return;
    }

    // Update in-memory session profile
    if (onUpdateUser) {
      onUpdateUser({
        ...user,
        full_name: trimmed,
      });
    }

    setMessage({
      type: 'info',
      text: 'Display name updated for this session. (Note: The FastAPI backend currently provides read-only profile access via GET /api/auth/me; permanent persistence requires the proposed PUT /api/auth/me endpoint).',
    });
    setIsEditing(false);
  };

  return (
    <div className="profile-page">
      {/* Hero card */}
      <div className="profile-hero">
        <div className="profile-avatar-xl">{initials}</div>
        <div className="profile-identity">
          <h1 className="profile-name">{user.full_name}</h1>
          <p className="profile-email-text">{user.email}</p>
          <span className="profile-active-badge">● Active Account</span>
        </div>
        {!isEditing && (
          <div className="profile-hero-actions">
            <button
              type="button"
              className="profile-edit-btn"
              onClick={handleStartEditing}
            >
              ✎ Edit Profile
            </button>
          </div>
        )}
      </div>

      {/* Feedback banner */}
      {message && (
        <div className={`profile-alert profile-alert-${message.type}`} role="status">
          <span>{message.type === 'error' ? '⚠ ' : 'ℹ '}{message.text}</span>
          <button
            type="button"
            className="profile-alert-close"
            onClick={() => setMessage(null)}
            aria-label="Dismiss message"
          >
            ×
          </button>
        </div>
      )}

      {/* Inline Editing Form */}
      {isEditing && (
        <form className="profile-edit-card" onSubmit={handleSave}>
          <div className="profile-edit-header">
            <h2 className="profile-edit-title">Edit Profile Information</h2>
            <p className="profile-edit-subtitle">Update your display name across the platform</p>
          </div>

          <div className="profile-form-group">
            <label htmlFor="profile-full-name" className="profile-form-label">
              Full Name
            </label>
            <input
              id="profile-full-name"
              type="text"
              className="profile-form-input"
              value={fullNameInput}
              onChange={(e) => setFullNameInput(e.target.value)}
              placeholder="Enter your full name"
              autoFocus
            />
            <span className="profile-form-hint">Between 2 and 100 characters</span>
          </div>

          <div className="profile-edit-actions">
            <button type="submit" className="profile-btn-save">
              Save Changes
            </button>
            <button
              type="button"
              className="profile-btn-cancel"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Info grid */}
      <div className="profile-info-grid">
        <div className="profile-info-card">
          <span className="profile-info-label">Full Name</span>
          <span className="profile-info-value">{user.full_name}</span>
        </div>
        <div className="profile-info-card">
          <span className="profile-info-label">Email Address</span>
          <span className="profile-info-value">{user.email}</span>
        </div>
        <div className="profile-info-card">
          <span className="profile-info-label">Account Status</span>
          <span className="profile-info-value profile-status-green">
            {user.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
        <div className="profile-info-card">
          <span className="profile-info-label">Member Since</span>
          <span className="profile-info-value">{joinedDate}</span>
        </div>
        <div className="profile-info-card">
          <span className="profile-info-label">User ID</span>
          <span className="profile-info-value profile-mono">#{user.id}</span>
        </div>
        <div className="profile-info-card">
          <span className="profile-info-label">Platform Role</span>
          <span className="profile-info-value">Data Analyst</span>
        </div>
      </div>

      {/* Stats row */}
      <div className="profile-stats-row">
        <div className="profile-stat-card">
          <span className="profile-stat-value">148</span>
          <span className="profile-stat-label">Orders Tracked</span>
        </div>
        <div className="profile-stat-card">
          <span className="profile-stat-value">₹15.1L</span>
          <span className="profile-stat-label">Revenue Analysed</span>
        </div>
        <div className="profile-stat-card">
          <span className="profile-stat-value">6</span>
          <span className="profile-stat-label">Months of Data</span>
        </div>
        <div className="profile-stat-card">
          <span className="profile-stat-value">₹0</span>
          <span className="profile-stat-label">Platform Cost</span>
        </div>
      </div>
    </div>
  );
}
