import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Code2, Sun, Moon, LogOut, User as UserIcon, Menu, X, Terminal } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="navbar">
      <div className="navbar-container">

        <Link to="/" className="navbar-brand">
          <Code2 className="navbar-logo-icon" size={22} />
          <span>CodeJudge</span>
        </Link>

        <nav className="navbar-nav">
          <NavLink to="/problems" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Problems
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/submissions" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                Submissions
              </NavLink>
              <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                Dashboard
              </NavLink>
            </>
          )}
        </nav>

        <div className="navbar-actions">
          <button
            onClick={toggleTheme}
            className="btn btn-ghost btn-icon"
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle Theme"
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Link to="/dashboard" className="btn btn-ghost btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <UserIcon size={16} />
                <span>{user?.username || 'Profile'}</span>
              </Link>
              <button onClick={handleLogout} className="btn btn-secondary btn-sm" title="Log out">
                <LogOut size={15} />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Link to="/login" className="btn btn-ghost btn-sm">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Register
              </Link>
            </div>
          )}

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="btn btn-ghost btn-icon"
            style={{ display: 'none' }}
            aria-label="Toggle Mobile Navigation"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
    </header>
  );
}
