import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyState({ title = 'No records found', message = 'There is nothing to display right now.', icon: Icon = Inbox, action }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '3rem 1.5rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)', border: '1px dashed var(--border-color)', margin: '1rem 0' }}>
      <Icon size={36} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem' }} />
      <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{title}</h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '400px', marginBottom: action ? '1rem' : 0 }}>{message}</p>
      {action}
    </div>
  );
}
