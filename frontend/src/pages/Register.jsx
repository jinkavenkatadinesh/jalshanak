import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Droplet, UserPlus, AlertTriangle, CheckCircle2 } from 'lucide-react';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('citizen'); // 'citizen' or 'admin'
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setLocalError('Please complete all form fields.');
      return;
    }
    if (password.length < 6) {
      setLocalError('Password must be at least 6 characters long.');
      return;
    }

    setIsSubmitting(true);
    setLocalError('');
    try {
      await register(name, email, password, role);
      setIsSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err) {
      setLocalError(err.message || 'Registration failed.');
    } finally {
      setIsSubmitting(false);
    }
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

        <h2>Create Account</h2>
        <p className="auth-subtitle">Join JalRakshak CivicTech Portal - Telangana division</p>

        {isSuccess ? (
          <div style={{
            backgroundColor: 'var(--bg-resolved-glass)',
            border: '1px solid var(--color-resolved)',
            color: '#a7f3d0',
            padding: '1.5rem',
            borderRadius: '12px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <CheckCircle2 size={42} />
            <div style={{ fontWeight: 600 }}>Registration Successful!</div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Redirecting you to the secure login gateway...</p>
          </div>
        ) : (
          <>
            {localError && (
              <div className="auth-error">
                <AlertTriangle size={18} />
                <span>{localError}</span>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  className="form-control"
                  placeholder="e.g. Jaishankar Prasad"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
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
                <label htmlFor="password">Create Password (min. 6 characters)</label>
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

              {/* Dynamic toggle selector for development roles */}
              <div className="form-group">
                <label>Select User Role Profile</label>
                <div className="role-selector-group">
                  <div 
                    className={`role-option ${role === 'citizen' ? 'selected' : ''}`}
                    onClick={() => setRole('citizen')}
                  >
                    Citizen Reporter
                  </div>
                  <div 
                    className={`role-option ${role === 'admin' ? 'selected' : ''}`}
                    onClick={() => setRole('admin')}
                  >
                    HMWS&SB Admin
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '1rem' }}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <UserPlus size={18} />
                    <span>Register User</span>
                  </>
                )}
              </button>
            </form>

            <div className="auth-footer">
              <span>Already registered? </span>
              <Link to="/login" style={{ fontWeight: 600 }}>Login here</Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Register;
