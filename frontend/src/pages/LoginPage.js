import React, { useState } from 'react';
import NotificationSystem from '../components/NotificationSystem';
import { 
  LoadingSpinner, 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { 
  ResponsiveStatsGrid, 
  ResponsiveActionBar,
  ResponsiveCardGrid 
} from '../components/ResponsiveComponents';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrl';

function LoginPage() {
  const [identifier, setIdentifier] = useState(''); // Can be username or email
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [multipleOrgs, setMultipleOrgs] = useState(null);
  const [selectedOrgId, setSelectedOrgId] = useState('');
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [showMagicLink, setShowMagicLink] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [magicLinkEmail, setMagicLinkEmail] = useState('');
  const [resetMessage, setResetMessage] = useState('');
  const [magicLinkMessage, setMagicLinkMessage] = useState('');
  const [resetLoading, setResetLoading] = useState(false);
  const [magicLinkLoading, setMagicLinkLoading] = useState(false);

  // Enhanced notification functions
  const showSuccessMessage = (message) => {
    if (window.showSuccess) window.showSuccess(message);
  };

  const showErrorMessage = (message) => {
    if (window.showError) window.showError(message);
  };

  const showInfoMessage = (message) => {
    if (window.showInfo) window.showInfo(message);
  };

  const showWarningMessage = (message) => {
    if (window.showWarning) window.showWarning(message);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Determine if identifier is email or username
      const isEmail = identifier.includes('@');
      const loginData = isEmail ? 
        { email: identifier, password } : 
        { username: identifier, password };
      
      if (selectedOrgId) {
        loginData.organization_id = parseInt(selectedOrgId);
      }
      
      const apiUrl = getApiUrl();
      const res = await axios.post(`${apiUrl}/auth/login`, loginData);
      
      // Check if user belongs to multiple organizations
      if (res.data.multiple_organizations && !selectedOrgId) {
        setMultipleOrgs(res.data.organizations);
        setLoading(false);
        return;
      }
      
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('refreshToken', res.data.refresh_token);
      localStorage.setItem('username', identifier); // Store the identifier used
      localStorage.setItem('role', res.data.role);
      localStorage.setItem('super_admin', res.data.super_admin ? 'true' : 'false');
      if (res.data.organization_id) localStorage.setItem('organization_id', res.data.organization_id);
      if (res.data.organization) localStorage.setItem('organization', res.data.organization);
      
      // Dispatch login event for session timeout component
      window.dispatchEvent(new CustomEvent('userLogin'));
      
      setLoading(false);
      
      // Check if user needs to change password (temporary password)
      if (res.data.requires_password_change) {
        window.location.href = '/change-password';
      } else {
        window.location.href = res.data.role === 'Admin' ? '/admin' : '/dashboard';
      }
    } catch (err) {
      console.error('Login error:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      setError(err.response?.data?.msg || 'Invalid credentials');
      setLoading(false);
      setMultipleOrgs(null);
      setSelectedOrgId('');
    }
  };

  const handleBackToLogin = () => {
    setShowPasswordReset(false);
    setShowMagicLink(false);
    setMultipleOrgs(null);
    setSelectedOrgId('');
    setError('');
    setResetMessage('');
    setMagicLinkMessage('');
    setResetEmail('');
    setMagicLinkEmail('');
  };

  const handleMagicLinkRequest = async (e) => {
    e.preventDefault();
    setMagicLinkLoading(true);
    setError('');
    setMagicLinkMessage('');
    
    try {
      const apiUrl = getApiUrl();
      await axios.post(`${apiUrl}/auth/magic-link-request`, {
        email: magicLinkEmail
      });
      
      setMagicLinkMessage('If an account with that email exists, a login link has been sent to your email.');
      setMagicLinkEmail('');
    } catch (err) {
      console.error('Magic link request error:', err);
      setError(err.response?.data?.msg || 'An error occurred. Please try again.');
    } finally {
      setMagicLinkLoading(false);
    }
  };

  const handleShowMagicLink = () => {
    setShowMagicLink(true);
    setShowPasswordReset(false);
    setError('');
    setResetMessage('');
    setMagicLinkMessage('');
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    setResetLoading(true);
    setError('');
    setResetMessage('');
    
    try {
      const apiUrl = getApiUrl();
      await axios.post(`${apiUrl}/auth/password-reset-request`, {
        email: resetEmail
      });
      
      setResetMessage('If an account with that email exists, a password reset link has been sent to your email.');
      setResetEmail('');
    } catch (err) {
      console.error('Password reset error:', err);
      setError(err.response?.data?.msg || 'An error occurred. Please try again.');
    } finally {
      setResetLoading(false);
    }
  };

  const handleShowPasswordReset = () => {
    setShowPasswordReset(true);
    setShowMagicLink(false);
    setError('');
    setResetMessage('');
    setMagicLinkMessage('');
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <h2 className="card-title text-center mb-4">
                <i className="bi bi-music-note me-2"></i>
                {showPasswordReset ? 'Reset Password' : 
                 showMagicLink ? 'Login with Email Link' : 'BandSync Login'}
              </h2>
              
              {showMagicLink ? (
                <form onSubmit={handleMagicLinkRequest}>
                  <div className="mb-3">
                    <label className="form-label">Email Address</label>
                    <input 
                      type="email"
                      className="form-control" 
                      value={magicLinkEmail} 
                      onChange={e => setMagicLinkEmail(e.target.value)} 
                      required 
                      disabled={magicLinkLoading}
                      placeholder="Enter your email address"
                    />
                    <div className="form-text">
                      We'll send a secure login link to this email address.
                    </div>
                  </div>
                  {error && <div className="alert alert-danger">{error}</div>}
                  {magicLinkMessage && <div className="alert alert-success">{magicLinkMessage}</div>}
                  <div className="d-grid gap-2">
                    <button className="btn btn-primary" type="submit" disabled={magicLinkLoading}>
                      {magicLinkLoading ? <LoadingSpinner size="sm" /> : 'Send Login Link'}
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary" 
                      onClick={handleBackToLogin}
                      disabled={magicLinkLoading}
                    >
                      Back to Login
                    </button>
                  </div>
                </form>
              ) : showPasswordReset ? (
                <form onSubmit={handlePasswordReset}>
                  <div className="mb-3">
                    <label className="form-label">Email Address</label>
                    <input 
                      type="email"
                      className="form-control" 
                      value={resetEmail} 
                      onChange={e => setResetEmail(e.target.value)} 
                      required 
                      disabled={resetLoading}
                      placeholder="Enter your email address"
                    />
                    <div className="form-text">
                      We'll send a password reset link to this email address.
                    </div>
                  </div>
                  {error && <div className="alert alert-danger">{error}</div>}
                  {resetMessage && <div className="alert alert-success">{resetMessage}</div>}
                  <div className="d-grid gap-2">
                    <button className="btn btn-primary" type="submit" disabled={resetLoading}>
                      {resetLoading ? <LoadingSpinner size="sm" /> : 'Send Reset Link'}
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary" 
                      onClick={handleBackToLogin}
                      disabled={resetLoading}
                    >
                      Back to Login
                    </button>
                  </div>
                </form>
              ) : !multipleOrgs ? (
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label className="form-label">Username or Email</label>
                    <input 
                      className="form-control" 
                      value={identifier} 
                      onChange={e => setIdentifier(e.target.value)} 
                      required 
                      disabled={loading}
                      placeholder="Enter username or email address"
                    />
                    <div className="form-text">
                      You can use either your username or email address to log in.
                    </div>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={password} 
                      onChange={e => setPassword(e.target.value)} 
                      required 
                      disabled={loading}
                    />
                  </div>
                  {error && <div className="alert alert-danger">{error}</div>}
                  <div className="d-grid">
                    <button className="btn btn-primary" type="submit" disabled={loading}>
                      {loading ? <LoadingSpinner size="sm" /> : 'Login'}
                    </button>
                  </div>
                </form>
              ) : (
                <div>
                  <div className="alert alert-info">
                    <i className="bi bi-info-circle me-2"></i>
                    You belong to multiple organizations. Please select which one to access:
                  </div>
                  <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                      <label className="form-label">Select Organization</label>
                      <select 
                        className="form-select" 
                        value={selectedOrgId} 
                        onChange={e => setSelectedOrgId(e.target.value)}
                        required
                        disabled={loading}
                      >
                        <option value="">Choose an organization...</option>
                        {multipleOrgs.map(org => (
                          <option key={org.id} value={org.id}>
                            {org.name} ({org.role})
                          </option>
                        ))}
                      </select>
                    </div>
                    {error && <div className="alert alert-danger">{error}</div>}
                    <div className="d-grid gap-2">
                      <button className="btn btn-primary" type="submit" disabled={loading || !selectedOrgId}>
                        {loading ? <LoadingSpinner size="sm" /> : 'Continue'}
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary" 
                        onClick={handleBackToLogin}
                        disabled={loading}
                      >
                        Back to Login
                      </button>
                    </div>
                  </form>
                </div>
              )}
              
              <div className="text-center mt-3">
                <p className="mb-0">No account? <a href="/register">Register</a></p>
                {!showPasswordReset && !showMagicLink && (
                  <div className="text-center">
                    <button 
                      type="button" 
                      className="btn btn-link p-0 text-decoration-none me-3" 
                      onClick={handleShowPasswordReset}
                    >
                      Forgot your password?
                    </button>
                    <span className="text-muted">|</span>
                    <button 
                      type="button" 
                      className="btn btn-link p-0 text-decoration-none ms-3" 
                      onClick={handleShowMagicLink}
                    >
                      Login with email link
                    </button>
                  </div>
                )}
              </div>
              
              {showPasswordReset && (
                <div className="mt-4">
                  <div className="alert alert-info">
                    <i className="bi bi-info-circle me-2"></i>
                    Enter your email to receive a password reset link.
                  </div>
                  <form onSubmit={handlePasswordReset}>
                    <div className="mb-3">
                      <label className="form-label">Email Address</label>
                      <input 
                        type="email" 
                        className="form-control" 
                        value={resetEmail} 
                        onChange={e => setResetEmail(e.target.value)} 
                        required 
                        disabled={resetLoading}
                        placeholder="Enter your email address"
                      />
                    </div>
                    {error && <div className="alert alert-danger">{error}</div>}
                    {resetMessage && <div className="alert alert-success">{resetMessage}</div>}
                    <div className="d-grid gap-2">
                      <button className="btn btn-primary" type="submit" disabled={resetLoading}>
                        {resetLoading ? <LoadingSpinner size="sm" /> : 'Send Reset Link'}
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary" 
                        onClick={handleBackToLogin}
                        disabled={resetLoading}
                      >
                        Back to Login
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <NotificationSystem />
    </div>
  );
}

export default LoginPage;
