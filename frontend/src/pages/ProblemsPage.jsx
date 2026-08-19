import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Code2, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import EmptyState from '../components/EmptyState';
import Skeleton from '../components/Skeleton';

export default function ProblemsPage() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('ALL');

  const fetchProblems = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProblems();
      setProblems(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load problems.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProblems();
  }, []);

  const filteredProblems = problems.filter((p) => {
    const matchesSearch =
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.problem_id.toString().includes(searchQuery) ||
      (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesDifficulty =
      selectedDifficulty === 'ALL' || p.difficulty.toLowerCase() === selectedDifficulty.toLowerCase();

    return matchesSearch && matchesDifficulty;
  });

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>Problems</h1>
          <p>Select a challenge to solve and test your algorithms.</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', minWidth: '220px' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="form-input"
              placeholder="Search problems..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '2rem' }}
            />
          </div>

          <select
            className="form-select"
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="ALL">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>
        </div>
      </div>

      <ErrorMessage message={error} onRetry={fetchProblems} />

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className="card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '60%' }}>
                <Skeleton width="30px" height="20px" />
                <Skeleton width="180px" height="20px" />
              </div>
              <Skeleton width="60px" height="24px" borderRadius="var(--radius-full)" />
            </div>
          ))}
        </div>
      )}

      {!loading && !error && filteredProblems.length > 0 && (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th style={{ width: '60px' }}>#</th>
                <th>Title</th>
                <th style={{ width: '120px' }}>Difficulty</th>
                <th style={{ width: '100px', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredProblems.map((p) => (
                <tr key={p.problem_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    #{p.problem_id}
                  </td>
                  <td>
                    <Link
                      to={`/problems/${p.problem_id}`}
                      style={{ fontWeight: 600, color: 'var(--text-primary)', display: 'inline-block' }}
                      className="nav-link"
                    >
                      {p.title}
                    </Link>
                    {p.description && (
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem', maxWidth: '600px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {p.description}
                      </p>
                    )}
                  </td>
                  <td>
                    <span className={`diff-badge diff-${p.difficulty}`}>
                      {p.difficulty}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <Link to={`/problems/${p.problem_id}`} className="btn btn-primary btn-sm">
                      <span>Solve</span>
                      <ArrowRight size={14} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && filteredProblems.length === 0 && (
        <EmptyState
          title="No problems found"
          message={
            searchQuery || selectedDifficulty !== 'ALL'
              ? 'Try adjusting your search query or difficulty filter.'
              : 'No coding problems are available at the moment.'
          }
        />
      )}
    </div>
  );
}
