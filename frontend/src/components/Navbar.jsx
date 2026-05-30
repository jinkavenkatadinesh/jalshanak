import React from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Droplet, LayoutDashboard, LogOut, LogIn, UserPlus, ClipboardList } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <Droplet size={26} strokeWidth={2.5} fill="currentColor" />
          <span>JalRakshak</span>
        </Link>

        <div className="navbar-links">
          {user ? (
            <>
              {user.role === 'admin' ? (
                <>
                  <NavLink to="/admin" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    <LayoutDashboard size={18} />
                    <span>Admin Dashboard</span>
                  </NavLink>
                </>
              ) : (
                <>
                  <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    <LayoutDashboard size={18} />
                    <span>Citizen Dashboard</span>
                  </NavLink>
                </>
              )}

              <div className="nav-user-badge">
                <span className={`role-tag ${user.role}`}>
                  {user.role}
                </span>
                <span style={{ fontWeight: 600 }}>{user.name}</span>
              </div>

              <button onClick={handleLogout} className="btn-logout" title="Log Out">
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">
                <LogIn size={18} />
                <span>Login</span>
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '0.4rem 1rem', fontSize: '0.9rem' }}>
                <UserPlus size={16} />
                <span>Sign Up</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
