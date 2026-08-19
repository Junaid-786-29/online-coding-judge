import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color }) {
  return (
    <div className="stat-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span className="stat-title">{title}</span>
        {Icon && <Icon size={18} style={{ color: color || 'var(--text-muted)' }} />}
      </div>
      <div className="stat-value" style={{ color: color || 'var(--text-primary)' }}>
        {value}
      </div>
      {subtitle && (
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          {subtitle}
        </span>
      )}
    </div>
  );
}
