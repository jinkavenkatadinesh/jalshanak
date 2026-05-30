import React from 'react';
import { Calendar, User, Clock, ArrowRight } from 'lucide-react';

const StatusHistoryTimeline = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div className="drawer-placeholder" style={{ padding: '2rem 0', minHeight: 'auto' }}>
        <p>No status history logs recorded yet.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="timeline-title">Maintenance Status History</h3>
      <div className="timeline-container">
        {history.map((log) => {
          const formattedDate = new Date(log.changed_at).toLocaleString(undefined, {
            dateStyle: 'medium',
            timeStyle: 'short',
          });

          return (
            <div key={log.id} className="timeline-item">
              {/* Dot colored according to transition status */}
              <div className={`timeline-dot ${log.new_status.toLowerCase().replace(' ', '-')}`}></div>
              
              <div className="timeline-meta">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <User size={12} />
                  <span style={{ fontWeight: 600 }}>{log.changed_by_name || 'Administrator'}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <Clock size={12} />
                  <span>{formattedDate}</span>
                </div>
              </div>

              <div className="timeline-content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', fontWeight: 600, marginBottom: '0.25rem' }}>
                  <span className={`status-badge ${log.old_status.toLowerCase().replace(' ', '-')}`}>
                    {log.old_status}
                  </span>
                  <ArrowRight size={14} style={{ color: '#64748b' }} />
                  <span className={`status-badge ${log.new_status.toLowerCase().replace(' ', '-')}`}>
                    {log.new_status}
                  </span>
                </div>
                
                {log.remarks ? (
                  <div className="timeline-remarks">
                    "{log.remarks}"
                  </div>
                ) : (
                  <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic' }}>
                    No remarks provided for this status change.
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StatusHistoryTimeline;
