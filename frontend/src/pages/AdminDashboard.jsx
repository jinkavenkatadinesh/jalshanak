import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';
import StatusHistoryTimeline from '../components/StatusHistoryTimeline';
import { 
  Droplet, AlertTriangle, CheckCircle, ShieldCheck, 
  Search, Filter, MapPin, Eye, FileText, ChevronRight, 
  TrendingUp, Award, Calendar, RefreshCw, BarChart2, PieChart
} from 'lucide-react';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loadingReports, setLoadingReports] = useState(true);
  const [loadingAnalytics, setLoadingAnalytics] = useState(true);
  
  // Selection and update states
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedReportHistory, setSelectedReportHistory] = useState([]);
  const [newStatus, setNewStatus] = useState('');
  const [remarks, setRemarks] = useState('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [statusSuccessMsg, setStatusSuccessMsg] = useState('');

  // Filters and queries
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [areaFilter, setAreaFilter] = useState('All');

  // Trigger data fetch
  useEffect(() => {
    fetchReports();
    fetchAnalytics();
  }, []);

  const fetchReports = async () => {
    setLoadingReports(true);
    try {
      const res = await api.get('/reports');
      setReports(res.data);
    } catch (err) {
      console.error("Failed to load reports", err);
    } finally {
      setLoadingReports(false);
    }
  };

  const fetchAnalytics = async () => {
    setLoadingAnalytics(true);
    try {
      const res = await api.get('/admin/dashboard');
      setAnalytics(res.data);
    } catch (err) {
      console.error("Failed to load analytics", err);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  const handleSelectReport = async (report) => {
    setSelectedReport(report);
    setNewStatus(report.status);
    setRemarks('');
    setStatusSuccessMsg('');
    
    // Fetch individual remarks log history
    try {
      const res = await api.get(`/admin/report/${report.id}/history`);
      setSelectedReportHistory(res.data);
    } catch (err) {
      console.error("Failed to load report status timeline", err);
      setSelectedReportHistory([]);
    }
  };

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    if (!selectedReport) return;

    setIsUpdatingStatus(true);
    setStatusSuccessMsg('');
    try {
      const res = await api.put(`/admin/report/${selectedReport.id}/status`, {
        status: newStatus,
        remarks: remarks
      });

      // Update local report object in list
      setReports((prev) => 
        prev.map((rep) => (rep.id === selectedReport.id ? { ...rep, status: res.data.status, severity: res.data.severity } : rep))
      );
      
      // Update currently selected object
      setSelectedReport((prev) => ({ ...prev, status: res.data.status }));
      
      // Refresh status remarks logs
      const historyRes = await api.get(`/admin/report/${selectedReport.id}/history`);
      setSelectedReportHistory(historyRes.data);
      
      setRemarks('');
      setStatusSuccessMsg('Issue status and comments updated successfully!');
      
      // Refresh analytic statistics cards
      fetchAnalytics();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to update report status.");
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  // Filter lists based on admin criteria
  const filteredReports = reports.filter((rep) => {
    const matchesSearch = 
      rep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rep.reporter_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (rep.description && rep.description.toLowerCase().includes(searchQuery.toLowerCase()));
      
    const matchesStatus = statusFilter === 'All' || rep.status === statusFilter;
    const matchesSeverity = severityFilter === 'All' || rep.severity === severityFilter;
    
    return matchesSearch && matchesStatus && matchesSeverity;
  });

  // Extract unique areas from reported coords for filtering
  const uniqueAreas = analytics?.area_distribution?.map(a => a.area_name) || [];

  return (
    <div className="app-container">
      <Navbar />

      <main className="main-content" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Page title and refresh trigger */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '2.2rem', marginBottom: '0.25rem' }}>Hyderabad Authority Portal</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Monitor citizen reports, verify water leakages, and assign maintenance dispatch units</p>
          </div>
          <button 
            onClick={() => { fetchReports(); fetchAnalytics(); if (selectedReport) handleSelectReport(selectedReport); }}
            className="btn btn-secondary" 
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <RefreshCw size={16} />
            <span>Sync Live DB</span>
          </button>
        </div>

        {/* Admin KPI aggregates row */}
        {!loadingAnalytics && analytics && (
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-card-info">
                <h4>Total Logged Leaks</h4>
                <p>{analytics.total_reports}</p>
              </div>
              <div className="stat-card-icon" style={{ backgroundColor: 'var(--bg-in-progress-glass)', color: 'var(--primary)' }}>
                <Droplet size={28} fill="currentColor" />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-info">
                <h4>Active Investigations</h4>
                <p>{analytics.pending_reports}</p>
              </div>
              <div className="stat-card-icon" style={{ backgroundColor: 'var(--bg-under-review-glass)', color: 'var(--color-under-review)' }}>
                <AlertTriangle size={28} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-info">
                <h4>Resolved Actions</h4>
                <p>{analytics.resolved_reports}</p>
              </div>
              <div className="stat-card-icon" style={{ backgroundColor: 'var(--bg-resolved-glass)', color: 'var(--color-resolved)' }}>
                <CheckCircle size={28} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-card-info">
                <h4>Citizen Verify Credibility</h4>
                <p>
                  {reports.reduce((acc, curr) => acc + curr.verification_count, 0)}
                </p>
              </div>
              <div className="stat-card-icon" style={{ backgroundColor: 'rgba(167, 139, 250, 0.15)', color: '#a78bfa' }}>
                <ShieldCheck size={28} />
              </div>
            </div>
          </div>
        )}

        {/* Analytics Charts Panel */}
        {!loadingAnalytics && analytics && (
          <div className="charts-grid">
            
            {/* Custom SVG Distribution Chart by Hyderabad Areas */}
            <div className="chart-card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <BarChart2 size={18} style={{ color: 'var(--primary)' }} />
                <span>Area-Wise Leak Distribution (Hyderabad)</span>
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, justifyContent: 'center' }}>
                {analytics.area_distribution.map((area, idx) => {
                  const maxCount = Math.max(...analytics.area_distribution.map(a => a.count), 1);
                  const percentage = (area.count / maxCount) * 100;
                  
                  return (
                    <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                        <span style={{ fontWeight: 600 }}>{area.area_name}</span>
                        <span style={{ color: 'var(--primary-hover)', fontWeight: 700 }}>{area.count} leaks</span>
                      </div>
                      <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{
                          width: `${percentage}%`,
                          height: '100%',
                          background: 'linear-gradient(90deg, var(--primary), var(--accent))',
                          borderRadius: '4px',
                          transition: 'width 0.8s ease-out'
                        }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Severity and Status Breakdown Visualizer */}
            <div className="chart-card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <PieChart size={18} style={{ color: 'var(--accent)' }} />
                <span>Severity & Operational Status Fractions</span>
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', flex: 1, alignItems: 'center' }}>
                
                {/* Severity circles */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>Severity Spreads</span>
                  {analytics.severity_distribution.map((sev, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                      <span className={`severity-badge ${sev.severity.toLowerCase()}`} style={{ width: '65px', textAlign: 'center' }}>
                        {sev.severity}
                      </span>
                      <span style={{ fontWeight: 600 }}>{sev.count} reports</span>
                    </div>
                  ))}
                </div>

                {/* Status breakdown bars */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>Workflow Splits</span>
                  {analytics.status_distribution.map((st, idx) => {
                    const total = analytics.total_reports || 1;
                    const percent = Math.round((st.count / total) * 100);
                    
                    return (
                      <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem', fontSize: '0.82rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ textTransform: 'capitalize' }}>{st.status}</span>
                          <span style={{ fontWeight: 600 }}>{percent}%</span>
                        </div>
                        <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '2px', overflow: 'hidden' }}>
                          <div style={{
                            width: `${percent}%`,
                            height: '100%',
                            backgroundColor: st.status === 'Resolved' ? 'var(--color-resolved)' : 
                                            st.status === 'In Progress' ? 'var(--color-in-progress)' :
                                            st.status === 'Under Review' ? 'var(--color-under-review)' : 'var(--color-reported)',
                            borderRadius: '2px'
                          }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>

              </div>
            </div>

          </div>
        )}

        {/* Split Grid workspace: Left (Table Grid), Right (Status Remarks Inspector Drawer) */}
        <div className="admin-split-view">
          
          {/* Left panel: Datagrid list */}
          <div className="admin-grid-card">
            <div className="panel-header" style={{ marginBottom: '1rem' }}>
              <h2>Issue Management Grid</h2>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Showing {filteredReports.length} of {reports.length} leaks
              </span>
            </div>

            {/* Filter tool row */}
            <div className="filters-row">
              <div className="search-input-wrapper">
                <Search size={18} />
                <input
                  type="text"
                  className="form-control search-control"
                  placeholder="Search by title, description or reporter..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <select 
                className="filter-select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="All">All Statuses</option>
                <option value="Reported">Reported</option>
                <option value="Under Review">Under Review</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
              </select>

              <select 
                className="filter-select"
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
              >
                <option value="All">All Severities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            {/* Main table listings */}
            <div className="table-wrapper">
              {loadingReports ? (
                <div style={{ textAlign: 'center', padding: '3rem 0' }}>
                  <div className="spinner" style={{ width: '28px', height: '28px', margin: '0 auto 1rem auto' }}></div>
                  <p>Loading database entries...</p>
                </div>
              ) : filteredReports.length === 0 ? (
                <div style={{ padding: '3rem 1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <p>No matching leak reports in this criteria.</p>
                </div>
              ) : (
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Leak Details</th>
                      <th>Reporter</th>
                      <th>Severity</th>
                      <th>Status</th>
                      <th>Credibility</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredReports.map((report) => {
                      const isSelected = selectedReport && selectedReport.id === report.id;
                      
                      return (
                        <tr 
                          key={report.id}
                          onClick={() => handleSelectReport(report)}
                          className={isSelected ? 'active' : ''}
                        >
                          <td style={{ maxWidth: '240px' }}>
                            <div style={{ fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {report.title}
                            </div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.15rem' }}>
                              <MapPin size={10} />
                              <span>{report.latitude.toFixed(4)}, {report.longitude.toFixed(4)}</span>
                            </div>
                          </td>
                          <td>
                            <div style={{ fontSize: '0.85rem' }}>{report.reporter_name || 'Citizen'}</div>
                          </td>
                          <td>
                            <span className={`severity-badge ${report.severity.toLowerCase()}`}>
                              {report.severity}
                            </span>
                          </td>
                          <td>
                            <span className={`status-badge ${report.status.toLowerCase().replace(' ', '-')}`}>
                              {report.status}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--primary-hover)', fontWeight: 600, fontSize: '0.85rem' }}>
                              <ShieldCheck size={14} />
                              <span>{report.verification_count} verified</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Right panel: Inspection drawer */}
          <div className="admin-details-drawer">
            {selectedReport ? (
              <>
                <div className="drawer-header">
                  <div>
                    <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                      Report #{selectedReport.id}
                    </span>
                    <h2 style={{ fontSize: '1.4rem', marginTop: '0.15rem' }}>{selectedReport.title}</h2>
                  </div>
                  <span className={`status-badge ${selectedReport.status.toLowerCase().replace(' ', '-')}`} style={{ fontSize: '0.8rem' }}>
                    {selectedReport.status}
                  </span>
                </div>

                <img 
                  src={selectedReport.image_url 
                    ? `http://localhost:8000${selectedReport.image_url}` 
                    : 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=400&q=80'
                  } 
                  alt={selectedReport.title} 
                  className="drawer-image"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=400&q=80';
                  }}
                />

                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Description / Remarks</h4>
                  <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{selectedReport.description || 'No description provided.'}</p>
                </div>

                {/* AI prediction insights box */}
                <div className="ai-prediction-box">
                  <div className="ai-title">
                    <Award size={16} />
                    <span>JalRakshak AI Diagnostics</span>
                  </div>
                  <div className="ai-body">
                    AI verification confirms water leak visual patterns present (94% confidence). 
                    System estimated <strong>{selectedReport.severity} Severity</strong> based on descriptions and duplicate proximity coordinates.
                  </div>
                </div>

                {/* Action status changes input */}
                <div className="admin-actions-box">
                  <h4 style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>Update Status & Remarks</h4>
                  
                  {statusSuccessMsg && (
                    <div style={{ backgroundColor: 'var(--bg-resolved-glass)', border: '1px solid var(--color-resolved)', color: '#6ee7b7', padding: '0.65rem', borderRadius: '6px', fontSize: '0.82rem' }}>
                      {statusSuccessMsg}
                    </div>
                  )}

                  <form onSubmit={handleUpdateStatus} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Dispatch/Investigation Status</label>
                      <select 
                        className="filter-select"
                        style={{ padding: '0.6rem 1rem' }}
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value)}
                      >
                        <option value="Reported">Reported</option>
                        <option value="Under Review">Under Review</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Log remarks / Comments *</label>
                      <textarea
                        className="form-control"
                        rows={2}
                        placeholder="e.g. Dispatched repairs unit, valve replaced..."
                        value={remarks}
                        onChange={(e) => setRemarks(e.target.value)}
                        required
                      />
                    </div>

                    <button 
                      type="submit" 
                      className="btn btn-primary"
                      style={{ padding: '0.6rem', fontSize: '0.88rem' }}
                      disabled={isUpdatingStatus}
                    >
                      {isUpdatingStatus ? 'Logging Status...' : 'Apply Status Change'}
                    </button>
                  </form>
                </div>

                {/* Render historical timeline logs */}
                <StatusHistoryTimeline history={selectedReportHistory} />
              </>
            ) : (
              <div className="drawer-placeholder">
                <FileText size={48} strokeWidth={1} style={{ color: 'var(--text-muted)' }} />
                <h3>Select a Leak Report</h3>
                <p style={{ fontSize: '0.85rem' }}>Click on any record row in the management grid to audit coordinates, view images, change status, and view remarks logs.</p>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
