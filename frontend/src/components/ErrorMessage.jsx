import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorMessage({ message, onRetry }) {
  if (!message) return null;

  return (
    <div className="alert alert-error" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <AlertCircle size={18} />
        <span>{message}</span>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-ghost btn-sm" style={{ color: 'inherit', padding: '0.2rem 0.5rem' }}>
          <RefreshCw size={14} />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
}
