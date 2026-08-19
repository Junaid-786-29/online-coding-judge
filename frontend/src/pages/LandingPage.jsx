import React from 'react';
import { Link } from 'react-router-dom';
import { Terminal, CheckCircle2, Zap, BarChart2, ArrowRight } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div style={{ padding: '3rem 0' }}>

      <div style={{ textAlign: 'center', maxWidth: '780px', margin: '0 auto 3.5rem auto' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-full)', background: 'var(--accent-subtle)', color: 'var(--accent-primary)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '1.25rem' }}>
          <Zap size={14} />
          <span>Fast, Isolated Python Execution</span>
        </div>

        <h1 style={{ fontSize: '2.75rem', lineHeight: '1.15', fontWeight: 800, marginBottom: '1rem', letterSpacing: '-0.025em' }}>
          Practice. Submit. Improve.
        </h1>

        <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', lineHeight: '1.6', marginBottom: '2rem' }}>
          An online coding judge where you can solve programming problems, submit Python solutions, and instantly evaluate your code against automated test cases.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/problems" className="btn btn-primary btn-lg" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>Explore Problems</span>
            <ArrowRight size={18} />
          </Link>
          <Link to={isAuthenticated ? '/submissions' : '/login'} className="btn btn-secondary btn-lg">
            <span>View Submissions</span>
          </Link>
        </div>
      </div>

      <div style={{ maxWidth: '740px', margin: '0 auto 4rem auto' }}>
        <div className="card" style={{ padding: '0', overflow: 'hidden', boxShadow: 'var(--shadow-md)' }}>
          <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Terminal size={16} style={{ color: 'var(--accent-primary)' }} />
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Live Evaluation Preview</span>
            </div>
            <StatusBadge status="ACCEPTED" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', divideX: '1px solid var(--border-color)' }}>

            <div style={{ padding: '1.25rem', borderRight: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                Standard Input
              </div>
              <pre className="code-block" style={{ marginBottom: '1rem', padding: '0.5rem' }}>5</pre>

              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                Submitted Python Code
              </div>
              <pre className="code-block" style={{ padding: '0.5rem', color: 'var(--accent-primary)' }}>
                {`n = int(input())\nprint(n * 2)`}
              </pre>
            </div>

            <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                  Execution Output
                </div>
                <pre className="code-block" style={{ marginBottom: '1rem', padding: '0.5rem' }}>10</pre>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Runtime</span>
                  <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>0.02s</strong>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Verdict</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--status-accepted)' }}>Accepted (All Passed)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', maxWidth: '1000px', margin: '0 auto' }}>
        <div className="card">
          <Zap size={22} style={{ color: 'var(--accent-primary)', marginBottom: '0.75rem' }} />
          <h3 style={{ marginBottom: '0.4rem' }}>Instant Evaluation</h3>
          <p style={{ fontSize: '0.875rem' }}>Submissions are executed inside isolated sandboxed processes with real-time feedback.</p>
        </div>

        <div className="card">
          <Terminal size={22} style={{ color: 'var(--accent-primary)', marginBottom: '0.75rem' }} />
          <h3 style={{ marginBottom: '0.4rem' }}>Modern Monaco Editor</h3>
          <p style={{ fontSize: '0.875rem' }}>Write Python code in a full-featured VS Code-powered editor with syntax highlighting.</p>
        </div>

        <div className="card">
          <BarChart2 size={22} style={{ color: 'var(--accent-primary)', marginBottom: '0.75rem' }} />
          <h3 style={{ marginBottom: '0.4rem' }}>Detailed Statistics</h3>
          <p style={{ fontSize: '0.875rem' }}>Track acceptance rates, execution times, and filter submission history with ease.</p>
        </div>
      </div>
    </div>
  );
}
