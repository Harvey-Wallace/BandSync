import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getApiUrl } from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import NotificationSystem from '../components/NotificationSystem';

function MagicLoginPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [multipleOrgs, setMultipleOrgs] = useState(null);
  const [selectedOrgId, setSelectedOrgId] = useState('');
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setError('Invalid login link. Missing token.');
      setLoading(false);
      return;
    }

    handleMagicLogin(token);
  }, [searchParams]);

  const handleMagicLogin = async (token) => {
    try {
      const apiUrl = getApiUrl();
      const res = await axios.post(`${apiUrl}/auth/magic-login`, { token });

      // Check if user belongs to multiple organizations
      if (res.data.multiple_organizations) {
        setMultipleOrgs(res.data.organizations);
        setUserId(res.data.user_id);
        setLoading(false);
        return;
      }

      // Single organization - complete login
      completeLogin(res.data);

    } catch (err) {
      console.error('Magic login error:', err);
      setError(err.response?.data?.msg || 'Invalid or expired login link.');
      setLoading(false);
    }
  };

  const handleOrgSelection = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const apiUrl = getApiUrl();
      // For magic login with org selection, we need a different approach
      // since the token is already consumed. We'll use a different endpoint.
      const res = await axios.post(`${apiUrl}/auth/magic-login-org`, {
        user_id: userId,
        organization_id: parseInt(selectedOrgId)
      });

      completeLogin(res.data);

    } catch (err) {
      console.error('Organization selection error:', err);
      setError(err.response?.data?.msg || 'Failed to complete login.');
      setLoading(false);
    }
  };

  const completeLogin = (loginData) => {
    localStorage.setItem('token', loginData.access_token);
    localStorage.setItem('refreshToken', loginData.refresh_token);
    localStorage.setItem('username', 'magic-login-user'); // We don't have username from magic login
    localStorage.setItem('role', loginData.role);
    localStorage.setItem('super_admin', loginData.super_admin ? 'true' : 'false');
    
    if (loginData.organization_id) localStorage.setItem('organization_id', loginData.organization_id);
    if (loginData.organization) localStorage.setItem('organization', loginData.organization);
    
    // Dispatch login event for session timeout component
    window.dispatchEvent(new CustomEvent('userLogin'));
    
    // Redirect to appropriate dashboard
    window.location.href = loginData.role === 'Admin' ? '/admin' : '/dashboard';
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-6">
            <div className="card shadow">
              <div className="card-body text-center">
                <h2 className="card-title mb-4">
                  <i className="bi bi-music-note me-2"></i>
                  Logging you in...
                </h2>
                <LoadingSpinner />
                <p className="mt-3 text-muted">Please wait while we verify your login link.</p>
              </div>
            </div>
          </div>
        </div>
        <NotificationSystem />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-6">
            <div className="card shadow">
              <div className="card-body">
                <h2 className="card-title text-center mb-4">
                  <i className="bi bi-exclamation-triangle text-danger me-2"></i>
                  Login Failed
                </h2>
                <div className="alert alert-danger">{error}</div>
                <div className="text-center">
                  <button 
                    className="btn btn-primary"
                    onClick={() => navigate('/login')}
                  >
                    Return to Login
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <NotificationSystem />
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <h2 className="card-title text-center mb-4">
                <i className="bi bi-music-note me-2"></i>
                Select Organization
              </h2>
              
              <div className="alert alert-info">
                <i className="bi bi-info-circle me-2"></i>
                You belong to multiple organizations. Please select which one to access:
              </div>
              
              <form onSubmit={handleOrgSelection}>
                <div className="mb-3">
                  <label className="form-label">Select Organization</label>
                  <select 
                    className="form-select" 
                    value={selectedOrgId} 
                    onChange={e => setSelectedOrgId(e.target.value)}
                    required
                  >
                    <option value="">Choose an organization...</option>
                    {multipleOrgs?.map(org => (
                      <option key={org.id} value={org.id}>
                        {org.name} ({org.role})
                      </option>
                    ))}
                  </select>
                </div>
                
                {error && <div className="alert alert-danger">{error}</div>}
                
                <div className="d-grid">
                  <button className="btn btn-primary" type="submit" disabled={loading}>
                    {loading ? <LoadingSpinner size="sm" /> : 'Continue'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      <NotificationSystem />
    </div>
  );
}

export default MagicLoginPage;
