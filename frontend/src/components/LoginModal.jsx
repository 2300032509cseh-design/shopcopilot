import React, { useState } from 'react';
import { ShoppingBag, Lock, Mail, Store, ArrowRight, LogIn, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';
import './LoginModal.css';

export default function LoginModal({ onLoginSuccess, apiBase }) {
  const [email, setEmail] = useState('demo@shopcopilot.com');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDemoLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email || 'demo@shopcopilot.com',
          password: password || 'password123'
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Demo login failed');

      localStorage.setItem('shop_copilot_token', data.token);
      localStorage.setItem('shop_copilot_user', JSON.stringify(data.user));

      onLoginSuccess(data.user, data.token);
    } catch (err) {
      setError(err.message || 'Error connecting to demo server');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleDemoLogin();
  };

  return (
    <div className="auth-overlay">
      <div className="auth-card glass-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-brand-icon">
            <ShoppingBag size={28} />
          </div>
          <h2 className="auth-title">SHOP COPILOT</h2>
          <p className="auth-subtitle">
            Voice-first inventory & intelligence for small shops
          </p>
        </div>

        {/* Demo Mode Feature Badge */}
        <div className="demo-notice-banner">
          <div className="demo-notice-header">
            <Sparkles size={16} color="#4F46E5" />
            <span>🎯 Live Demo Mode</span>
          </div>
          <p className="demo-notice-text">
            Pre-loaded with <strong>Sah's Store</strong> inventory, custom vocabulary, multilingual Telugu voice assistant, and analytics.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="auth-error-alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* 1-Click Launch Demo Button */}
        <button
          type="button"
          onClick={handleDemoLogin}
          disabled={loading}
          className="demo-primary-btn"
        >
          {loading ? (
            <span>🧠 Logging into Demo Shop...</span>
          ) : (
            <>
              <span>⚡ Launch Sah's Store (Demo)</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>

        {/* Divider */}
        <div className="auth-divider">
          <span>or sign in with credentials</span>
        </div>

        {/* Pre-filled Credentials Form */}
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label>Demo Shop Email</label>
            <div className="input-wrapper">
              <Mail size={16} className="input-icon" />
              <input
                type="email"
                required
                placeholder="demo@shopcopilot.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="auth-field">
            <label>Password</label>
            <div className="input-wrapper">
              <Lock size={16} className="input-icon" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button type="submit" disabled={loading} className="auth-submit-btn">
            {loading ? (
              'Processing...'
            ) : (
              <>
                <span>Sign In to Demo Shop</span>
                <LogIn size={18} />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

