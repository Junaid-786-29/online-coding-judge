import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, XCircle, AlertTriangle, Clock, Percent, Code2, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Skeleton from '../components/Skeleton';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statsData, subData] = await Promise.all([
        api.getMyStats(),
        api.getMySubmissions({ page: 1, pageSize: 5 }).catch(() => ({ items: [] })),
      ]);
      setStats(statsData);
      setRecentSubmissions(subData?.items || []);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>

      <div style={{ marginBottom: '2rem' }}>
        <h1>Welcome, {user?.username || 'Developer'}</h1>
        <p>Here is an overview of your coding performance and submission statistics.</p>
      </div>

      <ErrorMessage message={error} onRetry={fetchDashboardData} />

      {loading && (
        <div>
          <div className="stat-grid">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div key={n} className="card" style={{ height: '90px' }}>
                <Skeleton width="60%" height="16px" style={{ marginBottom: '0.75rem' }} />
                <Skeleton width="40%" height="28px" />
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && stats && (
        <div className="stat-grid">
          <StatCard
            title="Total Submissions"
            value={stats.total_submissions}
            icon={Code2}
          />
          <StatCard
            title="Accepted"
            value={stats.accepted}
            icon={CheckCircle2}
            color="var(--status-accepted)"
          />
          <StatCard
            title="Wrong Answers"
            value={stats.wrong_answer}
            icon={XCircle}
            color="var(--status-wrong)"
          />
          <StatCard
            title="Runtime Errors"
            value={stats.runtime_error}
            icon={AlertTriangle}
            color="var(--status-runtime)"
          />
          <StatCard
            title="Time Limit Exceeded"
            value={stats.time_limit_exceeded}
            icon={Clock}
            color="var(--status-timeout)"
          />
          <StatCard
            title="Acceptance Rate"
            value={`${stats.acceptance_rate}%`}
            icon={Percent}
            color="var(--accent-primary)"
          />
        </div>
      )}

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.15rem' }}>Recent Submissions</h2>
          <Link to="/submissions" className="btn btn-ghost btn-sm">
            <span>View All</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {recentSubmissions.length > 0 ? (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Problem</th>
                  <th>Language</th>
                  <th>Status</th>
                  <th>Runtime</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentSubmissions.map((sub) => (
                  <tr key={sub.submission_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      #{sub.submission_id}
                    </td>
                    <td>
                      <Link to={`/problems/${sub.problem_id}`} className="nav-link" style={{ fontWeight: 600 }}>
                        Problem #{sub.problem_id}
                      </Link>
                    </td>
                    <td style={{ textTransform: 'capitalize' }}>{sub.language}</td>
                    <td>
                      <StatusBadge status={sub.status} />
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {sub.execution_time != null ? `${sub.execution_time.toFixed(3)}s` : '—'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/submissions/${sub.submission_id}`} className="btn btn-ghost btn-sm">
                        <span>Details</span>
                        <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
            <p style={{ marginBottom: '1rem' }}>No recent submissions.</p>
            <Link to="/problems" className="btn btn-primary btn-sm">
              Start Solving Problems
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
