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
      console.log('Magic link debug info:', {
        apiUrl,
        email: magicLinkEmail,
        fullUrl: `${apiUrl}/auth/magic-link-request`
      });
      
      const response = await axios.post(`${apiUrl}/auth/magic-link-request`, {
        email: magicLinkEmail
      });
      
      console.log('Magic link response:', response.data);
      setMagicLinkMessage('If an account with that email exists, a login link has been sent to your email.');
      setMagicLinkEmail('');
      showSuccessMessage('Magic link request sent successfully!');
    } catch (err) {
      console.error('Magic link request error:', err);
      console.error('Error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        url: err.config?.url
      });
      setError(err.response?.data?.msg || 'An error occurred. Please try again.');
      showErrorMessage(err.response?.data?.msg || 'Failed to send magic link');
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
    <div className="min-vh-100 d-flex align-items-center" style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Pattern */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3Ccircle cx='37' cy='37' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        opacity: 0.3
      }} />
      
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-12 col-sm-10 col-md-8 col-lg-6 col-xl-5">
            <div className="card border-0 shadow-lg" style={{
              borderRadius: '20px',
              backdropFilter: 'blur(10px)',
              background: 'rgba(255, 255, 255, 0.95)'
            }}>
              <div className="card-body p-4 p-md-5">
                {/* Header */}
                <div className="text-center mb-4">
                  <div className="mb-3">
                    <div className="d-inline-flex align-items-center justify-content-center rounded-circle bg-primary text-white" style={{
                      width: '80px',
                      height: '80px',
                      fontSize: '2rem'
                    }}>
                      <i className="bi bi-music-note-beamed"></i>
                    </div>
                  </div>
                  <h1 className="h3 fw-bold text-dark mb-2">
                    {showPasswordReset ? 'Reset Password' : 
                     showMagicLink ? 'Magic Link Login' : 'Welcome to BandSync'}
                  </h1>
                  <p className="text-muted mb-0">
                    {showPasswordReset ? 'Enter your email to reset your password' : 
                     showMagicLink ? 'Get a secure login link sent to your email' : 
                     'Sign in to manage your band activities'}
                  </p>
                </div>
              
                {showMagicLink ? (
                  <form onSubmit={handleMagicLinkRequest}>
                    <div className="mb-4">
                      <label className="form-label fw-semibold text-dark">Email Address</label>
                      <div className="input-group">
                        <span className="input-group-text bg-light border-end-0">
                          <i className="bi bi-envelope text-muted"></i>
                        </span>
                        <input 
                          type="email"
                          className="form-control border-start-0 bg-light" 
                          value={magicLinkEmail} 
                          onChange={e => setMagicLinkEmail(e.target.value)} 
                          required 
                          disabled={magicLinkLoading}
                          placeholder="Enter your email address"
                          style={{ 
                            borderRadius: '0 10px 10px 0',
                            fontSize: '1rem',
                            padding: '12px 16px'
                          }}
                        />
                      </div>
                      <div className="form-text text-muted mt-2">
                        <i className="bi bi-info-circle me-1"></i>
                        We'll send a secure login link to this email address
                      </div>
                    </div>
                    
                    {error && (
                      <div className="alert alert-danger border-0 rounded-3 mb-4" style={{
                        background: 'linear-gradient(135deg, #ff6b6b, #ee5a5a)',
                        color: 'white'
                      }}>
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        {error}
                      </div>
                    )}
                    
                    {magicLinkMessage && (
                      <div className="alert alert-success border-0 rounded-3 mb-4" style={{
                        background: 'linear-gradient(135deg, #51cf66, #40c057)',
                        color: 'white'
                      }}>
                        <i className="bi bi-check-circle me-2"></i>
                        {magicLinkMessage}
                      </div>
                    )}
                    
                    <div className="d-grid gap-3">
                      <button 
                        className="btn btn-primary btn-lg fw-semibold" 
                        type="submit" 
                        disabled={magicLinkLoading}
                        style={{
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, #667eea, #764ba2)',
                          border: 'none',
                          padding: '12px',
                          fontSize: '1.1rem'
                        }}
                      >
                        {magicLinkLoading ? (
                          <>
                            <LoadingSpinner size="sm" /> Sending...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-send me-2"></i>
                            Send Magic Link
                          </>
                        )}
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary btn-lg" 
                        onClick={handleBackToLogin}
                        disabled={magicLinkLoading}
                        style={{
                          borderRadius: '12px',
                          padding: '12px'
                        }}
                      >
                        <i className="bi bi-arrow-left me-2"></i>
                        Back to Login
                      </button>
                    </div>
                  </form>
                ) : showPasswordReset ? (
                  <form onSubmit={handlePasswordReset}>
                    <div className="mb-4">
                      <label className="form-label fw-semibold text-dark">Email Address</label>
                      <div className="input-group">
                        <span className="input-group-text bg-light border-end-0">
                          <i className="bi bi-envelope text-muted"></i>
                        </span>
                        <input 
                          type="email"
                          className="form-control border-start-0 bg-light" 
                          value={resetEmail} 
                          onChange={e => setResetEmail(e.target.value)} 
                          required 
                          disabled={resetLoading}
                          placeholder="Enter your email address"
                          style={{ 
                            borderRadius: '0 10px 10px 0',
                            fontSize: '1rem',
                            padding: '12px 16px'
                          }}
                        />
                      </div>
                      <div className="form-text text-muted mt-2">
                        <i className="bi bi-info-circle me-1"></i>
                        We'll send a password reset link to this email address
                      </div>
                    </div>
                    
                    {error && (
                      <div className="alert alert-danger border-0 rounded-3 mb-4" style={{
                        background: 'linear-gradient(135deg, #ff6b6b, #ee5a5a)',
                        color: 'white'
                      }}>
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        {error}
                      </div>
                    )}
                    
                    {resetMessage && (
                      <div className="alert alert-success border-0 rounded-3 mb-4" style={{
                        background: 'linear-gradient(135deg, #51cf66, #40c057)',
                        color: 'white'
                      }}>
                        <i className="bi bi-check-circle me-2"></i>
                        {resetMessage}
                      </div>
                    )}
                    
                    <div className="d-grid gap-3">
                      <button 
                        className="btn btn-primary btn-lg fw-semibold" 
                        type="submit" 
                        disabled={resetLoading}
                        style={{
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, #667eea, #764ba2)',
                          border: 'none',
                          padding: '12px',
                          fontSize: '1.1rem'
                        }}
                      >
                        {resetLoading ? (
                          <>
                            <LoadingSpinner size="sm" /> Sending...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-key me-2"></i>
                            Send Reset Link
                          </>
                        )}
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary btn-lg" 
                        onClick={handleBackToLogin}
                        disabled={resetLoading}
                        style={{
                          borderRadius: '12px',
                          padding: '12px'
                        }}
                      >
                        <i className="bi bi-arrow-left me-2"></i>
                        Back to Login
                      </button>
                    </div>
                  </form>
                ) : !multipleOrgs ? (
                  <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                      <label className="form-label fw-semibold text-dark">Username or Email</label>
                      <div className="input-group">
                        <span className="input-group-text bg-light border-end-0">
                          <i className="bi bi-person text-muted"></i>
                        </span>
                        <input 
                          className="form-control border-start-0 bg-light" 
                          value={identifier} 
                          onChange={e => setIdentifier(e.target.value)} 
                          required 
                          disabled={loading}
                          placeholder="Enter username or email"
                          style={{ 
                            borderRadius: '0 10px 10px 0',
                            fontSize: '1rem',
                            padding: '12px 16px'
                          }}
                        />
                      </div>
                      <div className="form-text text-muted mt-2">
                        <i className="bi bi-info-circle me-1"></i>
                        You can use either your username or email address
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="form-label fw-semibold text-dark">Password</label>
                      <div className="input-group">
                        <span className="input-group-text bg-light border-end-0">
                          <i className="bi bi-lock text-muted"></i>
                        </span>
                        <input 
                          type="password" 
                          className="form-control border-start-0 bg-light" 
                          value={password} 
                          onChange={e => setPassword(e.target.value)} 
                          required 
                          disabled={loading}
                          placeholder="Enter your password"
                          style={{ 
                            borderRadius: '0 10px 10px 0',
                            fontSize: '1rem',
                            padding: '12px 16px'
                          }}
                        />
                      </div>
                    </div>
                    
                    {error && (
                      <div className="alert alert-danger border-0 rounded-3 mb-4" style={{
                        background: 'linear-gradient(135deg, #ff6b6b, #ee5a5a)',
                        color: 'white'
                      }}>
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        {error}
                      </div>
                    )}
                    
                    <div className="d-grid mb-4">
                      <button 
                        className="btn btn-primary btn-lg fw-semibold" 
                        type="submit" 
                        disabled={loading}
                        style={{
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, #667eea, #764ba2)',
                          border: 'none',
                          padding: '12px',
                          fontSize: '1.1rem'
                        }}
                      >
                        {loading ? (
                          <>
                            <LoadingSpinner size="sm" /> Signing in...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-box-arrow-in-right me-2"></i>
                            Sign In
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                ) : (
                  <div>
                    <div className="alert alert-info border-0 rounded-3 mb-4" style={{
                      background: 'linear-gradient(135deg, #74c0fc, #339af0)',
                      color: 'white'
                    }}>
                      <i className="bi bi-buildings me-2"></i>
                      You belong to multiple organizations. Please select which one to access:
                    </div>
                    <form onSubmit={handleSubmit}>
                      <div className="mb-4">
                        <label className="form-label fw-semibold text-dark">Select Organization</label>
                        <div className="input-group">
                          <span className="input-group-text bg-light border-end-0">
                            <i className="bi bi-building text-muted"></i>
                          </span>
                          <select 
                            className="form-select border-start-0 bg-light" 
                            value={selectedOrgId} 
                            onChange={e => setSelectedOrgId(e.target.value)}
                            required
                            disabled={loading}
                            style={{ 
                              borderRadius: '0 10px 10px 0',
                              fontSize: '1rem',
                              padding: '12px 16px'
                            }}
                          >
                            <option value="">Choose an organization...</option>
                            {multipleOrgs.map(org => (
                              <option key={org.id} value={org.id}>
                                {org.name} ({org.role})
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      {error && (
                        <div className="alert alert-danger border-0 rounded-3 mb-4" style={{
                          background: 'linear-gradient(135deg, #ff6b6b, #ee5a5a)',
                          color: 'white'
                        }}>
                          <i className="bi bi-exclamation-triangle me-2"></i>
                          {error}
                        </div>
                      )}
                      
                      <div className="d-grid gap-3">
                        <button 
                          className="btn btn-primary btn-lg fw-semibold" 
                          type="submit" 
                          disabled={loading || !selectedOrgId}
                          style={{
                            borderRadius: '12px',
                            background: 'linear-gradient(135deg, #667eea, #764ba2)',
                            border: 'none',
                            padding: '12px',
                            fontSize: '1.1rem'
                          }}
                        >
                          {loading ? (
                            <>
                              <LoadingSpinner size="sm" /> Continuing...
                            </>
                          ) : (
                            <>
                              <i className="bi bi-arrow-right me-2"></i>
                              Continue
                            </>
                          )}
                        </button>
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary btn-lg" 
                          onClick={handleBackToLogin}
                          disabled={loading}
                          style={{
                            borderRadius: '12px',
                            padding: '12px'
                          }}
                        >
                          <i className="bi bi-arrow-left me-2"></i>
                          Back to Login
                        </button>
                      </div>
                    </form>
                  </div>
                )}
                
                {/* Footer Links */}
                <div className="text-center mt-4 pt-4 border-top">
                  <div className="mb-3">
                    <span className="text-muted">Don't have an account? </span>
                    <a href="/register" className="text-decoration-none fw-semibold" style={{
                      color: '#667eea'
                    }}>
                      Create Account
                    </a>
                  </div>
                  
                  {!showPasswordReset && !showMagicLink && (
                    <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center align-items-center">
                      <button 
                        type="button" 
                        className="btn btn-link p-0 text-decoration-none fw-semibold" 
                        onClick={handleShowPasswordReset}
                        style={{ color: '#667eea' }}
                      >
                        <i className="bi bi-key me-1"></i>
                        Forgot Password?
                      </button>
                      <span className="text-muted d-none d-sm-inline">•</span>
                      <button 
                        type="button" 
                        className="btn btn-link p-0 text-decoration-none fw-semibold" 
                        onClick={handleShowMagicLink}
                        style={{ color: '#667eea' }}
                      >
                        <i className="bi bi-envelope-heart me-1"></i>
                        Email Login Link
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Footer */}
            <div className="text-center mt-4">
              <p className="text-white-50 mb-0">
                <i className="bi bi-shield-check me-1"></i>
                Secure • Reliable • Easy to Use
              </p>
            </div>
          </div>
        </div>
      </div>
      <NotificationSystem />
    </div>
  );
}

export default LoginPage;
