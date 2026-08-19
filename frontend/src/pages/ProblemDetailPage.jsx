import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Play, CheckCircle2, Clock, Zap, BarChart2, FileText, AlertCircle, ArrowLeft, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import CodeEditor from '../components/CodeEditor';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Skeleton from '../components/Skeleton';

const DEFAULT_PYTHON_STARTER = `# Read input from standard input and print output to standard output.
import sys

def main():
    # Example: line = sys.stdin.read().strip()
    pass

if __name__ == '__main__':
    main()
`;

export default function ProblemDetailPage() {
  const { id } = useParams();
  const problemId = Number(id);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [problem, setProblem] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [sourceCode, setSourceCode] = useState(DEFAULT_PYTHON_STARTER);
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  const fetchProblemData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [probData, testCaseData, statData] = await Promise.all([
        api.getProblemById(problemId),
        api.getProblemTestCases(problemId).catch(() => []),
        api.getProblemStats(problemId).catch(() => null),
      ]);

      setProblem(probData);
      setTestCases(testCaseData || []);
      setStats(statData);
    } catch (err) {
      setError(err.message || 'Failed to load problem details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProblemData();
  }, [problemId]);

  const handleSubmit = async () => {
    if (submitting) return;

    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/problems/${problemId}` } } });
      return;
    }

    if (!sourceCode.trim()) {
      setSubmitError('Source code cannot be empty.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitError(null);
      setSubmissionResult(null);

      const result = await api.createSubmission(problemId, sourceCode, 'python');
      setSubmissionResult(result);

      api.getProblemStats(problemId).then(setStats).catch(() => {});
    } catch (err) {
      setSubmitError(err.message || 'Submission failed. Please check your code and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem 0' }}>
        <LoadingSpinner message="Loading problem statement and editor..." />
      </div>
    );
  }

  if (error || !problem) {
    return (
      <div style={{ maxWidth: '600px', margin: '3rem auto' }}>
        <ErrorMessage message={error || 'Problem not found.'} onRetry={fetchProblemData} />
        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <Link to="/problems" className="btn btn-secondary">
            <ArrowLeft size={16} />
            <span>Back to Problems</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <Link to="/problems" className="btn btn-ghost btn-sm" style={{ paddingLeft: 0 }}>
          <ArrowLeft size={16} />
          <span>Back to Problems</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className={`diff-badge diff-${problem.difficulty}`}>
            {problem.difficulty}
          </span>
          {stats && (
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Acceptance: <strong>{stats.acceptance_rate}%</strong> ({stats.accepted_submissions}/{stats.total_submissions})
            </span>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(360px, 1.2fr)', gap: '1.5rem', alignItems: 'start' }}>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="card">
            <h1 style={{ fontSize: '1.5rem', marginBottom: '0.75rem' }}>
              #{problem.problem_id}. {problem.title}
            </h1>

            <div style={{ fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', marginBottom: '1.25rem' }}>
              {problem.description}
            </div>

            {problem.constraints && (
              <div style={{ marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                  Constraints
                </h3>
                <pre className="code-block" style={{ fontSize: '0.85rem' }}>{problem.constraints}</pre>
              </div>
            )}

            {(problem.input_format || problem.output_format) && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                {problem.input_format && (
                  <div>
                    <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                      Input Format
                    </h3>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{problem.input_format}</div>
                  </div>
                )}
                {problem.output_format && (
                  <div>
                    <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                      Output Format
                    </h3>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{problem.output_format}</div>
                  </div>
                )}
              </div>
            )}

            {testCases.filter(tc => !tc.is_hidden).length > 0 && (
              <div>
                <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.6rem' }}>
                  Sample Test Cases
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {testCases
                    .filter(tc => !tc.is_hidden)
                    .map((tc, idx) => (
                      <div key={tc.test_case_id} style={{ background: 'var(--bg-tertiary)', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                          Example {idx + 1}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Input:</span>
                            <pre className="code-block" style={{ padding: '0.35rem 0.5rem', marginTop: '0.2rem' }}>{tc.input_data || '—'}</pre>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Expected Output:</span>
                            <pre className="code-block" style={{ padding: '0.35rem 0.5rem', marginTop: '0.2rem' }}>{tc.expected_output || '—'}</pre>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>

          {stats && (
            <div className="card">
              <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                Problem Submissions Breakdown
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: '0.5rem', textAlign: 'center' }}>
                <div style={{ padding: '0.5rem', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>Total</span>
                  <strong style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>{stats.total_submissions}</strong>
                </div>
                <div style={{ padding: '0.5rem', background: 'var(--status-accepted-bg)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--status-accepted)', display: 'block' }}>Accepted</span>
                  <strong style={{ fontSize: '1.1rem', color: 'var(--status-accepted)' }}>{stats.accepted_submissions}</strong>
                </div>
                <div style={{ padding: '0.5rem', background: 'var(--status-wrong-bg)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--status-wrong)', display: 'block' }}>Wrong</span>
                  <strong style={{ fontSize: '1.1rem', color: 'var(--status-wrong)' }}>{stats.wrong_answers}</strong>
                </div>
                <div style={{ padding: '0.5rem', background: 'var(--status-runtime-bg)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--status-runtime)', display: 'block' }}>Error</span>
                  <strong style={{ fontSize: '1.1rem', color: 'var(--status-runtime)' }}>{stats.runtime_errors}</strong>
                </div>
              </div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', position: 'sticky', top: '75px' }}>
          <div className="card" style={{ padding: '0', overflow: 'hidden' }}>

            <div style={{ padding: '0.6rem 1rem', background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Language:</span>
                <span className="diff-badge" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}>
                  Python 3
                </span>
              </div>

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="btn btn-primary btn-sm"
                style={{ padding: '0.4rem 0.9rem' }}
              >
                <Zap size={14} />
                <span>
                  {submitting ? 'Submitting & Judging...' : 'Submit Solution'}
                </span>
              </button>
            </div>

            <div style={{ padding: '0' }}>
              <CodeEditor
                value={sourceCode}
                onChange={setSourceCode}
                language="python"
                height="460px"
              />
            </div>
          </div>

          <ErrorMessage message={submitError} />

          {submissionResult && (
            <div className="card" style={{ borderLeft: `4px solid ${submissionResult.status === 'ACCEPTED' ? 'var(--status-accepted)' : 'var(--status-wrong)'}` }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <StatusBadge status={submissionResult.status} />
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Submission #{submissionResult.submission_id}
                  </span>
                </div>
                <Link to={`/submissions/${submissionResult.submission_id}`} className="btn btn-ghost btn-sm" style={{ fontSize: '0.75rem' }}>
                  <span>View Details</span>
                  <ExternalLink size={12} />
                </Link>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', padding: '0.75rem', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Runtime</span>
                  <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {submissionResult.execution_time != null ? `${submissionResult.execution_time.toFixed(3)}s` : '—'}
                  </strong>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Memory</span>
                  <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {submissionResult.memory_used != null ? `${submissionResult.memory_used} KB` : '—'}
                  </strong>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
