import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Filter, Code, ArrowRight, Clock, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import Pagination from '../components/Pagination';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import EmptyState from '../components/EmptyState';
import Skeleton from '../components/Skeleton';

export default function SubmissionsPage() {
  const [data, setData] = useState({ items: [], page: 1, page_size: 10, total: 0, total_pages: 0, has_next: false, has_previous: false });
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [problemIdFilter, setProblemIdFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getMySubmissions({
        page,
        pageSize: 10,
        status: statusFilter || null,
        problemId: problemIdFilter ? Number(problemIdFilter) : null,
      });
      setData(res || { items: [], page: 1, page_size: 10, total: 0, total_pages: 0, has_next: false, has_previous: false });
    } catch (err) {
      setError(err.message || 'Failed to load submissions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions();
  }, [page, statusFilter, problemIdFilter]);

  const handleFilterChange = (newStatus) => {
    setStatusFilter(newStatus);
    setPage(1);
  };

  const handleProblemFilterChange = (e) => {
    setProblemIdFilter(e.target.value);
    setPage(1);
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>My Submissions</h1>
          <p>Track your submitted solutions and verdicts.</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <input
            type="number"
            className="form-input"
            placeholder="Problem ID"
            value={problemIdFilter}
            onChange={handleProblemFilterChange}
            style={{ width: '120px' }}
            min="1"
          />

          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => handleFilterChange(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">All Statuses</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="WRONG_ANSWER">Wrong Answer</option>
            <option value="RUNTIME_ERROR">Runtime Error</option>
            <option value="TIME_LIMIT_EXCEEDED">Time Limit Exceeded</option>
          </select>
        </div>
      </div>

      <ErrorMessage message={error} onRetry={fetchSubmissions} />

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className="card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                <Skeleton width="40px" height="20px" />
                <Skeleton width="120px" height="20px" />
                <Skeleton width="90px" height="20px" />
              </div>
              <Skeleton width="70px" height="24px" />
            </div>
          ))}
        </div>
      )}

      {!loading && !error && data.items.length > 0 && (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: '70px' }}>#</th>
                <th>Problem ID</th>
                <th>Language</th>
                <th>Status</th>
                <th>Runtime</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((sub) => (
                <tr key={sub.submission_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    #{sub.submission_id}
                  </td>
                  <td>
                    <Link to={`/problems/${sub.problem_id}`} className="nav-link" style={{ fontWeight: 600 }}>
                      Problem #{sub.problem_id}
                    </Link>
                  </td>
                  <td>
                    <span style={{ textTransform: 'capitalize', fontSize: '0.85rem' }}>{sub.language}</span>
                  </td>
                  <td>
                    <StatusBadge status={sub.status} />
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                    {sub.execution_time != null ? `${sub.execution_time.toFixed(3)}s` : '—'}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <Link to={`/submissions/${sub.submission_id}`} className="btn btn-secondary btn-sm">
                      <span>Details</span>
                      <ArrowRight size={14} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && data.items.length === 0 && (
        <EmptyState
          title="No submissions found"
          message={
            statusFilter || problemIdFilter
              ? 'No submissions match your active filter criteria.'
              : 'You have not made any code submissions yet.'
          }
          action={
            <Link to="/problems" className="btn btn-primary btn-sm">
              Solve a Problem
            </Link>
          }
        />
      )}

      {!loading && !error && (
        <Pagination
          page={data.page}
          totalPages={data.total_pages}
          hasNext={data.has_next}
          hasPrevious={data.has_previous}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
