import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Calendar, User, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// Custom DivIcon creator to avoid broken asset path packaging in React Vite
const createCustomIcon = (status) => {
  let color = '#ef4444'; // Red for Reported
  if (status === 'Under Review') color = '#f59e0b'; // Amber for Under Review
  if (status === 'In Progress') color = '#0ea5e9'; // Blue for In Progress
  if (status === 'Resolved') color = '#10b981'; // Green for Resolved

  return L.divIcon({
    html: `<div class="marker-pulse" style="
      background-color: ${color};
      width: 16px;
      height: 16px;
      border-radius: 50%;
      border: 2.5px solid #ffffff;
      box-shadow: 0 0 10px ${color};
      cursor: pointer;
    "></div>`,
    className: 'custom-leaflet-icon',
    iconSize: [16, 16],
    iconAnchor: [8, 8],
    popupAnchor: [0, -12],
  });
};

// Map recenterer module utilizing useMap hook
const ChangeMapView = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, 15, { animate: true, duration: 1 });
    }
  }, [center, map]);
  return null;
};

const MapView = ({ reports, centerPoint, onVerify, selectedReportId }) => {
  const { user } = useAuth();
  
  // Default coordinates centered on Hyderabad, Telangana
  const DEFAULT_HYDERABAD_CENTER = [17.3850, 78.4867];
  
  const mapCenter = centerPoint && centerPoint[0] ? centerPoint : DEFAULT_HYDERABAD_CENTER;

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '350px', position: 'relative' }}>
      <MapContainer 
        center={mapCenter} 
        zoom={12} 
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
      >
        {/* Modern styled Map tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <ChangeMapView center={centerPoint} />
        
        {reports.map((report) => {
          if (!report.latitude || !report.longitude) return null;
          
          const isSelected = report.id === selectedReportId;
          const imageSrc = report.image_url 
            ? `http://localhost:8000${report.image_url}` 
            : 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=400&q=80'; // fallback high-quality water image

          return (
            <Marker 
              key={report.id} 
              position={[report.latitude, report.longitude]}
              icon={createCustomIcon(report.status)}
            >
              <Popup>
                <div className="map-popup-card">
                  <img 
                    src={imageSrc} 
                    alt={report.title} 
                    className="popup-image" 
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=400&q=80';
                    }}
                  />
                  
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <span className={`status-badge ${report.status.toLowerCase().replace(' ', '-')}`}>
                        {report.status}
                      </span>
                      <span className={`severity-badge ${report.severity.toLowerCase()}`}>
                        {report.severity} Priority
                      </span>
                    </div>
                    <h3 className="popup-title">{report.title}</h3>
                  </div>

                  <p className="popup-desc">{report.description}</p>
                  
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <User size={12} />
                      <span>By: {report.reporter_name || 'Citizen'}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Calendar size={12} />
                      <span>{new Date(report.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="popup-footer">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#38bdf8', fontSize: '0.8rem', fontWeight: 600 }}>
                      <ShieldCheck size={14} />
                      <span>{report.verification_count} Verifications</span>
                    </div>

                    {/* Enable verification trigger inside Popup overlay for Citizens */}
                    {user && user.role === 'citizen' && user.id !== report.user_id && report.status !== 'Resolved' && (
                      <button 
                        onClick={() => onVerify && onVerify(report.id)}
                        className="btn btn-accent"
                        style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', borderRadius: '4px' }}
                      >
                        Verify
                      </button>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
      
      {/* Visual Floating Map Legend for Status Indicators */}
      <div style={{
        position: 'absolute',
        bottom: '15px',
        left: '15px',
        zIndex: 1000,
        backgroundColor: 'rgba(19, 27, 46, 0.85)',
        border: '1px solid rgba(56, 189, 248, 0.2)',
        borderRadius: '8px',
        padding: '0.75rem',
        backdropFilter: 'blur(8px)',
        fontSize: '0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.4rem',
        boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
      }}>
        <div style={{ fontWeight: 700, textTransform: 'uppercase', color: '#94a3b8', fontSize: '0.7rem', marginBottom: '0.15rem' }}>Map Legend</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444', display: 'inline-block' }}></span>
          <span>Reported</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#f59e0b', display: 'inline-block' }}></span>
          <span>Under Review</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#0ea5e9', display: 'inline-block' }}></span>
          <span>In Progress</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981', display: 'inline-block' }}></span>
          <span>Resolved</span>
        </div>
      </div>
    </div>
  );
};

export default MapView;
