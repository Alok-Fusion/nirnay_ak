import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const AppContent: React.FC = () => {
  const { user, loading, login, register, logout } = useAuth();
  const [isRegister, setIsRegister] = React.useState<boolean>(false);
  const [username, setUsername] = React.useState<string>('');
  const [email, setEmail] = React.useState<string>('');
  const [password, setPassword] = React.useState<string>('');
  const [mpin, setMpin] = React.useState<string>('');
  const [error, setError] = React.useState<string>('');
  const [submitting, setSubmitting] = React.useState<boolean>(false);

  if (loading) {
    return (
      <div className="app-loader-container">
        <div className="logo-spinner">
          <div className="spinner-inner">N</div>
        </div>
        <p>Initializing NIRNAY Decision Engines...</p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (isRegister) {
        if (mpin.length < 4 || mpin.length > 6 || !/^\d+$/.test(mpin)) {
          throw new Error('MPIN must be 4 to 6 numeric digits');
        }
        await register({ username, email, password, mpin });
      } else {
        await login({ username, password });
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="auth-wrapper">
        <div className="auth-card">
          <div className="auth-header">
            <h1 className="brand-title">NIRNAY</h1>
            <p className="brand-tagline">AI-Powered Financial Decision Intelligence Platform</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <h2 className="form-title">{isRegister ? 'Create Bank Account' : 'Secure Login'}</h2>
            
            {error && <div className="auth-error-alert">{error}</div>}

            <div className="input-group">
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter username"
              />
            </div>

            {isRegister && (
              <div className="input-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@bank.com"
                />
              </div>
            )}

            <div className="input-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </div>

            {isRegister && (
              <div className="input-group">
                <label>MPIN (4-6 digits for fast secure approval)</label>
                <input
                  type="password"
                  maxLength={6}
                  value={mpin}
                  onChange={(e) => setMpin(e.target.value)}
                  required
                  placeholder="1234"
                />
              </div>
            )}

            <button type="submit" disabled={submitting} className="auth-submit-btn">
              {submitting ? 'Authenticating...' : isRegister ? 'Register Account' : 'Authenticate & Enter'}
            </button>
          </form>

          <div className="auth-footer">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
              className="auth-switch-btn"
            >
              {isRegister ? 'Already have an account? Sign In' : 'New to NIRNAY? Open an Account'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-brand">
          <span className="brand-logo">N</span>
          <span className="brand-text">NIRNAY</span>
          <span className="badge-live">LIVE</span>
        </div>
        <div className="header-user">
          <span className="user-welcome">Welcome, <strong>{user.username}</strong></span>
          <span className="user-score" title="Your Transaction Security Health Score">
            Security Score: <strong>{user.security_score}%</strong>
          </span>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="placeholder-content">
          <h2>NIRNAY AI Decision Layer - Connected Successfully</h2>
          <p>This is the foundation template. Subsequent phases will populate this view with live Digital Twin tracking, real-time transaction scoring visualization, custom SVG analytics charts, and admin override controls.</p>
          <div className="dashboard-stats-row">
            <div className="stat-card">
              <h3>Balance</h3>
              <p className="stat-val">${user.balance.toLocaleString()}</p>
            </div>
            <div className="stat-card">
              <h3>Security Status</h3>
              <p className="stat-val status-safe">SECURE</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
