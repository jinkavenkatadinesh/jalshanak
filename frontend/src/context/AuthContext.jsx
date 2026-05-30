import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Validate active token at initialization
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('jalrakshak_token');
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('jalrakshak_user', JSON.stringify(res.data));
        } catch (err) {
          console.error("Session verification failed", err);
          logout();
        }
      }
      setLoading(false);
    };
    initializeAuth();
  }, []);

  const login = async (email, password) => {
    setError(null);
    try {
      const res = await api.post('/auth/login', { email, password });
      const { access_token } = res.data;
      
      localStorage.setItem('jalrakshak_token', access_token);
      
      // Fetch user profile info immediately after token storage
      const userRes = await api.get('/auth/me');
      setUser(userRes.data);
      localStorage.setItem('jalrakshak_user', JSON.stringify(userRes.data));
      
      return userRes.data;
    } catch (err) {
      const errMsg = err.response?.data?.detail || "Invalid credentials. Please try again.";
      setError(errMsg);
      throw new Error(errMsg);
    }
  };

  const register = async (name, email, password, role = "citizen") => {
    setError(null);
    try {
      const res = await api.post('/auth/register', { name, email, password, role });
      return res.data;
    } catch (err) {
      const errMsg = err.response?.data?.detail || "Registration failed. Try using another email.";
      setError(errMsg);
      throw new Error(errMsg);
    }
  };

  const logout = () => {
    localStorage.removeItem('jalrakshak_token');
    localStorage.removeItem('jalrakshak_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
