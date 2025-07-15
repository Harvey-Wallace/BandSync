import React, { useState } from 'react';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrl';

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [organization, setOrganization] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await axios.post(`${getApiUrl()}/auth/register`, { username, email, password, organization });
      setSuccess('Registration successful! You can now log in.');
      setError('');
      setLoading(false);
    } catch (err) {
      // Get the actual error message from backend
      const errorMessage = err.response?.data?.msg || 'Registration failed.';
      setError(errorMessage);
      setSuccess('');
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label>Username</label>
          <input className="form-control" value={username} onChange={e => setUsername(e.target.value)} required />
        </div>
        <div className="mb-3">
          <label>Email</label>
          <input type="email" className="form-control" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="mb-3">
          <label>Password</label>
          <input type="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <div className="mb-3">
          <label>Organization</label>
          <input className="form-control" value={organization} onChange={e => setOrganization(e.target.value)} required placeholder="Enter or create your organization name" />
        </div>
        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        <button className="btn btn-primary" type="submit" disabled={loading}>Register</button>
        {loading && <Spinner size={30} />}
      </form>
      <p className="mt-3">Already have an account? <a href="/login">Login</a></p>
    </div>
  );
}

export default RegisterPage;
