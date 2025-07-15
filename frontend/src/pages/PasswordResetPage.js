import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrl';

function PasswordResetPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState('');

  useEffect(() => {
    const tokenFromUrl = searchParams.get('token');
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    } else {
      setError('Invalid or missing reset token');
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      const res = await axios.post(`${getApiUrl()}/auth/password-reset`, {
        token,
        password
      });

      setSuccess(res.data.msg);
      setPassword('');
      setConfirmPassword('');
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      
    } catch (err) {
      console.error('Password reset error:', err);
      setError(err.response?.data?.msg || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <h2 className="card-title text-center mb-4">
                <i className="bi bi-shield-lock me-2"></i>
                Reset Password
              </h2>
              
              {!token ? (
                <div className="text-center">
                  <div className="alert alert-danger">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    Invalid or missing reset token
                  </div>
                  <button 
                    className="btn btn-primary" 
                    onClick={handleBackToLogin}
                  >
                    Back to Login
                  </button>
                </div>
              ) : success ? (
                <div className="text-center">
                  <div className="alert alert-success">
                    <i className="bi bi-check-circle me-2"></i>
                    {success}
                  </div>
                  <div className="alert alert-info">
                    <i className="bi bi-info-circle me-2"></i>
                    Redirecting to login page in 3 seconds...
                  </div>
                  <button 
                    className="btn btn-primary" 
                    onClick={handleBackToLogin}
                  >
                    Go to Login Now
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label className="form-label">New Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={password} 
                      onChange={e => setPassword(e.target.value)} 
                      required 
                      disabled={loading}
                      minLength="6"
                      placeholder="Enter your new password"
                    />
                    <div className="form-text">
                      Password must be at least 6 characters long
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Confirm New Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={confirmPassword} 
                      onChange={e => setConfirmPassword(e.target.value)} 
                      required 
                      disabled={loading}
                      minLength="6"
                      placeholder="Confirm your new password"
                    />
                  </div>
                  
                  {error && <div className="alert alert-danger">{error}</div>}
                  
                  <div className="d-grid gap-2">
                    <button className="btn btn-primary" type="submit" disabled={loading || !token}>
                      {loading ? <Spinner size={20} /> : 'Reset Password'}
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
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PasswordResetPage;
