import React, { useState } from 'react';
import { ShoppingBag, Lock, Mail, Store, ArrowRight, UserPlus, LogIn, AlertCircle } from 'lucide-react';
import './LoginModal.css';

export default function LoginModal({ onLoginSuccess, apiBase }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [shopName, setShopName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isRegister ? '/auth/register' : '/auth/login';
    const payload = isRegister
      ? { email, password, name, shop_name: shopName }
      : { email, password };

    try {
      const res = await fetch(`${apiBase}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Authentication failed');
      }

      // Store in localStorage
      localStorage.setItem('shop_copilot_token', data.token);
      localStorage.setItem('shop_copilot_user', JSON.stringify(data.user));

      onLoginSuccess(data.user, data.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'demo@shopcopilot.com',
          password: 'password123'
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Demo login failed');

      localStorage.setItem('shop_copilot_token', data.token);
      localStorage.setItem('shop_copilot_user', JSON.stringify(data.user));

      onLoginSuccess(data.user, data.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
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
            {isRegister
              ? 'Create an account to manage your shop voice inventory'
              : 'Your shop speaks. Copilot understands.'}
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="auth-error-alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form">
          {isRegister && (
            <>
              <div className="auth-field">
                <label>Your Name</label>
                <div className="input-wrapper">
                  <Mail size={16} className="input-icon" />
                  <input
                    type="text"
                    required
                    placeholder="e.g. Sah"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
              </div>

              <div className="auth-field">
                <label>Shop Name</label>
                <div className="input-wrapper">
                  <Store size={16} className="input-icon" />
                  <input
                    type="text"
                    required
                    placeholder="e.g. Sah's Store"
                    value={shopName}
                    onChange={(e) => setShopName(e.target.value)}
                  />
                </div>
              </div>
            </>
          )}

          <div className="auth-field">
            <label>Email Address</label>
            <div className="input-wrapper">
              <Mail size={16} className="input-icon" />
              <input
                type="email"
                required
                placeholder="shopkeeper@example.com"
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
            ) : isRegister ? (
              <>
                <span>Create Account</span>
                <UserPlus size={18} />
              </>
            ) : (
              <>
                <span>Sign In</span>
                <LogIn size={18} />
              </>
            )}
          </button>
        </form>

        {/* Demo Login Button */}
        <div className="auth-divider">
          <span>or use demo store</span>
        </div>

        <button type="button" onClick={handleDemoLogin} disabled={loading} className="demo-login-btn">
          <span>Login to Sah's Store (Demo)</span>
          <ArrowRight size={16} />
        </button>

        {/* Toggle Mode */}
        <div className="auth-footer">
          {isRegister ? (
            <p>
              Already have a shop account?{' '}
              <button type="button" onClick={() => setIsRegister(false)} className="auth-toggle-link">
                Sign In
              </button>
            </p>
          ) : (
            <p>
              New shopkeeper?{' '}
              <button type="button" onClick={() => setIsRegister(true)} className="auth-toggle-link">
                Create Account
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
