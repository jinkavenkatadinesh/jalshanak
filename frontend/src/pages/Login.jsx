import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Droplet, LogIn, AlertTriangle, Key } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Find redirect point if any
  const from = location.state?.from?.pathname || '/dashboard';
  const wasSessionExpired = new URLSearchParams(location.search).get('expired') === 'true';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setLocalError('Please fill in all credential fields.');
      return;
    }

    setIsSubmitting(true);
    setLocalError('');
    try {
      const loggedUser = await login(email, password);
      // Admin goes to admin panel, citizen goes to citizen dashboard
      if (loggedUser.role === 'admin') {
        navigate('/admin');
      } else {
        navigate(from === '/admin' ? '/dashboard' : from);
      }
    } catch (err) {
      setLocalError(err.message || 'Incorrect email or password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Demo account quick login helpers
  const handleQuickLogin = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            backgroundColor: 'var(--bg-in-progress-glass)',
            color: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid var(--border-glass)'
          }}>
            <Droplet size={32} fill="currentColor" />
          </div>
        </div>

        <h2>JalRakshak Sign In</h2>
        <p className="auth-subtitle">Smart Water Leak Reporting Hub - Telangana division</p>

        {wasSessionExpired && (
          <div className="auth-error" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid var(--color-under-review)', color: '#fef08a' }}>
            <Key size={18} />
            <span>Session expired. Please re-authenticate.</span>
          </div>
        )}

        {localError && (
          <div className="auth-error">
            <AlertTriangle size={18} />
            <span>{localError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Official / Personal Email</label>
            <input
              type="email"
              id="email"
              className="form-control"
              placeholder="e.g. shanker@gmail.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              className="form-control"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1.5rem' }}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                <span>Signing In...</span>
              </>
            ) : (
              <>
                <LogIn size={18} />
                <span>Access Portal</span>
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <span>New to JalRakshak? </span>
          <Link to="/register" style={{ fontWeight: 600 }}>Create an account</Link>
        </div>

        {/* Dynamic Demo Seed Badges Section */}
        <div style={{
          marginTop: '2.5rem',
          paddingTop: '1.5rem',
          borderTop: '1px dashed rgba(255, 255, 255, 0.08)'
        }}>
          <span style={{
            display: 'block',
            fontSize: '0.72rem',
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            fontWeight: 700,
            letterSpacing: '0.05em',
            marginBottom: '0.75rem',
            textAlign: 'center'
          }}>
            Quick Login (Demo Accounts)
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <button
              onClick={() => handleQuickLogin('shanker@gmail.com', 'citizen123')}
              className="btn btn-secondary"
              style={{ padding: '0.5rem', fontSize: '0.78rem', display: 'flex', flexDirection: 'column', gap: '0.15rem' }}
            >
              <span style={{ color: 'var(--primary)' }}>Citizen Account</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>shanker@gmail.com</span>
            </button>
            <button
              onClick={() => handleQuickLogin('admin@jalrakshak.org', 'admin123')}
              className="btn btn-secondary"
              style={{ padding: '0.5rem', fontSize: '0.78rem', display: 'flex', flexDirection: 'column', gap: '0.15rem' }}
            >
              <span style={{ color: '#a78bfa' }}>Authority Admin</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>admin@jalrakshak.org</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
