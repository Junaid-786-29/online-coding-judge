import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock, Zap, FileCode, ShieldAlert, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import CodeEditor from '../components/CodeEditor';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function SubmissionDetailPage() {
  const { id } = useParams();
  const submissionId = Number(id);

  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusCode, setStatusCode] = useState(null);

  const fetchSubmission = async () => {
    try {
      setLoading(true);
      setError(null);
      setStatusCode(null);
      const data = await api.getSubmissionById(submissionId);
      setSubmission(data);
    } catch (err) {
      setStatusCode(err.status);
      if (err.status === 403) {
        setError('You do not have permission to view this submission.');
      } else if (err.status === 404) {
        setError('Submission not found.');
      } else {
        setError(err.message || 'Failed to load submission details.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmission();
  }, [submissionId]);

  if (loading) {
    return (
      <div style={{ maxWidth: '800px', margin: '3rem auto' }}>
        <LoadingSpinner message="Loading submission details..." />
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div style={{ maxWidth: '600px', margin: '3rem auto' }}>
        <div className="card" style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
          {statusCode === 403 ? (
            <ShieldAlert size={40} style={{ color: 'var(--status-wrong)', marginBottom: '0.75rem' }} />
          ) : (
            <AlertCircle size={40} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem' }} />
          )}
          <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
            {statusCode === 403 ? 'Access Denied' : 'Submission Not Found'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>{error}</p>
          <Link to="/submissions" className="btn btn-secondary">
            <ArrowLeft size={16} />
            <span>Back to Submissions</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <Link to="/submissions" className="btn btn-ghost btn-sm" style={{ paddingLeft: 0 }}>
          <ArrowLeft size={16} />
          <span>Back to Submissions</span>
        </Link>
        <Link to={`/problems/${submission.problem_id}`} className="btn btn-secondary btn-sm">
          <span>View Problem #{submission.problem_id}</span>
        </Link>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h1 style={{ fontSize: '1.4rem', marginBottom: '0.2rem' }}>
              Submission #{submission.submission_id}
            </h1>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Submitted for <Link to={`/problems/${submission.problem_id}`} style={{ color: 'var(--accent-primary)', fontWeight: 500 }}>Problem #{submission.problem_id}</Link>
            </span>
          </div>

          <StatusBadge status={submission.status} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Language</span>
            <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)', textTransform: 'capitalize' }}>
              {submission.language}
            </strong>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Execution Time</span>
            <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
              {submission.execution_time != null ? `${submission.execution_time.toFixed(3)}s` : '—'}
            </strong>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Memory Used</span>
            <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
              {submission.memory_used != null ? `${submission.memory_used} KB` : '—'}
            </strong>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileCode size={16} style={{ color: 'var(--accent-primary)' }} />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Submitted Source Code (Read-Only)
          </span>
        </div>

        <CodeEditor
          value={submission.source_code}
          language={submission.language || 'python'}
          readOnly={true}
          height="400px"
        />
      </div>
    </div>
  );
}
