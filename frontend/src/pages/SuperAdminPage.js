import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../utils/apiUrl';
import { useNavigate } from 'react-router-dom';

function SuperAdminPage() {
  const [overview, setOverview] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [orgDetails, setOrgDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const isSuperAdmin = localStorage.getItem('super_admin') === 'true';

  useEffect(() => {
    if (!isSuperAdmin) {
      navigate('/dashboard');
      return;
    }
    loadOverview();
  }, [isSuperAdmin, navigate]);

  const loadOverview = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/overview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOverview(data);
      } else {
        setError('Failed to load overview');
      }
    } catch (err) {
      setError('Error loading overview');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadOrgDetails = async (orgId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/organization/${orgId}/details`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrgDetails(data);
        setSelectedOrg(orgId);
      } else {
        setError('Failed to load organization details');
      }
    } catch (err) {
      setError('Error loading organization details');
      console.error(err);
    }
  };

  const searchUsers = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/users/search?q=${encodeURIComponent(searchTerm)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.users);
      } else {
        setError('Failed to search users');
      }
    } catch (err) {
      setError('Error searching users');
      console.error(err);
    }
  };

  const troubleshootUser = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/troubleshoot/user/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('User troubleshooting data:', data);
        // Could open a modal or navigate to a detailed view
        alert(`User troubleshooting data logged to console for ${data.user.username}`);
      } else {
        setError('Failed to troubleshoot user');
      }
    } catch (err) {
      setError('Error troubleshooting user');
      console.error(err);
    }
  };

  if (!isSuperAdmin) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger">
          <h4>Access Denied</h4>
          <p>Super Admin access required.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-12">
          <h2 className="mb-4">
            <i className="bi bi-shield-check me-2"></i>
            Super Admin Dashboard
          </h2>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Overview Stats */}
      {overview && (
        <div className="row mb-4">
          <div className="col-md-3">
            <div className="card text-center">
              <div className="card-body">
                <h5 className="card-title">Total Organizations</h5>
                <h3 className="text-primary">{overview.stats.total_organizations}</h3>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card text-center">
              <div className="card-body">
                <h5 className="card-title">Total Users</h5>
                <h3 className="text-success">{overview.stats.total_users}</h3>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card text-center">
              <div className="card-body">
                <h5 className="card-title">Total Events</h5>
                <h3 className="text-info">{overview.stats.total_events}</h3>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card text-center">
              <div className="card-body">
                <h5 className="card-title">Active Today</h5>
                <h3 className="text-warning">-</h3>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* User Search */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-search me-2"></i>
                User Search & Troubleshooting
              </h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-8">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search users by username, name, or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && searchUsers()}
                  />
                </div>
                <div className="col-md-4">
                  <button className="btn btn-primary" onClick={searchUsers}>
                    Search Users
                  </button>
                </div>
              </div>
              
              {searchResults.length > 0 && (
                <div className="mt-3">
                  <h6>Search Results:</h6>
                  <div className="table-responsive">
                    <table className="table table-sm">
                      <thead>
                        <tr>
                          <th>Username</th>
                          <th>Name</th>
                          <th>Email</th>
                          <th>Organizations</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.map(user => (
                          <tr key={user.id}>
                            <td>{user.username}</td>
                            <td>{user.name}</td>
                            <td>{user.email}</td>
                            <td>
                              {user.organizations.map(org => (
                                <span key={org.id} className="badge bg-secondary me-1">
                                  {org.name} ({org.role})
                                </span>
                              ))}
                            </td>
                            <td>
                              <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => troubleshootUser(user.id)}
                              >
                                <i className="bi bi-bug me-1"></i>
                                Troubleshoot
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Organizations Overview */}
      {overview && (
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-building me-2"></i>
                  Organizations Overview
                </h5>
              </div>
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Organization</th>
                        <th>Users</th>
                        <th>Events</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overview.organizations.map(org => (
                        <tr key={org.id}>
                          <td>
                            <strong>{org.name}</strong>
                          </td>
                          <td>
                            <span className="badge bg-primary">{org.user_count}</span>
                          </td>
                          <td>
                            <span className="badge bg-info">{org.event_count}</span>
                          </td>
                          <td>
                            {org.created_at ? new Date(org.created_at).toLocaleDateString() : 'N/A'}
                          </td>
                          <td>
                            <button 
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => loadOrgDetails(org.id)}
                            >
                              <i className="bi bi-eye me-1"></i>
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Organization Details Modal */}
      {selectedOrg && orgDetails && (
        <div className="modal show d-block" tabIndex="-1" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-building me-2"></i>
                  {orgDetails.organization.name} Details
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => {setSelectedOrg(null); setOrgDetails(null);}}
                ></button>
              </div>
              <div className="modal-body">
                <div className="row">
                  <div className="col-md-6">
                    <h6>Users ({orgDetails.users.length})</h6>
                    <div className="table-responsive" style={{maxHeight: '300px', overflowY: 'auto'}}>
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Email</th>
                          </tr>
                        </thead>
                        <tbody>
                          {orgDetails.users.map(user => (
                            <tr key={user.id}>
                              <td>{user.username}</td>
                              <td>
                                <span className={`badge ${user.role === 'Admin' ? 'bg-warning' : 'bg-secondary'}`}>
                                  {user.role}
                                </span>
                              </td>
                              <td>{user.email}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <h6>Recent Events ({orgDetails.events.length})</h6>
                    <div className="table-responsive" style={{maxHeight: '300px', overflowY: 'auto'}}>
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Title</th>
                            <th>Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {orgDetails.events.map(event => (
                            <tr key={event.id}>
                              <td>{event.title}</td>
                              <td>{new Date(event.date).toLocaleDateString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {setSelectedOrg(null); setOrgDetails(null);}}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SuperAdminPage;
