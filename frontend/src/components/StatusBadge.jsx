import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Clock, Loader2, Hourglass } from 'lucide-react';

export default function StatusBadge({ status }) {
  const normalizedStatus = status ? status.toUpperCase() : 'PENDING';

  const getIcon = () => {
    switch (normalizedStatus) {
      case 'ACCEPTED':
        return <CheckCircle2 size={13} />;
      case 'WRONG_ANSWER':
        return <XCircle size={13} />;
      case 'RUNTIME_ERROR':
        return <AlertTriangle size={13} />;
      case 'TIME_LIMIT_EXCEEDED':
        return <Clock size={13} />;
      case 'RUNNING':
        return <Loader2 size={13} className="spin" />;
      case 'PENDING':
      default:
        return <Hourglass size={13} />;
    }
  };

  const getLabel = () => {
    switch (normalizedStatus) {
      case 'ACCEPTED':
        return 'Accepted';
      case 'WRONG_ANSWER':
        return 'Wrong Answer';
      case 'RUNTIME_ERROR':
        return 'Runtime Error';
      case 'TIME_LIMIT_EXCEEDED':
        return 'Time Limit Exceeded';
      case 'RUNNING':
        return 'Running';
      case 'PENDING':
      default:
        return 'Pending';
    }
  };

  return (
    <span className={`status-badge status-${normalizedStatus}`}>
      {getIcon()}
      <span>{getLabel()}</span>
    </span>
  );
}
