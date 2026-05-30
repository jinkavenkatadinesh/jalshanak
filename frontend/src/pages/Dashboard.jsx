import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';
import MapView from '../components/MapView';
import ReportModal from '../components/ReportModal';
import { Droplet, AlertTriangle, ShieldCheck, MapPin, ClipboardList, PlusCircle, CheckCircle, Search, Filter } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Map and UI state controllers
  const [mapCenter, setMapCenter] = useState([17.3850, 78.4867]);
  const [selectedReportId, setSelectedReportId] = useState(null);
  const [filterMode, setFilterMode] = useState('all'); // 'all', 'mine'
  const [searchQuery, setSearchQuery] = useState('');
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [successToast, setSuccessToast] = useState('');

  // Fetch reports on mount
  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await api.get('/reports');
      setReports(res.data);
    } catch (err) {
      console.error(err);
      setError('Could not retrieve water leak reports from server.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (reportId) => {
    try {
      const res = await api.post(`/reports/${reportId}/verify`);
      
      // Update local state instantly with new verification metrics
      setReports((prev) => 
        prev.map((rep) => (rep.id === reportId ? res.data : rep))
      );
      
      triggerToast('Leak verification registered successfully! Credibility increased.');
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || 'Failed to register verification.';
      triggerToast(errMsg, true);
    }
  };

  const handleReportSubmitted = (newReport) => {
    // Prepend new report to list
    setReports((prev) => [newReport, ...prev]);
    
    // Auto center map on new report coordinates
    setMapCenter([newReport.latitude, newReport.longitude]);
    setSelectedReportId(newReport.id);
    
    triggerToast('Water leak successfully logged! AI scanning complete.');
  };

  const triggerToast = (msg, isErr = false) => {
    setSuccessToast(isErr ? `⚠️ ${msg}` : `✅ ${msg}`);
    setTimeout(() => {
      setSuccessToast('');
    }, 4000);
  };

  const selectReport = (report) => {
    setSelectedReportId(report.id);
    setMapCenter([report.latitude, report.longitude]);
  };

  // Filter and search reports
  const filteredReports = reports.filter((rep) => {
    const matchesFilter = filterMode === 'all' || rep.user_id === user.id;
    const matchesSearch = 
      rep.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (rep.description && rep.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  // Calculate statistics
  const totalReported = reports.length;
  const activeCount = reports.filter((r) => r.status !== 'Resolved').length;
  const resolvedCount = reports.filter((r) => r.status === 'Resolved').length;
  const userReportsCount = reports.filter((r) => r.user_id === user.id).length;

  return (
    <div className="app-container">
      <Navbar />
      
      <main className="main-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', flex: 1 }}>
        
        {/* Floating notifications panel */}
        {successToast && (
          <div style={{
            position: 'fixed',
            top: '80px',
            right: '20px',
            backgroundColor: successToast.startsWith('⚠️') ? 'var(--bg-reported-glass)' : 'var(--bg-resolved-glass)',
            border: `1px solid ${successToast.startsWith('⚠️') ? 'var(--color-reported)' : 'var(--color-resolved)'}`,
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            zIndex: 3000,
            color: '#fff',
            fontWeight: 600,
            backdropFilter: 'blur(8px)',
            boxShadow: 'var(--shadow-lg)',
            animation: 'slideDown 0.25s ease-out'
          }}>
            {successToast}
          </div>
        )}

        {/* Citizen KPI Highlights */}
        <div className="stats-row" style={{ marginBottom: 0 }}>
          <div className="stat-card">
            <div className="stat-card-info">
              <h4>Total Leaks Reported</h4>
              <p>{totalReported}</p>
            </div>
            <div className="stat-card-icon" style={{ backgroundColor: 'var(--bg-in-progress-glass)', color: 'var(--primary)' }}>
              <Droplet size={28} fill="currentColor" />
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-info">
              <h4>Active Unresolved</h4>
              <p>{activeCount}</p>
            </div>
            <div className="stat-card-icon" style={{ backgroundColor: 'var(--bg-reported-glass)', color: 'var(--color-reported)' }}>
              <AlertTriangle size={28} />
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-info">
              <h4>Resolved Tasks</h4>
              <p>{resolvedCount}</p>
            </div>
            <div className="stat-card-icon" style={{ backgroundColor: 'var(--bg-resolved-glass)', color: 'var(--color-resolved)' }}>
              <CheckCircle size={28} />
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-info">
              <h4>Your Logged Submissions</h4>
              <p>{userReportsCount}</p>
            </div>
            <div className="stat-card-icon" style={{ backgroundColor: 'rgba(167, 139, 250, 0.15)', color: '#a78bfa' }}>
              <ClipboardList size={28} />
            </div>
          </div>
        </div>

        {/* Dashboard workspace grid */}
        <div className="dashboard-grid">
          
          {/* Left panel: Filters, Search and Leak Reports cards list */}
          <div className="sidebar-panel">
            <div className="panel-header">
              <h2>Water Leak Reports</h2>
              <button 
                onClick={() => setIsReportModalOpen(true)}
                className="btn btn-primary"
                style={{ padding: '0.5rem 1rem', fontSize: '0.88rem' }}
              >
                <PlusCircle size={16} />
                <span>Report Leak</span>
              </button>
            </div>

            {/* Filters dashboard bar */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div className="search-input-wrapper">
                <Search size={18} />
                <input
                  type="text"
                  className="form-control search-control"
                  placeholder="Search leaks by area or title..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => setFilterMode('all')}
                  className={`btn ${filterMode === 'all' ? 'btn-accent' : 'btn-secondary'}`}
                  style={{ flex: 1, padding: '0.5rem', fontSize: '0.82rem' }}
                >
                  All Leakages
                </button>
                <button
                  onClick={() => setFilterMode('mine')}
                  className={`btn ${filterMode === 'mine' ? 'btn-accent' : 'btn-secondary'}`}
                  style={{ flex: 1, padding: '0.5rem', fontSize: '0.82rem' }}
                >
                  My Reports
                </button>
              </div>
            </div>

            {/* List entries */}
            <div className="reports-list-container">
              {loading ? (
                <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
                  <div className="spinner" style={{ width: '28px', height: '28px', margin: '0 auto 1rem auto' }}></div>
                  <p>Loading leak database...</p>
                </div>
              ) : filteredReports.length === 0 ? (
                <div style={{
                  padding: '3rem 1.5rem',
                  textAlign: 'center',
                  backgroundColor: 'var(--bg-secondary)',
                  borderRadius: '12px',
                  border: '1px dashed var(--border-glass)',
                  color: 'var(--text-secondary)'
                }}>
                  <ClipboardList size={40} strokeWidth={1} style={{ color: 'var(--text-muted)', marginBottom: '1rem' }} />
                  <p style={{ fontWeight: 600 }}>No leak reports found</p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    {searchQuery ? 'Adjust your search terms' : 'Be the first to log a leakage in this area!'}
                  </p>
                </div>
              ) : (
                filteredReports.map((report) => {
                  const isActive = report.id === selectedReportId;
                  const reportDate = new Date(report.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  });

                  return (
                    <div 
                      key={report.id} 
                      className={`leak-card ${isActive ? 'active' : ''}`}
                      onClick={() => selectReport(report)}
                    >
                      <div className="leak-card-header">
                        <span className="leak-card-title">{report.title}</span>
                        <span className={`status-badge ${report.status.toLowerCase().replace(' ', '-')}`}>
                          {report.status}
                        </span>
                      </div>
                      
                      <p className="leak-card-desc">{report.description}</p>
                      
                      <div className="leak-card-footer">
                        <div className="leak-card-meta">
                          <span className={`severity-badge ${report.severity.toLowerCase()}`} style={{ scale: '0.9', originX: 0 }}>
                            {report.severity}
                          </span>
                          <div className="meta-item">
                            <MapPin size={12} />
                            <span>{report.latitude.toFixed(3)}, {report.longitude.toFixed(3)}</span>
                          </div>
                        </div>
                        <div className="leak-card-meta">
                          <div className="meta-item" style={{ color: 'var(--primary-hover)', fontWeight: 600 }}>
                            <ShieldCheck size={14} />
                            <span>{report.verification_count}</span>
                          </div>
                          <span>{reportDate}</span>
                        </div>
                      </div>

                      {/* Display quick inline verify button on card */}
                      {user.id !== report.user_id && report.status !== 'Resolved' && (
                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.03)', paddingTop: '0.75rem' }}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleVerify(report.id);
                            }}
                            className="btn btn-accent"
                            style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem', borderRadius: '4px' }}
                          >
                            Confirm Active Leak
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right panel: Leaflet Map Container */}
          <div className="map-panel">
            <MapView 
              reports={filteredReports} 
              centerPoint={mapCenter} 
              onVerify={handleVerify}
              selectedReportId={selectedReportId}
            />
          </div>

        </div>
      </main>

      <ReportModal 
        isOpen={isReportModalOpen} 
        onClose={() => setIsReportModalOpen(false)}
        onReportSubmitted={handleReportSubmitted}
      />
    </div>
  );
};

export default Dashboard;
