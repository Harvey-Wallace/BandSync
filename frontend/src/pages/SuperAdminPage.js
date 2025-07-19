import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../utils/apiUrl';
import { useNavigate } from 'react-router-dom';

function SuperAdminPage() {
  const [overview, setOverview] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [orgDetails, setOrgDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [bulkOperation, setBulkOperation] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
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
    loadSystemHealth();
  }, [isSuperAdmin, navigate]);

  const loadSystemHealth = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/system/health`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data);
      }
    } catch (err) {
      console.error('Error loading system health:', err);
    }
  };

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

  const resetUserPassword = async (userId, username) => {
    if (!window.confirm(`Reset password for ${username}? This will generate a temporary password.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/user/${userId}/reset-password`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Password reset for ${username}!\nNew password: ${data.new_password}\n\nUser will need to change this on next login.`);
      } else {
        setError('Failed to reset password');
      }
    } catch (err) {
      setError('Error resetting password');
      console.error(err);
    }
  };

  const impersonateUser = async (userId, username) => {
    if (!window.confirm(`Impersonate user ${username}? This will log you in as them.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/user/${userId}/impersonate`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Store the impersonation token
        localStorage.setItem('token', data.impersonation_token);
        localStorage.setItem('organization', data.organization.name);
        localStorage.setItem('organization_id', data.organization.id);
        localStorage.setItem('role', data.role);
        localStorage.setItem('impersonating', 'true');
        localStorage.setItem('original_admin', 'Harvey258');
        
        alert(`Now impersonating ${username}. You can return to Super Admin mode by logging out and back in.`);
        window.location.href = '/dashboard';
      } else {
        setError('Failed to impersonate user');
      }
    } catch (err) {
      setError('Error impersonating user');
      console.error(err);
    }
  };

  const handleBulkOperation = async () => {
    if (!bulkOperation || selectedUsers.length === 0) {
      alert('Please select an operation and at least one user.');
      return;
    }

    const operationNames = {
      'disable': 'disable',
      'enable': 'enable', 
      'reset_passwords': 'reset passwords for',
      'delete': 'delete'
    };

    if (!window.confirm(`${operationNames[bulkOperation]} ${selectedUsers.length} users?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/users/bulk-operations`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          operation: bulkOperation,
          user_ids: selectedUsers
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Bulk operation completed!\n${data.results.join('\n')}`);
        setSelectedUsers([]);
        setBulkOperation('');
        // Refresh search results
        if (searchTerm) {
          searchUsers();
        }
      } else {
        setError('Failed to perform bulk operation');
      }
    } catch (err) {
      setError('Error performing bulk operation');
      console.error(err);
    }
  };

  const toggleUserSelection = (userId) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
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

          {/* Navigation Tabs */}
          <ul className="nav nav-tabs mb-4">
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <i className="bi bi-graph-up me-1"></i>
                Overview
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'users' ? 'active' : ''}`}
                onClick={() => setActiveTab('users')}
              >
                <i className="bi bi-people me-1"></i>
                User Management
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'system' ? 'active' : ''}`}
                onClick={() => setActiveTab('system')}
              >
                <i className="bi bi-cpu me-1"></i>
                System Health
              </button>
            </li>
          </ul>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && overview && (
        <>
          {/* Overview Stats */}
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
                  <h5 className="card-title">System Status</h5>
                  <h3 className={`${systemHealth?.status === 'healthy' ? 'text-success' : 'text-warning'}`}>
                    {systemHealth?.status === 'healthy' ? '✅ Healthy' : '⚠️ Limited'}
                  </h3>
                </div>
              </div>
            </div>
          </div>

          {/* Organizations Overview */}
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
        </>
      )}

      {/* User Management Tab */}
      {activeTab === 'users' && (
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-search me-2"></i>
                  User Search & Management
                </h5>
              </div>
              <div className="card-body">
                <div className="row mb-3">
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
                  <>
                    {/* Bulk Operations */}
                    <div className="row mb-3">
                      <div className="col-md-4">
                        <select 
                          className="form-select"
                          value={bulkOperation}
                          onChange={(e) => setBulkOperation(e.target.value)}
                        >
                          <option value="">Select Bulk Operation...</option>
                          <option value="disable">Disable Users</option>
                          <option value="enable">Enable Users</option>
                          <option value="reset_passwords">Reset Passwords</option>
                          <option value="delete">Delete Users</option>
                        </select>
                      </div>
                      <div className="col-md-4">
                        <button 
                          className="btn btn-warning"
                          onClick={handleBulkOperation}
                          disabled={!bulkOperation || selectedUsers.length === 0}
                        >
                          Execute on {selectedUsers.length} users
                        </button>
                      </div>
                      <div className="col-md-4">
                        <small className="text-muted">
                          {selectedUsers.length} users selected
                        </small>
                      </div>
                    </div>

                    <div className="table-responsive">
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>
                              <input 
                                type="checkbox" 
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedUsers(searchResults.map(u => u.id));
                                  } else {
                                    setSelectedUsers([]);
                                  }
                                }}
                                checked={selectedUsers.length === searchResults.length && searchResults.length > 0}
                              />
                            </th>
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
                              <td>
                                <input 
                                  type="checkbox"
                                  checked={selectedUsers.includes(user.id)}
                                  onChange={() => toggleUserSelection(user.id)}
                                />
                              </td>
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
                                <div className="btn-group btn-group-sm">
                                  <button 
                                    className="btn btn-outline-primary"
                                    onClick={() => troubleshootUser(user.id)}
                                    title="Troubleshoot"
                                  >
                                    <i className="bi bi-bug"></i>
                                  </button>
                                  <button 
                                    className="btn btn-outline-warning"
                                    onClick={() => resetUserPassword(user.id, user.username)}
                                    title="Reset Password"
                                  >
                                    <i className="bi bi-key"></i>
                                  </button>
                                  <button 
                                    className="btn btn-outline-info"
                                    onClick={() => impersonateUser(user.id, user.username)}
                                    title="Impersonate User"
                                  >
                                    <i className="bi bi-person-badge"></i>
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Health Tab */}
      {activeTab === 'system' && systemHealth && (
        <div className="row">
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-cpu me-2"></i>
                  System Status
                </h5>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>Overall Status:</strong>
                  <span className={`ms-2 badge ${systemHealth.status === 'healthy' ? 'bg-success' : 'bg-warning'}`}>
                    {systemHealth.status}
                  </span>
                </div>
                
                <div className="mb-3">
                  <strong>Database:</strong>
                  <div className="ms-3">
                    <div>Status: <span className="badge bg-success">{systemHealth.database.status}</span></div>
                    {systemHealth.database.response_time_ms && (
                      <div>Response Time: {systemHealth.database.response_time_ms}ms</div>
                    )}
                  </div>
                </div>

                {systemHealth.system && (
                  <div className="mb-3">
                    <strong>System Metrics:</strong>
                    <div className="ms-3">
                      <div>CPU: {systemHealth.system.cpu_percent}%</div>
                      <div>Memory: {systemHealth.system.memory_percent}%</div>
                      <div>Disk: {systemHealth.system.disk_percent}%</div>
                    </div>
                  </div>
                )}

                <div className="mb-3">
                  <strong>Recent Activity (24h):</strong>
                  <div className="ms-3">
                    <div>Logins: {systemHealth.activity?.recent_logins_24h || 0}</div>
                    <div>Events Created: {systemHealth.activity?.recent_events_24h || 0}</div>
                  </div>
                </div>

                <small className="text-muted">
                  Last updated: {new Date(systemHealth.timestamp).toLocaleString()}
                </small>
              </div>
            </div>
          </div>
          
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-speedometer2 me-2"></i>
                  Quick Actions
                </h5>
              </div>
              <div className="card-body">
                <div className="d-grid gap-2">
                  <button 
                    className="btn btn-outline-primary"
                    onClick={loadSystemHealth}
                  >
                    <i className="bi bi-arrow-clockwise me-2"></i>
                    Refresh System Health
                  </button>
                  
                  <button 
                    className="btn btn-outline-info"
                    onClick={() => window.open('/api/super-admin/system/logs', '_blank')}
                  >
                    <i className="bi bi-file-text me-2"></i>
                    View System Logs
                  </button>
                  
                  <button 
                    className="btn btn-outline-warning"
                    onClick={() => {
                      if (window.confirm('This will log you out. Continue?')) {
                        localStorage.clear();
                        window.location.href = '/login';
                      }
                    }}
                  >
                    <i className="bi bi-box-arrow-right me-2"></i>
                    Emergency Logout
                  </button>
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
