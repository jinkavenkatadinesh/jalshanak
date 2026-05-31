import React, { useState, useEffect, useRef } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Droplet, LayoutDashboard, LogOut, LogIn, UserPlus, Bell } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);
  const dropdownRef = useRef(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  useEffect(() => {
    if (!user) return;

    fetchNotifications();

    // Poll for notifications every 20 seconds to keep updated
    const interval = setInterval(fetchNotifications, 20000);

    return () => clearInterval(interval);
  }, [user]);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowNotifDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error("Failed to load notifications", err);
    }
  };

  const handleNotificationClick = async (notif) => {
    if (notif.is_read === 0) {
      try {
        await api.put(`/notifications/${notif.id}/read`);
        // Update notification read state locally
        setNotifications(prev =>
          prev.map(n => n.id === notif.id ? { ...n, is_read: 1 } : n)
        );
      } catch (err) {
        console.error("Failed to mark notification as read", err);
      }
    }
  };

  const unreadCount = notifications.filter(n => n.is_read === 0).length;

  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHrs = Math.floor(diffMins / 60);
      if (diffHrs < 24) return `${diffHrs}h ago`;
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch (e) {
      return '';
    }
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

              {/* Notification Bell Panel */}
              <div className="notification-bell-container" ref={dropdownRef}>
                <button
                  className="notification-bell-btn"
                  onClick={() => setShowNotifDropdown(!showNotifDropdown)}
                  title="Notifications"
                >
                  <Bell size={20} />
                  {unreadCount > 0 && (
                    <span className="notification-badge">{unreadCount}</span>
                  )}
                </button>

                {showNotifDropdown && (
                  <div className="notification-dropdown">
                    <div className="notification-header">
                      <span>Civic Alerts Notifications</span>
                      {unreadCount > 0 && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--primary-hover)', fontWeight: 600 }}>
                          {unreadCount} unread
                        </span>
                      )}
                    </div>
                    <div className="notification-list">
                      {notifications.length === 0 ? (
                        <div className="notification-empty">
                          No recent notifications
                        </div>
                      ) : (
                        notifications.map((notif) => (
                          <div
                            key={notif.id}
                            className={`notification-item ${notif.is_read === 0 ? 'unread' : ''}`}
                            onClick={() => handleNotificationClick(notif)}
                          >
                            <div className="notification-item-text">
                              {notif.message}
                            </div>
                            <div className="notification-item-time">
                              {formatTime(notif.created_at)}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

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
